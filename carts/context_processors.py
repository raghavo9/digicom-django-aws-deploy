from .models import Cart,CartItem
from .views import _cart_id


def counter(request):

    if "admin" in request.path:
        return {}
        
    cart_count = 0
    try :
        cart = Cart.objects.filter(cart_id = _cart_id(request))
        

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user)

        else:
            cart_items = CartItem.objects.all().filter(cart = cart[:1])
        #because we have used objects.filter in cart,therefore while
        #using it in cart_items --> filter,therefore defining that we need only 1 object

        for cart_item in cart_items:
            cart_count += cart_item.quantity
        
    except Cart.DoesNotExist:
        cart_count = 0
    
    return dict(cart_count = cart_count)
