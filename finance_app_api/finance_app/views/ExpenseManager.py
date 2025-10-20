from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..models import Expense, Budget
from ..serializers import ExpenseSerializer

class ExpenseManager(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user
        expenses = Expense.objects.filter(user=user)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def post(self, request):
        user = request.user
        data = request.data.copy()
        data['user'] = user.id
        serializer = ExpenseSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            budget = Budget.objects.filter(user=user, month=serializer.validated_data['date'].month).first()
            if budget:
                budget.current_amount += serializer.validated_data['amount']
                budget.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET'])
    def getById(request, expense_id):
        user = request.user
        try:
            expense = Expense.objects.get(id=expense_id, user=user)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, expense_id):
        user = request.user
        try:
            expense = Expense.objects.get(id=expense_id, user=user)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExpenseSerializer(expense, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, expense_id):
        user = request.user
        try:
            expense = Expense.objects.get(id=expense_id, user=user)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        
        expense.delete()
        return Response({"message": "Expense deleted successfully"}, status=status.HTTP_200_OK)