# core/views.py
from django.shortcuts import render
from products.models import Product, Category
from django.core.paginator import Paginator
def home(request):
    categories = Category.objects.filter(hide=False)
    products = Product.objects.filter(hide=False)
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "home.html", {
        "categories": categories,
        "products": products,
        "page_obj": page_obj,
    })

