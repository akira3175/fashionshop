from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    
    # APIs
    path('api/product/<int:product_id>/', views.get_product_detail, name='api_product_detail'),
    path('api/add-to-cart/', views.add_to_cart_api, name='api_add_to_cart'),
]
