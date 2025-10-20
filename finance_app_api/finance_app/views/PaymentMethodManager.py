from rest_framework.views import APIView    
from rest_framework.response import Response
from rest_framework import status
from ..models import PaymentMethod
from ..serializers import PaymentMethodSerializer

class PaymentMethodManager(APIView):
    def get(self):
        payment_methods = PaymentMethod.objects.all()
        serializer = PaymentMethodSerializer(payment_methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
