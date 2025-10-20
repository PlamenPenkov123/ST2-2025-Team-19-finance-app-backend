from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..models import Budget, Income, Expense
from ..serializers import BudgetSerializer

class BudgetManager(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def getBudgetOverview(self, request):
        user = request.user
        incomes = Income.objects.filter(user=user)
        expenses = Expense.objects.filter(user=user)

        total_income = sum(income.amount for income in incomes)
        total_expense = sum(expense.amount for expense in expenses)
        balance = total_income - total_expense

        overview = {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance
        }

        return Response(overview, status=status.HTTP_200_OK)
    
    @api_view(['POST'])
    def setBudgetGoal(request):
        user = request.user
        goal_amount = request.data.get('amount')
        month = request.data.get('month')
        
        if goal_amount is None:
            return Response({"error": "Goal amount is required"}, status=status.HTTP_400_BAD_REQUEST)
        if month is None:
            return Response({"error": "Month is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BudgetSerializer(data={
            'user': user.id,
            'amount': goal_amount,
            'current_amount': goal_amount,
            'month': month
        })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @api_view(['GET'])
    def getBudget(request):
        user = request.user
        month = request.query_params.get('month')
        
        if month is None:
            return Response({"error": "Month is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            budget = Budget.objects.get(user=user, month=month)
        except Budget.DoesNotExist:
            return Response({"error": "Budget not found for the specified month"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BudgetSerializer(budget)
        return Response(serializer.data, status=status.HTTP_200_OK)