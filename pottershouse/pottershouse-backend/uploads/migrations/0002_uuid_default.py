from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("uploads", "0001_initial"),
        ("core", "0001_db_extensions"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE uploads ALTER COLUMN id SET DEFAULT gen_random_uuid();",
            reverse_sql="ALTER TABLE uploads ALTER COLUMN id DROP DEFAULT;",
        ),
    ]
