from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0002_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE bookings_confirmed_ranges
            ADD CONSTRAINT bookings_confirmed_ranges_booking_id_fk
            FOREIGN KEY (booking_id)
            REFERENCES bookings(id)
            ON DELETE CASCADE;
            """,
            reverse_sql="""
            ALTER TABLE bookings_confirmed_ranges
            DROP CONSTRAINT IF EXISTS bookings_confirmed_ranges_booking_id_fk;
            """,
        ),
    ]
