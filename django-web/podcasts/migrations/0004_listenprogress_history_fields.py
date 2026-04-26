from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("podcasts", "0003_library_auth_and_rss_cache"),
    ]

    operations = [
        migrations.AddField(
            model_name="listenprogress",
            name="completed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="listenprogress",
            name="duration",
            field=models.FloatField(default=0.0, verbose_name="Длительность в секундах"),
        ),
        migrations.AddField(
            model_name="listenprogress",
            name="episode_title",
            field=models.CharField(blank=True, max_length=400),
        ),
        migrations.AddField(
            model_name="listenprogress",
            name="image_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="listenprogress",
            name="podcast_title",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="listenprogress",
            name="podcast_url",
            field=models.URLField(blank=True),
        ),
        migrations.AlterModelOptions(
            name="listenprogress",
            options={"ordering": ["-updated_at"]},
        ),
    ]
