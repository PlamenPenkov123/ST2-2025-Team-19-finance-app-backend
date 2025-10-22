from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.contrib.auth.models import AbstractUser, BaseUserManager


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    current_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    month = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ['user', 'month']
        ordering = ['-month']

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Payment Methods"
    
    def __str__(self):
        return self.name

class IncomeCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Income Categories"
    
class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Expense Categories"
    
class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    income_category = models.ForeignKey(IncomeCategory, null=True, on_delete=models.CASCADE, related_name='incomes')
    budget = models.ForeignKey(Budget, null=True, on_delete=models.CASCADE, related_name='incomes')
    amount = models.FloatField(
        default=0.00,
        validators=[MinValueValidator(0.00)]
    )
    description = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=200)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
    
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    expense_category = models.ForeignKey(ExpenseCategory, null=True, on_delete=models.CASCADE, related_name='expenses')
    budget = models.ForeignKey(Budget, null=True, on_delete=models.CASCADE, related_name='expenses')
    amount = models.FloatField(
        default=0.00,
        validators=[MinValueValidator(0.00)]
    )
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
    



    