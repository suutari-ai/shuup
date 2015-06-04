Taxes in Shoop
==============

Shoop supports flexible taxation of order items by pluggable
:class:`~shoop.core.taxing.TaxModule` addons. Most important tax related
models provided by Shoop Core are :class:`~shoop.core.models.Tax`,
:class:`~shoop.core.models.TaxClass` and
:class:`~shoop.core.models.CustomerTaxGroup`.  Tax defines properties of
the tax, e.g. its rate, code, name and such.  TaxClass is is assigned to
products and payment & shipping methods and CustomerTaxGroup is assigned to customers, i.e. to :class:`~shoop.core.mofe

Settings
--------

shoop.core setting:

.. code-block:: python

   SHOOP_TAX_MODULE = "default_tax"

Classes
-------

LineTax interface
^^^^^^^^^^^^^^^^^

  * tax
  * name
  * amount
  * base_amount (Amount that this tax is calculated from)
  * rate (property calculated from amount / base_amount)

OrderLineTax (creatable from LineTax)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  * FK: order_line
  * FK: tax (NULL) # for reporting
  * name
  * amount
  * base_amount
  * ordering
  * rate (cached)

OrderLine
^^^^^^^^^

  .. code-block:: python

     def cache_prices(self):
         self.tax_amount = sum(t.amount for t in self.taxes)
         self.taxful_price = self.taxless_price + self.tax_amount
         self.tax_rate = self.tax_amount / self.taxless_amount

Tax
^^^

  * identifier (NULL)
  * name (i18n)
  * rate (%)
  * value (home currency)

TaxClass
^^^^^^^^

  * identifier
  * name (i18n)

CustomerTaxGroup
^^^^^^^^^^^^^^^^

  * identifier
  * name (i18n)

Product / Method
^^^^^^^^^^^^^^^^

  * ...
  * tax_class (FK)
  * ...

default_tax.TaxRule
^^^^^^^^^^^^^^^^^^^

  * tax_classes (M2M)
  * customer_tax_groups (M2M)
  * enabled
  * countries
  * regions (regexp? :D)
  * postal_codes (regexp? :D)
  * tax (FK)
  * priority (Rules with same priority are value-added (e.g. US taxes)
    and rules with different priority are compound taxes (e.g. Canada
    Quobec PST usecase))

TaxModule
^^^^^^^^^

  * get_product_tax_amount(tax_view, product) -> home currency (Called
    upon product price saving to recache things in ShopProduct)
  * get_method_tax_amount(tax_view, method) -> home currency
  * get_line_taxes(order_source, line) -> Iterable[LineTax]
  * ...


PriceTaxContext
^^^^^^^^^^^^^^^

  * customer_tax_group (FK)
  * location (country, region, postal_code, ...)
  * show_taxful_prices : bool
