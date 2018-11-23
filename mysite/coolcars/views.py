from django.contrib import auth
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

from django.views.decorators.csrf import ensure_csrf_cookie
from coolcars.forms import *
from coolcars.tokens import account_activation_token


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


# car stream
def car_stream(request):
    if request.user.is_authenticated:
        return render(request, 'carStream.html', {'logged': True})

    if request.method == "GET":
        #     posts = Post.objects.filter().order_by('time').reverse()
        #     post_form = PostForm(instance=request.user)
        #     max_time = Post.get_max_time()
        #
        #     context = {'posts': posts, 'max_time': max_time, 'post_form': post_form}
        return render(request, 'carStream.html', {'logged': False})
    else:
        raise Http404
