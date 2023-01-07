from datetime import datetime, timezone

from django.db import models
from django.utils.timezone import now
from cloudinary.models import CloudinaryField


class User(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    username = models.CharField(max_length=20, unique=True, null=False)
    email = models.EmailField(max_length=30, unique=True)
    password = models.CharField(max_length=256)
    dob = models.DateField()
    country = models.CharField(max_length=30, default='USA')
    phone = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(default=now, editable=False)
    is_account_private = models.BooleanField(default=False)
    is_sub_blue = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_affiliated = models.BooleanField(default=False)


class Bio(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=256, blank=True, default='')
    created_at = models.DateTimeField(default=now, editable=False)


class ProfileImage(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_image_user')
    image = CloudinaryField('profile_image')
    created_at = models.DateTimeField(default=now, editable=False)


class HeaderImage(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    image = CloudinaryField('header_image')
    created_at = models.DateTimeField(default=now, editable=False)


class Follow(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    follower_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='follower_id')
    followee_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='followee_id')
    created_at = models.DateTimeField(default=now, editable=False)


class Tweet(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tweet_user_id')
    text = models.CharField(max_length=256, blank=True)
    likes = models.ManyToManyField(User, default=None, null=True, blank=True, related_name='liked_by_users')
    retweets = models.ManyToManyField(User, default=None, null=True, blank=True, related_name='retweeted_by_users')
    is_comment = models.BooleanField(default=False)
    is_quote_tweet = models.BooleanField(default=False)
    is_commercial = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now, editable=False)

    def get_type(self):
        return 'normal'

    def age(self):
        difference = (datetime.now(timezone.utc) - self.created_at).total_seconds()
        if difference < 60:
            return str(int(difference)) + "s"
        elif difference < 60 * 60:
            return str(int(difference / 60)) + "m"
        elif difference < 60 * 60 * 24:
            return str(int(difference / (60 * 60))) + "h"
        elif difference < 60 * 60 * 24 * 30:
            return str(int(difference / (60 * 60 * 24))) + "d"
        elif difference < 60 * 60 * 24 * 30 * 12:
            return str(int(difference / (60 * 60 * 24 * 30))) + "mnths"
        else:
            return str(int(difference / (60 * 60 * 24 * 30 * 12))) + "y"


class Retweet(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    post_id = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='retweet_post_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='retweet_user_id')
    created_at = models.DateTimeField(default=now, editable=False)

    def get_type(self):
        return 'retweet'


class TweetImage(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    tweet_id = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='tweet_image_user_id')
    created_on = models.DateTimeField(default=now, editable=False)
    image = CloudinaryField('tweet_image')


class QuoteTweet(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    quoted_tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='quoted_tweet')
    actual_tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='quote_tweet')


class CommentTweet(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    parent_tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='parent_tweet')
    comment_tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comment_tweet')


class Like(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    post_id = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='like_post_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='like_user_id')
    created_at = models.DateTimeField(default=now, editable=False)


class Impression(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    post_id = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='impression_post_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='impression_user_id')
    created_at = models.DateTimeField(default=now, editable=False)


class Notification(models.Model):
    class Action(models.TextChoices):
        LIKE = ("1", "Like")
        RETWEET = ("2", "Retweet")
        COMMENT = ("3", "Comment")
    id = models.AutoField(primary_key=True, null=False, blank=False)
    user_to_notify = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_to_notify')
    post = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='action_on_post')
    action = models.CharField(max_length=20, choices=Action.choices, default=Action.LIKE)


class Message(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_id')
    receiver_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_id')
    text = models.CharField(max_length=1024)
    created_at = models.DateTimeField(default=now, editable=False)


class Advertiser(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advertiser_id')
    name = models.CharField(max_length=256, null=False, blank=False)


class Campaign(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    advertiser_id = models.ForeignKey(Advertiser, on_delete=models.CASCADE, related_name='campaign_advertiser_id')
    tweet_id = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='campaign_tweet_id')
    cost = models.IntegerField()


class AffiliatedEntity(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=256)
    country = models.CharField(max_length=50)
    description = models.CharField(max_length=1024)

