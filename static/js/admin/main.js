const $ = document.querySelector.bind(document);
const $$ = document.querySelectorAll.bind(document);
const itemManager = $$(".item__manager");

itemManager.forEach((item) => {
  item.addEventListener("click", () => {
    itemManager.forEach((item) => {
      item.classList.remove("item__manager__active");
    });
    item.classList.add("item__manager__active");
  });
});

function hideAllTables() {
  const allTables = $$(".table__wrap");
  allTables.forEach((table) => {
    table.classList.add("unactive");
  });
}

function toggleElenment(element, className) {
  const testClass = element.classList.contains("unactive");
  if (testClass) {
    hideAllTables();
    element.classList.remove("unactive");
    element.classList.add(className);
  } else {
    element.classList.add("unactive");
    element.classList.remove(className);
  }
}

const managerUser = $(".managerUser");
const managerProduct = $(".managerProduct");
const managerOrder = $(".managerOrder");

const tableUser = $(".table__user");
const tableProduct = $(".table__Product");
const tableOrder = $(".table__order");

managerUser.addEventListener("click", () =>
  toggleElenment(tableUser, "active")
);
managerProduct.addEventListener("click", () =>
  toggleElenment(tableProduct, "active")
);
managerOrder.addEventListener("click", () =>
  toggleElenment(tableOrder, "active")
);

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

const csrftoken = getCookie('csrftoken');

function searchOrder() {
    const orderId = document.getElementById('id-order').value.trim();
    const dateOrder = document.getElementById('date-order').value;
    const dateRange = document.getElementById('date-around').value;

    const params = new URLSearchParams();
    if (orderId) params.append('order_id', orderId);
    if (dateOrder) params.append('date', dateOrder);
    if (dateRange) params.append('date_range', dateRange);

    fetch(`/orders/api/search/?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateOrdersTable(data.orders);
                if (data.orders.length === 0) {
                    alert('Không tìm thấy đơn hàng phù hợp!');
                }
            } else {
                alert('Lỗi: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Lỗi tra cứu:', error);
            alert('Có lỗi xảy ra khi tra cứu đơn hàng!');
        });
}

function statis() {
    const dateRange = document.getElementById('date-around').value;

    fetch(`/orders/api/statistics/?date_range=${dateRange}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayStatistics(data.stats);
            } else {
                alert('Không thể tải thống kê: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Lỗi thống kê:', error);
            alert('Có lỗi xảy ra khi tải thống kê!');
        });
}

function updateStatis() {
}

function displayStatistics(stats) {
    const modal = document.querySelector('.statistics');
    const nameProduct = modal.querySelector('.name-product');

    nameProduct.innerHTML = `
        <div class="name-product-left">
            <p><strong>Tổng đơn hàng:</strong> ${stats.total_orders}</p>
            <p><strong>Chờ xác nhận:</strong> ${stats.pending_orders}</p>
            <p><strong>Đã xác nhận:</strong> ${stats.confirmed_orders}</p>
            <p><strong>Đang giao:</strong> ${stats.shipping_orders}</p>
            <p><strong>Hoàn thành:</strong> ${stats.completed_orders}</p>
            <p><strong>Đã hủy:</strong> ${stats.cancelled_orders}</p>
        </div>
        <div class="name-product-right">
            <div class="total-statis">
                Doanh thu ${stats.date_range_days} ngày qua:
                <span class="total-statis-price">${formatCurrency(stats.total_revenue)}</span>
            </div>
        </div>
    `;

    modal.style.display = 'block';
}

function cancelStatis() {
    const modal = document.querySelector('.statistics');
    modal.style.display = 'none';
}

function acceptOrder(orderId) {
    if (!confirm('Bạn có chắc chắn muốn chấp nhận đơn hàng này?')) {
        return;
    }

    fetch(`/orders/api/${orderId}/accept/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert('Lỗi: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Lỗi chấp nhận đơn hàng:', error);
            alert('Có lỗi xảy ra khi chấp nhận đơn hàng!');
        });
}

function cancelOrder(orderId) {
    const reason = prompt('Vui lòng nhập lý do hủy đơn hàng:');

    if (!reason || reason.trim() === '') {
        alert('Bạn phải nhập lý do để hủy đơn hàng!');
        return;
    }

    if (!confirm('Bạn có chắc chắn muốn hủy đơn hàng này?')) {
        return;
    }

    fetch(`/orders/api/${orderId}/cancel/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ reason: reason })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert('Lỗi: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Lỗi hủy đơn hàng:', error);
            alert('Có lỗi xảy ra khi hủy đơn hàng!');
        });
}

function updateOrdersTable(orders) {
    const tbody = document.querySelector('.listOrders');
    tbody.innerHTML = '';

    if (orders.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align:center;">
                    Không có đơn hàng nào.
                </td>
            </tr>
        `;
        return;
    }

    orders.forEach(order => {
        const row = document.createElement('tr');

        const itemsHtml = order.items.map(item =>
            `<p>${item.name} ${item.size} x ${item.quantity}</p>`
        ).join('');

        let actionsHtml = '';
        if (order.status === 'pending') {
            actionsHtml = `
                <button class="btn-accept" onclick="acceptOrder(${order.id})">Accept</button>
                <button class="btn-interrupt" onclick="cancelOrder(${order.id})">Cancel</button>
            `;
        } else if (order.status === 'confirmed') {
            actionsHtml = `
                <button class="btn-interrupt" onclick="cancelOrder(${order.id})">Cancel</button>
            `;
        }

        row.innerHTML = `
            <td>${order.id}</td>
            <td>${order.receiver}</td>
            <td>${itemsHtml}</td>
            <td>${formatCurrency(order.total_amount)}</td>
            <td>${order.created_at}</td>
            <td>${order.address}</td>
            <td>
                <span class="accepted-label">${order.status_display}</span>
            </td>
            <td>${actionsHtml}</td>
        `;

        tbody.appendChild(row);
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount) + ' đ';
}

document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.querySelector('.search-order button:first-of-type');
    if (searchBtn && !searchBtn.hasAttribute('onclick')) {
        searchBtn.addEventListener('click', searchOrder);
    }

    const statsBtn = document.querySelector('.search-order button:last-of-type');
    if (statsBtn && !statsBtn.hasAttribute('onclick')) {
        statsBtn.addEventListener('click', function() {
            statis();
            updateStatis();
        });
    }

    const orderTab = document.querySelector('.managerOrder');
    if (orderTab) {
        orderTab.addEventListener('click', function() {
        });
    }
});



