from datetime import datetime, time

from django.conf import settings
from django.db import connection, transaction, IntegrityError, DatabaseError
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.pagination import StandardResultsSetPagination
from core.permissions import IsAdminUser
from core.ratelimit import rate_limit
from core.utils import error_response, request_hash
from email_outbox.models import EmailOutbox
from idempotency_keys.models import IdempotencyKey
from .models import Booking
from .serializers import BookingSerializer, BookingAdminSerializer


def _store_idempotency_response(idem_key, request_hash, response, extra_headers=None):
    headers = extra_headers or {}
    IdempotencyKey.objects.create(
        key=idem_key,
        request_hash=request_hash,
        response_status=response.status_code,
        response_body=response.data,
        response_headers=headers,
        expires_at=IdempotencyKey.ttl_expires_at(),
    )


def _is_exclusion_violation(exc):
    # PostgreSQL SQLSTATE 23P01 = exclusion_violation
    if getattr(exc, "pgcode", None) == "23P01":
        return True
    cause = getattr(exc, "__cause__", None)
    return getattr(cause, "pgcode", None) == "23P01"


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

        with transaction.atomic():
            # Serialize same-key requests inside the DB transaction.
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", [idem_key])

            existing = IdempotencyKey.objects.select_for_update().filter(key=idem_key).first()
            if existing and existing.expires_at <= timezone.now():
                existing.delete()
                existing = None

            if existing:
                if existing.request_hash != payload_hash:
                    response = error_response(
                        code="idempotency_key_payload_mismatch",
                        message="Idempotency key payload mismatch.",
                        details=[{"field": None, "message": "Idempotency key already used with a different payload."}],
                        status=400,
                    )
                else:
                    response = Response(existing.response_body, status=existing.response_status)
                    if existing.response_headers:
                        for header, value in existing.response_headers.items():
                            response[header] = value
                return response

            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                response = error_response(
                    code="validation_error",
                    message="Validation failed",
                    details=[{"field": k, "message": v} for k, v in serializer.errors.items()],
                    status=400,
                )
                _store_idempotency_response(idem_key, payload_hash, response)
                return response

            try:
                # Save booking inside a nested transaction so we can still record idempotency on conflict.
                with transaction.atomic():
                    booking = serializer.save(status="confirmed", workflow_status="new")

                    with connection.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO bookings_confirmed_ranges (booking_id, event_range) VALUES (%s, tstzrange(%s, %s, '[)'))",
                            [str(booking.id), booking.event_date_start, booking.event_date_end],
                        )

                    EmailOutbox.queue_booking_email(booking)

                    response_data = BookingSerializer(booking).data
                    response = Response(response_data, status=201)
                    location = f"/api/v1/admin/bookings/{booking.id}/"
                    response["Location"] = location
                    _store_idempotency_response(
                        idem_key,
                        payload_hash,
                        response,
                        extra_headers={"Location": location},
                    )
                    return response

            except (IntegrityError, DatabaseError) as exc:
                if not _is_exclusion_violation(exc):
                    raise
                response = error_response(
                    code="booking_conflict",
                    message="Requested time conflicts with an existing booking.",
                    details=[],
                    status=409,
                    conflictingBookings=[],
                    suggested_alternatives=[],
                )
                _store_idempotency_response(idem_key, payload_hash, response)
                return response


class BookingAdminList(generics.ListAPIView):
    serializer_class = BookingAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def _default_tz(self):
        return timezone.get_default_timezone()

    def _parse_dt(self, raw_value, is_end):
        if not raw_value:
            return None
        dt = parse_datetime(raw_value)
        if dt:
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, self._default_tz())
            return dt
        date_value = parse_date(raw_value)
        if date_value:
            t_value = time.max if is_end else time.min
            dt = datetime.combine(date_value, t_value)
            return timezone.make_aware(dt, self._default_tz())
        raise ValueError("Invalid datetime format")

    def _filtered_queryset(self, request):
        qs = Booking.objects.all().order_by("-created_at")
        q_value = request.query_params.get("q")
        if q_value:
            qs = qs.filter(
                Q(customer_name__icontains=q_value)
                | Q(email__icontains=q_value)
                | Q(phone__icontains=q_value)
            )

        status_value = request.query_params.get("status")
        if status_value:
            status_values = {choice[0] for choice in Booking.STATUS_CHOICES}
            workflow_values = {choice[0] for choice in Booking.WORKFLOW_CHOICES}
            if status_value in status_values:
                qs = qs.filter(status=status_value)
            elif status_value in workflow_values:
                qs = qs.filter(workflow_status=status_value)
            else:
                return None, error_response(
                    code="validation_error",
                    message="Validation failed",
                    details=[{"field": "status", "message": "Invalid status value."}],
                    status=400,
                )

        try:
            from_dt = self._parse_dt(request.query_params.get("from"), is_end=False)
        except ValueError:
            return None, error_response(
                code="validation_error",
                message="Validation failed",
                details=[{"field": "from", "message": "Invalid datetime value."}],
                status=400,
            )

        try:
            to_dt = self._parse_dt(request.query_params.get("to"), is_end=True)
        except ValueError:
            return None, error_response(
                code="validation_error",
                message="Validation failed",
                details=[{"field": "to", "message": "Invalid datetime value."}],
                status=400,
            )

        if from_dt:
            qs = qs.filter(event_date_start__gte=from_dt)
        if to_dt:
            qs = qs.filter(event_date_end__lte=to_dt)

        return qs, None

    def list(self, request, *args, **kwargs):
        qs, error = self._filtered_queryset(request)
        if error:
            return error
        self.queryset = qs
        return super().list(request, *args, **kwargs)


class BookingAdminDetail(generics.RetrieveUpdateAPIView):
    serializer_class = BookingAdminSerializer
    permission_classes = [IsAdminUser]
    queryset = Booking.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return error_response(
                code="validation_error",
                message="Validation failed",
                details=[{"field": k, "message": v} for k, v in serializer.errors.items()],
                status=400,
            )

        new_status = serializer.validated_data.get("status", instance.status)
        new_start = serializer.validated_data.get("event_date_start", instance.event_date_start)
        new_end = serializer.validated_data.get("event_date_end", instance.event_date_end)
        range_changed = new_start != instance.event_date_start or new_end != instance.event_date_end

        try:
            with transaction.atomic():
                if new_status == "confirmed":
                    if instance.status != "confirmed" or range_changed:
                        with connection.cursor() as cursor:
                            cursor.execute("DELETE FROM bookings_confirmed_ranges WHERE booking_id = %s", [str(instance.id)])
                            cursor.execute(
                                "INSERT INTO bookings_confirmed_ranges (booking_id, event_range) VALUES (%s, tstzrange(%s, %s, '[)'))",
                                [str(instance.id), new_start, new_end]
                            )
                elif instance.status == "confirmed" and new_status == "cancelled":
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM bookings_confirmed_ranges WHERE booking_id = %s", [str(instance.id)])

                booking = serializer.save()
        except (IntegrityError, DatabaseError) as exc:
            if not _is_exclusion_violation(exc):
                raise
            return error_response(
                code="booking_conflict",
                message="Requested time conflicts with an existing booking.",
                details=[],
                status=409,
                conflictingBookings=[],
                suggested_alternatives=[],
            )

        return Response(BookingSerializer(booking).data, status=200)
