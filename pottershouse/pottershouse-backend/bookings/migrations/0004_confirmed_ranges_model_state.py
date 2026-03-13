from django.db import migrations, models
from django.contrib.postgres.fields import DateTimeRangeField


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0003_confirmed_ranges_fk"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="BookingConfirmedRange",
                    fields=[
                        (
                            "booking",
                            models.OneToOneField(
                                primary_key=True,
                                serialize=False,
                                db_column="booking_id",
                                to="bookings.booking",
                                on_delete=models.deletion.CASCADE,
                                related_name="confirmed_range",
                            ),
                        ),
                        ("event_range", DateTimeRangeField()),
                    ],
                    options={
                        "db_table": "bookings_confirmed_ranges",
                    },
                ),
            ],
        ),
    ]
