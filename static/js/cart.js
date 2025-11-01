class CartManager {
    constructor() {
        this.storageKey = 'fashionshop_cart';
    }
    
    // Lấy giỏ hàng từ localStorage
    getCart() {
        try {
            const cart = localStorage.getItem(this.storageKey);
            return cart ? JSON.parse(cart) : [];
        } catch (e) {
            console.error('Error loading cart:', e);
            return [];
        }
    }
    
    // Lưu giỏ hàng vào localStorage
    saveCart(cart) {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(cart));
            this.updateCartCount();
            return true;
        } catch (e) {
            console.error('Error saving cart:', e);
            return false;
        }
    }
    
    // Thêm sản phẩm vào giỏ hàng
    addItem(item) {
        const cart = this.getCart();
        
        // Kiểm tra sản phẩm đã tồn tại với cùng size
        const existingItemIndex = cart.findIndex(i => 
            i.product_id === item.product_id && 
            i.size_id === item.size_id
        );
        
        if (existingItemIndex !== -1) {
            // Nếu đã có, tăng số lượng
            cart[existingItemIndex].quantity += item.quantity;
        } else {
            // Nếu chưa có, thêm mới
            cart.push({
                product_id: item.product_id,
                size_id: item.size_id,
                product_name: item.product_name,
                size_name: item.size_name,
                price: item.price,
                quantity: item.quantity,
                image: item.image || ''
            });
        }
        
        this.saveCart(cart);
        return true;
    }
    
    // Xóa sản phẩm khỏi giỏ hàng
    removeItem(productId, sizeId) {
        let cart = this.getCart();
        cart = cart.filter(item => 
            !(item.product_id === productId && item.size_id === sizeId)
        );
        this.saveCart(cart);
    }
    
    // Cập nhật số lượng sản phẩm
    updateQuantity(productId, sizeId, quantity) {
        const cart = this.getCart();
        const item = cart.find(i => 
            i.product_id === productId && 
            i.size_id === sizeId
        );
        
        if (item) {
            item.quantity = Math.max(1, parseInt(quantity));
            this.saveCart(cart);
        }
    }
    
    // Xóa toàn bộ giỏ hàng
    clearCart() {
        localStorage.removeItem(this.storageKey);
        this.updateCartCount();
    }
    
    // Tính tổng tiền
    getTotalPrice() {
        const cart = this.getCart();
        return cart.reduce((total, item) => 
            total + (item.price * item.quantity), 0
        );
    }
    
    // Lấy tổng số lượng sản phẩm
    getTotalItems() {
        const cart = this.getCart();
        return cart.reduce((total, item) => 
            total + parseInt(item.quantity), 0
        );
    }
    
    // Cập nhật số lượng hiển thị trên icon giỏ hàng
    updateCartCount() {
        const count = this.getTotalItems();
        const cartCountElements = document.querySelectorAll('.cart-quantity-text, .cart-count');
        
        cartCountElements.forEach(element => {
            element.textContent = count;
            const parentDiv = element.closest('.cart-quantity');
            if (parentDiv) {
                parentDiv.style.display = count > 0 ? 'flex' : 'none';
            }
        });
    }
    
    // Chuẩn bị data để gửi lên server
    prepareCheckoutData() {
        const cart = this.getCart();
        return cart.map(item => ({
            product_id: item.product_id,
            size_id: item.size_id,
            quantity: item.quantity
        }));
    }
}

// Khởi tạo CartManager global
const cartManager = new CartManager();

// Format giá tiền
function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN').format(price) + 'đ';
}

// Get CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Cập nhật cart count khi trang load
document.addEventListener('DOMContentLoaded', function() {
    cartManager.updateCartCount();
});


// ===========================
// FILE: static/js/script.js (Updated)
// ===========================

document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("productInfo");
    const closeModal = document.getElementById("closeModal");
    const productName = document.getElementById("productname");
    const productPrice = document.getElementById("productprice");
    const productImage = document.getElementById("imgbig");
    const quantityInput = document.querySelector(".quantity-input");
    const decreaseBtn = document.querySelector(".decrease");
    const increaseBtn = document.querySelector(".increase");

    let currentProductId = null;

    // Open modal when product clicked
    document.querySelectorAll(".product__item").forEach(item => {
        item.addEventListener("click", function() {
            const name = this.querySelector(".product__name").innerText;
            const price = this.querySelector(".product__price").innerText;
            const imgSrc = this.querySelector(".product__img").getAttribute("src");
            const id = this.getAttribute("id");

            currentProductId = id;
            productName.innerText = name;
            productPrice.innerText = price;
            productImage.src = imgSrc;

            // Reset quantity
            quantityInput.value = 1;

            modal.classList.remove("unactive");
            modal.classList.add("active");
            modal.setAttribute("data-id", id);
        });
    });

    // Close modal
    closeModal.addEventListener("click", function() {
        modal.classList.add("unactive");
        modal.classList.remove("active");
    });

    // Close modal when clicking outside
    modal.addEventListener("click", function(e) {
        if (e.target === modal) {
            modal.classList.add("unactive");
            modal.classList.remove("active");
        }
    });

    // Quantity controls
    decreaseBtn.addEventListener("click", function() {
        let value = parseInt(quantityInput.value) || 1;
        if (value > 1) {
            quantityInput.value = value - 1;
        }
    });

    increaseBtn.addEventListener("click", function() {
        let value = parseInt(quantityInput.value) || 1;
        quantityInput.value = value + 1;
    });

    // Validate quantity input
    quantityInput.addEventListener("input", function() {
        let value = parseInt(this.value);
        if (isNaN(value) || value < 1) {
            this.value = 1;
        }
    });
});

