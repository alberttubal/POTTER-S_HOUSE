from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("admin_users", "0001_initial"),
        ("bookings", "0004_confirmed_ranges_model_state"),
        ("packages", "0001_initial"),
        ("uploads", "0001_initial"),
        ("testimonials", "0001_initial"),
        ("faqs", "0001_initial"),
        ("email_outbox", "0002_outbox_fields"),
        ("settings_app", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE IF EXISTS admin_users ALTER COLUMN id SET DEFAULT gen_random_uuid();
            ALTER TABLE IF EXISTS bookings ALTER COLUMN id SET DEFAULT gen_random_uuid();
            ALTER TABLE IF EXISTS packages ALTER COLUMN id SET DEFAULT gen_random_uuid();
            ALTER TABLE IF EXISTS uploads ALTER COLUMN id SET DEFAULT gen_random_uuid();
            ALTER TABLE IF EXISTS testimonials ALTER COLUMN id SET DEFAULT gen_random_uuid();
            ALTER TABLE IF EXISTS faqs ALTER COLUMN id SET DEFAULT gen_random_uuid();
            ALTER TABLE IF EXISTS email_outbox ALTER COLUMN id SET DEFAULT gen_random_uuid();
            ALTER TABLE IF EXISTS settings ALTER COLUMN id SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
            ALTER TABLE IF EXISTS admin_users ALTER COLUMN id DROP DEFAULT;
            ALTER TABLE IF EXISTS bookings ALTER COLUMN id DROP DEFAULT;
            ALTER TABLE IF EXISTS packages ALTER COLUMN id DROP DEFAULT;
            ALTER TABLE IF EXISTS uploads ALTER COLUMN id DROP DEFAULT;
            ALTER TABLE IF EXISTS testimonials ALTER COLUMN id DROP DEFAULT;
            ALTER TABLE IF EXISTS faqs ALTER COLUMN id DROP DEFAULT;
            ALTER TABLE IF EXISTS email_outbox ALTER COLUMN id DROP DEFAULT;
            ALTER TABLE IF EXISTS settings ALTER COLUMN id DROP DEFAULT;
            """,
        ),
    ]
