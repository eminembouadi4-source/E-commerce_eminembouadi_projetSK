from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_registration_email(user):
    """
    Envoie un email de confirmation d'inscription
    """
    try:
        subject = '🎉 Bienvenue sur E-commerce Django !'
        message = f"""
        Bonjour {user.username} !
        
        Félicitations ! Votre compte a été créé avec succès sur notre plateforme E-commerce.
        
        📋 Détails de votre compte :
        - Nom d'utilisateur : {user.username}
        - Type de compte : {user.get_user_type_display()}
        - Date d'inscription : {user.date_joined.strftime('%d/%m/%Y à %H:%M')}
        
        { "⏳ Votre compte vendeur est en attente de validation par notre équipe." if user.user_type == 'vendeur' else "✅ Votre compte client est activé !" }
        
        Vous pouvez dès maintenant :
        • Parcourir nos produits
        • Ajouter des articles à votre panier
        • Passer des commandes
        
        Merci de nous avoir rejoint !
        
        Cordialement,
        L'équipe E-commerce Django
        """
        
        send_mail(
            subject,
            message.strip(),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print(f"✅ Email d'inscription envoyé à {user.email}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur email inscription pour {user.email}: {e}")
        return False

def send_vendor_approval_email(user):
    """
    Envoie un email d'approbation de compte vendeur
    """
    try:
        subject = '✅ Votre compte vendeur a été approuvé !'
        message = f"""
        Félicitations {user.username} !
        
        Votre compte vendeur a été approuvé avec succès 🎉
        
        Vous pouvez dès maintenant :
        • Ajouter vos produits à la vente
        • Gérer votre inventaire
        • Suivre vos commandes
        • Consulter vos statistiques
        
        📈 Commencez à vendre dès maintenant !
        Accédez à votre dashboard vendeur pour ajouter vos premiers produits.
        
        Nous vous souhaitons beaucoup de succès dans vos ventes !
        
        Cordialement,
        L'équipe E-commerce Django
        """
        
        send_mail(
            subject,
            message.strip(),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print(f"✅ Email d'approbation vendeur envoyé à {user.email}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur email approbation vendeur pour {user.email}: {e}")
        return False

def send_order_confirmation_email(order):
    """
    Envoie un email de confirmation de commande
    """
    try:
        subject = f'📦 Confirmation de commande #{order.order_number}'
        
        # Détails des articles
        items_details = ""
        for item in order.items.all():
            items_details += f"• {item.product.name} x {item.quantity} = {item.total_price}€\n"
        
        message = f"""
        Bonjour {order.user.username},
        
        Votre commande a été enregistrée avec succès !
        
        📋 DÉTAILS DE LA COMMANDE :
        Numéro de commande : {order.order_number}
        Date : {order.created_at.strftime('%d/%m/%Y à %H:%M')}
        Statut : {order.get_status_display()}
        Montant total : {order.total_amount}€
        
        🛍️ ARTICLES COMMANDÉS :
        {items_details}
        
        🏠 ADRESSE DE LIVRAISON :
        {order.shipping_address}
        
        💳 ADRESSE DE FACTURATION :
        {order.billing_address}
        
        Nous vous tiendrons informé de l'avancement de votre commande.
        
        Merci pour votre achat !
        
        Cordialement,
        L'équipe E-commerce Django
        """
        
        send_mail(
            subject,
            message.strip(),
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )
        print(f"✅ Email de confirmation commande #{order.order_number} envoyé à {order.user.email}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur email commande #{order.order_number}: {e}")
        return False

def send_test_email():
    """
    Email de test - même que votre script qui fonctionne
    """
    try:
        subject = '🧪 Test Email Configuration - E-commerce'
        message = 'Ceci est un test de configuration email Django depuis l\'app E-commerce.'
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['kotchid6@gmail.com'],
            fail_silently=False,
        )
        print("✅ Email de test envoyé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur email test: {e}")
        return False