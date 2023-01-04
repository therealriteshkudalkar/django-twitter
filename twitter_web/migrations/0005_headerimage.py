# Generated by Django 3.2.16 on 2023-01-03 04:27

import cloudinary.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('twitter_web', '0004_advertiser_affiliatedentity_tweet_tweetimage_retweet_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeaderImage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('image', cloudinary.models.CloudinaryField(max_length=255, verbose_name='header_image')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='twitter_web.user')),
            ],
        ),
    ]
