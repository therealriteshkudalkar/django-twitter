"""Twitter Apps URL """

from django.urls import path
from . import views

app_name = 'twitter_web'

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('follow', views.follow, name='follow'),
    path('unfollow', views.unfollow, name='unfollow'),
    # The only user who should be able to access private profile are the ones that
    # follow the user whose account is being viewed
    path('profile/<username>', views.profile, name='profile'),
    path('edit-profile', views.edit_profile, name='edit_profile'),
    # Approved only if the respective user is authorized in otherwise redirect to 404
    path('timeline/<username>', views.timeline, name='timeline'),
    path('tweet/<tweet_id>', views.tweet, name='tweet'),
    path('search', views.search, name='search'),
    path('notification', views.notification, name='notification'),
    path('retweet', views.retweet, name='retweet'),  # make post request
    path('like', views.like, name='like'),  # make post request
    path('impression', views.impression, name='impression'),
    path('bookmark', views.bookmark, name='bookmark'),  # use it for both fetching and saving bookmarks
    path('messages', views.message, name='message'),
]
