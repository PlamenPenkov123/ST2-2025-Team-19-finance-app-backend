from django.contrib import admin

from finance_app.models import Budget, ExpenseCategory, Expense, Income, IncomeCategory, User, PaymentMethod

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)


@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
    model = IncomeCategory
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    ordering = ('name',)
@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    model = ExpenseCategory
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    ordering = ('name',)
@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    model = Income
    list_display = ('user', 'income_category', 'amount', 'source', 'date', 'created_at')
    search_fields = ('user__email', 'income_category__name', 'source')
    ordering = ('-date', '-created_at')
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    model = Expense
    list_display = ('user', 'expense_category', 'amount', 'payment_method', 'date', 'created_at')
    search_fields = ('user__email', 'expense_category__name', 'payment_method__name')
    ordering = ('-date', '-created_at')
@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    model = PaymentMethod
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    ordering = ('name',)
@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    model = Budget
    list_display = ('user', 'amount', 'month', 'created_at')
    search_fields = ('user__email', 'month')
    ordering = ('-month', '-created_at')

