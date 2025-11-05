from datetime import timezone
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
        now = timezone.now()

        # 1. Get year and month from query params, defaulting to current month/year
        try:
            year = int(request.GET.get('year', now.year))
            month = int(request.GET.get('month', now.month))
        except (ValueError, TypeError):
            # Handle invalid (non-integer) input
            year = now.year
            month = now.month

        # 2. Get the single Budget object using .get()
        #    This is safer because of your `unique_together` constraint
        try:
            # Assumes your Budget.month field is a DateField (e.g., 2023-11-01)
            budget = Budget.objects.get(user=user, month__year=year, month__month=month)
            budget_amount = budget.amount
            current_budget_amount = budget.current_amount
        except Budget.DoesNotExist:
            # No budget was found for this user/month
            budget_amount = None  # Or 0, depending on your desired default
            current_budget_amount = None # Or 0

        # 3. Filter Incomes and Expenses by *both* year and month
        incomes = Income.objects.filter(user=user, date__year=year, date__month=month)
        expenses = Expense.objects.filter(user=user, date__year=year, date__month=month)

        total_income = sum(income.amount for income in incomes)
        total_expense = sum(expense.amount for expense in expenses)
        balance = total_income - total_expense

        # 4. Add the new fields to your overview dictionary
        overview = {
            'total_income': total_income,
            'total_expense': total_expense,
            # NOTE: You are using BudgetSerializer. You probably mean to use
            # an IncomeSerializer and an ExpenseSerializer here.
            'incomes': BudgetSerializer(incomes, many=True).data,
            'expenses': BudgetSerializer(expenses, many=True).data,
            'balance': balance,
            'amount': budget_amount,             # Here is the budget amount
            'current_amount': current_budget_amount  # Here is the current amount
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

    