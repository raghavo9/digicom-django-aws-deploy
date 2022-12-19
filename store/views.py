from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from .models import Product
from category.models import Category
from carts.models import Cart,CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


# Create your views here.

def store(request,category_slug = None):

    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category,slug = category_slug)
        products = Product.objects.filter(category = categories , is_available = True)
        page = request.GET.get('page')
        paginator = Paginator(products,4)
        paged_products = paginator.get_page(page)

        product_count = products.count()
    else:
        page = request.GET.get('page')
        products = Product.objects.all().filter(is_available = True).order_by('id')
        paginator = Paginator(products,9)

        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        "products" : paged_products,
        "product_count" : product_count
    }

    return render(request , 'store/store.html',context)


def product_details(request,category_slug,product_slug):

    try:
        single_product = Product.objects.get(category__slug = category_slug , slug = product_slug)

        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists
        # here we used objects.filter()  and at last used .exists to return true or false value 

        context = {
            "single_product" : single_product,
            "in_cart" : in_cart
        }

    except Exception as e:
        raise e

    return render(request,'store/product_details.html',context) 


def search(request):

    products = None
    product_count = 0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']

        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains = keyword) | Q(product_name__icontains = keyword))
            product_count  = products.count()

            
    context = {
        "products" : products,
        "product_count" : product_count
    }

    return render(request,'store/store.html',context)

@login_required(login_url= 'login')
def checkout(request,total = 0 , quantity = 0 ,tax = 0, cart_items = None):

    try :
        #since checkout page is always shown after login , so filter cartItem based on user
        current_user = request.user
        grand_total = 0
        #cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(user = current_user , is_active = True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = 0.02*total
        grand_total = tax+total

    except ObjectDoesNotExist:
        pass

    context  = {
            "total" : total,
            "quantity": quantity,
            "cart_items" : cart_items,
            "tax" : tax,
            "grand_total" : grand_total
        }

    return render(request, 'store/checkout.html',context)
