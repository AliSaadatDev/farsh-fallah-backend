from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random

from django.db.models import Sum

from .models import Product, Order, OrderItem


class BulkDataReportTests(APITestCase):
    """Create many products and orders to test reporting endpoints."""

    def setUp(self):
        self.client = APIClient()

        # Create 400 carpets and 400 tableaus efficiently
        carpets = []
        tableaus = []
        for i in range(400):
            carpets.append(Product(
                type='carpet',
                branch='tabriz' if i % 2 == 0 else 'abrisham_qom',
                name=f'Carpet {i}',
                unit_price=Decimal('1000.00'),
                sale_price=Decimal('900.00'),
                size='3x4'
            ))

        for i in range(400):
            tableaus.append(Product(
                type='tableau',
                branch='gol' if i % 2 == 0 else 'fransi',
                name=f'Tableau {i}',
                unit_price=Decimal('1500.00'),
                sale_price=Decimal('1400.00'),
                length='100',
                width='150'
            ))

        Product.objects.bulk_create(carpets + tableaus)

        # Cache product ids for random selection
        self.products = list(Product.objects.values_list('id', flat=True))

        # Prepare date buckets: 1 year ago, 3 months, 2 months, 1 month, last week, today
        now = timezone.now()
        self.date_offsets = [365, 90, 60, 30, 7, 0]

        # Create 200 orders distributed across dates
        for i in range(200):
            days = random.choice(self.date_offsets)
            order_date = now - timedelta(days=days)

            order = Order.objects.create(
                customer_name=f'Customer {i}',
                customer_phone=f'0912{i:07d}'[:20],
                customer_address='Test Address',
                order_date=order_date,
                total_price=Decimal('0.00'),
                total_profit=Decimal('0.00')
            )

            # Add 1-4 items per order
            items_count = random.randint(1, 4)
            for _ in range(items_count):
                pid = random.choice(self.products)
                product = Product.objects.get(pk=pid)
                price = product.sale_price if product.sale_price is not None else product.unit_price
                discount = Decimal(str(random.choice([0, 50, 100, 150])))

                item = OrderItem(
                    order=order,
                    product=product,
                    price=price,
                    discount=discount
                )
                item.save()

            # Recalculate order totals
            totals = order.items.aggregate(total_price=Sum('final_price'), total_profit=Sum('profit'))
            order.total_price = totals.get('total_price') or Decimal('0.00')
            order.total_profit = totals.get('total_profit') or Decimal('0.00')
            order.save(update_fields=['total_price', 'total_profit'])

    def test_reports_endpoints_return_success(self):
        # total revenue
        r = self.client.get('/api/reports/total_revenue/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('total_revenue', r.data)

        # sales by product
        r = self.client.get('/api/reports/sales_by_product/')
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.data, list)
        self.assertGreater(len(r.data), 0)

        # top products
        r = self.client.get('/api/reports/top_products/')
        self.assertEqual(r.status_code, 200)

        # dashboard
        r = self.client.get('/api/reports/dashboard/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('today_sales', r.data)
        self.assertIn('month_sales', r.data)

        # sales range (from 400 days ago to today)
        start = (timezone.now() - timedelta(days=400)).date()
        end = timezone.now().date()
        r = self.client.get(f'/api/reports/sales_range/?start={start}&end={end}')
        self.assertEqual(r.status_code, 200)
        self.assertIn('total_sales', r.data)
