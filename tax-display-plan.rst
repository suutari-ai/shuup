Price displaying hide prides, pre-tax or with taxes
===================================================

Notes on how to implement displaying prices hide prices, pre-tax or with taxes
based on customer or customer group preference.

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

  * Currently I decided to use the same display taxness for prices in
    basket but not for orders.

* Should we block access to basket and checkout if prices is hidden?

* Should we block adding to basket if prices is hidden?

* Should we raise from pricing filters if the hide price mode is on?

Plan
----

 * Add a variable to the request object which controls display taxness.

   * Implemented as `request.price_display_options` which is a
     `shoop.core.pricing.PriceDisplayOptions` object.

 * Implement Jinja filters similar to the `money` which respects
   `request.price_display_options`.

   * See `shoop.core.templatetags.price`.

* Convert all appropriate usages of `money` filter to the new filters.

  * See the diffs in jinja files for examples.

TODO
----

* Calculating taxes for basket does not work yet.  It seems that
  ``basket.tax_amount`` always returns 0 EUR.
* Add translation for ``PriceDisplayOption`` enum
