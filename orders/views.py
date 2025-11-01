from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from django.contrib import messages
from products.models import Product, ProductSize
import json
from orders.models import Invoice, InvoiceItem
from django.db import transaction
from django.views.decorators.http import require_http_methods

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

@login_required
@require_http_methods(["POST"])
def process_checkout(request):
    # """Xử lý đơn hàng từ frontend"""
    # try:
    #     # Parse JSON data từ request
    #     data = json.loads(request.body)
        
    #     # Lấy thông tin giao hàng
    #     receiver = data.get('receiver', '').strip()
    #     phone = data.get('phone', '').strip()
    #     address = data.get('address', '').strip()
    #     note = data.get('note', '').strip()
    #     items = data.get('items', [])
    #     total_amount = data.get('total_amount', 0)
        
    #     # Validate dữ liệu
    #     if not receiver or not phone or not address:
    #         return JsonResponse({
    #             'status': 'error',
    #             'message': 'Vui lòng điền đầy đủ thông tin!'
    #         }, status=400)
        
    #     if not items or len(items) == 0:
    #         return JsonResponse({
    #             'status': 'error',
    #             'message': 'Giỏ hàng trống!'
    #         }, status=400)
        
    #     # Tạo đơn hàng trong transaction
    #     with transaction.atomic():
    #         # Tạo Order
    #         invoice = Invoice.objects.create(
    #             user=request.user,
    #             receiver=receiver,
    #             phone=phone,
    #             address=address,
    #             note=note,
    #             total_amount=total_amount,
    #             status='pending'  # pending, confirmed, shipping, completed, cancelled
    #         )
            
    #         # Tạo OrderItems
    #         for item_data in items:
    #             product_id = item_data.get('product_id')
    #             size_id = item_data.get('size_id')
    #             quantity = item_data.get('quantity', 1)
                
    #             # Lấy product size
    #             try:
    #                 product_size = ProductSize.objects.get(
    #                     product_id=product_id,
    #                     size_id=size_id
    #                 )
    #             except ProductSize.DoesNotExist:
    #                 return JsonResponse({
    #                     'status': 'error',
    #                     'message': f'Sản phẩm không tồn tại!'
    #                 }, status=400)
                
    #             # Kiểm tra tồn kho
    #             if product_size.quantity < quantity:
    #                 return JsonResponse({
    #                     'status': 'error',
    #                     'message': f'Sản phẩm {product_size.product.name} (Size {product_size.size.name}) không đủ số lượng!'
    #                 }, status=400)
                
    #             # Tạo order item
    #             InvoiceItem.objects.create(
    #                 invoice=invoice,
    #                 product_size=product_size,
    #                 quantity=quantity,
    #                 price=product_size.product.price
    #             )
                
    #             # Trừ số lượng tồn kho
    #             product_size.quantity -= quantity
    #             product_size.save()
            
    #         return JsonResponse({
    #             'status': 'success',
    #             'message': 'Đặt hàng thành công!',
    #             'invoice_id': invoice.id
    #         })
            
    # except json.JSONDecodeError:
    #     return JsonResponse({
    #         'status': 'error',
    #         'message': 'Dữ liệu không hợp lệ!'
    #     }, status=400)
    # except Exception as e:
    #     return JsonResponse({
    #         'status': 'error',
    #         'message': f'Có lỗi xảy ra: {str(e)}'
    #     }, status=500)
    pass

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
