document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("productInfo");
    const closeModal = document.getElementById("closeModal");
    const productName = document.getElementById("productname");
    const productPrice = document.getElementById("productprice");
    const productImage = document.getElementById("imgbig");
    const quantityInput = document.querySelector(".quantity-input");
    const decreaseBtn = document.querySelector(".decrease");
    const increaseBtn = document.querySelector(".increase");
    const sizesData = JSON.parse(document.getElementById("sizesData").textContent);

    let currentProductId = null;

    // Open modal when product clicked
    document.querySelectorAll(".product__item").forEach(item => {
        item.addEventListener("click", function () {

            const id = parseInt(this.getAttribute("id"));
            currentProductId = id;

            /* Gán thông tin sản phẩm như bạn đang làm */
            const name = this.querySelector(".product__name").innerText;
            const priceText = this.querySelector(".product__price").innerText;
            const imgSrc = this.querySelector(".product__img").getAttribute("src");

            productName.innerText = name;
            productPrice.innerText = priceText;
            productImage.src = imgSrc;

            quantityInput.value = 1;

            modal.classList.remove("unactive");
            modal.classList.add("active");
            modal.setAttribute("data-id", id);

            // ==== HIỂN THỊ SIZE THEO PRODUCT_ID ====
            const sizeSelect = document.getElementById("size");
            sizeSelect.innerHTML = ""; // clear list

            const product = sizesData.find(p => p.product_id === id);

            if (product && product.sizes.length > 0) {
                product.sizes.forEach(s => {
                    const option = document.createElement("option");
                    option.value = s.id;
                    option.innerText = s.name;
                    sizeSelect.appendChild(option);
                });
            } else {
                const opt = document.createElement("option");
                opt.disabled = true;
                opt.innerText = "No sizes available";
                sizeSelect.appendChild(opt);
            }
        });
    });


    // Close modal
    closeModal.addEventListener("click", function () {
        modal.classList.add("unactive");
        modal.classList.remove("active");
    });

    // Close modal when clicking outside
    modal.addEventListener("click", function (e) {
        if (e.target === modal) {
            modal.classList.add("unactive");
            modal.classList.remove("active");
        }
    });

    // Quantity controls
    if (decreaseBtn) {
        decreaseBtn.addEventListener("click", function () {
            let value = parseInt(quantityInput.value) || 1;
            if (value > 1) {
                quantityInput.value = value - 1;
            }
        });
    }

    if (increaseBtn) {
        increaseBtn.addEventListener("click", function () {
            let value = parseInt(quantityInput.value) || 1;
            quantityInput.value = value + 1;
        });
    }

    // Validate quantity input
    if (quantityInput) {
        quantityInput.addEventListener("input", function () {
            let value = parseInt(this.value);
            if (isNaN(value) || value < 1) {
                this.value = 1;
            }
        });
    }
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

    // Lấy giá từ text (loại bỏ "Giá:" và "đ", và dấu chấm phân cách)
    // Ví dụ: "Giá: 299.000đ" -> 299000
    let priceStr = priceText.replace(/[^0-9]/g, ''); // Chỉ lấy số
    const price = parseFloat(priceStr);

    const quantity = parseInt(quantityInput.value) || 1;
    const sizeOption = sizeSelect.options[sizeSelect.selectedIndex];
    const sizeName = sizeOption.text;
    const sizeId = sizeOption.value; // Có thể là ID hoặc name của size

    // Kiểm tra size có được chọn không
    if (!sizeId || sizeOption.disabled) {
        alert('Vui lòng chọn size!');
        return;
    }

    // Kiểm tra giá hợp lệ
    if (isNaN(price) || price <= 0) {
        alert('Giá sản phẩm không hợp lệ!');
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

    // Debug log
    console.log('Adding to cart:', item);

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
    if (quantityInput) {
        let value = parseInt(quantityInput.value);
        if (isNaN(value) || value < 1) {
            quantityInput.value = 1;
        }
    }
}