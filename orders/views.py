from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json
from .models import Order, OrderItem
from products.models import Product, ProductSize, Size

@login_required
def cart_view(request):
    """Hiển thị trang giỏ hàng"""
    # Lấy danh sách sizes để hiển thị trong modal (nếu cần)
    sizes = Size.objects.all()
    return render(request, 'orders/cart.html', {'sizes': sizes})


@login_required
def checkout_view(request):
    """Hiển thị trang thanh toán"""
    return render(request, 'orders/checkout.html')


@login_required
@require_http_methods(["POST"])
def process_checkout(request):
    """Xử lý đơn hàng từ frontend"""
    try:
        # Parse JSON data từ request
        data = json.loads(request.body)
        
        # Lấy thông tin giao hàng
        receiver = data.get('receiver', '').strip()
        phone = data.get('phone', '').strip()
        address = data.get('address', '').strip()
        note = data.get('note', '').strip()
        items = data.get('items', [])
        total_amount = float(data.get('total_amount', 0))
        
        # Validate dữ liệu
        if not receiver or not phone or not address:
            return JsonResponse({
                'status': 'error',
                'message': 'Vui lòng điền đầy đủ thông tin!'
            }, status=400)
        
        if not items or len(items) == 0:
            return JsonResponse({
                'status': 'error',
                'message': 'Giỏ hàng trống!'
            }, status=400)
        
        # Tạo đơn hàng trong transaction
        with transaction.atomic():
            # Tạo Order
            order = Order.objects.create(
                user=request.user,
                receiver=receiver,
                phone=phone,
                address=address,
                note=note,
                total_amount=total_amount,
                status='pending'
            )
            
            # Tạo OrderItems
            for item_data in items:
                product_id = int(item_data.get('product_id'))
                size_id = item_data.get('size_id')  # Có thể là string hoặc int
                quantity = int(item_data.get('quantity', 1))
                
                # Tìm ProductSize
                try:
                    # Thử tìm theo product_id và size_id
                    if isinstance(size_id, int):
                        product_size = ProductSize.objects.get(
                            product_id=product_id,
                            size_id=size_id
                        )
                    else:
                        # Nếu size_id là name (string)
                        product_size = ProductSize.objects.get(
                            product_id=product_id,
                            size__name=size_id
                        )
                except ProductSize.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Sản phẩm không tồn tại hoặc không có size này!'
                    }, status=400)
                
                # Kiểm tra tồn kho
                if product_size.quantity < quantity:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Sản phẩm {product_size.product.name} (Size {product_size.size.name}) không đủ số lượng! Còn {product_size.quantity} sản phẩm.'
                    }, status=400)
                
                # Tạo order item
                OrderItem.objects.create(
                    order=order,
                    product_size=product_size,
                    quantity=quantity,
                    price=float(product_size.product.price)  # Lấy giá từ product
                )
                
                # Trừ số lượng tồn kho
                product_size.quantity -= quantity
                product_size.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Đặt hàng thành công!',
                'order_id': order.id
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Dữ liệu không hợp lệ!'
        }, status=400)
    except ValueError as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Dữ liệu không đúng định dạng: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Có lỗi xảy ra: {str(e)}'
        }, status=500)


@login_required
def my_orders(request):
    """Hiển thị danh sách đơn hàng của user"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product_size__product', 'items__product_size__size').order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Hiển thị chi tiết đơn hàng"""
    try:
        order = Order.objects.prefetch_related('items__product_size__product', 'items__product_size__size').get(id=order_id, user=request.user)
        return render(request, 'orders/order_detail.html', {
            'order': order,
            'order_items': order.items.all()
        })
    except Order.DoesNotExist:
        return redirect('orders:my_orders')