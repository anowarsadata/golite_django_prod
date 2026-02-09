import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.coupons.models import Coupon, CouponUsage
from apps.plans.models import Plan
from .services import validate_coupon


# 🔹 1. PREVIEW COUPON (Checkout Page)
@csrf_exempt
def preview_coupon(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)

    code = data.get("code")
    amount = data.get("amount")
    plan_id = data.get("plan_id")

    coupon = get_object_or_404(Coupon, slug=code, status=Coupon.ACTIVE)

    plan = None
    if plan_id:
        plan = get_object_or_404(Plan, id=plan_id)

    valid, result = validate_coupon(
        coupon=coupon,
        user=request.user if request.user.is_authenticated else None,
        amount=amount,
        plan=plan
    )

    if not valid:
        return JsonResponse({"error": result}, status=400)

    discount = float(result)
    final_amount = max(float(amount) - discount, 0)

    return JsonResponse({
        "success": True,
        "coupon": coupon.name,
        "discount": discount,
        "final_amount": final_amount
    })


# 🔹 2. APPLY COUPON (Order Confirm)
@csrf_exempt
def apply_coupon(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)

    code = data.get("code")
    amount = data.get("amount")
    order_id = data.get("order_id")
    plan_id = data.get("plan_id")

    coupon = get_object_or_404(Coupon, slug=code, status=Coupon.ACTIVE)

    if CouponUsage.objects.filter(coupon=coupon, order_id=order_id).exists():
        return JsonResponse({"error": "Coupon already applied"}, status=400)

    plan = None
    if plan_id:
        plan = get_object_or_404(Plan, id=plan_id)

    valid, result = validate_coupon(
        coupon=coupon,
        user=request.user if request.user.is_authenticated else None,
        amount=amount,
        plan=plan
    )

    if not valid:
        return JsonResponse({"error": result}, status=400)

    discount = float(result)
    final_amount = max(float(amount) - discount, 0)

    with transaction.atomic():
        CouponUsage.objects.create(
            coupon=coupon,
            user=request.user if request.user.is_authenticated else None,
            order_id=order_id
        )
        coupon.used_count += 1
        coupon.save(update_fields=["used_count"])

    return JsonResponse({
        "success": True,
        "coupon": coupon.name,
        "discount": discount,
        "final_amount": final_amount
    })
