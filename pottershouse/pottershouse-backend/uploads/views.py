import uuid 
from rest_framework import generics 
from rest_framework.permissions import AllowAny
from core.permissions import IsAdminUser, RBACPermission
from rest_framework.parsers import MultiPartParser, FormParser 
from rest_framework.response import Response 
from core.utils import error_response 
from .models import Upload 
from .serializers import UploadSerializer, UploadRequestSerializer 
from .services import validate_upload, upload_fileobj, build_public_url, generate_presigned_url
 
class UploadCreateAdmin(generics.GenericAPIView): 
    parser_classes = [MultiPartParser, FormParser] 
    permission_classes = [IsAdminUser, RBACPermission]
    permission_map = {"POST": "uploads.add_upload"}

    def post(self, request, *args, **kwargs): 
        files = request.FILES.getlist('files') 
        if not files: 
            return error_response( 
                'validation_error', 
                'Validation failed', 
                details=[{'field': 'files', 'message': 'At least one file is required.'}], 
                status=400, 
            ) 
 
        for f in files: 
            try: 
                validate_upload(f.content_type, f.size) 
            except ValueError as e: 
                if str(e) == 'invalid_mime_type': 
                    return error_response('invalid_file_type', 'Invalid file type', details=[], status=400) 
                if str(e) == 'file_too_large': 
                    return error_response('file_too_large', 'File exceeds max size', details=[], status=413) 
 
        urls = [] 
        for f in files: 
            key = f'{uuid.uuid4()}-{f.name}' 
            try:
                upload_fileobj(f, key, f.content_type)
            except Exception:
                return error_response(
                        'upload_failed',
                        'Upload failed',
                        details=[],
                        status=500,
                        )
            public_url = build_public_url(key) 
            Upload.objects.create( 
                key=key, 
                url=public_url, 
                size=f.size, 
                mime_type=f.content_type, 
                alt_text=None, 
                published=False, 
            ) 
            urls.append({'url': public_url, 'key': key, 'size': f.size, 'alt_text': None, 'published': False}) 
 
        return Response({'urls': urls}, status=201) 
 
class UploadPresignAdmin(generics.GenericAPIView):
    serializer_class = UploadRequestSerializer
    permission_classes = [IsAdminUser, RBACPermission]
    permission_map = {"POST": "uploads.add_upload"}

    def post(self, request, *args, **kwargs):
        files = request.data.get("files")
        if not isinstance(files, list) or not files:
            return error_response(
                "validation_error",
                "Validation failed",
                details=[{"field": "files", "message": "At least one file is required."}],
                status=400,
            )

        urls = []
        for item in files:
            serializer = UploadRequestSerializer(data=item)
            if not serializer.is_valid():
                return error_response(
                    "validation_error",
                    "Validation failed",
                    details=[{"field": k, "message": v} for k, v in serializer.errors.items()],
                    status=400,
                )

            file_data = serializer.validated_data
            try:
                validate_upload(file_data["mime_type"], file_data["size"])
            except ValueError as e:
                if str(e) == "invalid_mime_type":
                    return error_response("invalid_file_type", "Invalid file type", details=[], status=400)
                if str(e) == "file_too_large":
                    return error_response("file_too_large", "File exceeds max size", details=[], status=413)

            key = str(uuid.uuid4()) + "-" + file_data["filename"]
            upload_url = generate_presigned_url(key, file_data["mime_type"])
            public_url = build_public_url(key)

            Upload.objects.create(
                key=key,
                url=public_url,
                size=file_data["size"],
                mime_type=file_data["mime_type"],
                alt_text=None,
                published=False,
            )

            urls.append({
                "url": public_url,
                "upload_url": upload_url,
                "key": key,
                "size": file_data["size"],
                "alt_text": None,
                "published": False,
            })

        return Response({"urls": urls}, status=201)


class GalleryPublic(generics.ListAPIView): 
    serializer_class = UploadSerializer 
    permission_classes = [AllowAny] 
    queryset = Upload.objects.filter(published=True).order_by('-created_at')


class UploadAdminList(generics.ListAPIView):
    serializer_class = UploadSerializer
    permission_classes = [IsAdminUser, RBACPermission]
    permission_map = {"GET": "uploads.view_upload"}
    queryset = Upload.objects.all().order_by("-created_at")

class UploadAdminDetail(generics.RetrieveUpdateAPIView):
    serializer_class = UploadSerializer
    permission_classes = [IsAdminUser, RBACPermission]
    permission_map = {"GET": "uploads.view_upload", "PUT": "uploads.change_upload", "PATCH": "uploads.change_upload"}
    queryset = Upload.objects.all()