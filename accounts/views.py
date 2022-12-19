from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account,MyAccountManager
from django.contrib import messages,auth
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

#Activation Email Imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site

from carts.models import Cart,CartItem
from carts.views import _cart_id

import requests


def register(request):

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name  = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()


            #user activation

            #current_site = get_current_site(request)
            #changing way to get current site ,so that we dont have to append http:// before it

            current_site = Site.objects.get_current()
            mail_subject = "Account Activation Mail"
            message = "activation mail"
            html_message = render_to_string('accounts/account_activation_email.html',{
                "user" : user,
                "domain" : current_site.domain,
                "uid" : urlsafe_base64_encode(force_bytes(user.pk)),
                "token" : default_token_generator.make_token(user)
            })

            to_email = email
            #send_email = EmailMessage(mail_subject,to=[to_email], html_message = message)
            from_email = settings.EMAIL_HOST_USER
            send_mail(mail_subject,message,from_email,[to_email],fail_silently=True,html_message=html_message)
            
            #send_email.send()

            messages.success(request, "Registration Successful")
            return redirect('/accounts/login/?command=verification&email='+email)

    else:
        form = RegistrationForm()

    context = {
        "form" : form,
    }

    return render (request,'accounts/register.html',context)

def login(request):

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        username = email.split("@")[0]

        # in add_cart we were doing  : make list of current product's variations , and make list of variations of all the products that are in the cart
        # match the current product's variations with existing variation list , and if found , get id of product , and update its quantity

        # now what we have to do is , check for all the cartItems that are in temporary cart before login , with the cartItems of logged in user's cart
        # if they match update quantity with quantity we had in temporary cart before login

        user = auth.authenticate(email = email , password = password)
        if user is not None:

            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart = cart).exists()
                if is_cart_item_exist : 
                    cart_items = CartItem.objects.filter(cart_id = cart)

                    #make list of all the product variations of cartItem in temporary cart before login
                    product_variation_list = []
                    current_cart_item_id_list = []
                    for item in cart_items:
                        product_variation = item.variations.all()
                        product_variation_list.append(list(product_variation))
                        current_cart_item_id_list.append(item.id)
                    
                    cart_items = CartItem.objects.filter(user = user)
                    ex_variation_list = []
                    id = []
                    for item in cart_items:
                        existing_variation = item.variations.all()
                        ex_variation_list.append(list(existing_variation))
                        id.append(item.id)


                    # now for all variation in product variations list , check if they exist in existing variation list 
                    # if they exist , increase their quantity
                    # else , those are already a cartItem , so just assign user to those cart item


                    #product variations in the list might print as [[<Variation:blue>,<Variation:large>]] , but they are actually the tupple of variation id's
                    # they might be of form [[1,4]] , since each variation has its own unique id , which is its primary key ,
                    # so blue , large of jeans might be [[1,4]] , while blue , large of Shirt might be [[9,10]]
                    # thus they both might look same or equal , but they are not , hence they wont be true for "if product_variation in ex_variation_list"  

                    #CHANGED THE COURSE LOGIC , WHERE ADDING SAME VARIATION PRODUCT AFTER LOGING OUT , CREATES A NEW ENTRY , BCZ IN ELSE EVERY PRODUCT IN CART IS NOW ASSIGNED TO A USER
                    print(product_variation_list,current_cart_item_id_list,id)
                    for pr in product_variation_list:
                        #keeping outside if else bcz its used in both
                        carts_item_index = product_variation_list.index(pr)
                        carts_item_id = current_cart_item_id_list[carts_item_index]
                        carts_item = CartItem.objects.get(id = carts_item_id)

                        if pr in ex_variation_list:
                            users_item_index = ex_variation_list.index(pr)
                            users_item_id = id[users_item_index]
                            users_item = CartItem.objects.get(id = users_item_id)
                            
                            users_item.quantity += carts_item.quantity
                            #we dont assign user to this product as we do with products that are not in users cart , bcz we already merged this product , 
                            # dont  want to make new entry of this already merged product while fetching cart_items on cart page
                            users_item.save()
                            # we can now delete the cart_item that was in cart and now has been merged in users cartItem 
                            carts_item.delete()
                        
                        else:
                            #cart_items = CartItem.objects.filter(cart = cart)
                            #for item in cart_items:
                            #    item.user = user
                            #    item.save()
                            carts_item.user = user
                            carts_item.save()

            except Exception as e:
                print(e)

            auth.login(request,user)

            messages.success(request,"Logged in Successfully ")
            url = request.META.get("HTTP_REFERER") 
            try:
                query = requests.utils.urlparse(url).query
                
                params = dict(x.split("=") for x in query.split('&'))
                if "next" in params:
                    next_page = params["next"]
                    return redirect(next_page)
            except:
                return redirect('dashboard')

        else:
            messages.error(request,"Invalid Login Credentials")
            return redirect('login')

    return render (request,'accounts/login.html')

@login_required(login_url= 'login')
def logout(request):

    auth.logout(request)
    messages.success(request,"Logged Out Successfully")
    return redirect('login')

    return 


def activate(request,uidb64, token):

    try :
        uid =urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)

    except (TypeError ,ValueError , OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,"Account Activated successfully")
        return redirect('login')        

    else:
        messages.error(request,"Invalid Activation Link")
        return redirect('register')


def dashboard(request):
    return render(request,'accounts/dashboard.html')


def forgotPassword(request):

    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email = email).exists():
            user  = Account.objects.get(email__iexact = email)

            #forgot password mail
            current_site = get_current_site(request)
            mail_subject = "Reset Password"
            message = "reset your password"
            html_message = render_to_string('accounts/forgot_password_mail.html',{
                "user" : user,
                "domain" : current_site,
                "uid" : urlsafe_base64_encode(force_bytes(user.pk)),
                "token" : default_token_generator.make_token(user)
            })

            to_email = email
            #send_email = EmailMessage(mail_subject,to=[to_email], html_message = message)
            from_email = settings.EMAIL_HOST_USER
            send_mail(mail_subject,message,from_email,[to_email],fail_silently=True,html_message=html_message)

            messages.success(request, "Reset Password Email has been sent to you email address")
            return redirect("login")

        else:
            messages.error(request,"Invalid Email Address , User Not Found")
            return redirect('forgotpassword')
    else:
        return render(request,"accounts/forgotpassword.html")

def resetpassword_validate(request,uidb64,token):
    try :
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)

    except (TypeError ,ValueError , OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session["uid"] = uid
        messages.success(request,"Please Reset Your Password")
        return redirect("resetpassword")

    else:
        messages.error(request,"The link has Expired or is Invalid")
        return redirect(request,"login")

def resetpassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session["uid"]
            user = Account.objects.get(pk = uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password updated successfully")
            return redirect("login")
        else : 
            messages.error(request,"Passwords do not match")
            return redirect("resetpassword")

    else:
        return render(request , "accounts/resetpassword.html")



