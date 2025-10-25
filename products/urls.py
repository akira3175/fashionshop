from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='home'),           # /products/
    path('category/<int:category_id>/', views.product_by_category, name='product_by_category')
]

