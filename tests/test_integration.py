"""
Tests d'intégration - Flux complets de l'application
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from shop.models import Cart, CartItem, Order, OrderItem, Product, Category
from decimal import Decimal

User = get_user_model()


@pytest.mark.django_db
class TestCompleteOrderFlow:
    """Tests d'intégration: Flux complet de commande"""
    
    def test_complete_purchase_flow(self, client, create_user, category):
        """Test: Flux complet d'achat (ajout panier -> checkout -> commande)"""
        # Créer un vendeur et un produit
        vendor = create_user(username='vendor1', user_type='vendeur', is_approved=True)
        client_user = create_user(username='buyer', user_type='client')
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        image = SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg')
        product = Product.objects.create(
            vendeur=vendor,
            name='Integration Test Product',
            description='Test',
            price=Decimal('29.99'),
            category=category,
            image=image,
            stock=10
        )
        
        # Se connecter en tant que client
        client.login(username='buyer', password='pass1234')
        
        # 1. Ajouter au panier
        response = client.get(reverse('add_to_cart', kwargs={'product_id': product.id}))
        assert response.status_code in (302, 301)
        
        # Vérifier que le panier contient le produit
        cart = Cart.objects.get(user=client_user)
        assert cart.items.count() == 1
        assert cart.items.first().product == product
        
        # 2. Voir le panier
        response = client.get(reverse('cart_view'))
        assert response.status_code == 200
        assert cart.total_items == 1
        
        # 3. Aller au checkout
        response = client.get(reverse('checkout'))
        assert response.status_code == 200
        
        # 4. Passer la commande
        response = client.post(reverse('checkout'), {
            'shipping_address': '123 Test Street',
            'billing_address': '123 Test Street'
        })
        assert response.status_code in (302, 301)
        
        # Vérifier que la commande a été créée
        order = Order.objects.filter(user=client_user).first()
        assert order is not None
        assert order.total_amount == product.price
        assert order.items.count() == 1
        assert order.items.first().product == product
        
        # Vérifier que le panier est vidé
        cart.refresh_from_db()
        assert cart.items.count() == 0


@pytest.mark.django_db
class TestVendorProductManagement:
    """Tests d'intégration: Gestion des produits par vendeur"""
    
    def test_vendor_adds_and_views_products(self, client, create_user, category):
        """Test: Vendeur ajoute et voit ses produits"""
        vendor = create_user(username='vendor2', user_type='vendeur', is_approved=True)
        client.login(username='vendor2', password='pass1234')
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io
        # Créer une vraie image PNG valide
        img = Image.new('RGB', (1, 1), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        image = SimpleUploadedFile('product.png', img_bytes.read(), content_type='image/png')
        
        # Ajouter un produit
        response = client.post(reverse('add_product'), {
            'name': 'New Product',
            'description': 'Description',
            'price': '49.99',
            'category': category.id,
            'stock': 5,
            'image': image
        })
        assert response.status_code in (302, 301)
        
        # Vérifier que le produit existe
        product = Product.objects.filter(vendeur=vendor, name='New Product').first()
        assert product is not None
        assert product.vendeur == vendor
        
        # Voir la liste des produits
        response = client.get(reverse('vendor_products'))
        assert response.status_code == 200
        assert product in response.context['products']


@pytest.mark.django_db
class TestUserRegistrationFlow:
    """Tests d'intégration: Flux d'inscription"""
    
    def test_client_registration_flow(self, client):
        """Test: Inscription et connexion d'un client"""
        # S'inscrire
        response = client.post(reverse('register'), {
            'username': 'newclient',
            'email': 'newclient@test.com',
            'user_type': 'client',
            'password1': 'testpass123',
            'password2': 'testpass123',
        })
        assert response.status_code in (302, 301)
        
        # Vérifier que l'utilisateur existe
        user = User.objects.get(username='newclient')
        assert user.user_type == 'client'
        assert user.is_approved is False  # Les clients sont approuvés par défaut
        
        # Se connecter
        response = client.post(reverse('login'), {
            'username': 'newclient',
            'password': 'testpass123'
        })
        assert response.status_code in (302, 301)
    
    def test_vendor_registration_flow(self, client):
        """Test: Inscription d'un vendeur (doit attendre approbation)"""
        # S'inscrire en tant que vendeur
        response = client.post(reverse('register'), {
            'username': 'newvendor',
            'email': 'newvendor@test.com',
            'user_type': 'vendeur',
            'password1': 'testpass123',
            'password2': 'testpass123',
        })
        assert response.status_code in (302, 301)
        
        # Vérifier que le vendeur existe mais n'est pas approuvé
        user = User.objects.get(username='newvendor')
        assert user.user_type == 'vendeur'
        assert user.is_approved is False
        
        # Tentative de connexion devrait échouer
        response = client.post(reverse('login'), {
            'username': 'newvendor',
            'password': 'testpass123'
        })
        # Devrait rester sur la page de login
        assert response.status_code == 200


@pytest.mark.django_db
class TestCartOperations:
    """Tests d'intégration: Opérations sur le panier"""
    
    def test_cart_add_update_remove(self, client, create_user, product):
        """Test: Ajouter, mettre à jour et retirer du panier"""
        user = create_user(username='cartuser', user_type='client')
        client.login(username='cartuser', password='pass1234')
        
        # Ajouter au panier
        response = client.get(reverse('add_to_cart', kwargs={'product_id': product.id}))
        assert response.status_code in (302, 301)
        
        cart = Cart.objects.get(user=user)
        cart_item = cart.items.first()
        assert cart_item.quantity == 1
        
        # Ajouter à nouveau (devrait incrémenter)
        response = client.get(reverse('add_to_cart', kwargs={'product_id': product.id}))
        cart_item.refresh_from_db()
        assert cart_item.quantity == 2
        
        # Mettre à jour la quantité
        response = client.post(reverse('update_cart_item', kwargs={'item_id': cart_item.id}), {
            'quantity': '5'
        })
        cart_item.refresh_from_db()
        assert cart_item.quantity == 5
        
        # Retirer du panier
        response = client.get(reverse('remove_from_cart', kwargs={'item_id': cart_item.id}))
        assert response.status_code in (302, 301)
        assert CartItem.objects.filter(id=cart_item.id).count() == 0


@pytest.mark.django_db
class TestDashboardIntegration:
    """Tests d'intégration: Dashboard selon le type d'utilisateur"""
    
    def test_client_dashboard_shows_orders(self, client, create_user, order):
        """Test: Dashboard client affiche les commandes"""
        client_user = order.user
        client.login(username=client_user.username, password='pass1234')
        
        response = client.get(reverse('dashboard'))
        assert response.status_code == 200
        assert 'orders' in response.context
    
    def test_vendor_dashboard_shows_stats(self, client, create_user, product):
        """Test: Dashboard vendeur affiche les statistiques"""
        vendor = product.vendeur
        client.login(username=vendor.username, password='pass1234')
        
        response = client.get(reverse('dashboard'))
        assert response.status_code == 200
        assert 'total_products' in response.context
        assert 'total_sales' in response.context

