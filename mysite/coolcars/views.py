from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import transaction
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from coolcars.forms import *
from coolcars.tokens import account_activation_token
from gsearch.googlesearch import search
import csv
import os
from coolcars.trainUserData import *
from haystack.generic_views import SearchView


# home
def home(request):
    return HttpResponseRedirect(reverse('car_stream'))


@ensure_csrf_cookie
@transaction.atomic
# user login
def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('car_stream'))

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('car_stream'))
        else:
            context = dict()
            context['status'] = "no"
            context.update(csrf(request))
            return render_to_response('login.html', context, RequestContext(request))

    else:
        return render(request, 'login.html')


# user logout
@ensure_csrf_cookie
@login_required
def user_logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('car_stream'))


# user registration
@ensure_csrf_cookie
@transaction.atomic
def registration(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('car_stream'))

    if request.method == 'POST':
        f = RegisterForm(request.POST)
        if f.is_valid():
            username = f.cleaned_data["username"]
            user = f.save(commit=False)
            user.is_active = False
            user.save()

            profile = Info(username=user)
            profile.save()

            vote = Vote(username=user)
            vote.save()

            s = Search(username=user)
            s.save()

            # send verify email
            current_user = User.objects.get(username=username)
            sbj = 'Account Verification'
            msg = 'Please click on this link to verify your email for Grumblr website~\n'
            current_site = get_current_site(request)
            token = account_activation_token.make_token(user)
            htmlurl = """http://%s%s""" % (
                request.get_host(),
                reverse('activate', args=(urlsafe_base64_encode(force_bytes(user.pk)).decode(), token)))
            message = render_to_string('fakeEmail.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': token,
                'htmlurl': htmlurl
            })
            send_email([current_user.email], sbj, msg + message)
            return HttpResponse("Please confirm your email address to complete the registration!")

        else:
            return reg_err(request, f)

    else:
        f = RegisterForm()
        c = {}
        c['form'] = f
        c.update(csrf(request))
        return render_to_response('registration.html', c, RequestContext(request))


# car stream
def car_stream(request):
    dic = {}
    if request.user.is_authenticated:
        dic['logged'] = True

    posts = Post.objects.all().order_by("-favorite")

    comments = Comment.objects.all().order_by("time")
    coms = {}
    for comment in comments:
        com = {}
        current_comment = "comment" + str(comment.id)
        current_post = "post" + str(comment.post.id)
        username = comment.username.username
        content = comment.content
        time = comment.time
        com["post_id"] = current_post
        com["username"] = username
        com["content"] = content
        com["time"] = time
        coms[current_comment] = com

    temp = {}
    count = 0
    for post in posts:
        current_post = posts[count]
        postno = 'post' + str(post.id)
        li = []
        username = current_post.username
        title = current_post.title
        content = current_post.content
        published_date = current_post.published_date
        li.append(postno)
        li.append(username)
        li.append(title)
        li.append(content)
        li.append(published_date)
        li.append(current_post.favorite)
        if len(current_post.tags.all()) > 0:
            ta = ''
            for t in current_post.tags.all():
                ta = ta + " #" + str(t) + "#"
            li.append(ta)
        else:
            li.append(None)
        count += 1
        temp[postno] = li

    dic["posts"] = temp
    dic["comments"] = coms
    return render(request, "carStream.html", dic)


