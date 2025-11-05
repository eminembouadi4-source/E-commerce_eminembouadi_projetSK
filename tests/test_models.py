import pytest
from decimal import Decimal

from django.utils import timezone

@pytest.mark.django_db
def test_custom_user_str(create_user):
    user = create_user(username='bob', user_type='client')
    assert str(user) == f"{user.username} ({user.get_user_type_display()})"

@pytest.mark.django_db
def test_category_str(category):
    assert str(category) == 'TestCat'

@pytest.mark.django_db
def test_product_str(product):
    assert str(product) == 'Prod1'
    assert product.stock == 5
    assert product.is_active is True

@pytest.mark.django_db
def test_cart_totals(cart):
    cart.refresh_from_db()
    # items: 1 product price 9.90 quantity 2 => total 19.80
    assert cart.total_items == 2
    assert float(cart.total_price) == pytest.approx(19.80, rel=1e-3)

@pytest.mark.django_db
def test_cartitem_total_price(cart):
    item = cart.items.first()
    assert float(item.total_price) == pytest.approx(float(item.product.price * item.quantity), rel=1e-3)

@pytest.mark.django_db
def test_order_item_total(order):
    item = order.items.first()
    assert float(item.total_price) == pytest.approx(float(item.price * item.quantity), rel=1e-3)

