import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_config():
    print("🧪 Test de configuration email...")
    
    try:
        # Test simple
        send_mail(
            subject='🧪 Test Email Configuration',
            message='Ceci est un test de configuration email Django.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['kotchid6@gmail.com'],  # ⚠️ REMPLACEZ
            fail_silently=False,
        )
        print("✅ Email envoyé avec succès!")
        print(f"📧 De: {settings.DEFAULT_FROM_EMAIL}")
        print(f"📧 À: kotchid6@gmail.com")  # ⚠️ REMPLACEZ
        print("🔧 Configuration SMTP fonctionne!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("💡 Solutions:")
        print("1. Vérifiez EMAIL_HOST_USER et EMAIL_HOST_PASSWORD dans settings.py")
        print("2. Activez l'authentification à 2 facteurs Gmail")
        print("3. Créez un mot de passe d'application")
        print("4. Vérifiez votre connexion internet")

if __name__ == "__main__":
    test_email_config()