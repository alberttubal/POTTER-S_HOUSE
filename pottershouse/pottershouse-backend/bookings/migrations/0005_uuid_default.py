from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0004_confirmed_ranges_model_state"),
        ("core", "0001_db_extensions"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE bookings ALTER COLUMN id SET DEFAULT gen_random_uuid();",
            reverse_sql="ALTER TABLE bookings ALTER COLUMN id DROP DEFAULT;",
        ),
    ]
