from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    hide = models.BooleanField(default=False)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'sizes'
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=255)
    price = models.FloatField()  # Hoặc DecimalField nếu muốn chính xác hơn
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    hide = models.BooleanField(default=False)

    class Meta:
        db_table = 'products'
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'

    def __str__(self):
        return self.name

    def formatted_price(self):
        """Format giá tiền kiểu Việt Nam"""
        return f"{self.price:,.0f}đ".replace(",", ".")


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.ForeignKey(Size, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0, verbose_name='Số lượng tồn kho')  # THÊM FIELD NÀY

    class Meta:
        unique_together = ('product', 'size')
        db_table = 'product_sizes'
        verbose_name = 'Size sản phẩm'
        verbose_name_plural = 'Size sản phẩm'

    def __str__(self):
        return f"{self.product.name} - {self.size.name} (SL: {self.quantity})"
