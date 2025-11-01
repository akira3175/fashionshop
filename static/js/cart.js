function getCart() {
  try {
    return JSON.parse(localStorage.getItem('cart') || '[]');
  } catch(e) { return []; }
}

function saveCart(cart) {
  localStorage.setItem('cart', JSON.stringify(cart));
}

function renderCart() {
  const container = document.getElementById('cart-container');
  const cart = getCart();
  if (!container) return;
  if (cart.length === 0) {
    container.innerHTML = '<p>Giỏ hàng trống</p>';
    document.getElementById('total-input').value = 0;
    return;
  }
  let html = '<ul>';
  let total = 0;
  cart.forEach(item => {
    html += `<li>${item.name} - Size: ${item.size_name} - Số lượng: <input type="number" min="1" value="${item.quantity}" data-psid="${item.product_size_id}" class="qty-input"></li>`;
    total += (item.price || 0) * (item.quantity || 0);
  });
  html += '</ul>';
  html += `<p>Tổng: ${total}</p>`;
  container.innerHTML = html;
  document.getElementById('total-input').value = total;

  document.querySelectorAll('.qty-input').forEach(inp => {
    inp.addEventListener('change', (e) => {
      const psid = e.target.dataset.psid;
      const qty = parseInt(e.target.value) || 1;
      const cart = getCart();
      const idx = cart.findIndex(c => String(c.product_size_id) === String(psid));
      if (idx >= 0) { cart[idx].quantity = qty; saveCart(cart); renderCart(); }
    });
  });
}

document.addEventListener('DOMContentLoaded', function() {
  renderCart();

  const form = document.getElementById('checkout-form');
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const cart = getCart();
      if (cart.length === 0) { alert('Giỏ hàng trống'); return; }
      const items = cart.map(c => ({ product_size_id: c.product_size_id, quantity: c.quantity }));
      const data = {
        items: items,
        receiver: form.receiver.value,
        address: form.address.value,
        phone: form.phone.value,
        total: parseFloat(document.getElementById('total-input').value) || 0
      };

      fetch('/cart/checkout/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
      }).then(r => r.json()).then(resp => {
        if (resp.status === 'ok') {
          localStorage.removeItem('cart');
          alert('Thanh toán thành công. Mã hóa đơn: ' + resp.invoice_id);
          window.location.href = '/';
        } else {
          alert('Lỗi khi tạo hóa đơn');
        }
      }).catch(err => { console.error(err); alert('Lỗi mạng'); });
    });
  }
});

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

document.addEventListener('DOMContentLoaded', function() {
  try {
    const cart = getCart();
    const q = cart.reduce((s, it) => s + (parseInt(it.quantity) || 0), 0);
    const els = document.getElementsByClassName('cart-quantity-text');
    for (let i=0;i<els.length;i++) els[i].textContent = q;
  } catch(e) { /* ignore */ }
});
