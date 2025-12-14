from django.db import models
from django.db.models import CheckConstraint, Q
from decimal import Decimal

# branch lists
CARPET_BRANCHES = [
    ("abrisham_qom", "ابریشم طرح قم"),
    ("tabriz", "تبریز"),
    ("naein", "نائین"),
    ("hood_birjand", "هود بیرجند"),
    ("qashqai", "قشقایی"),
    ("arak", "اراک"),
    ("qom", "قم"),
    ("torkaman", "ترکمن"),
    ("esfahan", "اصفهان"),
    ("saregh", "سارق"),
    ("ashayeri", "عشایری"),
    ("bakhtiar", "بختیار"),
    ("ardakan", "اردکان"),
    ("kashan", "کاشان"),
    ("kashm", "کاشم"),
    ("other_carpet", "متفرقه"),
]

TABLEAU_BRANCHES = [
    ("gol", "گل"),
    ("fransi", "فرانسوی"),
    ("mazhabi", "مذهبی"),
    ("animal", "حیوان و پرنده"),
    ("other_tableau", "متفرقه"),
    ("abrisham_qom", "ابریشم طرح قم"),
    ("chehre", "چهره"),
    ("tarikhi", "تاریخی"),
    ("manzare", "منظره"),
]

CROP_CHOICES = [("chele nakh abrisham", "چله نخ ابریشم"),
                ("chele abrisham", "چله ابریشم"),
            ]

class Product(models.Model):
    TYPE_CHOICES = [
        ('carpet', 'فرش'),
        ('tableau', 'تابلو فرش'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    branch = models.CharField(max_length=50, choices=CARPET_BRANCHES + TABLEAU_BRANCHES)
    serial_number = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    crop_sex = models.CharField(max_length=50, choices=CROP_CHOICES, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    length = models.CharField(max_length=50, null=True, blank=True)
    width = models.CharField(max_length=50, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            CheckConstraint(check=Q(unit_price__gte=0), name="unit_price_non_negative"),
            CheckConstraint(check=Q(sale_price__gte=0) | Q(sale_price__isnull=True), name="sale_price_non_negative"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.name + (f"({self.serial_number}) >>> ({self.length} x {self.width})" if self.serial_number else "")


class Order(models.Model):
    customer_name = models.CharField(max_length=255, default="مشتری ناشناخته")
    customer_phone = models.CharField(max_length=20, null=True, blank=True)
    customer_city = models.CharField(max_length=100, null=True, blank=True)
    customer_state = models.CharField(max_length=100, null=True, blank=True)
    customer_region = models.CharField(max_length=100, null=True, blank=True)
    customer_address = models.TextField(null=True, blank=True)

    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ["-order_date"]

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    final_price = models.DecimalField(max_digits=12, decimal_places=2)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.price is None:
            self.price = Decimal('0.00')
        if self.discount is None:
            self.discount = Decimal('0.00')

        self.final_price = self.price - self.discount
        if self.final_price < Decimal('0.00'):
            self.final_price = Decimal('0.00')

        unit_price = self.product.unit_price or Decimal('0.00')
        self.profit = self.final_price - unit_price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} in order {self.order_id}"
