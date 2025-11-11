from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from knox.auth import TokenAuthentication
from ..models import Income, Budget
from ..serializers import IncomeSerializer


class IncomeManager(APIView):
    # Set the permission and authentication classes for the entire view
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    # Get single or multiple incomes
    def get(self, request, income_id=None):
        user = request.user
        if income_id:
            try:
                income = Income.objects.get(id=income_id, user=user)
                serializer = IncomeSerializer(income)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Income.DoesNotExist:
                return Response({"error": "Income not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            incomes = Income.objects.filter(user=user)
            serializer = IncomeSerializer(incomes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    # Create an income
    def post(self, request):
        user = request.user
        data = request.data.copy()
        data['user'] = user.id
        try:
            with transaction.atomic():
                serializer = IncomeSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    budget = Budget.objects.filter(user=user, month__month=serializer.validated_data['date'].month, month__year=serializer.validated_data['date'].year).first()
                    if budget:
                        budget.current_amount += serializer.validated_data['amount']
                        budget.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Income.DoesNotExist:
            return Response({"error": "Income not found"}, status=status.HTTP_404_NOT_FOUND)
        
    # Patch an income
    def patch(self, request, income_id):
        user = request.user
        data = request.data.copy()
        data['user'] = user.id
        try:
            with transaction.atomic():
                income = Income.objects.get(id=income_id, user=user)

                old_amount = income.amount
                old_date = income.date

                serializer = IncomeSerializer(income, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    income.refresh_from_db()  # ✅ refresh updated data

                    new_amount = income.amount
                    new_date = income.date

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

                    # If the income was in a different month before
                    if old_budget and old_budget != new_budget:
                        old_budget.current_amount -= old_amount
                        old_budget.save()

                    if new_budget:
                        # Adjust new budget with new amount
                        new_budget.current_amount += (new_amount if old_budget != new_budget else (new_amount - old_amount))
                        new_budget.save()

                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Income.DoesNotExist:
            return Response({"error": "Income not found"}, status=status.HTTP_404_NOT_FOUND)
        
    # Delete an income
    def delete(self, request, income_id):
        user = request.user
        try:
            with transaction.atomic():
                income = Income.objects.get(id=income_id, user=user)
                budget = Budget.objects.filter(user=user, month__month=income.date.month, month__year=income.date.year).first()
                if budget:
                    budget.current_amount -= income.amount
                    budget.save()
                    income.delete()
                    return Response({"message": "Income deleted successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "No budget set for this month"}, status=status.HTTP_400_BAD_REQUEST)
        except Income.DoesNotExist:
            return Response({"error": "Income not found"}, status=status.HTTP_404_NOT_FOUND)
    