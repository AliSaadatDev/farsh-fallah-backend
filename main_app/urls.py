from rest_framework import routers
from django.urls import path, include
from .views import ProductViewSet, OrderViewSet, ReportsViewSet
from .vies_docs import api_docs

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reports/sales_by_product/', ReportsViewSet.as_view({'get': 'sales_by_product'})),
    path('reports/total_revenue/', ReportsViewSet.as_view({'get': 'total_revenue'})),
    path('reports/daily_sales/', ReportsViewSet.as_view({'get': 'daily_sales'})),
    path('reports/monthly_sales/', ReportsViewSet.as_view({'get': 'monthly_sales'})),
    path('reports/yearly_sales/', ReportsViewSet.as_view({'get': 'yearly_sales'})),
    path('reports/top_products/', ReportsViewSet.as_view({'get': 'top_products'})),
    path('reports/sales_range/', ReportsViewSet.as_view({'get': 'sales_range'})),
    path('reports/dashboard/', ReportsViewSet.as_view({'get': 'dashboard'})),
    path('reports/customers_by_region/', ReportsViewSet.as_view({'get': 'customers_by_region'})),
    path('reports/customers-by-region/', ReportsViewSet.as_view({'get': 'customers_by_region'})),
    path('reports/chart-sales/', ReportsViewSet.as_view({'get': 'chart_sales'})),
    path('reports/chart_sales/', ReportsViewSet.as_view({'get': 'chart_sales'})),
    path('docs/', api_docs, name='api_docs'),
]
