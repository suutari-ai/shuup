from django.utils.translation import activate

from shoop.testing.factories import (
    create_random_person, get_default_customer_group, get_shop
)
from shoop.testing.utils import apply_request_middleware


def initialize_test(rf, include_tax=False):
    activate("en")
    shop = get_shop(prices_include_tax=include_tax)

    group = get_default_customer_group()
    customer = create_random_person()
    customer.groups.add(group)
    customer.save()

    request = rf.get("/")
    request.shop = shop
    apply_request_middleware(request)
    request.customer = customer
    return request, shop, group
