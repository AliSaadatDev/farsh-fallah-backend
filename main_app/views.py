from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.db.models import Count, Sum, F, Q, IntegerField
from django.utils import timezone
from .models import Product, Order, OrderItem, CARPET_BRANCHES, TABLEAU_BRANCHES
from .serializers import ProductSerializer, OrderSerializer, OrderCreateSerializer
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate, Cast


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'serial_number', 'description']
    ordering_fields = ['unit_price', 'sale_price', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        search = params.get("search")
        if search:
            normalized = search.replace("ي", "ی").replace("ك", "ک").strip()
            words = normalized.split()

            for w in words:
                qs = qs.filter(
                    Q(name__icontains=w) |
                    Q(description__icontains=w) |
                    Q(serial_number__icontains=w) |
                    Q(branch__icontains=w) |
                    Q(type__icontains=w) |
                    Q(size__icontains=w) |
                    Q(length__icontains=w) |
                    Q(width__icontains=w)
                )

        min_price = params.get("min_price")
        max_price = params.get("max_price")
        if min_price:
            qs = qs.filter(unit_price__gte=min_price)
        if max_price:
            qs = qs.filter(unit_price__lte=max_price)

        type_filter = params.get("type")
        if type_filter:
            qs = qs.filter(type=type_filter)

        branch = params.get("branch")
        if branch:
            qs = qs.filter(branch=branch)

        size = params.get("size")
        if type_filter == "carpet":
            if size:
                qs = qs.filter(size=size)

        min_length = params.get("min_length")
        max_length = params.get("max_length")
        min_width = params.get("min_width")
        max_width = params.get("max_width")

        if type_filter == "tableau":
            if min_length:
                qs = qs.filter(length__gte=min_length)
            if max_length:
                qs = qs.filter(length__lte=max_length)
            if min_width:
                qs = qs.filter(width__gte=min_width)
            if max_width:
                qs = qs.filter(width__lte=max_width)

        sort = params.get("sort")
        if sort == "newest":
            qs = qs.order_by("-created_at")
        elif sort == "oldest":
            qs = qs.order_by("created_at")
        elif sort == "price_low":
            qs = qs.order_by("unit_price")
        elif sort == "price_high":
            qs = qs.order_by("-unit_price")

        return qs


    
    @action(detail=False, methods=['get'])
    def branches(self, request):
        product_type = request.query_params.get("type")

        if product_type == "carpet":
            return Response(CARPET_BRANCHES)

        elif product_type == "tableau":
            return Response(TABLEAU_BRANCHES)

        return Response({"error": "type لازم است"}, status=400)
        


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-order_date").prefetch_related('items__product')
    serializer_class = OrderSerializer
    search_fields = ['customer_name', 'customer_phone', 'customer_address', 'customer_city', 'customer_region']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        search = params.get("search")
        if search:
            normalized = search.replace("ي", "ی").replace("ك", "ک").strip()
            words = normalized.split()

            for w in words:
                qs = qs.filter(
                    Q(customer_name__icontains=w) |
                    Q(customer_phone__icontains=w) |
                    Q(customer_address__icontains=w) |
                    Q(customer_city__icontains=w) |
                    Q(customer_region__icontains=w)
                )
            
        return qs


    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        order.delete()
        return Response({"message": "Order deleted"}, status=status.HTTP_200_OK)


class ReportsViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def sales_by_product(self, request):
        qs = OrderItem.objects.values('product', 'product__name').annotate(
            sales_count=Count('id'),
            revenue=Sum('final_price')
        ).order_by('-sales_count')
        return Response(list(qs))

    @action(detail=False, methods=['get'])
    def total_revenue(self, request):
        total = OrderItem.objects.aggregate(total_revenue=Sum('final_price')) or {'total_revenue': 0}
        return Response(total)

    @action(detail=False, methods=['get'])
    def total_profit(self, request):
        total = Order.objects.aggregate(total_profit=Sum(F('total_profit'))) or {'total_profit': 0}
        return Response(total)

    @action(detail=False, methods=['get'])
    def top_products(self, request):
        items = (
            OrderItem.objects.values(name=F("product__name"))
            .annotate(sales_count=Count('id'), revenue=Sum('final_price'))
            .order_by("-sales_count")[:10]
        )
        return Response(list(items))

    @action(detail=False, methods=['get'])
    def sales_range(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if not start or not end:
            return Response({"error": "start & end required"}, status=400)
        total = Order.objects.filter(order_date__date__range=[start, end]).aggregate(total=Sum("total_price"))
        total_sales = total.get("total") or 0
        total_profit_agg = Order.objects.filter(order_date__date__range=[start, end]).aggregate(total_profit=Sum("total_profit"))
        total_profit = total_profit_agg.get("total_profit") or 0
        return Response({"start": start, "end": end, "total_sales": total_sales, "total_profit": total_profit})

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        today = timezone.localdate()
        year, month = today.year, today.month
        today_sales = Order.objects.filter(order_date__date=today).aggregate(total=Sum("total_price"))
        today_sales = today_sales.get("total") or 0
        today_profit_agg = Order.objects.filter(order_date__date=today).aggregate(total_profit=Sum("total_profit"))
        today_profit = today_profit_agg.get("total_profit") or 0
        today_orders = Order.objects.filter(order_date__date=today).count()
        month_sales = Order.objects.filter(order_date__year=year, order_date__month=month).aggregate(total=Sum("total_price"))
        month_sales = month_sales.get("total") or 0
        month_profit_agg = Order.objects.filter(order_date__year=year, order_date__month=month).aggregate(total_profit=Sum("total_profit"))
        month_profit = month_profit_agg.get("total_profit") or 0

        top = (
            OrderItem.objects.values(name=F("product__name"))
            .annotate(sales_count=Count('id'))
            .order_by("-sales_count")[:5]
        )

        last_7 = []
        for i in range(7):
            day = today - timezone.timedelta(days=i)
            total = Order.objects.filter(order_date__date=day).aggregate(total=Sum("total_price"))
            total = total.get("total") or 0
            profit_agg = Order.objects.filter(order_date__date=day).aggregate(total_profit=Sum("total_profit"))
            profit = profit_agg.get("total_profit") or 0
            last_7.append({"date": str(day), "sales": total, "profit": profit})
        last_7.reverse()

        inventory_value = None

        return Response({
            "today_sales": today_sales,
            "today_profit": today_profit,
            "today_orders": today_orders,
            "month_sales": month_sales,
            "month_profit": month_profit,
            "top_products": list(top),
            "last_7_days": last_7,
            "inventory_value": inventory_value
        })
    

    @action(detail=False, methods=['get'])
    def chart_sales(self, request):
        period = request.query_params.get('period')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        now = timezone.now()
        today = timezone.localdate()
    
        # ---------------- TODAY (hourly) ----------------
        def get_today_data():
            data = []
            for i in range(23, -1, -1):
                hour_start = now - timedelta(hours=i)
                hour_end = hour_start - timedelta(hours=1)
    
                agg = Order.objects.filter(
                    order_date__gte=hour_end,
                    order_date__lt=hour_start
                ).aggregate(
                    sales=Sum("total_price"),
                    profit=Sum("total_profit")
                )
    
                data.append({
                    "label": hour_end.strftime("%H:%M"),
                    "sales": agg["sales"] or 0,
                    "profit": agg["profit"] or 0,
                })
            return data
    
        # ---------------- WEEK (daily) ----------------
        def get_week_data():
            data = []
            qs = (
                Order.objects
                .filter(order_date__date__gte=today - timedelta(days=6))
                .annotate(day=TruncDate("order_date"))
                .values("day")
                .annotate(
                    sales=Sum("total_price"),
                    profit=Sum("total_profit")
                )
            )
    
            qs_map = {item["day"]: item for item in qs}
    
            for i in range(6, -1, -1):
                day = today - timedelta(days=i)
                item = qs_map.get(day)
                data.append({
                    "label": str(day),
                    "sales": item["sales"] if item else 0,
                    "profit": item["profit"] if item else 0,
                })
            return data
    
        # ---------------- MONTH (daily) ----------------
        def get_month_data():
            data = []
            start = today - timedelta(days=29)
    
            qs = (
                Order.objects
                .filter(order_date__date__range=(start, today))
                .annotate(day=TruncDate("order_date"))
                .values("day")
                .annotate(
                    sales=Sum("total_price"),
                    profit=Sum("total_profit")
                )
            )
    
            qs_map = {item["day"]: item for item in qs}
    
            current = start
            while current <= today:
                item = qs_map.get(current)
                data.append({
                    "label": str(current),
                    "sales": item["sales"] if item else 0,
                    "profit": item["profit"] if item else 0,
                })
                current += timedelta(days=1)
    
            return data
    
        # ---------------- YEAR (monthly) ----------------
        def get_year_data():
            data = []
    
            for i in range(11, -1, -1):
                month_date = today - timedelta(days=i * 30)
                year = month_date.year
                month = month_date.month
    
                agg = Order.objects.filter(
                    order_date__year=year,
                    order_date__month=month
                ).aggregate(
                    sales=Sum("total_price"),
                    profit=Sum("total_profit")
                )
    
                data.append({
                    "label": f"{year}-{month:02d}",
                    "sales": agg["sales"] or 0,
                    "profit": agg["profit"] or 0,
                })
    
            return data
    
        # ---------------- CUSTOM RANGE ----------------
        def get_custom_range_data(start_date, end_date):
            data = []
    
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
            qs = (
                Order.objects
                .filter(order_date__date__range=(start, end))
                .annotate(day=TruncDate("order_date"))
                .values("day")
                .annotate(
                    sales=Sum("total_price"),
                    profit=Sum("total_profit"),
                    count = Count("id"),
                )
                .order_by("day")
            )            

            qs_map = {item["day"]: item for item in qs}

            total_sales = 0
            total_profit = 0
            total_count = 0
            
            current = start
            while current <= end:
                item = qs_map.get(current)
                sales = item["sales"] if item else 0
                profit = item["profit"] if item else 0
                count = item["count"] if item else 0

                total_sales += sales
                total_profit += profit
                total_count += count

                data.append({
                    "label": str(current),
                    "sales": item["sales"] if item else 0,
                    "profit": item["profit"] if item else 0,
                    "count": item["count"] if item else 0,
                })
                current += timedelta(days=1)
    
            return {
                "period": "custom",
                "start_date": start_date,
                "end_date": end_date,
                "total_sales": total_sales,
                "total_profit": total_profit,
                "total_count": total_count,
                "data": data
            }
    
        # ---------------- PRIORITY: CUSTOM RANGE ----------------
        if start_date and end_date:
            return Response({
                "period": "custom",
                "start_date": start_date,
                "end_date": end_date,
                "data": get_custom_range_data(start_date, end_date)
            })
    
        # ---------------- DEFAULT (ALL) ----------------
        if period is None:
            return Response({
                "today": {"period": "today", "data": get_today_data()},
                "week": {"period": "week", "data": get_week_data()},
                "month": {"period": "month", "data": get_month_data()},
                "year": {"period": "year", "data": get_year_data()},
            })
    
        # ---------------- SINGLE PERIOD ----------------
        if period == "today":
            return Response({"period": period, "data": get_today_data()})
    
        if period == "week":
            return Response({"period": period, "data": get_week_data()})
    
        if period == "month":
            return Response({"period": period, "data": get_month_data()})
    
        if period == "year":
            return Response({"period": period, "data": get_year_data()})
    
        return Response(
            {"error": "period باید یکی از today, week, month, year باشد یا start_date و end_date ارسال شود"},
            status=400
        )

    @action(detail=False, methods=['get'])
    def customers_by_region(self, request):
        regions = (
            Order.objects
            .filter(
                customer_city='تهران',
                customer_region__isnull=False
            )
            .exclude(customer_region='')
            .annotate(
                region_int=Cast('customer_region', IntegerField())
            )
            .values('customer_region', 'region_int')
            .annotate(
                customer_count=Count('customer_name', distinct=True),
                order_count=Count('id')
            )
            .order_by('region_int')
        )
    
        regions_list = [
            {
                'region': r['customer_region'],
                'customer_count': r['customer_count'],
                'order_count': r['order_count'],
            }
            for r in regions
        ]
    
        return Response({
            'total_customers': sum(r['customer_count'] for r in regions_list),
            'total_orders': sum(r['order_count'] for r in regions_list),
            'regions': regions_list
        })
