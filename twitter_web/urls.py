"""Twitter Apps URL """

from django.urls import path
from . import views

app_name = 'twitter_web'

urlpatterns = [
    path('', views.home, name='home'),

    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    path('profile/<username>', views.profile, name='profile'),
    path('edit-profile', views.edit_profile, name='edit_profile'),
    path('timeline/<username>', views.timeline, name='timeline'),
    path('tweet/<tweet_id>', views.tweet, name='tweet'),
    path('post_tweet', views.post_tweet, name='post_tweet'),
    path('delete_tweet', views.delete_tweet, name='delete_tweet'),

    path('follow', views.follow, name='follow'),
    path('follower/<username>', views.follower_list, name='follower_list'),
    path('following/<username>', views.following_list, name='following_list'),

    path('retweet', views.retweet, name='retweet'),
    path('like', views.like, name='like'),
    path('impression', views.impression, name='impression'),

    path('messages', views.message, name='message'),
    path('conversation/<username>', views.conversation, name='conversation'),

    path('search', views.search, name='search'),
    path('notification', views.notification, name='notification'),
    path('bookmark', views.bookmark, name='bookmark'),
]
