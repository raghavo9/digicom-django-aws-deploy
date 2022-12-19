from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

#for signals to store user email in session for google oauth 

from django.db.models.signals import post_save
from django.dispatch import receiver

from .middlewares.middlewares import RequestMiddleware


from django.http import HttpRequest
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from category.views import misc_function

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site





class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')

        if not username:
            raise ValueError('User must have an username')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user






class Account(AbstractBaseUser):
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    username        = models.CharField(max_length=50, unique=True)
    email           = models.EmailField(max_length=100, unique=True)
    phone_number    = models.CharField(max_length=50 , null=True , blank=True)

    # required
    date_joined     = models.DateTimeField(auto_now_add=True)
    last_login      = models.DateTimeField(auto_now_add=True)
    is_admin        = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_active        = models.BooleanField(default=False)
    is_superadmin        = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

@receiver(post_save,sender = Account)
def email_in_session_signal(sender , instance , created ,**kwargs):
    
    if created:
        print(instance,instance.email)
        #request.session["user_email"] = instance.email
        #HttpRequest.session["user_email"] = instance.email
        #HttpRequest.COOKIES(dict(user_email = "raghav"))
        #request = RequestMiddleware(get_response=None)
        #nextUrl = request.build_absolute_uri(reverse('ordercomplete')+'?orderid='+order_number+'&transactionid='+transaction_id)
        #nextUrl = "http://127.0.0.1:8000/social/inactive?user_email="+instance.email
        #return HttpResponseRedirect(nextUrl)
        
        #current_site = get_current_site(request)
        #current_site = settings.BASE_DIR
        mail_subject = "Account Activation Mail"
        message = "activation mail"
        current_site = Site.objects.get_current()
        
        html_message = render_to_string('accounts/account_activation_email.html',{
            "user" : instance,
            "domain" : current_site.domain,
            "uid" : urlsafe_base64_encode(force_bytes(instance.pk)),
            "token" : default_token_generator.make_token(instance)
        })
        
        to_email = instance.email
        #send_email = EmailMessage(mail_subject,to=[to_email], html_message = message)
        from_email = settings.EMAIL_HOST_USER
        send_mail(mail_subject,message,from_email,[to_email],fail_silently=True,html_message=html_message)
        
        #send_email.send()



        #request.session['user_email'] = instance.email
        #misc_function(None)
    else:
        print("some error")