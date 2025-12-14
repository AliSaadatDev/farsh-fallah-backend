from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from main_app.models import Product, Order, OrderItem
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seed the database with test data for frontend development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Product.objects.all().delete()
            Order.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Data cleared'))

        self.stdout.write('Seeding database with test data...')
        
        # Carpet branches
        carpet_branches = [
            "abrisham_qom", "tabriz", "naein", "hood_birjand", "qashqai",
            "arak", "qom", "torkaman", "esfahan", "saregh",
            "ashayeri", "bakhtiar", "ardakan", "kashan", "kashm", "other_carpet"
        ]
        
        # Tableau branches
        tableau_branches = [
            "gol", "fransi", "mazhabi", "animal", "other_tableau",
            "abrisham_qom", "chehre", "tarikhi", "manzare"
        ]

        # Create products
        self.stdout.write('Creating products...')
        
        # Create 50 carpet products
        carpets = []
        for i in range(50):
            carpet = Product.objects.create(
                type='carpet',
                branch=random.choice(carpet_branches),
                name=f'فرش شماره {i+1}',
                description=f'فرش با کیفیت عالی و دوام بالا',
                serial_number=f'CARPET-{i+1:04d}',
                unit_price=Decimal(str(random.randint(500000, 5000000))),
                sale_price=Decimal(str(random.randint(600000, 6000000))),
                length=f'{random.randint(150, 400)}',
                width=f'{random.randint(150, 400)}',
                size=f'{random.randint(150, 400)} x {random.randint(150, 400)}',
            )
            carpets.append(carpet)
        
        # Create 50 tableau products
        tableaus = []
        for i in range(50):
            tableau = Product.objects.create(
                type='tableau',
                branch=random.choice(tableau_branches),
                name=f'تابلو فرش شماره {i+1}',
                description=f'تابلو فرش با طرح زیبا و متنوع',
                serial_number=f'TABLEAU-{i+1:04d}',
                unit_price=Decimal(str(random.randint(300000, 3000000))),
                sale_price=Decimal(str(random.randint(400000, 4000000))),
                length=f'{random.randint(50, 150)}',
                width=f'{random.randint(50, 150)}',
                size=f'{random.randint(50, 150)} x {random.randint(50, 150)}',
            )
            tableaus.append(tableau)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(carpets)} carpets and {len(tableaus)} tableaus'))

        # Create orders with varied dates and cities
        self.stdout.write('Creating orders...')
        now = timezone.now()
        
        # مناطق تهران (1 تا 22)
        tehran_regions = [
            'منطقه 1', 'منطقه 2', 'منطقه 3', 'منطقه 4', 'منطقه 5',
            'منطقه 6', 'منطقه 7', 'منطقه 8', 'منطقه 9', 'منطقه 10',
            'منطقه 11', 'منطقه 12', 'منطقه 13', 'منطقه 14', 'منطقه 15',
            'منطقه 16', 'منطقه 17', 'منطقه 18', 'منطقه 19', 'منطقه 20',
            'منطقه 21', 'منطقه 22'
        ]
        
        # شهرهای مختلف ایران (بیشتر تهران)
        cities = [
            'تهران', 'تهران', 'تهران', 'تهران', 'تهران',  # 50% تهران
            'تهران', 'تهران', 'تهران', 'تهران', 'تهران',
            'اصفهان', 'شیراز', 'مشهد', 'تبریز', 'کرج',  # شهرهای دیگر
            'قم', 'کاشان', 'یزد', 'اهواز', 'ساری'
        ]
        
        customer_names = [
            'علی محمدی', 'فاطمه احمدی', 'محمد رضایی', 'زهرا کریمی',
            'حسن علوی', 'مریم موسوی', 'علیرضا سلیمانی', 'نسیم فرهادی',
            'جمال صادقی', 'سارا شریفی', 'حسین رفاقتی', 'ندا نوری',
            'مهدی صادقی', 'لیلا شاهسوندی', 'رضا یعقوبی', 'آیدا امیری',
            'کاوه سهرابی', 'نیلوفر امیری', 'احمد ملکی', 'لیا نورایی',
            'محمود شریفی', 'فرانک علوی', 'نادر رفیعی', 'سپیده کریمی'
        ]
        
        for order_num in range(300):
            # Spread orders across the last 90 days
            days_ago = random.randint(0, 90)
            order_date = now - timedelta(days=days_ago)
            
            # انتخاب شهر (تهران بیشتر احتمال دارد)
            city = random.choice(cities)
            
            # اگر تهران است، منطقه را انتخاب کن، وگرنه None
            region = random.choice(tehran_regions) if city == 'تهران' else None
            
            order = Order.objects.create(
                customer_name=random.choice(customer_names),
                customer_phone=f'09{random.randint(100000000, 999999999)}',
                customer_city=city,
                customer_region=region,
                customer_address=f'{city}، خیابان {random.choice(["انقلاب", "ولیعصر", "پیروزی", "آزادی", "رسالت"])}, پلاک {random.randint(1, 500)}',
                order_date=order_date,
            )
            
            # Add 1-4 items to each order
            num_items = random.randint(1, 4)
            total_price = Decimal('0')
            total_profit = Decimal('0')
            
            for _ in range(num_items):
                product = random.choice(carpets + tableaus)
                price = product.sale_price or product.unit_price
                discount = Decimal(str(random.randint(0, int(float(price) * 0.2))))
                
                item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=price,
                    discount=discount,
                )
                
                total_price += item.final_price
                total_profit += item.profit
            
            order.total_price = total_price
            order.total_profit = total_profit
            order.save()
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created 300 orders with items (mostly Tehran)'))

        self.stdout.write(self.style.SUCCESS('✓ Database seeding complete!'))
        self.stdout.write('\nDatabase Summary:')
        self.stdout.write(f'  Products: {Product.objects.count()}')
        self.stdout.write(f'  Orders: {Order.objects.count()}')
        self.stdout.write(f'  Order Items: {OrderItem.objects.count()}')
        self.stdout.write('\nYou can now access the API:')
        self.stdout.write('  • GET /api/products/')
        self.stdout.write('  • GET /api/orders/')
        self.stdout.write('  • GET /api/reports/dashboard/')
