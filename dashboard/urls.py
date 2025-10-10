from django.urls import path
from .views import *

urlpatterns = [
    path('', management, name='management'),

    path("create-user/", create_user, name="create_user"),
    path('edit-user/<int:user_id>/', edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'),

    path("add_product/", add_product, name='add_product'),
    path('edit_product/<int:product_id>/', edit_product, name='edit_product'),
]
