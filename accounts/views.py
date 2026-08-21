

# Create your views here.
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer

# 1. REGISTER VIEW
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Automatically generate JWT tokens upon successful registration
        refresh = RefreshToken.for_user(user)
        
        headers = self.get_success_headers(serializer.data)

        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            }, 
        status=status.HTTP_201_CREATED,
        headers=headers
        )



# 2. LOGIN VIEW
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens for the authenticated user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Login successful.",
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)


# 3. PROFILE VIEW (Handles both GET profile and PUT/PATCH updates)
class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated] 
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logged out successfully."},
                status=status.HTTP_200_OK,
            )

        except Exception:
            return Response(
                {"error": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )