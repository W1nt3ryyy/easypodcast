from django.conf import settings
from django.db import models


class PodcastFeed(models.Model):
    url = models.URLField(unique=True, verbose_name="RSS URL")
    title = models.CharField(max_length=255, blank=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    image_url = models.URLField(blank=True, null=True, verbose_name="URL обложки")
    category = models.CharField(max_length=100, blank=True, verbose_name="Категория")
    rss_cache = models.JSONField(blank=True, null=True, verbose_name="Кеш RSS")
    rss_cache_updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title or self.url


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="podcast_subscriptions")
    feed = models.ForeignKey(PodcastFeed, on_delete=models.CASCADE, related_name="subscriptions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "feed"], name="unique_user_subscription")
        ]

    def __str__(self):
        return f"Subscription: {self.feed.title}"


class ListenProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listen_progress", null=True, blank=True)
    episode_url = models.URLField(verbose_name="URL эпизода (mp3)")
    current_time = models.FloatField(default=0.0, verbose_name="Текущее время в секундах")
    duration = models.FloatField(default=0.0, verbose_name="Длительность в секундах")
    episode_title = models.CharField(max_length=400, blank=True)
    podcast_title = models.CharField(max_length=255, blank=True)
    podcast_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "episode_url"], name="unique_user_episode_progress")
        ]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Progress: {self.episode_title or self.episode_url} - {self.current_time}s"
