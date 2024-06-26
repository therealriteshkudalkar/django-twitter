import datetime as dt

from cloudinary import uploader
from datetime import datetime
from itertools import chain

from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.db import transaction, Error
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Count

from .models import User, Bio, ProfileImage, HeaderImage, Follow, Tweet, TweetImage, QuoteTweet, CommentTweet, Retweet, \
    Like, Impression, Bookmark, Message, Conversation, Notification
from .helper import int_to_string


def error_404(request, template_name='twitter_web/404.html'):
    response = render(request, template_name)
    response.status_code = 404
    return response


def home(request):
    username = request.session.get("username")
    if username:
        return HttpResponseRedirect(reverse('twitter_web:timeline', kwargs={
                'username': username}))
    return render(request, 'twitter_web/home.html')


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
            'date': datetime.now().strftime("%Y-%m-%d"),
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

        if len(fname) > 30:
            request.session["error_message"] = "First name can only have 30 characters at max."
            return HttpResponseRedirect(reverse('twitter_web:register'))

        if len(lname) > 30:
            request.session["error_message"] = "Last name can only have 30 characters at max."
            return HttpResponseRedirect(reverse('twitter_web:register'))

        if len(username) > 30:
            request.session["error_message"] = "Username can only have 30 characters at max."
            return HttpResponseRedirect(reverse('twitter_web:register'))

        try:
            User.objects.get(username=username)
            request.session["error_message"] = "User with given username already exists."
            return HttpResponseRedirect(reverse('twitter_web:register'))
        except User.DoesNotExist:
            pass

        if len(email) > 30:
            request.session["error_message"] = "Email can only have 50 characters at max."
            return HttpResponseRedirect(reverse('twitter_web:register'))

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
        try:
            dob_datetime = datetime.strptime(dob, '%Y-%m-%d').timestamp()
        except ValueError:
            request.session["error_message"] = "Incorrect format for date of birth."
            return HttpResponseRedirect(reverse('twitter_web:register'))

        if dob_datetime > (timezone.now() - dt.timedelta(days=1)).timestamp():
            # user is not of appropriate age
            request.session["error_message"] = "You're not old enough to join Twitter."
            return HttpResponseRedirect(reverse('twitter_web:register'))

        # check if password and confirm_password are matching
        if password != confirm_password:
            request.session["error_message"] = "Passwords don't match"
            return HttpResponseRedirect(reverse('twitter_web:register'))

        if len(password) < 7:
            request.session["error_message"] = "Password must have at least 7 characters."
            return HttpResponseRedirect(reverse('twitter_web:register'))

        special_character = set("%$@#!&^*-")

        if not special_character.intersection(password):
            request.session["error_message"] = "Password must have at least one special character; # % ^ @ ! * - &"
            return HttpResponseRedirect(reverse('twitter_web:register'))

        if password == password.lower():
            request.session["error_message"] = "Password must have at least one upper case character."
            return HttpResponseRedirect(reverse('twitter_web:register'))

        numbers = set('0123456789')

        if not numbers.intersection(password):
            request.session["error_message"] = "Password must have at least one number."
            return HttpResponseRedirect(reverse('twitter_web:register'))

        try:
            new_user = User(fname=fname,
                            lname=lname,
                            username=username.lower(),
                            email=email,
                            password=make_password(password),
                            country=country,
                            dob=dob)
            new_user.save()
        except Error:
            request.session["error_message"] = "Error occurred while making new user."
            return HttpResponseRedirect(reverse('twitter_web:register'))

        request.session["error_message"] = "Registered successfully."
        request.session["error_message_color"] = "green"
        return HttpResponseRedirect(reverse('twitter_web:login'))


def login(request):
    if request.method == 'GET':
        session_username = request.session.get('username')
        if session_username:
            return HttpResponseRedirect(reverse('twitter_web:timeline', kwargs={
                'username': session_username}))

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
        request.session["error_message"] = "Your haven't logged in!"
        return HttpResponseRedirect(reverse('twitter_web:login'))


