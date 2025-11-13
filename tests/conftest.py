import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

@pytest.fixture
def create_user(db):
    def _create(username='user1', password='pass1234', user_type='client', is_approved=False):
        user = User.objects.create_user(username=username, password=password, user_type=user_type)
        user.is_approved = is_approved
        user.save()
        return user
    return _create

@pytest.fixture
def category(db):
    from shop.models import Category
    return Category.objects.create(name='TestCat', description='Desc')

@pytest.fixture
def product(db, create_user, category):
    from shop.models import Product
    vendeur = create_user(username='vendeur1', user_type='vendeur', is_approved=True)
    # create a small image file to satisfy ImageField
    image = SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg')
    return Product.objects.create(vendeur=vendeur, name='Prod1', description='desc', price=Decimal('9.90'), category=category, image=image, stock=5)

@pytest.fixture
def cart(db, create_user, product):
    from shop.models import Cart, CartItem
    user = create_user(username='client1')
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    return cart

@pytest.fixture
def order(db, create_user, product):
    from shop.models import Order, OrderItem
    user = create_user(username='client2')
    order = Order.objects.create(user=user, order_number='CMDTEST', total_amount=product.price * 2, shipping_address='A', billing_address='B')
    OrderItem.objects.create(order=order, product=product, quantity=2, price=product.price)
    return order






