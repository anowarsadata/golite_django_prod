from django.utils import timezone
from .models import Coupon


def validate_coupon(coupon: Coupon, user=None, amount=0):
    if coupon.limit is not None and coupon.used_count >= coupon.limit:
        return False, "Coupon usage limit reached"

    if coupon.is_use_once_per_customer and user:
        already_used = Coupon.objects.filter(
            id=coupon.id,
            user=user
        ).exists()

        if already_used:
            return False, "Coupon already used by this customer"

    if coupon.type == "percentage":
        discount_amount = (amount * coupon.discount) / 100
    else:
        discount_amount = coupon.discount

    return True, discount_amount
