from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import logout, get_user_model
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer
from .forms import UserRegistrationForm


class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        code_expired_message = None

        if user.referral_code and not user.is_referral_code_valid():
            user.referral_code = None
            user.referral_code_expiration = None
            user.save()
            code_expired_message = "Your referral code has expired."

        referral_code = user.referral_code if user.referral_code else ""

        return render(
            request,
            'accounts/home.html',
            {'referral_code': referral_code, 'code_expired_message': code_expired_message}
        )

    def post(self, request, *args, **kwargs):
        referral_code = request.data.get('referral_code')

        if referral_code and get_user_model().objects.filter(referral_code=referral_code).exists():
            return Response({'error': 'This referral code is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.referral_code = referral_code
        request.user.referral_code_expiration = timezone.now() + timedelta(minutes=1)
        request.user.save()

        return Response({'message': 'Referral code updated successfully'}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        request.user.referral_code = None
        request.user.referral_code_expiration = None
        request.user.save()

        return Response({'message': 'Referral code deleted successfully'}, status=status.HTTP_200_OK)


class RegistrationFormView(FormView):
    template_name = 'accounts/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])

        referral_code = form.cleaned_data.get('referral_code')

        if referral_code:
            referred_by_user = get_user_model().objects.filter(referral_code=referral_code).first()
            if referred_by_user:
                user.referred_by = referred_by_user
            else:
                form.add_error('referral_code', 'Invalid referral code.')
                return self.form_invalid(form)

        user.referral_code = None
        user.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)


class CustomTokenObtainPairView(TokenObtainPairView):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/login.html')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            access_token = serializer.validated_data['access']
            refresh_token = serializer.validated_data['refresh']
            response = redirect('accounts:home')

            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                secure=False,
                samesite='Lax'
            )

            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                secure=False,
                samesite='Lax'
            )

            return response

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        response = redirect('accounts:login')
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response


class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        email = request.GET.get('email')

        if user_id:
            try:
                user = get_user_model().objects.get(id=user_id)
            except get_user_model().DoesNotExist:
                return Response({'error': 'User not found'}, status=404)

            referred_users = get_user_model().objects.filter(referred_by=user)
            serializer = UserSerializer(referred_users, many=True)

            return Response({
                'message': f'Referrals of {user.username} | id: {user.pk}',
                'data': serializer.data
            }, status=200)

        if email:
            users = get_user_model().objects.filter(email=email)
            if users.exists():
                serializer = UserSerializer(users, many=True)

                return Response(serializer.data, status=200)
            else:
                return Response({'error': 'User not found'}, status=404)
        else:
            users = get_user_model().objects.all()
            serializer = UserSerializer(users, many=True)

            return Response(serializer.data, status=200)
