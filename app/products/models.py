from functools import lru_cache

import pycountry
from django.contrib.auth import get_user_model
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


@lru_cache
def get_countries_choices():
    return [(country.alpha_2, country.alpha_2) for country in pycountry.countries]


class Supplier(models.Model):
    name = models.CharField(max_length=50, unique=True)

    address = models.CharField(max_length=150)

    phone_number = models.CharField(max_length=15)

    since_date = models.DateTimeField(auto_now_add=True)


class Session(models.Model):
    session_id = models.IntegerField(unique=True)

    supplier = models.ForeignKey(
        Supplier, null=True, on_delete=models.SET_NULL, related_name="sessions"
    )

    user = models.ForeignKey(
        get_user_model(), null=True, on_delete=models.SET_NULL, related_name="sessions"
    )

    start_time = models.DateTimeField()

    ent_time = models.DateTimeField()


class Category(models.Model):
    categ_id = models.IntegerField(null=True, default=None)

    category_id = models.CharField(null=True, default=None, max_length=15)

    name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["categ_id", "category_id"], name="unique_category"
            )
        ]


class MeatInfo(models.Model):
    country_of_disassembly = models.CharField(
        max_length=2, null=True, default=None, choices=get_countries_choices()
    )

    country_of_rearing = models.CharField(
        max_length=2, null=True, default=None, choices=get_countries_choices()
    )

    country_of_slaughter = models.CharField(
        max_length=2, null=True, default=None, choices=get_countries_choices()
    )

    cutting_plant_registration = models.CharField(
        max_length=150, null=True, default=None
    )

    slaughterhouse_registration = models.CharField(
        max_length=150, null=True, default=None
    )

    lot_number = models.CharField(max_length=50, null=True, default=None)


