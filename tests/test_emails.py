"""
Tests unitaires pour les fonctions d'envoi d'emails
"""
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from shop.models import Order, OrderItem
from shop.emails import (
    send_registration_email,
    send_order_confirmation_email,
    send_vendor_approval_email,
    send_test_email
)

User = get_user_model()


@pytest.mark.django_db
class TestEmailFunctions:
    """Tests unitaires pour les fonctions d'email"""
    
    @patch('shop.emails.send_mail')
    def test_send_registration_email_success(self, mock_send_mail, create_user):
        """Test: Envoi email d'inscription réussi"""
        mock_send_mail.return_value = True
        user = create_user(username='emailtest')
        user.email = 'test@example.com'
        user.save()
        
        result = send_registration_email(user)
        
        assert result is True
        assert mock_send_mail.called
        call_args = mock_send_mail.call_args
        # send_mail(subject, message, from_email, recipient_list, fail_silently)
        assert 'Bienvenue' in call_args[0][0]  # Subject
        assert user.email in call_args[0][3]  # recipient_list is the 4th positional arg
    
    @patch('shop.emails.send_mail')
    def test_send_registration_email_failure(self, mock_send_mail, create_user):
        """Test: Échec d'envoi email d'inscription"""
        mock_send_mail.side_effect = Exception("SMTP Error")
        user = create_user(username='emailfail')
        user.email = 'fail@example.com'
        user.save()
        
        result = send_registration_email(user)
        
        assert result is False
    
    @patch('shop.emails.send_mail')
    def test_send_order_confirmation_email_success(self, mock_send_mail, order):
        """Test: Envoi email de confirmation de commande réussi"""
        mock_send_mail.return_value = True
        order.user.email = 'order@example.com'
        order.user.save()
        
        result = send_order_confirmation_email(order)
        
        assert result is True
        assert mock_send_mail.called
        call_args = mock_send_mail.call_args
        # send_mail(subject, message, from_email, recipient_list, fail_silently)
        assert order.order_number in call_args[0][0]  # Subject
        assert order.user.email in call_args[0][3]  # recipient_list is the 4th positional arg
    
    @patch('shop.emails.send_mail')
    def test_send_order_confirmation_email_failure(self, mock_send_mail, order):
        """Test: Échec d'envoi email de confirmation"""
        mock_send_mail.side_effect = Exception("SMTP Error")
        
        result = send_order_confirmation_email(order)
        
        assert result is False
    
    @patch('shop.emails.send_mail')
    def test_send_vendor_approval_email_success(self, mock_send_mail, create_user):
        """Test: Envoi email d'approbation vendeur réussi"""
        mock_send_mail.return_value = True
        vendor = create_user(username='vendor', user_type='vendeur')
        vendor.email = 'vendor@test.com'
        vendor.save()
        
        result = send_vendor_approval_email(vendor)
        
        assert result is True
        assert mock_send_mail.called
        call_args = mock_send_mail.call_args
        # send_mail(subject, message, from_email, recipient_list, fail_silently)
        assert 'approuvé' in call_args[0][0].lower()  # Subject
        assert vendor.email in call_args[0][3]  # recipient_list is the 4th positional arg
    
    @patch('shop.emails.send_mail')
    def test_send_test_email(self, mock_send_mail):
        """Test: Envoi email de test"""
        mock_send_mail.return_value = True
        
        result = send_test_email()
        
        assert result is True
        assert mock_send_mail.called

