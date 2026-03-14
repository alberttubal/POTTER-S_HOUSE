from unittest.mock import patch 
 
from django.core.files.uploadedfile import SimpleUploadedFile 
from rest_framework.test import APITestCase 
 
from admin_users.models import AdminUser 
 
UPLOAD_URL = '/api/v1/admin/uploads/' 

class UploadCreateAdminTests(APITestCase): 
    def setUp(self): 
        self.admin = AdminUser.objects.create_superuser( 
            email='admin@example.com', 
            password='AdminPass123!', 
            full_name='Admin User', 
        ) 
        self.client.force_authenticate(user=self.admin) 

    @patch('uploads.views.upload_fileobj') 
    @patch('uploads.views.build_public_url') 
    def test_upload_create_includes_published_flag(self, build_public_url, upload_fileobj): 
        build_public_url.return_value = 'https://cdn.example.com/test.png' 
        upload_fileobj.return_value = None 
        file_obj = SimpleUploadedFile('test.png', b'fake', content_type='image/png') 
 
        resp = self.client.post(UPLOAD_URL, {'files': [file_obj]}, format='multipart') 
 
        self.assertEqual(resp.status_code, 201) 
        self.assertEqual(len(resp.data['urls']), 1) 
        item = resp.data['urls'][0] 
        self.assertIn('published', item) 
        self.assertFalse(item['published']) 
        self.assertIsNone(item['alt_text'])
 
from uploads.models import Upload 
 
class UploadPublishValidationTests(APITestCase): 
    def setUp(self): 
        self.admin = AdminUser.objects.create_superuser( 
            email='admin2@example.com', 
            password='AdminPass123!', 
            full_name='Admin User', 
        ) 
        self.client.force_authenticate(user=self.admin) 
 
    def test_publish_requires_alt_text(self): 
        upload = Upload.objects.create( 
            key='test-key', 
            url='https://cdn.example.com/test.png', 
            size=123, 
            mime_type='image/png', 
            alt_text=None, 
            published=False, 
        ) 
        resp = self.client.patch( 
            f'/api/v1/admin/uploads/{upload.id}/', 
            {'published': True}, 
            format='json', 
        ) 
        self.assertEqual(resp.status_code, 400) 
        self.assertEqual(resp.data['error']['code'], 'validation_error') 
        fields = [item.get('field') for item in resp.data['error']['details']] 
        self.assertIn('alt_text', fields)
