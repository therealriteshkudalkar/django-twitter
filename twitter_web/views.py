import datetime as dt

from cloudinary import uploader
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from django.utils import timezone

from .models import User, Follow

# uploader.upload(request.FILES['file'])


def error_404(request, exception, template_name='twitter_web/404.html'):
    response = render(request, template_name)
    response.status_code = 404
    return response


def home(request):
    # if user is present in session then take them to timeline
    # else redirect to search page
    return HttpResponseRedirect(reverse('twitter_web:login'))


def register(request):
    if request.method == 'GET':
        error_message = request.session.get('error_message')

        if error_message:
            request.session.pop('error_message')

        print('error_message: ', error_message)

        template_context = {
            'error_message': error_message
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
        return HttpResponseRedirect(reverse('twitter_web:login'))


def login(request):
    if request.method == 'GET':
        # if user is already logged in then redirect to timeline

        error_message = request.session.get('error_message')

        if error_message:
            request.session.pop('error_message')

        print('error_message: ', error_message)

        template_context = {
            'error_message': error_message
        }

        return render(request, 'twitter_web/login.html', context=template_context)
    else:
        username_or_email = request.POST["email_or_username"]
        password = request.POST["password"]

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
    if request.method == 'GET':
        if request.session.get("username"):
            request.session.pop("username")
            return HttpResponseRedirect(reverse('twitter_web:search'))
        return HttpResponseRedirect(reverse('twitter_web:login'))


def profile(request, username):
    # if profile of user is private check is session user is a follower
    #       if session user is a follower then show profile
    #       else show the incomplete profile and say it's private
    # if not private then show the profile
    # if both user profile and session user match then also show edit profile button
    if request.method == 'GET':
        print(username)
        session_username = request.session.get('username')
        if session_username:
            # user is authenticated
            # check if the username is same as session_username
            if session_username.lower() == username.lower():
                # show user profile with edit profile button
                template_context = {}
                return render(request, 'twitter_web/profile.html', context=template_context)
            else:
                # check if username has a private profile
                try:
                    profile_user = User.objects.get(username=username.lower())
                except User.DoesNotExist:
                    # show error on search page
                    return HttpResponseRedirect(reverse('search_page'))

                if profile_user.is_account_private:
                    # check if session user is one of the followers
                    try:
                        follow = Follow.objects.get(follower_id=session_username.lower(),
                                                    followee_id=username.lower())
                    except Follow.DoesNotExist:
                        template_context = {}
                        return render(request, 'twitter_web/profile', context=template_context)

                template_context = {}
                return render(request, 'twitter_web/profile.html', context=template_context)
        else:
            # user is not authenticated
            # check if user of username is private
            pass

        return render(request, 'twitter_web/profile.html')


def edit_profile(request):
    # if user is logged in then show to profile else redirect to search page
    pass


def timeline(request, profile_id):
    # if user is logged in then show timeline else redirect to search page
    pass


def retweet(request):
    # if user is logged in the add retweet to their tweets
    # else ask them to login
    pass


def like(request):
    # if user is logged in the add retweet to their tweets
    # else ask them to login
    pass


def impression(request):
    # register impression event if user is not logged in
    pass


def bookmark(request):
    # if user is logged in then show bookmark page else redirect them to login page
    pass


def message(request):
    # if user is logged in then show messages page else redirect them to login page
    pass
