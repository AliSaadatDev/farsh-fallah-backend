# سریع شروع تست - Quick Start Guide

## تست کامل برنامه

```bash
# فعال کردن محیط مجازی (اگر بر روی ویندوز نیستید)
source env/bin/activate

# برای Windows:
env\Scripts\activate.bat

# اجرای تمام تست‌ها
python manage.py test main_app.test_complete

# با نمایش جزئیات بیشتر
python manage.py test main_app.test_complete -v 2

# تست کلاس خاص
python manage.py test main_app.test_complete.ProductModelTests

# تست متد خاص
python manage.py test main_app.test_complete.ProductModelTests.test_product_creation
```

## ساختار تست‌ها

| تعداد تست | نام کلاس | توضیح |
|----------|---------|--------|
| 4 | ProductModelTests | تست‌های مدل Product |
| 6 | OrderModelTests | تست‌های مدل Order و OrderItem |
| 6 | ProductSerializerTests | تست‌های Serializer و validation |
| 12 | ProductViewSetTests | تست‌های API محصولات |
| 4 | OrderViewSetTests | تست‌های API سفارشات |
| 9 | ReportsViewSetTests | تست‌های گزارشات |
| 2 | IntegrationTests | تست‌های جریان کامل |
| 4 | EdgeCaseTests | تست‌های خطا و موارد حاشیه‌ای |
| **48** | **جمع** | **تمام تست‌ها** |

## نتیجه انتظار‌رفته

```
Ran 48 tests in 0.1-0.2 seconds
OK
```

## دستورات مفید

### اجرای تست‌های خاص
```bash
# تست‌های Product فقط
python manage.py test main_app.test_complete.ProductModelTests
python manage.py test main_app.test_complete.ProductViewSetTests

# تست‌های Order فقط
python manage.py test main_app.test_complete.OrderModelTests
python manage.py test main_app.test_complete.OrderViewSetTests

# تست‌های Reports
python manage.py test main_app.test_complete.ReportsViewSetTests

# تست‌های Integration
python manage.py test main_app.test_complete.IntegrationTests
```

### بررسی پوشش تست (Coverage)
```bash
# نصب coverage اگر نصب نشده
pip install coverage

# اجرای تست‌ها با coverage
coverage run --source='.' manage.py test main_app.test_complete

# نمایش گزارش
coverage report

# تولید گزارش HTML
coverage html
# بازکردن htmlcov/index.html در مرورگر
```

## ساختار فایل تست

```
main_app/
├── test_complete.py          # فایل تست جامع (48 تست)
├── TEST_DOCUMENTATION.md      # مستندات کامل
├── models.py
├── views.py
├── serializers.py
└── urls.py
```

## چیزهایی که تست می‌شود

✅ **مدل‌ها (Models)**
- ایجاد محصول و سفارش
- محاسبات خودکار (سود، قیمت نهایی)
- تایید صحت داده‌ها

✅ **Serializers**
- تایید صحت قیمت‌ها (منفی نباشد)
- بررسی سازگاری نوع محصول و شاخه
- الزام به فیلدهای مورد نیاز (size برای فرش، length/width برای تابلو)

✅ **API (Views)**
- لیست محصولات و سفارشات
- جستجو و فیلتر کردن
- مرتب‌سازی
- صفحه‌بندی
- ایجاد، به‌روزرسانی، حذف

✅ **گزارشات**
- کل درآمد
- کل سود
- فروش روزانه/ماهانه/سالانه
- بهترین محصولات
- داده‌های داشبورد

✅ **موارد خاص**
- خطاهای اعتبارسنجی
- جریان‌های کامل (ایجاد محصول → سفارش)
- صفحه‌بندی برای داده‌های زیاد

## اگر تست ناموفق باشد

### 1. بررسی محیط Python
```bash
python --version  # باید 3.8+
pip list | grep Django  # باید نصب شده باشد
```

### 2. اطمینان از تهیه مایل‌کشن
```bash
cd farsh
python manage.py migrate
```

### 3. اجرای تست واحد
```bash
# تست یک متد خاص برای یافتن خطا
python manage.py test main_app.test_complete.ProductModelTests.test_product_creation -v 3
```

### 4. پاک کردن پایگاه داده تست
```bash
# اگر مشکل مربوط به کش باشد
python manage.py test main_app.test_complete --keepdb=False
```

## نکات مهم

1. **تست‌های جدید بنویسید**: برای هر ویژگی جدید یک تست بنویسید
2. **تست‌ها را اجرا کنید**: قبل از commit کردن کد
3. **مستندات**: مستندات خود را به‌روز نگه دارید
4. **Coverage**: سعی کنید coverage بالای 80% را حفظ کنید

## منابع

- [Django Testing Documentation](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [TEST_DOCUMENTATION.md](./TEST_DOCUMENTATION.md) - مستندات کامل

---

**نکته**: تمام متن‌های فارسی توسط تست‌ها پشتیبانی می‌شود ✅
