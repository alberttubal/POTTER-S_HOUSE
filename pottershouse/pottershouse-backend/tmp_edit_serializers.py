import re
from pathlib import Path

path = Path('bookings/serializers.py')
text = path.read_text()
text = re.sub(r'\n\s{8}def validate\(self, attrs\):.*?return attrs\n', '\n', text, flags=re.S)

if '    def validate(self, attrs):' not in text:
    insert = (
        \"    def validate(self, attrs):\n\" )
        \"        now = timezone.now()\n\" )
        \"        instance = getattr(self, 'instance', None)\n\" )
        \"\n\" )
        \"        start = attrs.get('event_date_start', getattr(instance, 'event_date_start', None))\n\" )
        \"        end = attrs.get('event_date_end', getattr(instance, 'event_date_end', None))\n\" )
        \"\n\" )
        \"        # Only enforce 'start in future' on create or when start changes.\n\" )
        \"        start_changed = instance is None or ('event_date_start' in attrs and start != instance.event_date_start)\n\" )
        \"\n\" )
        \"        if start and start_changed and start < now:\n\" )
        \"            raise serializers.ValidationError(\n\" )
        \"                {'event_date_start': 'event_date_start cannot be in the past.'}\n\" )
        \"            )\n\" )
        \"        if start and end and end < start:\n\" )
        \"            raise serializers.ValidationError(\n\" )
        \"                {'event_date_end': 'event_date_end must be after or equal to event_date_start.'}\n\" )
        \"            )\n\" )
        \"        return attrs\n\" )
        \"\n\" )
    )
    text = text.replace('    event_all_day = serializers.BooleanField(required=True)\n\n', '    event_all_day = serializers.BooleanField(required=True)\n\n' + insert)

path.write_text(text)
