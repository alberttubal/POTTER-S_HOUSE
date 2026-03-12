from django.db import transaction, IntegrityError 
from rest_framework import generics 
from rest_framework.permissions import AllowAny, IsAuthenticated 
from django.db import connection 
from .models import Booking 
from .serializers import BookingSerializer 
from core.utils import error_response, request_hash 
from email_outbox.models import EmailOutbox 
from rest_framework.response import Response 
from idempotency_keys.models import IdempotencyKey 
from django.conf import settings 
from core.ratelimit import rate_limit 
 
 
class BookingCreatePublic(generics.CreateAPIView): 
    serializer_class = BookingSerializer 
    permission_classes = [AllowAny] 
 
    def dispatch(self, request, *args, **kwargs): 
        limiter = rate_limit( 
            "bookings_create",
            limit=getattr(settings, "BOOKINGS_RATE_LIMIT", 60), 
            window_seconds=getattr(settings, "BOOKINGS_RATE_WINDOW", 3600), 
        ) 
        return limiter(super().dispatch)(request, *args, **kwargs) 
    def create(self, request, *args, **kwargs): 
        idem_key = request.headers.get("Idempotency-Key") 
        if not idem_key: 
            return error_response( 
                code="missing_idempotency_key", 
                message="Idempotency-Key header is required.", 
                details=[], 
                status=400, 
            ) 
 
        payload_hash = request_hash(request.data) 
 
        existing = IdempotencyKey.objects.filter(key=idem_key).first() 
        if existing: 
            if existing.request_hash != payload_hash: 
                return error_response( 
                    code="idempotency_key_payload_mismatch", 
                    message="Idempotency key payload mismatch.", 
                    details=[], 
                    status=400, 
                ) 
            return Response(existing.response_body, status=existing.response_status) 
 
        serializer = self.get_serializer(data=request.data) 
        if not serializer.is_valid(): 
            return error_response( 
                code="validation_error", 
                message="Validation failed", 
                details=[ 
                    {"field": k, "message": v} for k, v in serializer.errors.items() 
                ], 
                status=400, 
            ) 
        try: 
            with transaction.atomic(): 
                booking = serializer.save(status="confirmed", workflow_status="new") 
 
                with connection.cursor() as cursor: 
                    cursor.execute( 
                        "INSERT INTO bookings_confirmed_ranges (booking_id, event_range) VALUES (%s, tstzrange(%s, %s, '[)'))", 
                        [str(booking.id), booking.event_date_start, booking.event_date_end], 
                    ) 
 
                EmailOutbox.queue_booking_email(booking) 
 
                response_data = BookingSerializer(booking).data 
                IdempotencyKey.objects.create( 
                    key=idem_key, 
                    request_hash=payload_hash, 
                    response_status=201, 
                    response_body=response_data, 
                    response_headers={}, 
                    expires_at=IdempotencyKey.ttl_expires_at(), 
                ) 
 
        except IntegrityError: 
            return error_response( 
                code="booking_conflict", 
                message="Requested time conflicts with an existing booking.", 
                details=[], 
                status=409, 
                conflictingBookings=[], 
                suggested_alternatives=[], 
            ) 
 
        return Response(response_data, status=201) 

class BookingAdminList(generics.ListAPIView): 
    serializer_class = BookingSerializer 
    permission_classes = [IsAuthenticated] 
 
    def get_queryset(self): 
        return Booking.objects.all().order_by("-created_at") 
 
 
class BookingAdminDetail(generics.RetrieveAPIView): 
    serializer_class = BookingSerializer 
    permission_classes = [IsAuthenticated] 
    queryset = Booking.objects.all()