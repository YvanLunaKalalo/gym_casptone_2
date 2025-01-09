from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from django.http import HttpResponse
from django.template import loader
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from .models import Account

def registration_view(request):
    template = loader.get_template('register_&_login/register.html')
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User will not be active until email is confirmed
            user.save()

            # Send confirmation email
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            message = render_to_string('register_&_login/register_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            send_mail(mail_subject, message, 'kalaloyvan07@gmail.com', [user.email])

            return render(request, 'register_&_login/register_done.html')
        else:
            context['registration_form'] = form
    else:  # GET request
        form = RegistrationForm()
        context['registration_form'] = form

    return HttpResponse(template.render(context, request))

def terms_and_conditions_view(request):
    template = loader.get_template('terms_and_conditions.html')
    return HttpResponse(template.render({}, request))

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('register_complete')  # Redirect to the home page or dashboard
    else:
        return HttpResponse('Activation link is invalid!')

def register_complete_view(request):
    template = loader.get_template("register_&_login/register_complete.html")
    return HttpResponse(template.render())

def logout_view(request):
	logout(request)
	return redirect('index') 

def login_view(request):
    template = loader.get_template('register_&_login/login.html')

    context = {}

    user = request.user

    if user.is_authenticated:
        return redirect('index')
    
    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:  # Check if the user is active
                    context['login_form'] = form
                    context['error_messages'] = "Your account is not activated. Please check your email to activate your account."
                    return HttpResponse(template.render(context, request))
                
				# Prevent superusers from logging in through user login
                if user.is_superuser:
                    context['login_form'] = form
                    context['error_message'] = "Admin account cannot log in here."
                    return HttpResponse(template.render(context, request))
				
                login(request, user)
                return redirect('index')
    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form
    return HttpResponse(template.render(context, request))

def account_view(request):
	template = loader.get_template('account.html')

	if not request.user.is_authenticated:
		return redirect("login")

	context = {}

	if request.POST:
		form = AccountUpdateForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
	else:
		form = AccountUpdateForm(
				initial= {
					"email": request.user.email,
					"username": request.user.username,
				}
			)
	context['account_form'] = form
	return HttpResponse(template.render(context, request))