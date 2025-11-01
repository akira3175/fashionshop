from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from orders.models import Invoice, InvoiceItem
from products.models import ProductSize


def cart_page(request):
    return render(request, 'cart.html')


@require_http_methods(["POST"])
@login_required
def checkout(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')

    items = data.get('items')
    receiver = data.get('receiver')
    address = data.get('address')
    phone = data.get('phone')
    total = data.get('total')

    if not items or not receiver or not address or not phone:
        return HttpResponseBadRequest('Missing fields')

    invoice = Invoice.objects.create(
        user=request.user,
        receiver=receiver,
        address=address,
        phone=phone,
        total=total or 0.0,
    )

    for it in items:
        ps_id = it.get('product_size_id')
        qty = int(it.get('quantity') or 0)
        try:
            ps = ProductSize.objects.get(pk=ps_id)
        except ProductSize.DoesNotExist:
            ps = None
        InvoiceItem.objects.create(invoice=invoice, product_size=ps, quantity=qty)

    return JsonResponse({'status': 'ok', 'invoice_id': invoice.id})
