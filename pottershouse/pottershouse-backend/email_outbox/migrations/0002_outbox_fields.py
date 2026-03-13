from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("email_outbox", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailoutbox",
            name="error_message",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="emailoutbox",
            name="manual_review",
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name="emailoutbox",
            index=models.Index(fields=["status", "created_at"]),
        ),
        migrations.AddIndex(
            model_name="emailoutbox",
            index=models.Index(fields=["to_email"]),
        ),
        migrations.AddIndex(
            model_name="emailoutbox",
            index=models.Index(fields=["sent_at"]),
        ),
    ]
