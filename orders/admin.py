from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline để hiển thị OrderItem trong Order admin"""
    model = OrderItem
    extra = 0
    readonly_fields = ('product_info', 'size_name', 'quantity', 'price', 'item_total')
    fields = ('product_info', 'size_name', 'quantity', 'price', 'item_total')
    can_delete = False
    
    def product_info(self, obj):
        """Hiển thị thông tin sản phẩm"""
        if obj.product_size:
            return f"{obj.product_size.product.name}"
        return "-"
    product_info.short_description = "Sản phẩm"
    
    def size_name(self, obj):
        """Hiển thị size"""
        if obj.product_size:
            return obj.product_size.size.name
        return "-"
    size_name.short_description = "Size"
    
    def item_total(self, obj):
        """Hiển thị tổng tiền của item"""
        return format_html(
            '<strong style="color: #00a65a;">{:,.0f}đ</strong>',
            obj.get_total()
        )
    item_total.short_description = "Thành tiền"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin cho Order model"""
    list_display = (
        'order_id',
        'user_info',
        'receiver',
        'phone',
        'total_display',
        'status_display',
        'created_at_display',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'receiver', 'phone', 'address')
    readonly_fields = (
        'user',
        'created_at',
        'updated_at',
        'total_display',
        'order_items_count'
    )
    fieldsets = (
        ('Thông tin đơn hàng', {
            'fields': (
                'user',
                'status',
                'total_display',
                'order_items_count',
                'created_at',
                'updated_at',
            )
        }),
        ('Thông tin giao hàng', {
            'fields': (
                'receiver',
                'phone',
                'address',
                'note',
            )
        }),
    )
    inlines = [OrderItemInline]
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    def order_id(self, obj):
        """Hiển thị mã đơn hàng"""
        return f"#{obj.id}"
    order_id.short_description = "Mã đơn"
    order_id.admin_order_field = 'id'
    
    def user_info(self, obj):
        """Hiển thị thông tin user"""
        return format_html(
            '<strong>{}</strong><br/><small style="color: #666;">{}</small>',
            obj.user.username,
            obj.user.email if obj.user.email else 'Chưa có email'
        )
    user_info.short_description = "Khách hàng"
    user_info.admin_order_field = 'user__username'
    
    def total_display(self, obj):
        """Hiển thị tổng tiền với format đẹp"""
        return format_html(
            '<strong style="color: #00a65a; font-size: 14px;">{:,.0f}đ</strong>',
            obj.total_amount
        )
    total_display.short_description = "Tổng tiền"
    total_display.admin_order_field = 'total_amount'
    
    def status_display(self, obj):
        """Hiển thị trạng thái với màu sắc"""
        colors = {
            'pending': '#f39c12',      # Vàng cam
            'confirmed': '#3498db',     # Xanh dương
            'shipping': '#9b59b6',      # Tím
            'completed': '#27ae60',     # Xanh lá
            'cancelled': '#e74c3c',     # Đỏ
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold; display: inline-block;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = "Trạng thái"
    status_display.admin_order_field = 'status'
    
    def created_at_display(self, obj):
        """Hiển thị ngày tạo"""
        return obj.created_at.strftime("%d/%m/%Y %H:%M")
    created_at_display.short_description = "Ngày đặt"
    created_at_display.admin_order_field = 'created_at'
    
    def order_items_count(self, obj):
        """Đếm số lượng sản phẩm trong đơn"""
        count = obj.items.count()
        total_qty = sum(item.quantity for item in obj.items.all())
        return format_html(
            '<span style="color: #3498db; font-weight: bold;">{} sản phẩm ({} items)</span>',
            count,
            total_qty
        )
    order_items_count.short_description = "Số lượng sản phẩm"
    
    def has_add_permission(self, request):
        """Không cho phép tạo order từ admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Chỉ cho phép xóa order ở trạng thái pending hoặc cancelled"""
        if obj and obj.status in ['pending', 'cancelled']:
            return True
        return False
    
    # Custom actions
    actions = ['mark_as_confirmed', 'mark_as_shipping', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_confirmed(self, request, queryset):
        """Action: Xác nhận đơn hàng"""
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f"Đã xác nhận {updated} đơn hàng.")
    mark_as_confirmed.short_description = "✅ Xác nhận đơn hàng"
    
    def mark_as_shipping(self, request, queryset):
        """Action: Chuyển sang đang giao"""
        updated = queryset.filter(status='confirmed').update(status='shipping')
        self.message_user(request, f"Đã chuyển {updated} đơn sang trạng thái đang giao.")
    mark_as_shipping.short_description = "🚚 Đang giao hàng"
    
    def mark_as_completed(self, request, queryset):
        """Action: Hoàn thành đơn hàng"""
        updated = queryset.filter(status='shipping').update(status='completed')
        self.message_user(request, f"Đã hoàn thành {updated} đơn hàng.")
    mark_as_completed.short_description = "✔️ Hoàn thành"
    
    def mark_as_cancelled(self, request, queryset):
        """Action: Hủy đơn hàng"""
        # Chỉ hủy những đơn chưa shipping
        updated = queryset.exclude(status__in=['shipping', 'completed']).update(status='cancelled')
        self.message_user(request, f"Đã hủy {updated} đơn hàng.")
    mark_as_cancelled.short_description = "❌ Hủy đơn hàng"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin cho OrderItem model (optional - có thể không cần)"""
    list_display = (
        'order_id',
        'product_name',
        'size_name',
        'quantity',
        'price_display',
        'total_display',
    )
    list_filter = ('order__status', 'order__created_at')
    search_fields = (
        'order__id',
        'product_size__product__name',
    )
    readonly_fields = ('order', 'product_size', 'quantity', 'price', 'total_display')
    
    def order_id(self, obj):
        """Link đến order"""
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">#{}</a>', url, obj.order.id)
    order_id.short_description = "Mã đơn"
    order_id.admin_order_field = 'order__id'
    
    def product_name(self, obj):
        """Tên sản phẩm"""
        return obj.product_size.product.name
    product_name.short_description = "Sản phẩm"
    product_name.admin_order_field = 'product_size__product__name'
    
    def size_name(self, obj):
        """Size"""
        return obj.product_size.size.name
    size_name.short_description = "Size"
    
    def price_display(self, obj):
        """Giá"""
        return format_html('{:,.0f}đ', obj.price)
    price_display.short_description = "Giá"
    price_display.admin_order_field = 'price'
    
    def total_display(self, obj):
        """Thành tiền"""
        return format_html(
            '<strong style="color: #00a65a;">{:,.0f}đ</strong>',
            obj.get_total()
        )
    total_display.short_description = "Thành tiền"
    
    def has_add_permission(self, request):
        """Không cho phép thêm OrderItem từ admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Không cho phép xóa OrderItem từ admin"""
        return False