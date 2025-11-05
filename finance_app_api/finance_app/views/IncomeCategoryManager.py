from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import IncomeCategory
from ..serializers import IncomeCategorySerializer
from rest_framework.permissions import AllowAny

class IncomeCategoryManager(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        income_types = IncomeCategory.objects.all()
        serializer = IncomeCategorySerializer(income_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)