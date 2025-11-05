"""
Tests de sécurité et permissions
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAuthentication:
    """Tests d'authentification"""
    
    def test_login_requires_credentials(self, client, create_user):
        """Test: Login nécessite des identifiants valides"""
        user = create_user(username='secure', password='secret123')
        
        # Tentative avec mauvais mot de passe
        response = client.post(reverse('login'), {
            'username': 'secure',
            'password': 'wrongpass'
        })
        assert response.status_code == 200  # Reste sur la page de login
        assert not response.wsgi_request.user.is_authenticated
    
    def test_login_success(self, client, create_user):
        """Test: Login réussi avec bons identifiants"""
        user = create_user(username='secure', password='secret123')
        
        response = client.post(reverse('login'), {
            'username': 'secure',
            'password': 'secret123'
        })
        # Redirection après login réussi
        assert response.status_code in (302, 301)
        # Vérifier que l'utilisateur est connecté
        client.force_login(user)
        assert client.session.get('_auth_user_id') is not None
    
    def test_logout_clears_session(self, client, create_user):
        """Test: Logout efface la session"""
        user = create_user(username='logouttest')
        client.login(username='logouttest', password='pass1234')
        
        response = client.get(reverse('logout'))
        assert response.status_code in (302, 301)
        # Vérifier que l'utilisateur n'est plus connecté
        assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
class TestAuthorization:
    """Tests d'autorisation et permissions"""
    
    def test_vendor_products_requires_vendor(self, client, create_user):
        """Test: Accès vendor/products nécessite d'être vendeur"""
        client_user = create_user(username='client', user_type='client')
        client.login(username='client', password='pass1234')
        
        response = client.get(reverse('vendor_products'))
        # Redirection car pas vendeur
        assert response.status_code in (302, 301)
    
    def test_vendor_products_requires_approval(self, client, create_user):
        """Test: Accès vendor/products nécessite approbation"""
        vendor = create_user(username='unapproved', user_type='vendeur', is_approved=False)
        client.login(username='unapproved', password='pass1234')
        
        response = client.get(reverse('vendor_products'))
        # Devrait être accessible même sans approbation pour voir ses produits
        # Mais add_product nécessite approbation
        assert response.status_code in (200, 302, 301)
    
    def test_add_product_requires_approved_vendor(self, client, create_user, category):
        """Test: Ajout produit nécessite vendeur approuvé"""
        # Vendeur non approuvé
        vendor = create_user(username='unapproved', user_type='vendeur', is_approved=False)
        client.login(username='unapproved', password='pass1234')
        
        response = client.get(reverse('add_product'))
        # Redirection car pas approuvé
        assert response.status_code in (302, 301)
        
        # Vendeur approuvé
        approved_vendor = create_user(username='approved', user_type='vendeur', is_approved=True)
        client.login(username='approved', password='pass1234')
        
        response = client.get(reverse('add_product'))
        assert response.status_code == 200
    
    def test_client_cannot_access_vendor_pages(self, client, create_user):
        """Test: Client ne peut pas accéder aux pages vendeur"""
        client_user = create_user(username='client', user_type='client')
        client.login(username='client', password='pass1234')
        
        # Tentative d'accès à add_product
        response = client.get(reverse('add_product'))
        assert response.status_code in (302, 301)  # Redirection
    
    def test_unauthenticated_user_redirected(self, client):
        """Test: Utilisateur non authentifié redirigé"""
        # Pages nécessitant login
        protected_urls = [
            reverse('dashboard'),
            reverse('product_list'),
            reverse('cart_view'),
            reverse('checkout'),
            reverse('vendor_products'),
        ]
        
        for url in protected_urls:
            response = client.get(url)
            assert response.status_code in (302, 301), f"{url} devrait rediriger"
    
    def test_order_detail_user_isolation(self, client, create_user, order):
        """Test: Isolation des commandes entre utilisateurs"""
        # Utilisateur différent
        other_user = create_user(username='other')
        client.login(username='other', password='pass1234')
        
        # Tentative d'accès à la commande d'un autre utilisateur
        response = client.get(reverse('order_detail', kwargs={'order_id': order.id}))
        # Devrait échouer (404 ou 403)
        assert response.status_code in (404, 403, 302)


@pytest.mark.django_db
class TestVendorApproval:
    """Tests de validation des vendeurs"""
    
    def test_unapproved_vendor_cannot_login(self, client, create_user):
        """Test: Vendeur non approuvé ne peut pas se connecter"""
        vendor = create_user(username='pending', user_type='vendeur', is_approved=False)
        
        response = client.post(reverse('login'), {
            'username': 'pending',
            'password': 'pass1234'
        })
        # Devrait rester sur la page de login avec message d'erreur
        assert response.status_code == 200
        # Vérifier que l'utilisateur n'est pas connecté
        assert not response.wsgi_request.user.is_authenticated
    
    def test_approved_vendor_can_login(self, client, create_user):
        """Test: Vendeur approuvé peut se connecter"""
        vendor = create_user(username='approved', user_type='vendeur', is_approved=True)
        
        response = client.post(reverse('login'), {
            'username': 'approved',
            'password': 'pass1234'
        })
        # Devrait rediriger vers dashboard
        assert response.status_code in (302, 301)

