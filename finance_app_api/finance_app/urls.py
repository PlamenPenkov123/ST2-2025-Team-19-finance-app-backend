from django.urls import path
from .views.AuthManager import AuthManager
from .views.IncomeCategoryManager import IncomeCategoryManager
from .views.ExpenseCategoryManager import ExpenseCategoryManager
from .views.PaymentMethodManager import PaymentMethodManager
from .views.ExpenseManager import ExpenseManager
from .views.IncomeManager import IncomeManager

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

    path('incomes', IncomeManager.as_view(), name='get_incomes'),
    path('incomes/create', IncomeManager.as_view(), name='create_income'),
    path('incomes/<int:income_id>', IncomeManager.getById, name='get_income_by_id'),
    path('incomes/<int:income_id>/update', IncomeManager.as_view(), name='update_income'),
    path('incomes/<int:income_id>/delete', IncomeManager.as_view(), name='delete_income'),

    path('expenses', ExpenseManager.as_view(), name='get_expenses'),
    path('expenses/create', ExpenseManager.as_view(), name='create_expense'),
    path('expenses/<int:expense_id>/', ExpenseManager.getById, name='get_expense_by_id'),
    path('expenses/<int:expense_id>/update', ExpenseManager.as_view(), name='update_expense'),
    path('expenses/<int:expense_id>/delete', ExpenseManager.as_view(), name='delete_expense'),
]