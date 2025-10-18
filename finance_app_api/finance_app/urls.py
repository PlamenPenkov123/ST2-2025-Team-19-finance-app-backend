from django.urls import path

from . import views 

urlpatterns = [
    path('income-categories', views.IncomeCategoryManager.getIncomeTypes, name='get_income_types'),

    path('expense-categories', views.ExpenseCategoryManager.getExpenseTypes, name='get_expense_types'),

    path('payment-methods', views.PaymentMethodManager.getPaymentMethods, name='get_payment_methods'),

    path('register', views.AuthManager.registerUser, name='register'),
    path('login', views.AuthManager.loginUser, name='login'),
    path('logout', views.AuthManager.logoutUser, name='logout'),
    path('logout-all', views.AuthManager.logoutAllSessions, name='logout_all'),
    path('profile', views.AuthManager.getCurrentUser, name='profile'),
    path('profile/update', views.AuthManager.updateUser, name='update_profile'),

    path('incomes', views.IncomeManager.getIncomes, name='get_incomes'),
    path('incomes/create', views.IncomeManager.createIncome, name='create_income'),
    path('incomes/<int:income_id>', views.IncomeManager.getIncomeById, name='get_income_by_id'),
    path('incomes/<int:income_id>/update', views.IncomeManager.updateIncome, name='update_income'),
    path('incomes/<int:income_id>/delete', views.IncomeManager.deleteIncome, name='delete_income'),

    path('expenses', views.ExpenseManager.getExpenses, name='get_expenses'),
    path('expenses/create', views.ExpenseManager.createExpense, name='create_expense'),
    path('expenses/<int:expense_id>', views.ExpenseManager.getExpenseById, name='get_expense_by_id'),
    path('expenses/<int:expense_id>/update', views.ExpenseManager.updateExpense, name='update_expense'),
    path('expenses/<int:expense_id>/delete', views.ExpenseManager.deleteExpense, name='delete_expense'),
]