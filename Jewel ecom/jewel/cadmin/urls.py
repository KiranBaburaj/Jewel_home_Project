from django.urls import path
from . import views
from django.conf import settings
from django.urls import path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from product.models import Category

from .views import block_user, unblock_user

urlpatterns = [

    path(r'^media/', serve, {'document_root': settings.MEDIA_ROOT}),

    path('superuser_login/', views.superuser_login, name='superuser_login'),

    path('custom_admin/', views.custom_admin_homepage, name='custom_admin_homepage'),
  path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),

  path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('user_list/', views.user_list, name='user_list'),
     path('create_user/', views.create_user, name='create_user'),
        path('adlogout/', views.adlogout_view, name='adlogout'),
        path('search_users/', views.search_users, name='search_users'),
         path('product_list/', views.products_list, name='products_list'),
      path('user/block/<int:user_id>/', block_user, name='block_user'),
    path('user/unblock/<int:user_id>/', unblock_user, name='unblock_user'),
         path('create_product/', views.create_product, name='create_product'),
         path('category/<int:category_pk>/detail', views.category_detailad, name='category_detailad'),
         path('create_category/', views.create_category, name='create_category'),
          path('gold_rate_list/', views.gold_rate_list, name='gold_rate_list'),
         path('create_gold_rate/', views.create_gold_rate, name='create_gold_rate'),
         path('viewcategory/', views.viewcategory, name='viewcategory'),
         path('product/<int:product_pk>/detailad/', views.product_detailad, name='product_detailad'),
    path('product/<int:pk>/edit/', views.product_edit, name='product_edit'),
  
 path('product/<int:product_pk>/soft-delete/', views.soft_delete_product, name='soft_delete_product'),
    path('category/<int:category_pk>/edit/', views.edit_category, name='edit_category'),
    path('category/<int:category_pk>/soft-delete/', views.soft_delete_category, name='soft_delete_category'),
     path('product/<int:product_pk>/delete/', views.product_delete, name='product_delete'),

      path('banners/', views.banner_list, name='banner_list'),
    path('banners/<int:pk>/', views.banner_detail, name='banner_detail'),
    path('banners/create/', views.banner_create, name='banner_create'),
    path('banners/<int:pk>/edit/', views.banner_edit, name='banner_edit'),
    path('banners/<int:pk>/delete/', views.banner_delete, name='banner_delete'),


     path('order/list/', views.admin_order_list, name='admin_order_list'),
    path('order/detail/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('order/change-status/<int:order_id>/', views.admin_change_order_status, name='admin_change_order_status'),
    path('order/cancel/<int:order_id>/', views.admin_cancel_order, name='admin_cancel_order'),
        path('order/ship/<int:order_id>/', views.admin_ship_order, name='admin_ship_order'),
            path('order/deliver/<int:order_id>/', views.admin_deliver_order, name='admin_deliver_order'),

  path('sales/', views.sales_report, name='sales_report'),
    path('sales/daily/', views.sales_report, {'period': 'daily'}, name='daily_sales_report'),
    path('sales/weekly/', views.sales_report, {'period': 'weekly'}, name='weekly_sales_report'),
    path('sales/monthly/', views.sales_report, {'period': 'monthly'}, name='monthly_sales_report'),
    path('sales/yearly/', views.sales_report, {'period': 'yearly'}, name='yearly_sales_report'),
    path('sales/custom/', views.sales_report, {'period': 'custom'}, name='custom_sales_report'),
path('sales-report/pdf/<str:period>/<str:start_date>/<str:end_date>/', views.download_sales_report_pdf, name='download_sales_report_pdf'),


       path('sales-report/pdf/<str:period>/', views.download_sales_report_pdf, name='download_sales_report_pdf'),
    # ... other URL patterns

      path('sales-report/excel/<str:period>/', views.sales_report_excel, name='sales_report_excel'),

    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

