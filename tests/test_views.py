import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_accueil_view(client, product):
    url = reverse('accueil')
    resp = client.get(url)
    assert resp.status_code == 200
    assert 'products' in resp.context

@pytest.mark.django_db
def test_product_list_requires_login(client):
    url = reverse('product_list')
    resp = client.get(url)
    # should redirect to login
    assert resp.status_code in (302, 301)

@pytest.mark.django_db
def test_product_detail_view(client, product):
    # login a user
    from django.contrib.auth import get_user_model
    User = get_user_model()
    u = User.objects.create_user(username='cli', password='1234')
    client.login(username='cli', password='1234')
    url = reverse('product_detail', kwargs={'pk': product.pk})
    resp = client.get(url)
    assert resp.status_code == 200
    assert 'product' in resp.context

@pytest.mark.django_db
def test_add_to_cart_flow(client, create_user, product):
    user = create_user(username='cadd')
    client.login(username='cadd', password='pass1234')
    url = reverse('add_to_cart', kwargs={'product_id': product.id})
    resp = client.get(url)
    # add_to_cart redirects to cart_view
    assert resp.status_code in (302, 301)
    from shop.models import Cart
    cart = Cart.objects.get(user=user)
    assert cart.items.count() >= 1

@pytest.mark.django_db
def test_update_cart_item_delete_when_zero(client, create_user, product):
    # add cart and item
    user = create_user(username='cupdate')
    client.login(username='cupdate', password='pass1234')
    from shop.models import Cart, CartItem
    cart = Cart.objects.create(user=user)
    item = CartItem.objects.create(cart=cart, product=product, quantity=1)
    url = reverse('update_cart_item', kwargs={'item_id': item.id})
    # simulate POST with quantity=0 -> should delete
    resp = client.post(url, data={'quantity': '0'})
    assert resp.status_code in (302, 301)
    assert CartItem.objects.filter(id=item.id).count() == 0

@pytest.mark.django_db
def test_update_cart_item_ajax_updates_totals(client, create_user, product):
    user = create_user(username='cajax')
    client.login(username='cajax', password='pass1234')
    from shop.models import Cart, CartItem
    cart = Cart.objects.create(user=user)
    item = CartItem.objects.create(cart=cart, product=product, quantity=1)
    url = reverse('update_cart_item', kwargs={'item_id': item.id})
    response = client.post(
        url,
        data={'quantity': '3'},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    assert response.status_code == 200, f"Une requête AJAX devrait renvoyer 200, reçu {response.status_code}"
    payload = response.json()
    assert payload.get('item_total') == str(product.price * 3)
    assert payload.get('cart_total') == str(product.price * 3)

@pytest.mark.django_db
def test_checkout_creates_order(client, create_user, product):
    user = create_user(username='ccheckout')
    client.login(username='ccheckout', password='pass1234')
    from shop.models import Cart, CartItem
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    url = reverse('checkout')
    # get the form
    resp = client.get(url)
    assert resp.status_code == 200
    # post the order form minimal payload (shipping/billing)
    data = {'shipping_address': 'A', 'billing_address': 'B'}
    resp2 = client.post(url, data=data)
    # should redirect to order detail
    assert resp2.status_code in (302, 301)






