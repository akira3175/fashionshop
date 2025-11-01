from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]
