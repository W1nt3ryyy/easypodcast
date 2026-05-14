from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("podcasts", "0004_listenprogress_history_fields"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Bookmark",
        ),
    ]
