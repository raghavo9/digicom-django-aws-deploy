from django.http import HttpResponse
from django.shortcuts import render
from store.models import Product
from django.contrib.auth.decorators import login_required

@login_required(login_url= 'login')
def home(request):

    products = Product.objects.all().filter(is_available = True)
    product_count = products.count()

    context = {
        "products" : products
    }

    return render(request,'home.html',context)
