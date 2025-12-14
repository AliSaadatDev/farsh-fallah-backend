# create_test_products.py
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "farsh.settings")  # جای farsh.settings نام پروژه خودت باشه
django.setup()

from main_app.models import Product


def create_test_carpet_products():
    for i in range(1, 201):
        Product.objects.create(
            type='carpet',
            branch='tabriz',
            crop_sex='chele abrisham',
            serial_number=f'CARPET-{i:03}',
            name=f'Test Carpet Product {i}',
            description='This is a test carpet product.',
            unit_price=100000 + i * 1000,
            sale_price=120000 + i * 1000,
            size='9',
            image= r"C:\Users\Digiyol\Desktop\farsh_falah\farsh\media\products\default_carpet.jpg"
        )

def create_test_tableau_products():
    for i in range(1, 201):
        Product.objects.create(
            type='tableau',
            branch='gol',
            crop_sex='chele nakh abrisham',
            serial_number=f'TABLEAU-{i:03}',
            name=f'Test Tableau Product {i}',
            description='This is a test tableau product.',
            unit_price=150000 + i * 1500,
            sale_price=180000 + i * 1500,
            length='100',
            width='150',
            image= r"C:\Users\Digiyol\Desktop\farsh_falah\farsh\media\products\default_tableau.jpg"
        )

print("Creating test carpet products...")
create_test_carpet_products()
print("Creating test tableau products...")
create_test_tableau_products()
print("Test products created successfully.")



