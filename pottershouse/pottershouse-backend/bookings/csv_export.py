import csv
from datetime import datetime, time

from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from core.permissions import IsAdminUser
from rest_framework.views import APIView

from core.utils import error_response
from .models import Booking


class BookingAdminCSV(APIView):
    permission_classes = [IsAdminUser]

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
        raise ValueError('Invalid datetime format')

    def _iso(self, value):
        if not value:
            return ''
        if timezone.is_naive(value):
            value = timezone.make_aware(value, self._default_tz())
        value = timezone.localtime(value, self._default_tz())
        return value.isoformat().replace('+00:00', 'Z')

    def _bool(self, value):
        return 'true' if value else 'false'

    def get(self, request):
        qs = Booking.objects.all().order_by('-created_at')

        q_value = request.query_params.get('q')
        if q_value:
            qs = qs.filter(
                Q(customer_name__icontains=q_value)
                | Q(email__icontains=q_value)
                | Q(phone__icontains=q_value)
            )

        status_value = request.query_params.get('status')
        if status_value:
            status_values = {choice[0] for choice in Booking.STATUS_CHOICES}
            workflow_values = {choice[0] for choice in Booking.WORKFLOW_CHOICES}
            if status_value in status_values:
                qs = qs.filter(status=status_value)
            elif status_value in workflow_values:
                qs = qs.filter(workflow_status=status_value)
            else:
                return error_response(
                    code='validation_error',
                    message='Validation failed',
                    details=[{'field': 'status', 'message': 'Invalid status value.'}],
                    status=400,
                )

        try:
            from_dt = self._parse_dt(request.query_params.get('from'), is_end=False)
        except ValueError:
            return error_response(
                code='validation_error',
                message='Validation failed',
                details=[{'field': 'from', 'message': 'Invalid datetime value.'}],
                status=400,
            )

        try:
            to_dt = self._parse_dt(request.query_params.get('to'), is_end=True)
        except ValueError:
            return error_response(
                code='validation_error',
                message='Validation failed',
                details=[{'field': 'to', 'message': 'Invalid datetime value.'}],
                status=400,
            )

        if from_dt:
            qs = qs.filter(event_date_start__gte=from_dt)
        if to_dt:
            qs = qs.filter(event_date_end__lte=to_dt)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=bookings.csv'

        writer = csv.writer(response)
        writer.writerow(
            [
                'id',
                'created_at',
                'customer_name',
                'phone',
                'email',
                'event_type',
                'event_date_start',
                'event_date_end',
                'event_all_day',
                'guests',
                'package_id',
                'dietary_needs',
                'status',
                'workflow_status',
                'deposit_paid',
                'notes',
            ]
        )

        for booking in qs.iterator():
            writer.writerow(
                [
                    str(booking.id),
                    self._iso(booking.created_at),
                    booking.customer_name,
                    booking.phone,
                    booking.email,
                    booking.event_type,
                    self._iso(booking.event_date_start),
                    self._iso(booking.event_date_end),
                    self._bool(booking.event_all_day),
                    booking.guests,
                    str(booking.package_id) if booking.package_id else '',
                    booking.dietary_needs or '',
                    booking.status,
                    booking.workflow_status,
                    self._bool(booking.deposit_paid),
                    booking.notes or '',
                ]
            )

        return response
