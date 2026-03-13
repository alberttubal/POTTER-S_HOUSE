from django.utils import timezone 
from rest_framework import serializers 
from packages.models import Package 
from .models import Booking 
 
class BookingBaseSerializer(serializers.ModelSerializer): 
    event_all_day = serializers.BooleanField(required=True)
    package_id = serializers.PrimaryKeyRelatedField( 
        source='package', 
        queryset=Package.objects.all(), 
        required=False, 
        allow_null=True, 
    ) 

    class Meta: 
        model = Booking 
        fields = [ 
            'id', 
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
            'notes', 
            'status',
            'workflow_status', 
            'deposit_paid', 
            'created_at', 
            'updated_at', 
        ] 
        read_only_fields = ['id', 'created_at', 'updated_at'] 

    def validate(self, attrs): 
        now = timezone.now() 
        instance = getattr(self, 'instance', None) 
 
        start = attrs.get('event_date_start', getattr(instance, 'event_date_start', None)) 
        end = attrs.get('event_date_end', getattr(instance, 'event_date_end', None)) 

        start_changed = instance is None or 'event_date_start' in attrs and start != instance.event_date_start 

        if start and start_changed and start < now:
            raise serializers.ValidationError( 
                {'event_date_start': 'event_date_start cannot be in the past.'} 
            )
        if start and end and end < start:
            raise serializers.ValidationError( 
                {'event_date_end': 'event_date_end must be after or equal to event_date_start.'} 
            )
        return attrs 
 

class BookingSerializer(BookingBaseSerializer): 
    honeypot = serializers.CharField(write_only=True, required=True, allow_blank=True) 

    class Meta(BookingBaseSerializer.Meta): 
        fields = BookingBaseSerializer.Meta.fields + ['honeypot'] 
        read_only_fields = ['id', 'status', 'workflow_status', 'created_at', 'updated_at'] 

    def validate_honeypot(self, value): 
        if value: 
            raise serializers.ValidationError('Honeypot field must be empty.') 
        return value 
 
    def create(self, validated_data): 
        validated_data.pop('honeypot', None) 
        return super().create(validated_data) 
 

class BookingAdminSerializer(BookingBaseSerializer): 
    class Meta(BookingBaseSerializer.Meta): 
        read_only_fields = ['id', 'created_at', 'updated_at']