// Add to cart function
function addToCart() {
    const modal = document.getElementById("productInfo");
    const productId = modal.getAttribute("data-id");
    const productName = document.getElementById("productname").innerText;
    const priceText = document.getElementById("productprice").innerText;
    const sizeSelect = document.getElementById("size");
    const quantityInput = document.querySelector(".quantity-input");
    const productImage = document.getElementById("imgbig").src;

    // Lấy giá từ text (loại bỏ "Giá:" và "đ")
    const price = parseFloat(priceText.replace(/[^0-9]/g, ''));
    const quantity = parseInt(quantityInput.value) || 1;
    const sizeOption = sizeSelect.options[sizeSelect.selectedIndex];
    const sizeName = sizeOption.text;
    const sizeId = sizeOption.value;

    // Kiểm tra size có được chọn không
    if (!sizeId || sizeOption.disabled) {
        alert('Vui lòng chọn size!');
        return;
    }

    // Tạo object item
    const item = {
        product_id: parseInt(productId),
        size_id: sizeId,
        product_name: productName,
        size_name: sizeName,
        price: price,
        quantity: quantity,
        image: productImage
    };

    // Thêm vào giỏ hàng
    if (cartManager.addItem(item)) {
        alert('Đã thêm vào giỏ hàng!');
        
        // Đóng modal
        modal.classList.add("unactive");
        modal.classList.remove("active");
        
        // Reset quantity
        quantityInput.value = 1;
    } else {
        alert('Có lỗi khi thêm vào giỏ hàng!');
    }
}

// Check quantity function
function checkQuantity() {
    const quantityInput = document.querySelector(".quantity-input");
    let value = parseInt(quantityInput.value);
    if (isNaN(value) || value < 1) {
        quantityInput.value = 1;
    }
}


// ===========================
// CART PAGE RENDERING
// ===========================

function renderCartPage() {
    const cartItems = cartManager.getCart();
    const container = document.getElementById('cartItems');
    
    if (!container) return;
    
    if (cartItems.length === 0) {
        container.innerHTML = `
            <div class="cart-empty">
                <div class="cart-empty-icon">🛒</div>
                <p>Giỏ hàng của bạn trống</p>
            </div>
        `;
        updateCartSummary([]);
        return;
    }
    
    let html = '';
    cartItems.forEach(item => {
        const itemTotal = item.price * item.quantity;
        
        html += `
            <div class="cart-item">
                <div class="cart-item-image">
                    <img src="${item.image}" alt="${item.product_name}">
                </div>
                <div class="cart-item-info">
                    <h3>${item.product_name}</h3>
                    <p>Size: ${item.size_name}</p>
                    <p>Giá: ${formatPrice(item.price)}</p>
                </div>
                <div class="cart-item-actions">
                    <div class="cart-item-quantity">
                        <button onclick="changeCartQuantity(${item.product_id}, '${item.size_id}', -1)">−</button>
                        <input type="number" value="${item.quantity}" 
                               onchange="updateCartQuantity(${item.product_id}, '${item.size_id}', this.value)" 
                               min="1">
                        <button onclick="changeCartQuantity(${item.product_id}, '${item.size_id}', 1)">+</button>
                    </div>
                    <div class="cart-item-price">${formatPrice(itemTotal)}</div>
                    <button class="cart-item-delete" 
                            onclick="removeFromCart(${item.product_id}, '${item.size_id}')">×</button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    updateCartSummary(cartItems);
}

function changeCartQuantity(productId, sizeId, change) {
    const cart = cartManager.getCart();
    const item = cart.find(i => 
        i.product_id === productId && 
        i.size_id === sizeId
    );
    
    if (item) {
        const newQuantity = item.quantity + change;
        if (newQuantity >= 1) {
            cartManager.updateQuantity(productId, sizeId, newQuantity);
            renderCartPage();
        }
    }
}

function updateCartQuantity(productId, sizeId, quantity) {
    cartManager.updateQuantity(productId, sizeId, quantity);
    renderCartPage();
}

function removeFromCart(productId, sizeId) {
    if (confirm('Bạn có chắc muốn xóa sản phẩm này?')) {
        cartManager.removeItem(productId, sizeId);
        renderCartPage();
    }
}

function updateCartSummary(cartItems) {
    const subtotal = cartItems.reduce((sum, item) => 
        sum + (item.price * item.quantity), 0
    );
    
    const subtotalElement = document.getElementById('subtotal');
    const totalElement = document.getElementById('totalPrice');
    const checkoutBtn = document.getElementById('checkoutBtn');
    
    if (subtotalElement) subtotalElement.textContent = formatPrice(subtotal);
    if (totalElement) totalElement.textContent = formatPrice(subtotal);
    if (checkoutBtn) checkoutBtn.disabled = cartItems.length === 0;
}

function goToCheckout() {
    const cartItems = cartManager.getCart();
    if (cartItems.length === 0) {
        alert('Giỏ hàng của bạn trống');
        return;
    }
    
    // Redirect to checkout page
    window.location.href = '/orders/checkout/';
}

// Render cart nếu đang ở trang cart
if (document.getElementById('cartItems')) {
    document.addEventListener('DOMContentLoaded', renderCartPage);
}