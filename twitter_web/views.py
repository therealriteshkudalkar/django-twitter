import datetime as dt

from cloudinary import uploader
from datetime import datetime
from itertools import chain

from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import User, Bio, ProfileImage, HeaderImage, Follow, Tweet, TweetImage, QuoteTweet, CommentTweet, Retweet,\
    Like, Impression, Message, Notification, Advertiser, Campaign
from .helper import int_to_string


def error_404(request, exception, template_name='twitter_web/404.html'):
    response = render(request, template_name)
    response.status_code = 404
    return response


def home(request):
    # if user is present in session then take them to timeline
    # else redirect to search page
    # show a design page
    return HttpResponseRedirect(reverse('twitter_web:login'))


def register(request):
    if request.method == 'GET':
        error_message = request.session.get('error_message')
        error_message_color = request.session.get('error_message_color')

        if error_message:
            request.session.pop('error_message')
        if error_message_color:
            request.session.pop('error_message_color')

        template_context = {
            'error_message': error_message,
            'error_message_color': error_message_color,
        }
        return render(request, 'twitter_web/register.html', context=template_context)
    else:
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        username = request.POST["username"]
        country = request.POST["country"]
        dob = request.POST["date_of_birth"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        # check if fname is less than 30 characters
        if len(fname) > 30:
            request.session["error_message"] = "First name can only have 30 characters at max."
            return HttpResponseRedirect(reverse('twitter_web:register'))

        # check if lname is less than 30 characters
        if len(lname) > 30:
            request.session["error_message"] = "Last name can only have 30 characters at max."
            return HttpResponseRedirect(reverse('twitter_web:register'))

        # check if username already exits or not
        try:
            User.objects.get(username=username)
            request.session["error_message"] = "User with given username already exists."
            return HttpResponseRedirect(reverse('twitter_web:register'))
        except User.DoesNotExist:
            pass

        # check if email already exits or not
        try:
            validate_email(email)
        except ValidationError:
            request.session["error_message"] = "Email entered is not valid!"
            return HttpResponseRedirect(reverse('twitter_web:register'))

        try:
            User.objects.get(email=email)
            request.session["error_message"] = "User with given email already exists."
            return HttpResponseRedirect(reverse('twitter_web:register'))
        except User.DoesNotExist:
            pass

        # check if dob is less than 18 years ago from today
        dob_datetime = datetime.strptime(dob, '%Y-%m-%d').timestamp()
        if dob_datetime > (timezone.now() - dt.timedelta(days=1)).timestamp():
            # user is not of appropriate age
            request.session["error_message"] = "You're not old enough to join Twitter."
            return HttpResponseRedirect(reverse('twitter_web:register'))

        # check if password and confirm_password are matching
        if password != confirm_password:
            request.session["error_message"] = "Passwords don't match"
            return HttpResponseRedirect(reverse('twitter_web:register'))

        new_user = User(fname=fname,
                        lname=lname,
                        username=username.lower(),
                        email=email,
                        password=make_password(password),
                        country=country,
                        dob=dob)

        new_user.save()
        request.session["error_message"] = "Registered successfully."
        request.session["error_message_color"] = "green"
        return HttpResponseRedirect(reverse('twitter_web:login'))


def login(request):
    if request.method == 'GET':
        # if user is already logged in then redirect to timeline
        session_username = request.session.get('username')
        if session_username:
            return HttpResponseRedirect(reverse('twitter_web:timeline', kwargs={'username': session_username}))

        error_message = request.session.get('error_message')
        error_message_color = request.session.get('error_message_color')

        if error_message:
            request.session.pop('error_message')
        if error_message_color:
            request.session.pop('error_message_color')

        template_context = {
            'error_message': error_message,
            'error_message_color': error_message_color,
        }

        return render(request, 'twitter_web/login.html', context=template_context)
    else:
        username_or_email = request.POST.get("email_or_username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username_or_email)
            if check_password(password, user.password):
                request.session["username"] = user.username
                return HttpResponseRedirect(reverse('twitter_web:profile', kwargs={'username': user.username}))
        except User.DoesNotExist:
            pass

        try:
            user = User.objects.get(email=username_or_email)
            if check_password(password, user.password):
                request.session["username"] = user.username
                return HttpResponseRedirect(reverse('twitter_web:profile', kwargs={'username': user.username}))
        except User.DoesNotExist:
            # user does not exist so show an error
            pass

        request.session["error_message"] = "Your username, email or password don't match."
        return HttpResponseRedirect(reverse('twitter_web:login'))


def logout(request):
    if request.method == 'POST':
        if request.session.get("username"):
            request.session.pop("username")
            return HttpResponseRedirect(reverse('twitter_web:search'))
        return HttpResponseRedirect(reverse('twitter_web:login'))


def profile(request, username):
    if request.method == 'GET':

        session_username = request.session.get('username', ' ')
        session_user_query = User.objects.filter(username=session_username.lower())
        user_query = User.objects.filter(username=username.lower())

        if not user_query.exists():
            print("hello", username, 'haghi')
            request.session["error_message"] = "User does not exist"
            return HttpResponseRedirect(reverse('twitter_web:search'))

        user = user_query.first()

        tweets = Tweet.objects.filter(user_id=user.id).order_by('-created_at')
        retweets = Retweet.objects.filter(user_id=user.id).order_by("-created_at")

        result_list = sorted(
            list(chain(tweets, retweets)),
            key=lambda instance: instance.created_at,
            reverse=True,
        )

        followers = Follow.objects.filter(followee_id=user.id)
        followings = Follow.objects.filter(follower_id=user.id)
        bio = Bio.objects.filter(user_id=user.id).order_by('-created_at')
        profile_image = ProfileImage.objects.filter(user_id=user.id).order_by('-created_at')
        header_image = HeaderImage.objects.filter(user_id=user.id).order_by('-created_at')

        if profile_image.exists():
            profile_image_url = profile_image.first().image.url
        else:
            profile_image_url = 'default'

        if header_image.exists():
            header_image_url = header_image.first().image.url
        else:
            header_image_url = 'default'

        if bio.exists():
            bio_text = bio.first().text
        else:
            bio_text = ''

        template_context = {
            'user': {
                'name': user.fname + ' ' + user.lname,
                'fname': user.fname,
                'lname': user.lname,
                'username': user.username,
                'tweet_count': tweets.count() + retweets.count(),
                'visitor': user.username,
                'country': user.country,
                'joined_month': user.created_at.strftime("%B"),
                'joined_year': user.created_at.strftime("%Y"),
                'following_count': int_to_string(followings.count()),
                'follower_count': int_to_string(followers.count()),
                'is_verified': user.is_verified,
                'bio': bio_text,
                'profile_image_url': profile_image_url,
                'header_image_url': header_image_url,
                'tweets': result_list,
            }
        }

        if session_user_query.exists():
            session_user = session_user_query.first()
            # user is authenticated
            is_same_user = session_username.lower() == username.lower()
            # print('is_same_user', is_same_user, session_username, username)
            template_context["user"]["is_logged_in"] = True
            template_context["user"]["is_same_user"] = is_same_user
            template_context["user"]["session_user"] = session_user

            if is_same_user:
                template_context["user"]["show_profile"] = True
            else:

                follow_rel = Follow.objects.filter(follower_id=session_user.id,
                                                   followee_id=user.id)

                template_context["user"]["is_follower"] = follow_rel.exists()

                if user.is_account_private:
                    template_context["user"]["show_profile"] = follow_rel.exists()
                else:
                    template_context["user"]["show_profile"] = True
        else:
            # user is not authenticated
            template_context["user"]["is_same_user"] = False
            template_context["user"]["is_follower"] = False
            template_context["user"]["show_profile"] = not user.is_account_private

        return render(request, 'twitter_web/profile.html', context=template_context)


def edit_profile(request):
    # if user is logged in then show to profile else redirect to search page
    session_username = request.session.get("username")

    session_user_filtered = User.objects.filter(username=session_username)

    if session_user_filtered:
        session_user = session_user_filtered.first()
    else:
        return HttpResponseRedirect(reverse('twitter_web:search'))

    if request.method == "GET":
        # show the edit page with values filled already

        bio = Bio.objects.filter(user_id=session_user.id).order_by('-created_at')
        if bio.exists():
            bio_text = bio.first().text
        else:
            bio_text = 'default'

        profile_image = ProfileImage.objects.filter(user_id=session_user.id).order_by('-created_at')
        if profile_image.exists():
            profile_image_url = profile_image.first().image.url
        else:
            profile_image_url = 'default'

        header_image = HeaderImage.objects.filter(user_id=session_user.id).order_by('-created_at')
        if header_image.exists():
            header_image_url = header_image.first().image.url
        else:
            header_image_url = 'default'

        template_context = {
            'user': {
                'fname': session_user.fname,
                'lname': session_user.lname,
                'username': session_user.username,
                'email': session_user.email,
                'country': session_user.country,
                'bio': bio_text,
                'profile_image_url': profile_image_url,
                'header_image_url': header_image_url,
                'is_account_private': session_user.is_account_private,
                'dob': session_user.dob.strftime("%Y-%m-%d"),
            }
        }
        return render(request, 'twitter_web/edit_profile.html', context=template_context)
    else:
        is_private = len(request.POST.getlist("is_account_private")) != 0

        with transaction.atomic():
            session_user_filtered.update(
                fname=request.POST.get("fname"),
                lname=request.POST.get("lname"),
                username=request.POST.get("username"),
                email=request.POST.get("email"),
                country=request.POST.get("country"),
                is_account_private=is_private,
                dob=request.POST.get("dob")
            )

            updated_bio = request.POST.get("bio")
            Bio.objects.create(
                user_id=session_user,
                text=updated_bio,
            )

            updated_profile_image = request.FILES.get("profile_image", False)
            if updated_profile_image:
                ProfileImage.objects.create(
                    user_id=session_user,
                    image=uploader.upload_resource(updated_profile_image),
                )

            updated_header_image = request.FILES.get("header_image", False)
            if updated_header_image:
                HeaderImage.objects.create(
                    user_id=session_user,
                    image=uploader.upload_resource(updated_header_image),
                )

            print(session_user.username)
            return HttpResponseRedirect(reverse('twitter_web:profile', kwargs={'username': session_user.username}))


def post_tweet(request):
    if request.method == "POST":
        session_username = request.session.get("username")

        session_user_filtered = User.objects.filter(username=session_username)

        if session_user_filtered.exists():
            session_user = session_user_filtered.first()
        else:
            return HttpResponseRedirect(reverse('twitter_web:search'))

        is_comment = request.POST.get("is_comment", False)
        is_quote_tweet = request.POST.get("is_quote_tweet", False)
        is_commercial = request.POST.get("is_commercial", False)
        tweet_text = request.POST.get("tweet_text", '')

        with transaction.atomic():
            new_tweet = Tweet.objects.create(
                user_id=session_user,
                text=tweet_text,
                is_comment=is_comment,
                is_quote_tweet=is_quote_tweet,
                is_commercial=is_commercial,
            )

            if is_comment:
                parent_tweet_id = request.POST.get("parent_tweet_id")
                parent_tweet = Tweet.objects.filter(id=parent_tweet_id)
                if parent_tweet.exists():
                    CommentTweet.object.create(
                        parent_tweet=parent_tweet.first(),
                        comment_tweet=new_tweet,
                    )

            if is_quote_tweet:
                quoted_tweet_id = request.POST.get("quoted_tweet_id")
                quoted_tweet = Tweet.objects.filter(id=quoted_tweet_id)
                if quoted_tweet.exists():
                    QuoteTweet.objects.create(
                        quoted_tweet=quoted_tweet.first(),
                        actual_tweet=new_tweet,
                    )

            images = request.FILES.getlist("images")
            counter = 0

            if len(images) != 0:
                # there are some images so download them
                for image in images:
                    if counter > 3:
                        break
                    # upload file
                    TweetImage.objects.create(
                        tweet_id=new_tweet,
                        image=uploader.upload_resource(image),
                    )
                    counter += 1

            return HttpResponseRedirect(reverse('twitter_web:profile', kwargs={'username': session_username}))


def delete_tweet(request):
    if request.method == "POST":
        session_username = request.session.get("username")
        session_user_filtered = User.objects.filter(username=session_username)
        if session_user_filtered.exists():
            pass


def tweet(request, tweet_id):
    if request.method == "GET":
        pass


def retweet(request):
    # if user is logged in the add retweet to their tweets
    # else ask them to login
    if request.method == "POST":
        post_id = request.POST.get("tweet_id")
        filtered_posts = Tweet.objects.filter(id=post_id)
        post = filtered_posts.first()
        response = {}

        if not filtered_posts.exists():
            response["response"] = "error"
            response["response_message"] = "Post does not exist!"
            return JsonResponse(data=response, safe=False)

        session_username = request.session.get("username")
        session_user_filtered = User.objects.filter(username=session_username)

        if session_user_filtered.exists():
            session_user = session_user_filtered.first()
            existing_retweet = Retweet.objects.filter(post_id=post, user_id=session_user)
            if existing_retweet.exists():
                post.retweets.remove(session_user)
                existing_retweet.delete()
                response["response"] = "successful"
                response["message"] = "Un-retweet successfully"
            else:
                post.retweets.add(session_user)
                Retweet.objects.create(
                    user_id=session_user,
                    post_id=post
                )
                response["response"] = "successful"
                response["message"] = "Retweeted successfully"
            post.save()
        else:
            response["response"] = "login"
            response["response_message"] = "You need to login to proceed with the action."
        return JsonResponse(data=response, safe=False)


def like(request):
    if request.method == "POST":
        post_id = request.POST.get("tweet_id")
        filtered_posts = Tweet.objects.filter(id=post_id)
        post = filtered_posts.first()
        response = {}

        if not filtered_posts.exists():
            response["response"] = "error"
            response["response_message"] = "Post does not exist!"
            return JsonResponse(data=response, safe=False)

        session_username = request.session.get("username")
        session_user_filtered = User.objects.filter(username=session_username)

        if session_user_filtered.exists():
            session_user = session_user_filtered.first()
            existing_like = Like.objects.filter(post_id=post, user_id=session_user)
            if existing_like.exists():
                existing_like.first().delete()
                post.likes.remove(session_user)
                response["response"] = "successful"
                response["message"] = "Tweet unliked successfully"
            else:
                Like.objects.create(
                    user_id=session_user,
                    post_id=post
                )
                post.likes.add(session_user)
                response["response"] = "successful"
                response["message"] = "Liked successfully"
            post.save()
        else:
            response["response"] = "login"
            response["response_message"] = "You need to login to proceed with the action."
        return JsonResponse(data=response, safe=False)


def impression(request):
    # register impression event if user is not logged in
    if request.method == "POST":
        post_id = request.POST.get("tweet_id")
        filtered_posts = Tweet.objects.filter(id=post_id)
        post = filtered_posts.first()
        response = {}

        if not post.exists():
            response["response"] = "error"
            response["response_message"] = "Post does not exist!"
            return JsonResponse(data=response, safe=False)

        session_username = request.session.get("username")
        session_user_filtered = User.objects.filter(username=session_username)

        if session_user_filtered.exists():
            session_user = session_user_filtered.first()
            Impression.objects.create(
                user_id=session_user,
                post_id=post
            )
            response["response"] = "successful"
            response["message"] = "Liked successfully"
        else:
            response["response"] = "login"
            response["response_message"] = "You need to login to proceed with the action."
        return JsonResponse(data=response, safe=False)


def search(request):
    if request.method == "GET":
        # check if there is any user error
        # if yes, then show that error on search page
        # else show the trending page
        error_message = request.session.get("search_error_message")
        if error_message:
            template_context = {
                'error_message': error_message,
            }
        else:
            template_context = {}
        return render(request, 'twitter_web/search.html', context=template_context)
    else:
        # perform the search query
        query = request.POST.get("search")
        # you can use like command from postgresql
        # search for people
        # search for trending topics
        # search for trending topics in news
        # if user has logged in then search for trending topics tailored to him
        template_context = {}
        return render(request, 'twitter_web/search.html', context=template_context)


def follow(request):
    if request.method == "POST":
        session_username = request.session.get("username", " ")
        username_being_followed = request.POST.get("followee", " ")
        session_user = User.objects.filter(username=session_username)
        user_being_followed = User.objects.filter(username=username_being_followed)

        response = {}

        if session_user.exists():
            if user_being_followed.exists():

                has_a_follow = Follow.objects.filter(
                    follower_id=session_user.first().id,
                    followee_id=user_being_followed.first().id,
                )

                if has_a_follow.exists():
                    has_a_follow.delete()
                    response["response"] = "successful"
                    response["message"] = "Unfollowed successfully"
                else:
                    Follow.objects.create(
                        follower_id=session_user.first(),
                        followee_id=user_being_followed.first()
                    )
                    response["response"] = "successful"
                    response["message"] = "Followed successfully"
            else:
                response["response"] = "error"
                response["message"] = "User not found"
        else:
            # user has to log in first
            response["response"] = "login"
            response["message"] = 'Please login first'
        return JsonResponse(data=response, safe=False)


def timeline(request, username):
    if request.method == "GET":
        # if user is logged in then show timeline else redirect to search page
        session_username = request.session.get("username", " ")
        session_user_filtered = User.objects.filter(username=session_username)
        session_user = session_user_filtered.first()

        if session_user_filtered.exists():
            if username.lower() == session_username.lower():
                # get all the tweets by users who the session user follows and arrange them by created at
                # get all followers of user
                followings = Follow.objects.filter(follower_id=session_user).values_list('followee_id')
                tweets_of_followings = Tweet.objects.filter(user_id__in=followings).order_by('-created_at')
                retweets_of_followings = Retweet.objects.filter(user_id__in=followings).order_by('-created_at')
                result_list = sorted(
                    list(chain(tweets_of_followings, retweets_of_followings)),
                    key=lambda instance: instance.created_at,
                    reverse=True,
                )
                template_context = {
                    'user': {
                        'session_user': session_user,
                        'tweets': result_list,
                        'is_logged_in': True,
                    }
                }
                return render(request, 'twitter_web/timeline.html', context=template_context)
            else:
                return HttpResponseRedirect(reverse('twitter_web:timeline', kwargs={'username': session_username}))
        else:
            request.session["error_message"] = "Page does not exist"
            return HttpResponseRedirect(reverse('twitter_web:search'))


def following_list(request, username):
    if request.method == "GET":
        pass


def follower_list(request, username):
    if request.method == "GET":
        pass


def notification(request):
    if request.method == "GET":
        pass


def bookmark(request):
    # if user is logged in then show bookmark page else redirect them to login page
    if request.method == "GET":
        pass
    else:
        pass


def message(request):
    # if user is logged in then show messages page else redirect them to login page
    if request.method == "GET":
        pass
    else:
        pass


def conversation(request, username):
    if request.method == "GET":
        pass
    else:
        pass
