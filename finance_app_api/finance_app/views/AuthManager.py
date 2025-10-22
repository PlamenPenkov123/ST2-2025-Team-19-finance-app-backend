from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from django.db import transaction
from ..serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer


class AuthManager():
    # Register an user
    @api_view(['POST'])
    @permission_classes([AllowAny])
    def registerUser(request):
        if request.method == 'POST':
            serializer = UserRegistrationSerializer(data=request.data)
            try:
                with transaction.atomic():
                    if serializer.is_valid():
                        user = serializer.save()
                        token, _ = AuthToken.objects.create(user=user)
                        reponseDate = {
                            'message': 'User registered successfully',
                            'user': UserSerializer(user).data,
                            'token': token
                        }
                        return Response(reponseDate, status=status.HTTP_201_CREATED)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    # Login an user
    @api_view(['POST'])
    @permission_classes([AllowAny])
    def loginUser(request):
        serializer = UserLoginSerializer(data=request.data)
        
        try:
            with transaction.atomic():
                if serializer.is_valid():
                    user = serializer.validated_data['user']
                    _, token = AuthToken.objects.create(user)
                    reponseData = {
                        'message': 'User logged in successfully',
                        'user': UserSerializer(user).data,
                        'token': token
                    }
                    return Response(reponseData, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    # Get current user
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def getCurrentUser(request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Logout an user from current device
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def logoutUser(request):
        try:
            with transaction.atomic():
                request._auth.delete()  # Delete the token to log out the user
                return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    # Logout an user from all devices
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def logoutAllSessions(request):
        try:
            with transaction.atomic():
                request.user.auth_token_set.all().delete()  # Delete all tokens for the user
                return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    # Update an user
    @api_view(['PATCH'])
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def updateUser(request):
        user = request.user
        try:
            with transaction.atomic():
                serializer = UserSerializer(user, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
