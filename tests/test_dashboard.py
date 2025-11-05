import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_vendor_dashboard_access(client, create_user, product):
    vendor = create_user(username='vtest', user_type='vendeur', is_approved=True)
    client.login(username='vtest', password='pass1234')
    url = reverse('dashboard')
    resp = client.get(url)
    assert resp.status_code == 200
    assert 'products' in resp.context

@pytest.mark.django_db
def test_client_dashboard_access(client, create_user):
    client_user = create_user(username='ctest', user_type='client')
    client.login(username='ctest', password='pass1234')
    from django.urls import reverse
    resp = client.get(reverse('dashboard'))
    assert resp.status_code == 200

