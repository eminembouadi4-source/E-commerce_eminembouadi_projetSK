import pytest
from decimal import Decimal

@pytest.mark.django_db
def test_order_str_and_items(order):
    assert 'CMDTEST' in str(order)
    assert order.items.count() == 1






