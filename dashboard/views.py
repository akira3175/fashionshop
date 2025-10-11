from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages
from django.core import serializers
from django.shortcuts import redirect, get_object_or_404

from dashboard.admin import ProductForm
from dashboard.check_admin import admin_required
from products.models import Product, Category, Size, ProductSize


# Create your views here.
@admin_required
def management(request):
    search_user = request.GET.get('search_user', '').strip()

    if search_user:
        users = User.objects.filter(username__icontains=search_user)
    else:
        users = User.objects.all()

    # --- Search cho Product ---
    search_product = request.GET.get('search_product', '').strip()

    if search_product:
        products = Product.objects.filter(name__icontains=search_product)
    else:
        products = Product.objects.all()

    context = {
        # User data
        'users': users,
        'search_user': search_user,

        # Product data
        'products': products,
        'search_product': search_product,
    }
    return render(request, 'management.html', context)

@admin_required
def create_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Kiểm tra dữ liệu
        if password != confirm_password:
            messages.error(request, "Mật khẩu xác nhận không khớp!")
            return redirect("management")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên người dùng đã tồn tại!")
            return redirect("management")

        # Tạo user mới
        user = User.objects.create_user(
            username=username,
            password=password,
        )
        user.is_staff = False
        user.is_superuser = False
        user.save()

        messages.success(request, "Tạo người dùng thành công!")
        return redirect("management")

    return render(request, "management.html")

@admin_required
def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not user.check_password(old_password):
            messages.error(request, "Mật khẩu cũ không chính xác!")
            return render(request, 'edit_user.html', {'user': user})

        if not new_password or not confirm_password:
            messages.error(request, "Vui lòng nhập đầy đủ mật khẩu mới và xác nhận!")
            return render(request, 'edit_user.html', {'user': user})

        if new_password != confirm_password:
            messages.error(request, "Mật khẩu xác nhận không khớp!")
            return render(request, 'edit_user.html', {'user': user})

        user.set_password(new_password)
        user.save()
        messages.success(request, f"Đã cập nhật mật khẩu cho người dùng '{user.username}' thành công!")

        return redirect('management')

    return render(request, 'edit_user.html', {'user': user})

@admin_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Không cho phép xóa tài khoản admin
    if user.is_superuser:
        messages.error(request, "Không thể xóa tài khoản admin!")
        return redirect('management')

    user.delete()
    messages.success(request, f"Đã xóa người dùng '{user.username}' thành công.")
    return redirect('management')

@admin_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        sizes = request.POST.getlist('sizes[]')  # Lấy danh sách size từ form JS

        if form.is_valid():
            product = form.save()

            # Thêm các size tương ứng
            for size_id in sizes:
                if size_id:
                    ProductSize.objects.create(product_id=product.id, size_id=size_id)

            messages.success(request, "Thêm sản phẩm thành công!")
            return redirect('management')
        else:
            messages.error(request, "Có lỗi xảy ra. Vui lòng kiểm tra lại form!")
    else:
        form = ProductForm()

    context = {
        'form': form,
        'sizes': Size.objects.all(),
    }
    return render(request, 'add_product.html', context)

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    sizes = Size.objects.all()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Lưu các field chính của product
            updated_product = form.save()

            # Lấy danh sách size được chọn từ form (name="sizes[]")
            selected_size_ids = [int(s) for s in request.POST.getlist('sizes[]') if s]

            # Thay thế toàn bộ quan hệ ProductSize bằng danh sách mới
            # (xóa các liên kết cũ rồi tạo mới)
            ProductSize.objects.filter(product=product).delete()
            if selected_size_ids:
                objs = [ProductSize(product=product, size_id=size_id) for size_id in selected_size_ids]
                ProductSize.objects.bulk_create(objs)

            messages.success(request, 'Cập nhật sản phẩm thành công!')
            return redirect('management')
        else:
            messages.error(request, 'Có lỗi khi cập nhật. Vui lòng kiểm tra lại form.')
    else:
        form = ProductForm(instance=product)

    # Lấy id của các size hiện có để hiển thị selected trong template
    product_size_ids = list(ProductSize.objects.filter(product=product).values_list('size_id', flat=True))

    context = {
        'form': form,
        'sizes': sizes,
        'product': product,
        'product_size_ids': product_size_ids,
    }
    return render(request, 'edit_product.html', context)
