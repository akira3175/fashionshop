from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # User URLs
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    # Admin URLs
    path('api/search/', views.search_orders, name='search_orders'),
    path('api/statistics/', views.order_statistics, name='order_statistics'),
    path('api/<int:order_id>/accept/', views.accept_order, name='accept_order'),
    path('api/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('api/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
]
