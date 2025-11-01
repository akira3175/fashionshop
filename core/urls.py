from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
   path('', views.home, name='home'),
   # path('checkout/', views.checkout, name='checkout'),
   # path('product-info/<int:product_size_id>/', views.get_product_info, name='get_product_info'),
]
