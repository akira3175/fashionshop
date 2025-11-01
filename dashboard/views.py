from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages
from django.core import serializers
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from dashboard.admin import ProductForm
from dashboard.check_admin import admin_required
from products.models import Product, Category, Size, ProductSize


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

        if password != confirm_password:
            messages.error(request, "Mật khẩu xác nhận không khớp!")
            return redirect("management")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên người dùng đã tồn tại!")
            return redirect("management")

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
        sizes = request.POST.getlist('sizes[]')  # Lấy danh sách size
        quantities = request.POST.getlist('quantities[]')  # Lấy danh sách quantity

        if form.is_valid():
            product = form.save()

            # Thêm các size với quantity tương ứng
            for i, size_id in enumerate(sizes):
                if size_id:
                    quantity = int(quantities[i]) if i < len(quantities) and quantities[i] else 0
                    ProductSize.objects.create(
                        product_id=product.id, 
                        size_id=size_id,
                        quantity=quantity
                    )

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


@admin_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    sizes = Size.objects.all()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Lưu các field chính của product
            updated_product = form.save()

            # Lấy danh sách size và quantity được chọn từ form
            selected_size_ids = [int(s) for s in request.POST.getlist('sizes[]') if s]
            quantities = request.POST.getlist('quantities[]')

            # Xóa tất cả ProductSize cũ
            ProductSize.objects.filter(product=product).delete()
            
            # Tạo ProductSize mới với quantity
            if selected_size_ids:
                objs = []
                for i, size_id in enumerate(selected_size_ids):
                    quantity = int(quantities[i]) if i < len(quantities) and quantities[i] else 0
                    objs.append(ProductSize(
                        product=product, 
                        size_id=size_id,
                        quantity=quantity
                    ))
                ProductSize.objects.bulk_create(objs)

            messages.success(request, 'Cập nhật sản phẩm thành công!')
            return redirect('management')
        else:
            messages.error(request, 'Có lỗi khi cập nhật. Vui lòng kiểm tra lại form.')
    else:
        form = ProductForm(instance=product)

    # Lấy ProductSize hiện có với quantity
    product_sizes = ProductSize.objects.filter(product=product).select_related('size')

    context = {
        'form': form,
        'sizes': sizes,
        'product': product,
        'product_sizes': product_sizes,  # Đổi từ product_size_ids
    }
    return render(request, 'edit_product.html', context)


def login_view(request):
    """Function-based view để xử lý login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Chào mừng {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    
    return render(request, 'login.html')


def signup_view(request):
    """Function-based view để xử lý đăng ký"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Mật khẩu không trùng khớp.')
            return render(request, 'signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
            return render(request, 'signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được sử dụng.')
            return render(request, 'signup.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, 'Đăng ký thành công!')
        return redirect('home')
    
    return render(request, 'signup.html')


def logout_view(request):
    """Function-based view để xử lý logout"""
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công.')
    return redirect('home')