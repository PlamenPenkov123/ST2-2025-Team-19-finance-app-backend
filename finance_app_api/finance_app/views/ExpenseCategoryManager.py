from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import ExpenseCategory
from ..serializers import ExpenseCategorySerializer
from rest_framework.permissions import AllowAny

class ExpenseCategoryManager(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        expense_types = ExpenseCategory.objects.all()
        serializer = ExpenseCategorySerializer(expense_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)