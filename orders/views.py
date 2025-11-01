from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from django.contrib import messages
from products.models import Product, ProductSize
import json

@login_required(login_url='login')
def cart_view(request):
    """Hiển thị trang giỏ hàng"""
    return render(request, 'orders/cart.html')


@require_GET
def get_product_detail(request, product_id):
    """API trả về chi tiết sản phẩm (dùng cho cart)"""
    try:
        product = get_object_or_404(Product, id=product_id, hide=False)
        product_sizes = ProductSize.objects.filter(product=product).values('id', 'size__name')

        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image': product.image.url if product.image else '',
            'sizes': list(product_sizes),
            'formatted_price': product.formatted_price()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required(login_url='login')
def checkout_view(request):
    """Hiển thị form checkout"""
    if request.method == 'GET':
        return render(request, 'orders/checkout.html')

    # if request.method == 'POST':
    #     try:
    #         cart_data = json.loads(request.POST.get('cart_data', '[]'))
    #         receiver_name = request.POST.get('receiver_name')
    #         receiver_phone = request.POST.get('receiver_phone')
    #         receiver_address = request.POST.get('receiver_address')
    #
    #         # Validate dữ liệu
    #         if not cart_data or not all([receiver_name, receiver_phone, receiver_address]):
    #             messages.error(request, 'Vui lòng điền đầy đủ thông tin')
    #             return redirect('checkout')
    #
    #         # Tính tổng tiền và tạo order
    #         total_price = 0
    #         order = Order.objects.create(
    #             user=request.user,
    #             receiver_name=receiver_name,
    #             receiver_phone=receiver_phone,
    #             receiver_address=receiver_address,
    #             total_price=0  # Sẽ update sau
    #         )
    #
    #         # Tạo OrderItem cho mỗi item trong cart
    #         for item in cart_data:
    #             product_size = get_object_or_404(ProductSize, id=item['product_size_id'])
    #             quantity = int(item['quantity'])
    #             price = float(item['price'])
    #
    #             OrderItem.objects.create(
    #                 order=order,
    #                 product_size=product_size,
    #                 quantity=quantity,
    #                 price=price
    #             )
    #             total_price += price * quantity
    #
    #         # Update tổng tiền
    #         order.total_price = total_price
    #         order.save()
    #
    #         messages.success(request, 'Đặt hàng thành công! Đơn hàng của bạn đang được xử lý.')
    #         return redirect('order_detail', order_id=order.id)
    #
    #     except Exception as e:
    #         messages.error(request, f'Lỗi: {str(e)}')
    #         return redirect('checkout')


@login_required(login_url='login')
def my_orders_view(request):
    """Hiển thị danh sách đơn hàng của user"""
    # orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/my_orders.html')


@login_required(login_url='login')
def order_detail_view(request, order_id):
    """Hiển thị chi tiết đơn hàng"""
    # order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html')


@require_POST
def add_to_cart_api(request):
    """API thêm sản phẩm vào cart (server-side validation)"""
    try:
        data = json.loads(request.body)
        product_size_id = data.get('product_size_id')
        quantity = data.get('quantity', 1)

        product_size = get_object_or_404(ProductSize, id=product_size_id)
        product = product_size.product

        if product.hide:
            return JsonResponse({'error': 'Sản phẩm không khả dụng'}, status=400)

        return JsonResponse({
            'success': True,
            'product_id': product.id,
            'product_name': product.name,
            'price': product.price,
            'size_name': product_size.size.name,
            'formatted_price': product.formatted_price()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