class Product(MPTTModel):
    # type
    GTIN = "gtin"
    WHITELISTED_PLU = "whitelisted_plu"

    # packaging
    PUG = "PUG"
    CT = "CT"
    CU = "CU"
    BO = "BO"
    NE = "NE"
    BX = "BX"
    CR = "CR"
    BJ = "BJ"
    JR = "JR"
    PU = "PU"

    # trade_item_unit_descriptor
    CASE = "CASE"
    BASE_UNIT_OR_EACH = "BASE_UNIT_OR_EACH"

    # trade_item_unit_descriptor_name
    KARTON = "Karton"
    BASISEINHEIT = "Basiseinheit"

    # Validated status
    VALIDATED = "validated"
    UNVALIDATED = "unvalidated"

    # vat_rate
    STANDARD = "STANDARD"
    LOW = "LOW"

    # hierarchical relationship:
    parent = TreeForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL, related_name="products"
    )

    session = models.ForeignKey(
        Session, null=True, on_delete=models.SET_NULL, related_name="products"
    )

    code = models.CharField(max_length=40)

    TYPE_CHOICES = [
        (GTIN, "gtin"),
        (WHITELISTED_PLU, "whitelisted_plu"),
    ]
    # It might not be present in the request's payload.
    # But when it is, it will be in:
    # item -> type
    code_type = models.CharField(
        max_length=len(WHITELISTED_PLU), choices=TYPE_CHOICES, null=True, default=None
    )

    # It always appears in the request payload, but it could be "", null or a valid str.
    comment = models.CharField(blank=True, null=True, default=None, max_length=100)

    amount_multiplier = models.IntegerField()

    brand = models.CharField(max_length=150)

    description = models.CharField(max_length=200)

    # If present and False, set None
    edeka_article_number = models.CharField(max_length=20, null=True, default=None)

    # IN the payload could be a float or a dict:
    # "net_weight": {
    # 		"amount": 1,
    # 		"unit": 3
    # },
    net_weight = models.FloatField()

    # IN the payload could be a float, not be present or a dict:
    # "gross_weight": {
    # 		"amount": 1,
    # 		"unit": 3
    # },
    gross_weight = models.FloatField(null=True, default=None)

    # Sometimes it isn't present for an "item" as an independent field.
    # But in that case, it's most probably inside the received net_weight field:
    # net_weight.unit as a number.
    # Should be investigated how to convert from # -> str before store in the database.
    unit_name = models.CharField(max_length=3)

    # If false, set None
    notes = models.CharField(null=True, default=None, max_length=200)

    PACKAGING_CHOICES = [
        (PUG, "PUG"),
        (CT, "CT"),
        (CU, "CU"),
        (BO, "BO"),
        (NE, "NE"),
        (BX, "BX"),
        (CR, "CR"),
        (BJ, "BJ"),
        (JR, "JR"),
        (PU, "PU"),
    ]
    # If it appears two times like in:
    # "packaging": false,
    # "packaging": "NE",
    # Use the last one
    packaging = models.CharField(
        max_length=5,
        choices=PACKAGING_CHOICES,
    )

    TRADE_ITEM_UNIT_DESCRIPTOR_CHOICES = [
        (CASE, "CASE"),
        (BASE_UNIT_OR_EACH, "BASE_UNIT_OR_EACH"),
    ]
    # In the request payload it is always present, but could appear as either:
    # - trade_item_unit_descriptor
    # - trade_item_descriptor
    # But if it appears as "trade_item_descriptor", THEN it should be stored as
    # "trade_item_unit_descriptor" in the database.
    trade_item_unit_descriptor = models.CharField(
        max_length=len(BASE_UNIT_OR_EACH), choices=TRADE_ITEM_UNIT_DESCRIPTOR_CHOICES
    )

    TRADE_ITEM_UNIT_DESCRIPTOR_NAME_CHOICES = [
        (KARTON, "Karton"),
        (BASISEINHEIT, "Basiseinheit"),
    ]
    # It could not exist in the request's payload for an "item".
    # In that case, null/None should be inserted
    trade_item_unit_descriptor_name = models.CharField(
        null=True,
        default=None,
        max_length=len(BASISEINHEIT),
        choices=TRADE_ITEM_UNIT_DESCRIPTOR_NAME_CHOICES,
    )

    # It could not be present in the request's payload for an "item".
    # In that case, null/None should be inserted
    requires_best_before_date = models.BooleanField(null=True, default=None)

    # It could not exist in the request's payload for an "item".
    # In that case, False should be inserted.
    # ONLY if that field is present, should the following fields be looked after in the request's payload:
    # - country_of_disassembly
    # - country_of_rearing
    # - country_of_slaughter
    # - cutting_plant_registration
    # - slaughterhouse_registration
    # - lot_number
    requires_meat_info = models.BooleanField(default=False)

    # Should ONLY be set to a MeatInfo IF requires_meat_info is True
    meat_info = models.OneToOneField(MeatInfo, null=True, on_delete=models.SET_NULL)

    VALIDATED_STATUS_CHOICES = [
        (VALIDATED, "validated"),
        (UNVALIDATED, "unvalidated"),
    ]
    # It might appear as any of the two following forms:
    # - validation_status
    # - status
    # It should be stored as "validation_status"
    validation_status = models.CharField(
        max_length=len(UNVALIDATED), choices=VALIDATED_STATUS_CHOICES
    )

    # If present, it will appear under the key "item" in:
    # "vat": {
    #     "DEU": { ------------------> "DEU" will be used as "vat_country_name"
    #         "label": "DE7",
    #         "rate": 19
    #     }
    # },
    vat_country_name = models.CharField(max_length=30, null=True, default=None)

    # If present, it will appear under the key "item" in:
    # "vat": {
    #     "DEU": {
    #         "label": "DE7",------------------> "DE7" will be used as "vat_label"
    #         "rate": 19
    #     }
    # },
    vat_label = models.CharField(max_length=15, null=True, default=None)

    # If present, it will appear under the key "item" in:
    # "vat": {
    #     "DEU": {
    #         "label": "DE7",
    #         "rate": 19------------------> "19 will be used as "vat_rate_code"
    #     }
    # },
    vat_rate_code = models.IntegerField(null=True, default=None)

    VAT_RATE_CHOICES = [
        (STANDARD, "STANDARD"),
        (LOW, "LOW"),
    ]
    # If present, it will appear under the key "item" in:
    # "item": {
    #     ...
    #     "vat_rate": "LOW"
    #     ...
    # },
    vat_rate = models.CharField(
        max_length=len(STANDARD), choices=VAT_RATE_CHOICES, null=True, default=None
    )

    regulated_name = models.CharField(max_length=100, null=True, default=None)


class StocksByBestBeforeDate(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stocks_by_expiry_date"
    )
    bbd = models.DateTimeField(null=True, default=None)
    amount = models.IntegerField()
