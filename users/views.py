from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


def get_tokens_for_user(user):
    """Generate JWT access + refresh tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
    }


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Register a new Patient or Doctor.

    Patient example:
    {
        "full_name": "John Doe",
        "phone": "9812345678",
        "email": "john@example.com",       ← optional
        "password": "pass1234",
        "confirm_password": "pass1234",
        "role": "patient",
        "date_of_birth": "1995-05-15",     ← optional
        "gender": "male",                  ← optional
        "blood_group": "O+",               ← optional
        "address": "Kathmandu, Nepal"      ← optional
    }

    Doctor example:
    {
        "full_name": "Balen Shah",
        "phone": "9800000001",
        "password": "pass1234",
        "confirm_password": "pass1234",
        "role": "doctor",
        "specialization": "Cardiology",    ← required for doctor
        "license_number": "NMC-12345",     ← required for doctor
        "years_experience": 12,
        "available_days": "Mon, Wed, Fri"
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user   = serializer.save()
        tokens = get_tokens_for_user(user)

        return Response({
            'message': f'{user.role.capitalize()} registered successfully!',
            'user':    UserSerializer(user).data,
            'tokens':  tokens,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Login with phone + password. Works for both doctors and patients.

    {
        "phone": "9812345678",
        "password": "pass1234"
    }

    Response includes:
    - user info (with role so frontend knows where to redirect)
    - access token  (use this in headers for protected routes)
    - refresh token (use this to get a new access token)
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user   = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)

        return Response({
            'message': f'Welcome back, {user.full_name}!',
            'user':    UserSerializer(user).data,
            'tokens':  tokens,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Blacklists the refresh token so it can't be used again.

    {
        "refresh": "your_refresh_token_here"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """
    GET /api/auth/profile/
    Returns the logged-in user's full profile.
    Requires: Authorization: Bearer <access_token>
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)