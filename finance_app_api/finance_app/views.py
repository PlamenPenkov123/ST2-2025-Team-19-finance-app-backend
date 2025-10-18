from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes, authentication_classes
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from knox.models import AuthToken
from .models import Budget, Expense, ExpenseCategory, Income, IncomeCategory, PaymentMethod, User
from .serializers import BudgetSerializer, ExpenseCategorySerializer, ExpenseSerializer, IncomeCategorySerializer, IncomeSerializer, PaymentMethodSerializer, PaymentMethodSerializer, UserLoginSerializer, UserRegistrationSerializer, UserSerializer

# Create your views here.

class AuthManager:
    @staticmethod
    @api_view(['GET'])
    def getUsers(request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    @api_view(['GET'])
    def getUserById(request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    @permission_classes([AllowAny])
    def registerUser(request):
        if request.method == 'POST':
            serializer = UserRegistrationSerializer(data=request.data)

            if serializer.is_valid():
                try:
                    user = serializer.save()
                    print(type(user))
                    token, _ = AuthToken.objects.create(user=user)
                    reponseDate = {
                        'message': 'User registered successfully',
                        'user': UserSerializer(user).data,
                        'token': token
                    }
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

                return Response(reponseDate, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    @api_view(['POST'])
    @permission_classes([AllowAny])
    def loginUser(request):
        if request.method == 'POST':
            serializer = UserLoginSerializer(data=request.data)

            if serializer.is_valid():
                user = serializer.validated_data['user']
                _, token = AuthToken.objects.create(user)
                reponseDate = {
                    'message': 'User logged in successfully',
                    'user': UserSerializer(user).data,
                    'token': token
                }
                return Response(reponseDate, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def logoutUser(request):
        if request.method == 'POST':
            request._auth.delete()  # Delete the token to log out the user
            return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def logoutAllSessions(request):
        if request.method == 'POST':
            request.user.auth_token_set.all().delete()  # Delete all tokens for the user
            return Response({"message": "User logged out from all sessions successfully"}, status=status.HTTP_200_OK)

    @staticmethod
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def getCurrentUser(request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    @api_view(['PUT'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def updateUser(request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PaymentMethodManager:
    @staticmethod
    @api_view(['GET'])
    def getPaymentMethods(request):
        payment_methods = PaymentMethod.objects.all()
        serializer = PaymentMethodSerializer(payment_methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class IncomeCategoryManager:
    @staticmethod
    @api_view(['GET'])
    def getIncomeTypes(request):
        income_types = IncomeCategory.objects.all()
        serializer = IncomeCategorySerializer(income_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ExpenseCategoryManager:
    @staticmethod
    @api_view(['GET'])
    def getExpenseTypes(request):
        expense_types = ExpenseCategory.objects.all()
        serializer = ExpenseCategorySerializer(expense_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class BudgetManager:
    @staticmethod
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def getBudgetOverview(request):
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
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
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
    
    @staticmethod
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
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


class IncomeManager:
    @staticmethod
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def getIncomes(request):
        user = request.user
        incomes = Income.objects.filter(user=user)
        serializer = IncomeSerializer(incomes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def createIncome(request):
        user = request.user
        data = request.data.copy()
        data['user'] = user.id
        serializer = IncomeSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            budget = Budget.objects.filter(user=user, month=serializer.validated_data['date'].month).first()
            if budget:
                budget.current_amount += serializer.validated_data['amount']
                budget.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def getIncomeById(request, income_id):
        user = request.user
        try:
            income = Income.objects.get(id=income_id, user=user)
        except Income.DoesNotExist:
            return Response({"error": "Income not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = IncomeSerializer(income)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @staticmethod
    @api_view(['PATCH'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def updateIncome(request, income_id):
        user = request.user
        try:
            income = Income.objects.get(id=income_id, user=user)
        except Income.DoesNotExist:
            return Response({"error": "Income not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = IncomeSerializer(income, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @staticmethod
    @api_view(['DELETE'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def deleteIncome(request, income_id):
        user = request.user
        try:
            income = Income.objects.get(id=income_id, user=user)
        except Income.DoesNotExist:
            return Response({"error": "Income not found"}, status=status.HTTP_404_NOT_FOUND)
        
        income.delete()
        return Response({"message": "Income deleted successfully"}, status=status.HTTP_200_OK)
    
class ExpenseManager:
    @staticmethod
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def getExpenses(request):
        user = request.user
        expenses = Expense.objects.filter(user=user)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def createExpense(request):
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
    
    @staticmethod
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def getExpenseById(request, expense_id):
        user = request.user
        try:
            expense = Expense.objects.get(id=expense_id, user=user)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @staticmethod
    @api_view(['PATCH'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def updateExpense(request, expense_id):
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
    
    @staticmethod
    @api_view(['DELETE'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def deleteExpense(request, expense_id):
        user = request.user
        try:
            expense = Expense.objects.get(id=expense_id, user=user)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        
        expense.delete()
        return Response({"message": "Expense deleted successfully"}, status=status.HTTP_200_OK)