Price displaying pre-tax or with taxes
======================================

Notes on how to implement displaying prices pre-tax or with taxes based
on customer or customer group preference.

Terms
-----

original taxness
    Active `PricingModule` might return prices as `TaxfulPrice` or
    `TaxlessPrice` objects.  Usually this depends directly on how shop
    stores prices, pre-tax or with taxes (`Shop.prices_include_tax`).
    Let's call this *original taxness*.

display taxness
    In Front, prices should be displayed pre-tax or with taxes depending
    on a different factor.  It might be customer group setting
    controlled by the merchant, or customer preference, or something
    else.  Let's call this *display taxness*.

Open Questions
--------------
    
* Should we use same display taxness for product and service prices as
  we use for basket line and order line prices?

Plan
----
  
 * Add a variable to the request object which controls display taxness,
   e.g. `request.display_prices_including_taxes`.
 * Implement a Jinja filter similar to the "money" which respects
   request.display_prices_including_taxes. This filter should probably
   have a short name like "price".
 * Convert all usages of "money" filter to use "price" filter where
   possible.
