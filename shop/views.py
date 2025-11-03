from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import *
from .forms import *
from .emails import *

def accueil(request):
    products = Product.objects.filter(is_active=True)[:8]
    return render(request, 'home.html', {'products': products})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # ENVOI EMAIL - Version corrigée
            email_sent = send_registration_email(user)
            if email_sent:
                messages.success(request, 'Compte créé avec succès! Email de confirmation envoyé.')
            else:
                messages.warning(request, 'Compte créé mais email de confirmation non envoyé.')
            
            if user.user_type == 'vendeur':
                messages.info(request, 'Votre compte vendeur est en attente de validation.')
            
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = cart.total_price
            order.order_number = f"CMD{timezone.now().strftime('%Y%m%d%H%M%S')}"
            order.save()
            
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            cart.items.all().delete()
            
            # ENVOI EMAIL - Version corrigée
            email_sent = send_order_confirmation_email(order)
            if email_sent:
                messages.success(request, f'Commande {order.order_number} passée avec succès! Email de confirmation envoyé.')
            else:
                messages.warning(request, f'Commande {order.order_number} passée mais email non envoyé.')
            
            Notification.objects.create(
                user=request.user,
                message=f'Votre commande {order.order_number} a été passée avec succès.',
                link=f'/orders/{order.id}/'
            )
            
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm(initial={
            'shipping_address': request.user.address,
            'billing_address': request.user.address,
        })
    
    return render(request, 'checkout.html', {'cart': cart, 'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.user_type == 'vendeur' and not user.is_approved:
                    messages.error(request, 'Votre compte vendeur est en attente de validation.')
                    return render(request, 'registration/login.html', {'form': form})
                
                login(request, user)
                messages.success(request, f'Bienvenue {username}!')
                return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.user_type == 'vendeur':
        products = Product.objects.filter(vendeur=request.user)
        total_products = products.count()
        low_stock_products = products.filter(stock__lt=10).count()
        
        orders = OrderItem.objects.filter(product__vendeur=request.user)
        total_sales = orders.aggregate(total=Sum('price'))['total'] or 0
        
        recent_orders = Order.objects.filter(
            items__product__vendeur=request.user
        ).distinct().order_by('-created_at')[:5]
        
        context = {
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'total_sales': total_sales,
            'recent_orders': recent_orders,
            'products': products[:5],
        }
        return render(request, 'dashboard/vendeur.html', context)
    
    elif request.user.user_type == 'client':
        orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
        return render(request, 'dashboard/client.html', {'orders': orders})
    
    else:
        total_users = CustomUser.objects.count()
        total_vendeurs = CustomUser.objects.filter(user_type='vendeur').count()
        pending_vendeurs = CustomUser.objects.filter(user_type='vendeur', is_approved=False).count()
        total_orders = Order.objects.count()
        recent_orders = Order.objects.all().order_by('-created_at')[:5]
        
        context = {
            'total_users': total_users,
            'total_vendeurs': total_vendeurs,
            'pending_vendeurs': pending_vendeurs,
            'total_orders': total_orders,
            'recent_orders': recent_orders,
        }
        return render(request, 'dashboard/admin.html', context)

@login_required
def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'products/list.html', {'products': products})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, 'products/detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} ajouté au panier!')
    return redirect('cart_view')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/view.html', {'cart': cart})

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Panier mis à jour!')
        else:
            cart_item.delete()
            messages.success(request, 'Article retiré du panier!')
    
    return redirect('cart_view')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Article retiré du panier!')
    return redirect('cart_view')
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})

# ⚠️ SUPPRIMER LES FONCTIONS DUPLIQUÉES CI-DESSOUS ⚠️
# GARDER UNE SEULE VERSION DE vendor_products

@login_required
def vendor_products(request):
    if request.user.user_type != 'vendeur':
        messages.error(request, 'Accès réservé aux vendeurs.')
        return redirect('dashboard')
    
    products = Product.objects.filter(vendeur=request.user)
    
    # Debug: afficher le chemin du template
    import os
    template_path = os.path.join('templates', 'vendor', 'products.html')
    print(f"Chemin du template: {template_path}")
    print(f"Template existe: {os.path.exists(template_path)}")
    
    return render(request, 'vendor/products.html', {'products': products})

@login_required
def add_product(request):
    if request.user.user_type != 'vendeur' or not request.user.is_approved:
        messages.error(request, 'Accès réservé aux vendeurs approuvés.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendeur = request.user
            product.save()
            messages.success(request, 'Produit ajouté avec succès!')
            return redirect('vendor_products')
    else:
        form = ProductForm()
    
    return render(request, 'vendor/add_product.html', {'form': form})

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifications.update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifications})

def custom_logout(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('accueil')