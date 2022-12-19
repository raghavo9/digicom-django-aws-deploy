from django.shortcuts import render,redirect
from carts.models import Cart,CartItem
from .forms import OrderForm,PaymentForm
from .models import Order,Payment,OrderProduct
import time,calendar
from django.contrib import messages
from django.http import HttpResponse
from store.models import Product
from django.urls import reverse
from django.http import HttpResponseRedirect

#for random string
import random,string


# Create your views here.

def place_order(request,grand_total = 0, tax = 0):

    current_user = request.user
    cart_items = CartItem.objects.filter(user = current_user)
    cart_items_count = cart_items.count()
    if cart_items_count <= 0:
        return redirect('store')

    grand_total = 0
    tax= 0
    total = 0
    quantity = 0

    for cart_item  in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity



    tax = 0.02*total
    grand_total = tax+total

    if request.method == "POST":
        
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()

            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            #generate order number 
            current_gmt = time.gmtime()
            timestamp = calendar.timegm(current_gmt)

            order_number = str(timestamp) + str(data.id)
            data.order_number = order_number
            data.save()

            #preparing data to pass in context to display on payments page

            order = Order.objects.get(user = current_user , is_ordered = False , order_number = order_number)

            context = {
                "order" : order,
                "cart_items" : cart_items,
                "tax" : tax,
                "total" : total,
                "grand_total" : grand_total,
                "quantity" : quantity
            }            

            return render(request,'orders/payments.html',context)
        else:
            #when form is not valid
            messages.error(request , "Something went wrong")
            return redirect('checkout')

    else:
        #messages.success(request,"method not post")
        #return redirect('checkout')
        pass


def random_string(length = 4):
    space_string = "abcdefghijklmnopqrstuvwxyz0123456789"
    result = ''.join((random.choice(space_string)) for x in range(length))
    return result

def payments(request):


    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            data = Payment()

            current_user = request.user
            data.user = current_user

            order_number = form.cleaned_data['order_id']

            #create custom transaction ID => timestamp + random string of 4 characters
            current_gmt = time.gmtime()
            timestamp = calendar.timegm(current_gmt)
            random_value = random_string(4)
            transaction_id = str(timestamp) + str(random_value)

            data.payment_id = transaction_id
            data.payment_method = form.cleaned_data['payment_method']
            data.status = form.cleaned_data['status']

            order = Order.objects.get(user = current_user , order_number = order_number)
            data.amount_paid = order.order_total

            data.save()

            order.is_ordered = True
            order.payment = data
            order.save()

            #move cart items to orderProducts

            cart_items = CartItem.objects.filter(user = current_user)

            for item in cart_items:
                order_product = OrderProduct()
                order_product.order_id = order.id
                order_product.payment = data
                order_product.user_id = request.user.id
                order_product.product_id = item.product_id
                order_product.quantity = item.quantity
                order_product.product_price = item.product.price
                order_product.ordered = True
                order_product.save()

                # we cannot directly save the many to many relation (for variations) , so we need to save the object first , and then fetch 
                # it again and then set its values

                cart_item = CartItem.objects.get(id = item.id)
                product_variations = cart_item.variations.all()
                orderproduct = OrderProduct.objects.get(id = order_product.id)
                orderproduct.variations.set(product_variations)
                orderproduct.save()

                # reduce the product quantity

                product = Product.objects.get(id = item.product_id)
                product.stock -= item.quantity
                product.save()


            # delete cart items when moved to orderProduct

            CartItem.objects.filter(user = current_user).delete()

            #send order confirmation email to user
            #-----------skippping the mail part ---------------

            #redirect user to ordercomplete page

            context = {
                "order_number" : order_number,
                "transId" : transaction_id,
            }

            #return render(request,"orders/ordercomplete.html",context)

            #now after payment setting , order products setting , cart items deletion order completion , redirect to ordercomplete page 
            #with parameters that define its comming from right url

            nextUrl = request.build_absolute_uri(reverse('ordercomplete')+'?orderid='+order_number+'&transactionid='+transaction_id)
            return HttpResponseRedirect(nextUrl)

    else:
        return redirect('store')
        #return render(request,"orders/payments.html")





def order_complete(request):

    if request.method == "GET":

        if request.GET.get('orderid') == None or request.GET.get('transactionid') == None :
            messages.error(request,"orderid or transactionid missing")
            return redirect('store')
        
        order_number = request.GET['orderid']
        transaction_id = request.GET['transactionid']

        try:
            order = Order.objects.get(user = request.user , order_number = order_number)
            payment = Payment.objects.get(payment_id = transaction_id)
            orderproducts = OrderProduct.objects.filter(user = request.user , order = order)
            subtotal = 0
            for item in orderproducts:
                subtotal+= item.quantity * item.product_price


            context = {
                "order" : order,
                "orderproducts" : orderproducts,
                "payment" : payment,
                "subtotal" : subtotal,
            }

            return render(request,'orders/ordercomplete.html',context)

        except (Order.DoesNotExist):
            messages.error(request,"Invalid order number")
            return redirect('store')



        return HttpResponse("if part  ==> "+order_number+"====>"+transaction_id)

    else:
        return HttpResponse("else part")
        return redirect('store')


