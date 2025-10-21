from django.urls import path
from .views.AuthManager import AuthManager
from .views.IncomeCategoryManager import IncomeCategoryManager
from .views.ExpenseCategoryManager import ExpenseCategoryManager
from .views.PaymentMethodManager import PaymentMethodManager
from .views.ExpenseManager import ExpenseManager
from .views.IncomeManager import IncomeManager
from .views.BudgetManager import BudgetManager

urlpatterns = [
    path('income-categories', IncomeCategoryManager.as_view(), name='get_income_types'),

    path('expense-categories', ExpenseCategoryManager.as_view(), name='get_expense_types'),

    path('payment-methods', PaymentMethodManager.as_view(), name='get_payment_methods'),

    path('register', AuthManager.registerUser, name='register'),
    path('login', AuthManager.loginUser, name='login'),
    path('logout', AuthManager.logoutUser, name='logout'),
    path('logout-all', AuthManager.logoutAllSessions, name='logout_all'),
    path('profile', AuthManager.getCurrentUser, name='profile'),
    path('profile/update', AuthManager.updateUser, name='update_profile'),

    path('budgets', BudgetManager.as_view(), name='get_budgets'),

    path('incomes', IncomeManager.as_view(), name='get_incomes'),
    path('incomes/<int:income_id>', IncomeManager.getById, name='get_income_by_id'),

    path('expenses', ExpenseManager.as_view(), name='get_expenses'),
    path('expenses/<int:expense_id>/', ExpenseManager.getById, name='get_expense_by_id'),
]