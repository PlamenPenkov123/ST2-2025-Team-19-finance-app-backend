from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from knox.auth import TokenAuthentication
from ..models import Budget, Income, Expense
from ..serializers import BudgetSerializer

class BudgetManager(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user
        budget = Budget.objects.filter(user=user, month__year=request.GET.get('month', None))
        incomes = Income.objects.filter(user=user, date__month=request.GET.get('month', None))
        expenses = Expense.objects.filter(user=user, date__month=request.GET.get('month', None)
                                          )

        total_income = sum(income.amount for income in incomes)
        total_expense = sum(expense.amount for expense in expenses)
        balance = total_income - total_expense

        overview = {
            'total_income': total_income,
            'total_expense': total_expense,
            'incomes': BudgetSerializer(incomes, many=True).data,
            'expenses': BudgetSerializer(expenses, many=True).data,
            'balance': balance
        }

        return Response(overview, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        goal_amount = request.data.get('amount')
        month = request.data.get('month')
        
        if goal_amount is None:
            return Response({"error": "Goal amount is required"}, status=status.HTTP_400_BAD_REQUEST)
        if month is None:
            return Response({"error": "Month is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
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
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, budget_id):
        user = request.user
        try:
            with transaction.atomic():
                budget = Budget.objects.get(id=budget_id, user=user)
                goal_amount = request.data.get('amount')
                if goal_amount is None:
                    return Response({"error": "Goal amount is required"}, status=status.HTTP_400_BAD_REQUEST)

                old_amount = budget.amount
                budget.amount = goal_amount
                budget.current_amount += (goal_amount - old_amount)
                budget.save()

                serializer = BudgetSerializer(budget)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Budget.DoesNotExist:
            return Response({"error": "Budget not found"}, status=status.HTTP_404_NOT_FOUND)

        
    
    def delete(self, request, budget_id):
        user = request.user
        try:
            with transaction.atomic():
                budget = Budget.objects.get(id=budget_id, user=user)
                budget.delete()
                return Response({"message": "Budget deleted successfully"}, status=status.HTTP_200_OK)
        except Budget.DoesNotExist:
            return Response({"error": "Budget not found"}, status=status.HTTP_404_NOT_FOUND)

    