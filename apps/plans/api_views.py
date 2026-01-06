from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Plan
from .serializers import PlanSerializer


class PlanListAPI(APIView):
    def get(self, request):
        sim_type = request.GET.get('sim_type')

        plans = Plan.objects.filter(is_active=True)

        if sim_type:
            plans = plans.filter(sim_type=sim_type)

        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)


class PlanDetailAPI(APIView):
    def get(self, request, slug):
        plan = get_object_or_404(
            Plan,
            slug=slug,
            is_active=True
        )

        serializer = PlanSerializer(plan)
        return Response(serializer.data, status=status.HTTP_200_OK)
