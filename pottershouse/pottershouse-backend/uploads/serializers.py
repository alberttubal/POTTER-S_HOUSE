from rest_framework import serializers 
from .models import Upload 
 
class UploadSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Upload 
        fields = [ 
            'id', 'key', 'url', 'size', 'mime_type', 
            'alt_text', 'published', 'created_at', 'updated_at', 
        ] 
        read_only_fields = ['id', 'created_at', 'updated_at'] 
 
    def validate(self, attrs): 
        published = attrs.get('published', getattr(self.instance, 'published', False)) 
        alt_text = attrs.get('alt_text', getattr(self.instance, 'alt_text', None)) 
        if published and not alt_text: 
            raise serializers.ValidationError( 
                {'alt_text': 'alt_text is required before publishing an image.'} 
            ) 
        return attrs 
 
 
class UploadRequestSerializer(serializers.Serializer): 
    filename = serializers.CharField() 
    mime_type = serializers.CharField() 
    size = serializers.IntegerField()