def profile(request, username):
    if request.method == 'GET':

        session_username = request.session.get('username', ' ')
        session_user_query = User.objects.filter(username=session_username.lower())
        if session_user_query.exists():
            session_user = session_user_query.first()
        else:
            session_user = None

        user_query = User.objects.filter(username=username.lower())
        if not user_query.exists():
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

        liked_tweets = Like.objects.filter(user_id=user).order_by('-created_at')

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
                'visitor': session_user.username,
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
                'liked_tweets': liked_tweets,
                'object': user,
                'session_user': session_user,
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
            'user': session_user,
            'user_': {
                'is_logged_in': True,
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

        is_comment = request.POST.get("is_comment", "False")
        is_quote_tweet = request.POST.get("is_quote_tweet", "False")
        is_commercial = request.POST.get("is_commercial", "False")
        tweet_text = request.POST.get("tweet_text", '')

        with transaction.atomic():
            new_tweet = Tweet.objects.create(
                user_id=session_user,
                text=tweet_text,
                is_comment=is_comment,
                is_quote_tweet=is_quote_tweet,
                is_commercial=is_commercial,
            )

            if is_comment == "True":
                parent_tweet_id = request.POST.get("parent_tweet_id")
                parent_tweet = Tweet.objects.filter(id=parent_tweet_id)
                if parent_tweet.exists():
                    CommentTweet.objects.create(
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
    else:

        return HttpResponseRedirect(reverse('twitter_web:search'))


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
                response["count"] = post.retweets.count()
            else:
                post.retweets.add(session_user)
                Retweet.objects.create(
                    user_id=session_user,
                    post_id=post
                )
                response["response"] = "successful"
                response["message"] = "Retweeted successfully"
                response["count"] = post.retweets.count()
            post.save()
        else:
            response["response"] = "login"
            response["response_message"] = "You need to login to proceed with the action."
        return JsonResponse(data=response, safe=False)
    else:
        request.session["error_message"] = "Not a valid url!"
        return HttpResponseRedirect(reverse('twitter_web:search'))


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
                response["count"] = post.likes.count()
            else:
                Like.objects.create(
                    user_id=session_user,
                    post_id=post
                )
                post.likes.add(session_user)
                response["response"] = "successful"
                response["message"] = "Liked successfully"
                response["count"] = post.likes.count()
            post.save()
        else:
            response["response"] = "login"
            response["response_message"] = "You need to login to proceed with the action."
        return JsonResponse(data=response, safe=False)
    else:
        request.session["error_message"] = "Not a valid url!"
        return HttpResponseRedirect(reverse('twitter_web:search'))


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


def follow(request):
    if request.method == "POST":
        with transaction.atomic():
            session_username = request.session.get("username", " ")
            username_being_followed = request.POST.get("followee", " ")
            filtered_session_user = User.objects.filter(username=session_username)

            user_being_followed_filtered = User.objects.filter(username=username_being_followed)

            response = {}

            if filtered_session_user.exists():
                session_user = filtered_session_user.first()
                if user_being_followed_filtered.exists():
                    user_being_followed = user_being_followed_filtered.first()

                    has_a_follow = Follow.objects.filter(
                        follower_id=session_user,
                        followee_id=user_being_followed,
                    )

                    print(session_user.followings.all(), session_user.followers.all(),
                          user_being_followed.followings.all(), user_being_followed.followers.all())

                    if has_a_follow.exists():
                        # session_user.followings.remove(user_being_followed)
                        user_being_followed.followers.remove(session_user)
                        has_a_follow.delete()
                        response["response"] = "successful"
                        response["message"] = "Unfollowed successfully"
                    else:
                        # session_user.followings.add(user_being_followed)
                        user_being_followed.followers.add(session_user)
                        Follow.objects.create(
                            follower_id=session_user,
                            followee_id=user_being_followed,
                        )
                        response["response"] = "successful"
                        response["message"] = "Followed successfully"
                    session_user.save()
                    user_being_followed.save()

                    print(session_user.followings.all(), session_user.followers.all(),
                          user_being_followed.followings.all(), user_being_followed.followers.all())

                else:
                    response["response"] = "error"
                    response["message"] = "User not found"
            else:
                # user has to log in first
                response["response"] = "login"
                response["message"] = 'Please login first'
            return JsonResponse(data=response, safe=False)


def follow_list(request, selected, username):
    if request.method == "GET":
        session_username = request.session.get("username", " ")
        session_user_filtered = User.objects.filter(username=session_username)

        filtered_user = User.objects.filter(username=username)
        if not filtered_user.exists():
            request.session["error_message"] = "User does not exist"
            return HttpResponseRedirect(reverse('twitter_web:search'))

        user = filtered_user.first()
        session_user = None
        if session_user_filtered.exists():
            session_user = session_user_filtered.first()

        if user.is_account_private:
            if session_user == user:
                pass
            elif session_user not in user.followers.all():
                request.session["error_message"] = "Private user, can't access their followings"
                return HttpResponseRedirect(reverse('twitter_web:search'))

        template_context = {
            'session_user': session_user,
            'user': {
                'object': user,
                'is_logged_in': session_user is not None,
            },
            'selected': selected,
        }
        return render(request, 'twitter_web/follow-list.html', context=template_context)


def timeline(request, username):
    if request.method == "GET":
        session_username = request.session.get("username", " ")
        session_user_filtered = User.objects.filter(username=session_username)

        if session_user_filtered.exists():
            session_user = session_user_filtered.first()
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


def bookmark(request):
    if request.method == "GET":
        session_username = request.session.get("username", " ")
        session_user_filtered = User.objects.filter(username=session_username)

        if session_user_filtered.exists():
            session_user = session_user_filtered.first()
            user_bookmarks = Bookmark.objects.filter(user_id=session_user)
            template_context = {
                'user': {
                    'session_user': session_user,
                    'bookmarks': user_bookmarks,
                    'is_logged_in': True
                }
            }
            return render(request, 'twitter_web/bookmarks.html', context=template_context)
        else:
            request.session["error_message"] = "Page does not exist"
            return HttpResponseRedirect(reverse('twitter_web:search'))
    else:
        post_id = request.POST.get("tweet_id")
        filtered_posts = Tweet.objects.filter(id=post_id)
        response = {}

        if not filtered_posts.exists():
            response["response"] = "error"
            response["response_message"] = "Post does not exist!"
            return JsonResponse(data=response, safe=False)

        post = filtered_posts.first()

        session_username = request.session.get("username")
        session_user_filtered = User.objects.filter(username=session_username)

        if session_user_filtered.exists():
            session_user = session_user_filtered.first()
            existing_bookmarks = Bookmark.objects.filter(user_id=session_user, post_id=post)
            if existing_bookmarks.exists():
                existing_bookmarks.first().delete()
                session_user.bookmarks.remove(post)
                response["response"] = "successful"
                response["message"] = "Tweet removed from bookmarks!"
            else:
                session_user.bookmarks.add(post)
                Bookmark.objects.create(
                    user_id=session_user,
                    post_id=post
                )
                response["response"] = "successful"
                response["message"] = "Tweet bookmarked successfully!"
                response["count"] = post.likes.count()
            session_user.save()
        else:
            response["response"] = "login"
            response["response_message"] = "You need to login to proceed with the action."
        return JsonResponse(data=response, safe=False)


def delete_tweet(request):
    if request.method == "POST":
        tweet_id = request.POST.get("tweet_id")
        filtered_tweets = Tweet.objects.filter(id=tweet_id)

        if filtered_tweets.exists:
            tweet = filtered_tweets.first()
        else:
            response = {
                "response": "error",
                "message": "Tweet not found or may have been deleted!"
            }
            return JsonResponse(data=response, safe=False)

        session_username = request.session.get("username")
        session_user_filtered = User.objects.filter(username=session_username)

        if session_user_filtered.exists():
            session_user = session_user_filtered.first()
            if session_user == tweet.user_id:
                tweet.delete()
                response = {
                    "response": "success",
                    "message": "Tweet deleted successfully!"
                }
            else:
                response = {
                    "response": "error",
                    "message": "You cannot delete someone else's tweet!",
                }
        else:
            response = {
                "response": "login",
                "message": "User not logged in!",
            }

        return JsonResponse(data=response, safe=False)
    else:
        request.session["error_message"] = "Not a valid url!"
        return HttpResponseRedirect(reverse('twitter_web:search'))


def show_tweet(request, tweet_id):
    if request.method == "GET":
        filtered_tweets = Tweet.objects.filter(id=tweet_id)

        if filtered_tweets.exists:
            tweet = filtered_tweets.first()
        else:
            request.session["response"] = "Error"
            request.session["message"] = "Tweet not found or may have been deleted!"
            return HttpResponseRedirect(reverse('twitter_web:search'))

        comments = CommentTweet.objects.filter(parent_tweet=tweet)

        session_username = request.session.get("username")
        filtered_users = User.objects.filter(username=session_username)

        session_user = None

        if filtered_users.exists():
            session_user = filtered_users.first()

        template_context = {
            'post': tweet,
            'comments': comments,
            'user': {
                'is_logged_in': session_user is not None,
                'session_user': session_user,
            }
        }

        return render(request, 'twitter_web/tweet_view.html', context=template_context)
    else:
        request.session["error_message"] = "Not a valid url!"
        return HttpResponseRedirect(reverse('twitter_web:search'))


def search(request):
    if request.method == "GET":
        # check if there is any user error
        # if yes, then show that error on search page
        # else show the trending page
        error_message = request.session.get("error_message")
        search_term = request.session.get("search_term")

        session_username = request.session.get("username")
        filtered_session_user = User.objects.filter(username=session_username)

        if filtered_session_user.exists():
            session_user = filtered_session_user.first()
        else:
            session_user = None

        # get top 10 trending topics
        tweets = Tweet.objects.all().order_by('-created_at')[:100]
        word_dict = {}
        for tweet in tweets:
            words = tweet.text.split()
            for word in words:
                if len(word) < 4:
                    continue
                if word.lower() in word_dict:
                    word_dict[word.lower()] += 1
                else:
                    word_dict[word.lower()] = 1
        top_ten_words = sorted(word_dict.items(), key=lambda x: -x[1])
        top_ten_words_list = [{'word': x[0], 'count': x[1]} for x in top_ten_words]

        if error_message:
            request.session.pop('error_message')
            template_context = {
                'error_message': error_message,
                'trends': top_ten_words_list,
                'user': {
                    'is_logged_in': session_user is not None,
                },
                'session_user': session_user,
            }
        elif search_term:
            # get people related to search term
            people_by_username = User.objects.filter(username__icontains=search_term)
            people_by_fname = User.objects.filter(fname__icontains=search_term)
            people_by_lname = User.objects.filter(lname__icontains=search_term)
            people = people_by_username.union(people_by_fname, people_by_lname)

            # get the latest tweets related to search term limit to 20
            latest_tweets = Tweet.objects.filter(text__icontains=search_term).order_by('-created_at')[:20]

            template_context = {
                'session_user': session_user,
                'people': people,
                'trends': top_ten_words_list,
                'latest_tweets': latest_tweets,
                'user': {
                    'is_logged_in': session_user is not None,
                },
                'country': 'India',
            }

        else:
            # get people with most following
            people = User.objects.annotate(followers_count=Count('followers')).order_by('-followers_count')

            # get the latest tweets limit to 10
            latest_tweets = Tweet.objects.all().order_by('-created_at')[:20]

            print(latest_tweets)

            template_context = {
                'session_user': session_user,
                'people': people,
                'trends': top_ten_words_list,
                'latest_tweets': latest_tweets,
                'user': {
                    'is_logged_in': session_user is not None,
                },
                'country': 'India',
            }
        return render(request, 'twitter_web/search.html', context=template_context)
    else:
        # perform the search query
        query = request.POST.get("search")
        request.session["search_term"] = query
        return HttpResponseRedirect(reverse('twitter_web:search'))


def message(request):
    # if user is logged in then show messages page else redirect them to login page
    if request.method == "GET":
        session_username = request.session.get("username")
        filtered_session_user = User.objects.filter(username=session_username)

        if filtered_session_user.exists():
            session_user = filtered_session_user.first()
            # fetch all the messages where sender and receiver is session_user
            conversation_initiator = Conversation.objects.filter(initiator=session_user)
            conversation_receiver = Conversation.objects.filter(receiver=session_user)
            all_conversations = conversation_receiver.union(conversation_initiator)

            template_context = {
                'session_user': session_user,
                'conversations': all_conversations,
                'user': {
                    'is_logged_in': True,
                }
            }

            return render(request, 'twitter_web/messages.html', context=template_context)
        else:
            request.session["error_message"] = "Login to access the page!"
            return HttpResponseRedirect(reverse('twitter_web:search'))

    else:
        request.session["error_message"] = "Not a valid url!"
        return HttpResponseRedirect(reverse('twitter_web:search'))


def conversation(request, username):

    session_username = request.session.get("username")
    filtered_session_user = User.objects.filter(username=session_username)

    filtered_user = User.objects.filter(username=username)

    if not filtered_user.exists() or not filtered_session_user.exists():
        request.session["error_message"] = "Login to access the page!"
        return HttpResponseRedirect(reverse('twitter_web:search'))

    user = filtered_user.first()
    session_user = filtered_session_user.first()

    conversation_initiator = Conversation.objects.filter(initiator=session_user, receiver=user)
    conversation_receiver = Conversation.objects.filter(initiator=user, receiver=session_user)

    conv = None

    if conversation_initiator.exists():
        conv = conversation_initiator.first()

    if conversation_receiver.exists():
        conv = conversation_receiver.first()

    # now get all the messages from that conversation

    if conv is None:
        # create a new conversation
        conv = Conversation.objects.create(
            initiator=session_user,
            receiver=user,
        )

    if request.method == "GET":
        template_context = {
            'conversation': conv,
            'session_user': session_user,
            'user': {
                'is_logged_in': True,
                'object': user,
            }
        }
        return render(request, 'twitter_web/conversation.html', context=template_context)
    else:
        # write post logic for the conversation
        message_text = request.POST.get('message')
        new_message = Message.objects.create(
            conversation=conv,
            text=message_text,
            sender=session_user,
            receiver=user,
        )
        conv.messages.add(new_message)
        conv.save()

        response = {
            'response': 'successful',
            'message': 'send new data'
        }

        return JsonResponse(response, safe=False)


def settings(request):
    if request.method == "GET":
        session_username = request.session.get("username")
        filtered_session_user = User.objects.filter(username=session_username)

        if filtered_session_user.exists():
            session_user = filtered_session_user.first()
            template_context = {
                'session_user': session_user,
                'user': {
                    'is_logged_in': True,
                }
            }
        else:
            template_context = {
                'session_user': None,
                'user': {
                    'is_logged_in': False,
                }
            }
        return render(request, 'twitter_web/settings.html', context=template_context)
    else:
        request.session["error_message"] = "Not a valid url!"
        return HttpResponseRedirect(reverse('twitter_web:search'))


def notification(request):
    if request.method == "GET":
        session_username = request.session.get("username", " ")
        session_user_filtered = User.objects.filter(username=session_username)

        if session_user_filtered.exists():
            session_user = session_user_filtered.first()
            # fetch notifications for the user with unread first
            # once loaded make them unread using javascript
        else:
            request.session["error_message"] = "Login to access the link"
            return HttpResponseRedirect(reverse('twitter_web:search'))
    else:
        request.session["error_message"] = "Not a valid url!"
        return HttpResponseRedirect(reverse('twitter_web:search'))
