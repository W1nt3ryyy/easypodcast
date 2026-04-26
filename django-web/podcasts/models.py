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


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="podcast_bookmarks", null=True, blank=True)
    feed = models.ForeignKey(PodcastFeed, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "feed"], name="unique_user_bookmark")
        ]

    def __str__(self):
        return f"Bookmark: {self.feed.title}"


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


class PodcastFolder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="podcast_folders")
    name = models.CharField(max_length=120)
    feeds = models.ManyToManyField(PodcastFeed, through="PodcastFolderItem", related_name="folders")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="unique_user_folder")
        ]

    def __str__(self):
        return self.name


class PodcastFolderItem(models.Model):
    folder = models.ForeignKey(PodcastFolder, on_delete=models.CASCADE, related_name="items")
    feed = models.ForeignKey(PodcastFeed, on_delete=models.CASCADE, related_name="folder_items")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["folder", "feed"], name="unique_folder_feed")
        ]


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
