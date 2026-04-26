from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_feeds, name='get_feeds'),
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/me/', views.me, name='me'),
    path('auth/profile/', views.update_profile, name='update_profile'),
    path('add/', views.add_feed, name='add_feed'),
    path('search/', views.search_podcasts, name='search_podcasts'),
    path('popular/', views.popular_podcasts, name='popular_podcasts'),
    path('preview/', views.preview_feed, name='preview_feed'),
    path('<int:feed_id>/parse/', views.parse_feed, name='parse_feed'),
    path('progress/', views.get_progress, name='get_progress'),
    path('progress/save/', views.save_progress, name='save_progress'),
    path('history/', views.history, name='history'),
    path('library/', views.library, name='library'),
    path('bookmarks/toggle/', views.toggle_bookmark, name='toggle_bookmark'),
    path('subscriptions/toggle/', views.toggle_subscription, name='toggle_subscription'),
    path('folders/', views.folders, name='folders'),
    path('folders/<int:folder_id>/add/', views.add_to_folder, name='add_to_folder'),
]
