from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("podcasts", "0005_delete_bookmark"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PodcastFolderItem",
        ),
        migrations.DeleteModel(
            name="PodcastFolder",
        ),
    ]
