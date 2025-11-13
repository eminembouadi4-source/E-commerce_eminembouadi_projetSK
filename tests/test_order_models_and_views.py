import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_order_str_and_items(order):
    assert 'CMDTEST' in str(order)
    assert order.items.count() == 1

@pytest.mark.django_db
def test_checkout_decrements_product_stock(client, create_user, product):
    user = create_user(username='stockuser')
    client.login(username='stockuser', password='pass1234')
    from shop.models import Cart, CartItem, Product
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    response = client.post(
        reverse('checkout'),
        data={'shipping_address': 'Adr', 'billing_address': 'Adr'}
    )
    assert response.status_code in (302, 301)
    refreshed = Product.objects.get(pk=product.pk)
    assert refreshed.stock == product.stock - 2, "Le stock produit doit être décrémenté après commande."






