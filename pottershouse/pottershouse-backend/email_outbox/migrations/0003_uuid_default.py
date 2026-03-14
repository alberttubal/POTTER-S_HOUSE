from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("email_outbox", "0002_outbox_fields"),
        ("core", "0001_db_extensions"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE email_outbox ALTER COLUMN id SET DEFAULT gen_random_uuid();",
            reverse_sql="ALTER TABLE email_outbox ALTER COLUMN id DROP DEFAULT;",
        ),
    ]
