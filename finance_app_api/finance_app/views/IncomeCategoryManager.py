from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import IncomeCategory
from ..serializers import IncomeCategorySerializer

class IncomeCategoryManager(APIView):
    def get(self):
        income_types = IncomeCategory.objects.all()
        serializer = IncomeCategorySerializer(income_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)