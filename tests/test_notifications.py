import pytest

@pytest.mark.django_db
def test_notifications_marked_read(client, create_user):
    user = create_user(username='notif')
    from shop.models import Notification
    Notification.objects.create(user=user, message='Hello')
    client.login(username='notif', password='pass1234')
    from django.urls import reverse
    resp = client.get(reverse('notifications'))
    assert resp.status_code == 200
    # notifications should be marked read
    assert Notification.objects.filter(user=user, is_read=True).exists()






