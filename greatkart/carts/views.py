from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

# private function, get to the cart_id by session key
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
# Add to cart
def add_cart(request, product_id):
   
    product = Product.objects.get(id=product_id) # get to the product
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request)) # get the cart_id using the cart_id present on the session
    except Cart.DoesNotExist :
       cart =  Cart.objects.create(
            cart_id = _cart_id(request)
       )
    
    cart.save()

    # Variation handling
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass
            #print(variation)
    #return HttpResponse(color+' '+size)
    #exit()
    is_cart_item_exist = CartItem.objects.filter(product=product,  cart=cart).exists()
    if is_cart_item_exist:
    #try:
        cart_item = CartItem.objects.filter(product=product,  cart=cart)
        # Grouping Variation
        # existing_variation -> database, current_variation -> product_variation and item id -> database
        exist_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variation.all()
            exist_var_list.append(list(existing_variation))
            id.append(item.id)
        #print(exist_var_list)

        if product_variation in exist_var_list:
            # increase the cart item quantity
            index = exist_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            # create a new cart item
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                item.variation.clear()      
                item.variation.add(*product_variation)
            
            #cart_item.quantity += 1 # increment the quantity
            item.save()
    else:
    #except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
        if len(product_variation) > 0:
           cart_item.variation.clear()
           cart_item.variation.add(*product_variation)
                
        cart_item.save()
    #return HttpResponse(cart_item.product) # check to the product

    return redirect('cart')

# Decrement qunatity remove_cart
def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

# remove cart item from cart
def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

# Cart View
def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100 # add 2% tax
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items':cart_items,
        'tax': tax,
        'grand_total':grand_total,
    }
    return render(request, 'store/cart.html', context)
