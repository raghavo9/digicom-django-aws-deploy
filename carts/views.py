from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,Variation
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

# Create your views here.


def cart(request,total = 0 , quantity = 0 ,tax = 0, cart_items = None):

    try :
        grand_total = 0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user , is_active = True)
        
        else :
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart , is_active = True)

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

    return render(request, "store/cart.html",context)

def _cart_id(request):

    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request,product_id):

    current_user = request.user
    product = Product.objects.get(id = product_id)

    #if the user is authenticated , then we wont create a new cart object , we will filter all the cart based on user key 
    if current_user.is_authenticated :
    
        if request.method == "POST":

        #color  = request.GET['color']
        #size = request.GET['size']

            product_variation_list = []
            for param in request.POST:
                key = param
                value = request.POST[key]
                try :
                    product_variation = Variation.object.get(product = product, variation_category__iexact = key , variation_value__iexact = value)
                    product_variation_list.append(product_variation)
                except:
                    pass

    
        cart_id = _cart_id(request)
        

        is_cart_item_exist = CartItem.objects.filter(product = product , user = current_user).exists()
        if is_cart_item_exist : 
            cart_item = CartItem.objects.filter(product = product , user = current_user)
            ex_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_variation_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation_list in ex_variation_list:

                index = ex_variation_list.index(product_variation_list)
                item_id = id[index]
                item = CartItem.objects.get(id = item_id , user = current_user)

                item.quantity +=1
                item.save()

            else : 

                cart_item = CartItem.objects.create(product = product , user = current_user, quantity = 1)
                if len(product_variation_list) > 0 :
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation_list)

                cart_item.save()

        else:
            cart_item = CartItem.objects.create(product = product , user = current_user, quantity = 1)
            if len(product_variation_list) > 0 :
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation_list)

            cart_item.save()

        return redirect('cart')

    #if the user is not authenticated
    else:


        if request.method == "POST":
            #color  = request.GET['color']
            #size = request.GET['size']

            product_variation_list = []
            for param in request.POST:
                key = param
                value = request.POST[key]
                try :
                    product_variation = Variation.object.get(product = product, variation_category__iexact = key , variation_value__iexact = value)
                    product_variation_list.append(product_variation)
                except:
                    pass

                
        cart_id = _cart_id(request)
        try : 
            cart = Cart.objects.get(cart_id = cart_id)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = cart_id
            )
        cart.save()

        is_cart_item_exist = CartItem.objects.filter(product = product , cart = cart).exists()
        if is_cart_item_exist : 
            cart_item = CartItem.objects.filter(product = product , cart = cart)
            ex_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_variation_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation_list in ex_variation_list:

                index = ex_variation_list.index(product_variation_list)
                item_id = id[index]
                item = CartItem.objects.get(id = item_id , cart = cart)

                item.quantity +=1
                item.save()

            else : 

                cart_item = CartItem.objects.create(product = product , cart = cart, quantity = 1)
                if len(product_variation_list) > 0 :
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation_list)

                cart_item.save()

        else:
            cart_item = CartItem.objects.create(product = product , cart = cart, quantity = 1)
            if len(product_variation_list) > 0 :
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation_list)

            cart_item.save()

        return redirect('cart')
    

def remove_cart(request,product_id, cart_item_id):

    
    product = get_object_or_404(Product, id = product_id)
    current_user = request.user
    try:
        if current_user.is_authenticated:
            cart_item = CartItem.objects.get(user = current_user , product = product , id = cart_item_id)
            print(cart_item)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(cart= cart , product = product , id = cart_item_id)
            print(cart_item)
    
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
    
        else :
            cart_item.delete()
    
    except Exception as e:
        print(e)

    return redirect('cart')


def remove_cart_item(request,product_id, cart_item_id):
    product = get_object_or_404(Product, id = product_id)
    current_user = request.user
    if current_user.is_authenticated:
        cart_item = CartItem.objects.get(user= current_user , product = product, id =cart_item_id )
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(cart= cart , product = product, id =cart_item_id )
        
    cart_item.delete()

    return redirect('cart')
