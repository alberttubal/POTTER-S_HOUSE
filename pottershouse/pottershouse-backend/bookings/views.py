from django.db import transaction, IntegrityError
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import connection
from .models import Booking
from .serializers import BookingSerializer
from core.utils import error_response
from email_outbox.models import EmailOutbox
from rest_framework.response import Response

class BookingCreatePublic(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                code="validation_error",
                message="Validation failed",
                details=[
                    {"field": k, "message": v[0]} for k, v in serializer.errors.items()
                ],
                status=400,
            )

        try:
            with transaction.atomic():
                booking = serializer.save(status="confirmed", workflow_status="new")

                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO bookings_confirmed_ranges (booking_id, event_range)
                        VALUES (%s, tstzrange(%s, %s, '[)'))
                        """,
                        [str(booking.id), booking.event_date_start, booking.event_date_end],
                    )

                EmailOutbox.queue_booking_email(booking)

        except IntegrityError:
            return error_response(
                code="booking_conflict",
                message="Requested time conflicts with an existing booking.",
                details=[],
                status=409,
                conflictingBookings=[],
                suggested_alternatives=[],
            )

        return Response(BookingSerializer(booking).data, status=201)


class BookingAdminList(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.all().order_by("-created_at")

class BookingAdminDetail(generics.RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()