# following stream
@ensure_csrf_cookie
@login_required
@transaction.atomic
def followerstream(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    current_user = Info.objects.get(username=request.user)
    followees_info = current_user.followers.all().values_list('info__followers', flat=True)
    posts = Post.objects.filter(username__in=followees_info).order_by("-published_date")

    comments = Comment.objects.all().order_by("time")
    coms = {}
    for comment in comments:
        com = {}
        current_comment = "comment" + str(comment.id)
        current_post = "post" + str(comment.post.id)
        username = comment.username.username
        content = comment.content
        time = comment.time
        com["post_id"] = current_post
        com["username"] = username
        com["content"] = content
        com["time"] = time
        coms[current_comment] = com

    dic = {}
    temp = {}
    count = 0
    for post in posts:
        current_post = posts[count]
        li = []
        post_id = "post" + str(current_post.id)
        username = current_post.username
        title = current_post.title
        content = current_post.content
        published_date = current_post.published_date
        li.append(post_id)
        li.append(username)
        li.append(title)
        li.append(content)
        li.append(published_date)
        temp[post_id] = li
        count += 1

    dic["posts"] = temp
    dic["comments"] = coms
    return render(request, "followerStream.html", dic)


# add a new post
@ensure_csrf_cookie
@login_required
@transaction.atomic
def add_post(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if not 'title' in request.POST or not request.POST['title']:
        return HttpResponseRedirect(reverse('car_stream'))
    elif not 'content' in request.POST or not request.POST['content']:
        return HttpResponseRedirect(reverse('car_stream'))
    else:
        username = request.user
        new_post = Post(title=request.POST['title'], content=request.POST["content"], username=username)
        new_post.save()

    dic = {
        "title": new_post.title,
        "content": new_post.content,
        "published_date": new_post.published_date,
    }

    return render(request, "newPost_success.html", dic)


# user profile
@csrf_exempt
@login_required
def profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    username = request.GET.get("username", '')
    current_user = User.objects.get(username=username)

    if username == request.user.username:
        return redirect(reverse('myprofile'))

    username = current_user.username
    firstname = current_user.first_name
    lastname = current_user.last_name
    dic = {
        "username": username,
        "firstname": firstname,
        "lastname": lastname
    }

    comments = Comment.objects.all().order_by("time")
    coms = {}
    for comment in comments:
        com = {}
        current_comment = "comment" + str(comment.id)
        current_post = "post" + str(comment.post.id)
        username = comment.username.username
        content = comment.content
        time = comment.time
        com["post_id"] = current_post
        com["username"] = username
        com["content"] = content
        com["time"] = time
        coms[current_comment] = com
    dic["comments"] = coms

    followee = Info.objects.get(username=current_user)
    dic["followed"] = True if Info.objects.get(username=request.user).followers.filter(
        username=followee).exists() else False

    posts = Post.objects.all().filter(username=current_user).order_by("-published_date")
    temp = {}
    count = 0
    for post in posts:
        current_post = posts[count]
        li = []
        post_id = "post" + str(post.id)
        username = current_post.username
        title = current_post.title
        content = current_post.content
        published_date = current_post.published_date
        li.append(post_id)
        li.append(username)
        li.append(title)
        li.append(content)
        li.append(published_date)
        temp[post_id] = li
        count += 1
    dic["post"] = temp

    dic["age"] = ""
    dic['bio'] = "A happy CMU student!"
    for item in Info.objects.all().filter(username=current_user):
        dic["age"] = item.age
        dic["bio"] = item.bio

    return render(request, "profile.html", dic)


# my profile
@ensure_csrf_cookie
@login_required
def myprofile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    current_user = User.objects.get(username=request.user.username)

    username = current_user.username
    firstname = current_user.first_name
    lastname = current_user.last_name
    dic = {
        "username": username,
        "firstname": firstname,
        "lastname": lastname
    }

    comments = Comment.objects.all().order_by("time")
    coms = {}
    for comment in comments:
        com = {}
        current_comment = "comment" + str(comment.id)
        current_post = "post" + str(comment.post.id)
        username = comment.username.username
        content = comment.content
        time = comment.time
        com["post_id"] = current_post
        com["username"] = username
        com["content"] = content
        com["time"] = time
        coms[current_comment] = com
    dic["comments"] = coms

    posts = Post.objects.all().filter(username=current_user).order_by("-published_date")
    temp = {}
    count = 0
    for post in posts:
        current_post = posts[count]
        li = []
        post_id = "post" + str(post.id)
        username = current_post.username
        title = current_post.title
        content = current_post.content
        published_date = current_post.published_date
        li.append(post_id)
        li.append(username)
        li.append(title)
        li.append(content)
        li.append(published_date)
        temp[post_id] = li
        count += 1
    dic["post"] = temp

    dic["age"] = ""
    dic['bio'] = "A happy CMU student!"
    for item in Info.objects.all().filter(username=current_user):
        dic["age"] = item.age
        dic["bio"] = item.bio

    return render(request, "myprofile.html", dic)


@ensure_csrf_cookie
@login_required
@transaction.atomic
def follow(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    follower = Info.objects.get(username=request.user)
    followee = Info.objects.get(username=User.objects.filter(username=request.POST.get("followee", ''))[0])

    follower.followers.add(followee)
    follower.save()
    followee.save()
    return HttpResponseRedirect(reverse('followerstream'))


@ensure_csrf_cookie
@login_required
@transaction.atomic
def unfollow(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    follower = Info.objects.get(username=request.user)
    followee = Info.objects.get(username=User.objects.filter(username=request.POST.get("followee", ''))[0])

    follower.followers.remove(followee)
    follower.save()
    followee.save()

    return HttpResponseRedirect(reverse('followerstream'))


# add comment
@login_required
@transaction.atomic
@csrf_exempt
def add_comment(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    post_id = request.POST.get('post_id', '')
    comment_content = request.POST.get('comment_content', '')
    current_uesr = request.user

    new_comment = Comment(username=current_uesr, post=Post.objects.get(id=post_id[4:]), content=comment_content)
    new_comment.save()
    return redirect(reverse('car_stream'))


# activate account
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth.login(request, user)
        return redirect(reverse('car_stream'))
    else:
        return HttpResponse('Activation link is invalid!')


# send email helper function
def send_email(address, sbj, msg):
    send_mail(subject=sbj, message=msg, from_email="coolcars@gmail.com", recipient_list=address)


# handle registration errors
@ensure_csrf_cookie
def reg_err(request, f):
    form = RegisterForm()
    c = {}
    c['form'] = form
    c['f'] = f
    c.update(csrf(request))
    return render(request, 'registration.html', c)


# reset password
def resetPw(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('car_stream'))

    if request.method == 'POST':
        try:
            username = request.POST.get('username', '')
            user = User.objects.get(username=username)
        except:
            return render(request, 'noSuchUserWithoutLogin.html')

        if not user:
            return render(request, 'noSuchUser.html')
        else:
            c = {}
            c['status'] = "yes"
            email = user.email
            current_site = get_current_site(request)
            msg = 'Please click on this link to reset your password!\n'
            token = account_activation_token.make_token(user)
            htmlurl = """http://%s%s""" % (request.get_host(), reverse('password_reset_confirm', args=(
                urlsafe_base64_encode(force_bytes(user.pk)).decode(), token)))
            message = render_to_string('fakePwReset.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': token,
                'htmlurl': htmlurl
            })

            send_email([email], 'Password Reset', msg + message)
            c.update(csrf(request))
            return render(request, 'reset.html', c)

    else:
        return render(request, 'reset.html')


# confirm password reset
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'pwReset.html')
    else:
        return HttpResponse('Activation link is invalid!')


# password
def pw(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        try:
            user = User.objects.get(username=username)
        except:
            return render(request, 'noSuchUser.html')

        user.set_password(password)
        user.save()
        return render(request, 'login.html', {"pw_status": 'ok'})


@login_required
def search_user(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'GET':
        return render(request, 'searchUser.html')

    dic = {}
    usernames = request.POST.get('name', '')
    username = str.split(usernames, ',')
    user = []
    try:
        # sort acoording to num of votes for user
        us = User.objects.filter(username__in=username)
        votes = Vote.objects.filter(username__in=us).order_by('-no_vote')
        for v in votes:
            user.append(v.username)
    except:
        return render(request, 'noSuchUser.html')

    posts = Post.objects.filter(username__in=user)
    comments = Comment.objects.all().order_by("time")

    tmp = []
    for u in user:
        p = Post.objects.filter(username=u).order_by("-favorite")
        for p1 in p:
            tmp.append(p1)
    posts = tmp

    coms = {}
    for comment in comments:
        com = {}
        current_comment = "comment" + str(comment.id)
        current_post = "post" + str(comment.post.id)
        username = comment.username.username
        content = comment.content
        time = comment.time
        com["post_id"] = current_post
        com["username"] = username
        com["content"] = content
        com["time"] = time
        coms[current_comment] = com

    temp = {}
    count = 0
    for post in posts:
        current_post = posts[count]
        postno = 'post' + str(post.id)
        li = []
        username = current_post.username
        title = current_post.title
        content = current_post.content
        published_date = current_post.published_date
        li.append(postno)
        li.append(username)
        li.append(title)
        li.append(content)
        li.append(published_date)
        li.append(Vote.objects.get(username=current_post.username).no_vote)
        li.append(current_post.favorite)
        if len(current_post.tags.all()) > 0:
            ta = ''
            for t in current_post.tags.all():
                ta = ta + " #" + str(t) + "#"
            li.append(ta)
        else:
            li.append(None)
        count += 1
        temp[postno] = li

    dic["posts"] = temp
    dic["comments"] = coms
    return render(request, "searchUser.html", dic)


@login_required
def notification(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'GET':
        context = {}
        notifications = Notification.objects.filter(read=False).order_by("-time")
        context['notifications'] = notifications
        return render(request, 'notification.html', context)

    notification_id = request.POST.get('notification_id', '')
    n = Notification.objects.get(id=notification_id)
    n.read = True
    n.save()
    context = {}
    notifications = Notification.objects.filter(read=False).order_by("-time")
    context['notifications'] = notifications
    return render(request, 'notification.html', context)


@login_required
def vote(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'GET':
        context = {}
        votes = Vote.objects.all().order_by('-no_vote')
        context['votes'] = votes
        return render(request, 'vote.html', context)

    context = {}
    user_id = request.POST.get('user_id', '')
    try:
        user = User.objects.get(id=user_id)
        me = request.user
    except:
        return render_to_response('noSuchUser.html')

    if user is me:
        context['voteMyself'] = True
        return render(request, 'vote.html', context)

    v = Vote.objects.get(username=user)
    v.no_vote = v.no_vote + 1
    v.save()

    votes = Vote.objects.all().order_by('-no_vote')
    context['votes'] = votes
    return render(request, 'vote.html', context)


@login_required
def favorite(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    post_id = request.POST.get('post_id', '')
    post = Post.objects.get(id=post_id[4:])
    post.favorite = post.favorite + 1
    post.save()

    return redirect(reverse('car_stream'))


@login_required
def tagging(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    tag = request.POST.get('tagging', '')
    post_id = request.POST.get('post_id', '')
    post = Post.objects.get(id=post_id[4:])
    post.tags.add(tag)
    post.save()

    return redirect(reverse('car_stream'))


@login_required
def search_by_tagging(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'GET':
        return render(request, 'SearchByTagging.html')

    dic = {}
    tag = request.POST.get('tag', '')
    try:
        posts = Post.objects.filter(tags__in=tag).order_by("-favorite")
    except:
        return render_to_response('noSuchTag.html')
    comments = Comment.objects.all().order_by("time")

    coms = {}
    for comment in comments:
        com = {}
        current_comment = "comment" + str(comment.id)
        current_post = "post" + str(comment.post.id)
        username = comment.username.username
        content = comment.content
        time = comment.time
        com["post_id"] = current_post
        com["username"] = username
        com["content"] = content
        com["time"] = time
        coms[current_comment] = com

    temp = {}
    count = 0
    for post in posts:
        current_post = posts[count]
        postno = 'post' + str(post.id)
        li = []
        username = current_post.username
        title = current_post.title
        content = current_post.content
        published_date = current_post.published_date
        li.append(postno)
        li.append(username)
        li.append(title)
        li.append(content)
        li.append(published_date)
        li.append(Vote.objects.get(username=current_post.username).no_vote)
        li.append(current_post.favorite)
        if len(current_post.tags.all()) > 0:
            ta = ''
            for t in current_post.tags.all():
                ta = ta + " #" + str(t) + "#"
            li.append(ta)
        else:
            li.append(None)
        count += 1
        temp[postno] = li

    dic["posts"] = temp
    dic["comments"] = coms
    return render(request, "SearchByTagging.html", dic)


@login_required
def NLSearch(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'GET':
        return render(request, 'NLSearch.html')
    context = {}
    content = request.POST.get('content', '')

    s = Search.objects.get(username=request.user)
    s.searches.add(content)
    s.save()

    results = search(content, num_results=15)
    context['items'] = results
    return render(request, 'NLSearch.html', context)


@login_required
def recommendations(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    # export csv
    if os.path.exists("stats.csv"):
        os.remove("stats.csv")
    else:
        print("The file does not exist")

    with open('stats.csv', 'w', newline='') as csvfile:
        users = User.objects.all()
        for user in users:
            if user.username == 'admin':
                continue
            posts = Post.objects.filter(username=user)
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            tmp = [user.username]
            for post in posts:
                tags = post.tags.all()
                for t in tags:
                    tmp.append(t)
            spamwriter.writerow(tmp)

    # training model
    recommendation = train(request.user.username)
    recommendations = {}
    for key, val in recommendation.items():
        tmp = ''
        for v in val:
            tmp = tmp + ' #' + v + '# '
        recommendations[key] = tmp

    context = {}
    context['recommendations'] = recommendations

    return render(request, 'recommendation.html', context)
