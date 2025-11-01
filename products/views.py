from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Size
from django.db.models import Q
from django.core.paginator import Paginator
def product_list(request):
    categories = Category.objects.filter(hide=False)
    query = request.GET.get('search')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query),
            hide=False
        ).distinct()
    else:
        products = Product.objects.filter(hide=False)
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    sizes = Size.objects.all()
    return render(request, 'home.html', {
        'categories': categories,
        'products': products,
        'search_query': query,
        "page_obj": page_obj,
        "sizes": sizes,
    })


def product_by_category(request, category_id):
    categories = Category.objects.filter(hide=False)
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category, hide=False)
    return render(request, 'home.html', {
        'categories': categories,
        'products': products,
        'active_category': category.id,
    })
