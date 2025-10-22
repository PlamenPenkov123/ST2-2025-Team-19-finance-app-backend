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
    @api_view(['GET'])
    def getById(request, expense_id):
        user = request.user
        try:
            expense = Expense.objects.get(id=expense_id, user=user)    
            serializer = ExpenseSerializer(expense)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        
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
                    budget = Budget.objects.filter(user=user, month=serializer.validated_data['date'].month).first()
                    if budget:
                        budget.current_amount += serializer.validated_data['amount']
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
        try:
            with transaction.atomic():
                expense = Expense.objects.get(id=expense_id, user=user)
                serializer = ExpenseSerializer(expense, data=request.data, partial=True)
                if serializer.is_valid():
                    budget = Budget.objects.filter(user=user, month=serializer.validated_data['date'].month).first()
                    if budget:
                        old_amount = expense.amount
                        new_amount = serializer.validated_data.get('amount', old_amount)
                        budget.current_amount += (new_amount - old_amount)
                        budget.save()
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response({"error": "No budget set for this month"}, status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        
    # Delete an expense
    def delete(self, request, expense_id):
        user = request.user
        try:
            with transaction.atomic():
                expense = Expense.objects.get(id=expense_id, user=user)
                budget = Budget.objects.filter(user=user, expense=expense).first()
                if budget:
                    budget.current_amount += expense.amount
                    budget.save()
                    expense.delete()
                    return Response({"message": "Expense deleted successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "No budget set for this month"}, status=status.HTTP_400_BAD_REQUEST)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)