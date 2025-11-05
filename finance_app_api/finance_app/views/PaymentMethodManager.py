from rest_framework.views import APIView    
from rest_framework.response import Response
from rest_framework import status
from ..models import PaymentMethod
from ..serializers import PaymentMethodSerializer
from rest_framework.permissions import AllowAny

class PaymentMethodManager(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        payment_methods = PaymentMethod.objects.all()
        serializer = PaymentMethodSerializer(payment_methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
