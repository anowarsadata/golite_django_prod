import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from apps.coupons.models import Coupon, CouponUsage
from .services import validate_coupon


@csrf_exempt  # use proper auth later (JWT)
def apply_coupon(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST method required"},
            status=405
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    code = data.get("code")
    amount = float(data.get("amount", 0))
    order_id = data.get("order_id", "ORDER123")  # static fallback

    if not code:
        return JsonResponse(
            {"error": "Coupon code is required"},
            status=400
        )

    coupon = get_object_or_404(Coupon, slug=code, is_active=True)

    # prevent duplicate apply
    if CouponUsage.objects.filter(
        coupon=coupon,
        order_id=order_id
    ).exists():
        return JsonResponse(
            {"error": "Coupon already applied to this order"},
            status=400
        )

    valid, discount = validate_coupon(
        coupon=coupon,
        user=request.user if request.user.is_authenticated else None,
        amount=amount
    )

    if not valid:
        return JsonResponse({"error": discount}, status=400)

    # store usage
    CouponUsage.objects.create(
        coupon=coupon,
        user=request.user if request.user.is_authenticated else None,
        order_id=order_id
    )

    final_amount = max(amount - discount, 0)

    return JsonResponse({
        "success": True,
        "coupon": coupon.name,
        "discount": discount,
        "final_amount": final_amount,
        "order_id": order_id
    })
