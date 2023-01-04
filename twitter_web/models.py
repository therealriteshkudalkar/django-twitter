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
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
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
    created_at = models.DateTimeField(default=now, editable=False)
    text = models.CharField(max_length=256)
    is_comment = models.BooleanField(default=False)
    is_commercial = models.BooleanField(default=False)


class TweetImage(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    tweet_id = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='tweet_image_user_id')
    created_on = models.DateTimeField(default=now, editable=False)
    image = CloudinaryField('tweet_image')


class Message(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_id')
    receiver_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_id')
    text = models.CharField(max_length=1024)
    created_at = models.DateTimeField(default=now, editable=False)


class Retweet(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    post_id = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='retweet_post_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='retweet_user_id')
    created_at = models.DateTimeField(default=now, editable=False)


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

