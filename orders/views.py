from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta
import json
from .models import Order, OrderItem
from products.models import Product, ProductSize, Size
from dashboard.check_admin import admin_required

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


@admin_required
@require_http_methods(["GET"])
def search_orders(request):
    """API tìm kiếm đơn hàng cho admin"""
    try:
        order_code = request.GET.get('order_id', '').strip()
        date_str = request.GET.get('date', '').strip()
        date_range = request.GET.get('date_range', '7')  # 7, 30, 365

        # Bắt đầu với tất cả orders
        orders = Order.objects.all()

        # Tìm theo mã đơn hàng
        if order_code:
            orders = orders.filter(id=order_code)

        # Tìm theo ngày cụ thể
        if date_str:
            try:
                search_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                orders = orders.filter(created_at__date=search_date)
            except ValueError:
                pass

        # Tìm theo khoảng thời gian
        elif date_range:
            days = int(date_range)
            start_date = datetime.now() - timedelta(days=days)
            orders = orders.filter(created_at__gte=start_date)

        # Prefetch related data
        orders = orders.prefetch_related(
            'items__product_size__product',
            'items__product_size__size',
            'user'
        ).order_by('-created_at')

        # Serialize data
        orders_data = []
        for order in orders:
            items_detail = []
            for item in order.items.all():
                items_detail.append({
                    'name': item.product_size.product.name,
                    'size': item.product_size.size.name,
                    'quantity': item.quantity,
                    'price': float(item.price)
                })

            orders_data.append({
                'id': order.id,
                'receiver': order.receiver,
                'phone': order.phone,
                'address': order.address,
                'total_amount': float(order.total_amount),
                'status': order.status,
                'status_display': order.get_status_display(),
                'created_at': order.created_at.strftime('%d/%m/%Y %H:%M'),
                'items': items_detail
            })

        return JsonResponse({
            'success': True,
            'orders': orders_data,
            'count': len(orders_data)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@admin_required
@require_http_methods(["GET"])
def order_statistics(request):
    """API thống kê đơn hàng cho admin"""
    try:
        date_range = int(request.GET.get('date_range', '7'))
        start_date = datetime.now() - timedelta(days=date_range)

        # Lấy orders trong khoảng thời gian
        orders = Order.objects.filter(created_at__gte=start_date)

        # Thống kê theo status
        stats = {
            'total_orders': orders.count(),
            'pending_orders': orders.filter(status='pending').count(),
            'confirmed_orders': orders.filter(status='confirmed').count(),
            'shipping_orders': orders.filter(status='shipping').count(),
            'completed_orders': orders.filter(status='completed').count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
        }

        # Tính tổng doanh thu (chỉ tính completed)
        total_revenue = orders.filter(status='completed').aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        stats['total_revenue'] = float(total_revenue)
        stats['date_range_days'] = date_range

        return JsonResponse({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@admin_required
@require_http_methods(["POST"])
def accept_order(request, order_id):
    """Chấp nhận đơn hàng - chuyển sang confirmed"""
    try:
        order = Order.objects.get(id=order_id)

        if order.status != 'pending':
            return JsonResponse({
                'success': False,
                'message': 'Chỉ có thể chấp nhận đơn hàng đang chờ xác nhận!'
            }, status=400)

        order.status = 'confirmed'
        order.save()

        return JsonResponse({
            'success': True,
            'message': 'Đã chấp nhận đơn hàng!',
            'order_id': order.id,
            'new_status': order.status,
            'status_display': order.get_status_display()
        })

    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy đơn hàng!'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@admin_required
@require_http_methods(["POST"])
def cancel_order(request, order_id):
    """Hủy đơn hàng"""
    try:
        data = json.loads(request.body)
        reason = data.get('reason', '').strip()

        if not reason:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng nhập lý do hủy đơn!'
            }, status=400)

        order = Order.objects.get(id=order_id)

        if order.status not in ['pending', 'confirmed']:
            return JsonResponse({
                'success': False,
                'message': 'Không thể hủy đơn hàng ở trạng thái này!'
            }, status=400)

        # Hoàn lại số lượng sản phẩm
        with transaction.atomic():
            for item in order.items.all():
                product_size = item.product_size
                product_size.quantity += item.quantity
                product_size.save()

            # Lưu lý do vào note
            if order.note:
                order.note += f"\n[HỦY ĐƠN] Lý do: {reason}"
            else:
                order.note = f"[HỦY ĐƠN] Lý do: {reason}"

            order.status = 'cancelled'
            order.save()

        return JsonResponse({
            'success': True,
            'message': 'Đã hủy đơn hàng!',
            'order_id': order.id,
            'new_status': order.status,
            'status_display': order.get_status_display()
        })

    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy đơn hàng!'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dữ liệu không hợp lệ!'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@admin_required
@require_http_methods(["POST"])
def update_order_status(request, order_id):
    """Cập nhật trạng thái đơn hàng (shipping, completed)"""
    try:
        data = json.loads(request.body)
        new_status = data.get('status')

        if new_status not in ['pending', 'confirmed', 'shipping', 'completed', 'cancelled']:
            return JsonResponse({
                'success': False,
                'message': 'Trạng thái không hợp lệ!'
            }, status=400)

        order = Order.objects.get(id=order_id)
        order.status = new_status
        order.save()

        return JsonResponse({
            'success': True,
            'message': 'Đã cập nhật trạng thái!',
            'order_id': order.id,
            'new_status': order.status,
            'status_display': order.get_status_display()
        })

    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy đơn hàng!'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)