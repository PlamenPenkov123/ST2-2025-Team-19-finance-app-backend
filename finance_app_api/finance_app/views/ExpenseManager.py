from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from knox.auth import TokenAuthentication
from ..models import Expense, Budget
from ..serializers import ExpenseSerializer


class ExpenseManager(APIView):
    # Set the permission and authentication classes for the entire view
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    # Get all expenses for the authenticated user
    def get(self, request):
        user = request.user
        expenses = Expense.objects.filter(user=user)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Get a single expense by it's id
    def get(self, request, expenes_id=None):
        user = request.user
        if expenes_id:
            try:
                expense = Expense.objects.get(id=expenes_id, user=user)
                serializer = ExpenseSerializer(expense)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Expense.DoesNotExist:
                return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            expenses = Expense.objects.filter(user=user)
            serializer = ExpenseSerializer(expenses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    # Create an expense
    def post(self, request):
        user = request.user
        data = request.data.copy()
        data['user'] = user.id
        
        try:
            with transaction.atomic():
                serializer = ExpenseSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    budget = Budget.objects.filter(user=user, month__month=serializer.validated_data['date'].month, month__year=serializer.validated_data['date'].year).first()
                    if budget:
                        budget.current_amount -= serializer.validated_data['amount']
                        budget.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"error": "No budget set for this month"}, status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        
    # Patch an expense
    def patch(self, request, expense_id):
        user = request.user
        data = request.data.copy()
        data['user'] = user.id

        try:
            with transaction.atomic():
                expense = Expense.objects.get(id=expense_id, user=user)

                old_amount = expense.amount
                old_date = expense.date

                serializer = ExpenseSerializer(expense, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    expense.refresh_from_db()  # ✅ refresh updated data

                    new_amount = expense.amount
                    new_date = expense.date

                    # Handle the case where the date/month changed
                    old_budget = Budget.objects.filter(
                        user=user,
                        month__month=old_date.month,
                        month__year=old_date.year
                    ).first()
                    new_budget = Budget.objects.filter(
                        user=user,
                        month__month=new_date.month,
                        month__year=new_date.year
                    ).first()

                    # If the expense moved to another month, adjust both budgets
                    if old_budget and old_budget != new_budget:
                        old_budget.current_amount += old_amount  # ✅ refund the old expense
                        old_budget.save()

                    if new_budget:
                        # ✅ subtract the new expense amount from the current month’s budget
                        if old_budget != new_budget:
                            new_budget.current_amount -= new_amount
                        else:
                            new_budget.current_amount -= (new_amount - old_amount)
                        new_budget.save()

                    return Response(serializer.data, status=status.HTTP_200_OK)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        
    # Delete an expense
    def delete(self, request, expense_id):
        user = request.user
        try:
            with transaction.atomic():
                expense = Expense.objects.get(id=expense_id, user=user)
                budget = Budget.objects.filter(user=user, month__month=expense.date.month, month__year=expense.date.year).first()
                if budget:
                    budget.current_amount += expense.amount
                    budget.save()
                    expense.delete()
                    return Response({"message": "Expense deleted successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "No budget set for this month"}, status=status.HTTP_400_BAD_REQUEST)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)