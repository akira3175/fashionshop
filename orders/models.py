from django.db import models
from django.contrib.auth.models import User
from products.models import ProductSize

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao hàng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    receiver = models.CharField(max_length=200, verbose_name='Người nhận')
    phone = models.CharField(max_length=20, verbose_name='Số điện thoại')
    address = models.TextField(verbose_name='Địa chỉ')
    note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')
    total_amount = models.FloatField(verbose_name='Tổng tiền')  # FloatField để match với Product.price
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Trạng thái')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
    def formatted_total(self):
        """Format tổng tiền"""
        return f"{self.total_amount:,.0f}đ".replace(",", ".")
    
    def get_status_display_color(self):
        """Màu sắc cho status"""
        colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'shipping': 'purple',
            'completed': 'green',
            'cancelled': 'red',
        }
        return colors.get(self.status, 'gray')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_size = models.ForeignKey(ProductSize, on_delete=models.PROTECT)  # PROTECT để giữ lịch sử
    quantity = models.IntegerField(verbose_name='Số lượng')
    price = models.FloatField(verbose_name='Giá')  # FloatField để match với Product.price
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'
    
    def __str__(self):
        return f"{self.product_size.product.name} {self.product_size.size.name} x {self.quantity}"
    
    def get_total(self):
        """Tính thành tiền"""
        return self.price * self.quantity
    
    def formatted_total(self):
        """Format thành tiền"""
        return f"{self.get_total():,.0f}đ".replace(",", ".")