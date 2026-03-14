import uuid 
from concurrent.futures import ThreadPoolExecutor 
from datetime import timedelta 
 
from django.db import connections 
from django.test import TransactionTestCase, override_settings 
from django.utils import timezone 
from rest_framework.test import APIClient, APITestCase 
 
from admin_users.models import AdminUser 
from .models import Booking 
 
BOOKING_URL = '/api/v1/bookings/' 
BOOKING_CSV_URL = '/api/v1/admin/bookings.csv' 
 
def booking_payload(): 
    start = timezone.now() + timedelta(days=10) 
    end = start + timedelta(hours=2) 
    return { 
        'customer_name': 'Test User', 
        'phone': '09170000000', 
        'email': 'test@example.com', 
        'event_type': 'wedding', 
        'event_date_start': start.isoformat().replace('+00:00', 'Z'), 
        'event_date_end': end.isoformat().replace('+00:00', 'Z'), 
        'event_all_day': False, 
        'guests': 50, 
        'honeypot': '', 
    }
 
class BookingIdempotencyTests(APITestCase): 
    def test_missing_idempotency_key_returns_400(self): 
        resp = self.client.post(BOOKING_URL, booking_payload(), format='json') 
        self.assertEqual(resp.status_code, 400) 
        self.assertEqual(resp.data['error']['code'], 'missing_idempotency_key') 
 
    def test_idempotency_replay_same_payload(self): 
        payload = booking_payload() 
        idem_key = str(uuid.uuid4()) 
        resp1 = self.client.post(BOOKING_URL, payload, format='json', HTTP_IDEMPOTENCY_KEY=idem_key) 
        resp2 = self.client.post(BOOKING_URL, payload, format='json', HTTP_IDEMPOTENCY_KEY=idem_key) 
        self.assertEqual(resp2.status_code, resp1.status_code) 
        self.assertEqual(resp2.data, resp1.data) 
 
    def test_idempotency_replay_includes_location_header(self): 
        payload = booking_payload() 
        idem_key = str(uuid.uuid4()) 
        resp1 = self.client.post(BOOKING_URL, payload, format='json', HTTP_IDEMPOTENCY_KEY=idem_key) 
        self.assertEqual(resp1.status_code, 201) 
        self.assertTrue(resp1.has_header('Location')) 
        location = resp1['Location'] 
        resp2 = self.client.post(BOOKING_URL, payload, format='json', HTTP_IDEMPOTENCY_KEY=idem_key) 
        self.assertEqual(resp2.status_code, 201) 
        self.assertEqual(resp2['Location'], location) 
 
    def test_idempotency_payload_mismatch(self): 
        payload = booking_payload() 
        idem_key = str(uuid.uuid4()) 
        self.client.post(BOOKING_URL, payload, format='json', HTTP_IDEMPOTENCY_KEY=idem_key) 
        payload2 = dict(payload) 
        payload2['guests'] = payload['guests'] + 1  
        resp = self.client.post(BOOKING_URL, payload2, format='json', HTTP_IDEMPOTENCY_KEY=idem_key) 
        self.assertEqual(resp.status_code, 400) 
        self.assertEqual(resp.data['error']['code'], 'idempotency_key_payload_mismatch')

    @override_settings(BOOKINGS_RATE_LIMIT=1, BOOKINGS_RATE_WINDOW=3600)
    def test_idempotency_replay_rate_limit_includes_retry_after(self):
        payload = booking_payload()
        self.client.post(BOOKING_URL, payload, format='json', HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()))
        rate_key = str(uuid.uuid4())
        resp1 = self.client.post(BOOKING_URL, payload, format='json', HTTP_IDEMPOTENCY_KEY=rate_key)
        self.assertEqual(resp1.status_code, 429)
        self.assertTrue(resp1.has_header('Retry-After'))
        retry_after = resp1['Retry-After']
        resp2 = self.client.post(BOOKING_URL, payload, format='json', HTTP_IDEMPOTENCY_KEY=rate_key)
        self.assertEqual(resp2.status_code, 429)
        self.assertEqual(resp2['Retry-After'], retry_after)
 
class BookingConcurrencyTests(TransactionTestCase): 
    reset_sequences = True 
 
    def _post(self, payload, idem_key): 
        client = APIClient() 
        try: 
            return client.post(BOOKING_URL, payload, format='json', HTTP_IDEMPOTENCY_KEY=idem_key) 
        finally: 
            connections.close_all() 
 
    def test_concurrent_booking_conflict(self): 
        payload = booking_payload() 
        keys = [str(uuid.uuid4()), str(uuid.uuid4())] 
        with ThreadPoolExecutor(max_workers=2) as executor: 
            futures = [executor.submit(self._post, payload, k) for k in keys] 
        statuses = sorted([f.result().status_code for f in futures]) 
        self.assertEqual(statuses, [201, 409]) 
 
class BookingConflictResponseTests(APITestCase): 
    def test_conflict_returns_expected_wrapper(self): 
        payload = booking_payload() 
        resp1 = self.client.post(BOOKING_URL, payload, format='json', HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4())) 
        self.assertEqual(resp1.status_code, 201) 
        resp2 = self.client.post(BOOKING_URL, payload, format='json', HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4())) 
        self.assertEqual(resp2.status_code, 409) 
        error = resp2.data['error'] 
        self.assertEqual(error['code'], 'booking_conflict') 
        self.assertIn('conflictingBookings', error) 
        self.assertIn('suggested_alternatives', error) 
        self.assertIsInstance(error['conflictingBookings'], list) 
        self.assertIsInstance(error['suggested_alternatives'], list)
 
class BookingCSVExportTests(APITestCase): 
    def setUp(self): 
        self.admin = AdminUser.objects.create_superuser( 
            email='admin@example.com', 
            password='AdminPass123!', 
            full_name='Admin User', 
        ) 
        self.client.force_authenticate(user=self.admin) 
        now = timezone.now() 
        self.booking = Booking.objects.create( 
            customer_name='CSV User', 
            phone='09990000000', 
            email='csv@example.com', 
            event_type='wedding', 
            event_date_start=now + timedelta(days=20), 
            event_date_end=now + timedelta(days=20, hours=2), 
            event_all_day=False, 
            guests=10, 
            status='confirmed', 
            workflow_status='new', 
        ) 
 
    def test_csv_export_headers_and_body(self): 
        resp = self.client.get(BOOKING_CSV_URL) 
        self.assertEqual(resp.status_code, 200) 
        self.assertIn('text/csv', resp['Content-Type']) 
        self.assertIn('attachment; filename=bookings.csv', resp['Content-Disposition']) 
        content = resp.content.decode('utf-8').splitlines() 
        expected_header = 'id,created_at,customer_name,phone,email,event_type,event_date_start,event_date_end,event_all_day,guests,package_id,dietary_needs,status,workflow_status,deposit_paid,notes' 
        self.assertEqual(content[0], expected_header) 
        self.assertEqual(len(content), 2) 
 
    def test_csv_export_invalid_status(self): 
        resp = self.client.get(BOOKING_CSV_URL + '?status=bad') 
        self.assertEqual(resp.status_code, 400) 
        self.assertEqual(resp.data['error']['code'], 'validation_error')
