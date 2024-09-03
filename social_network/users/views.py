from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import User, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer,CustomTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from datetime import datetime, timedelta
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import update_last_login
from django.contrib.auth import get_user_model

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = get_user_model().objects.get(email=request.data['email'])
        update_last_login(None, user)
        return response

class SearchUserView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return User.objects.filter(Q(email__iexact=query) | Q(username__icontains=query))[:10]

class FriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        receiver_id = request.data.get('receiver_id')
        if receiver_id:
            try:
                receiver = User.objects.get(id=receiver_id)
            except User.DoesNotExist:
                return Response({"error": "Receiver not found"}, status=status.HTTP_404_NOT_FOUND)

            sender = request.user

            # Prevent sending friend requests to oneself
            if sender.id == receiver.id:
                return Response({"error": "You cannot send a friend request to yourself"}, status=status.HTTP_400_BAD_REQUEST)

            # Rate limit check
            one_minute_ago = timezone.now() - timedelta(minutes=1)
            if FriendRequest.objects.filter(sender=sender, created_at__gte=one_minute_ago).count() >= 3:
                return Response({"error": "Rate limit exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # Check for existing request
            if not FriendRequest.objects.filter(sender=sender, receiver=receiver).exists():
                friend_request = FriendRequest(sender=sender, receiver=receiver)
                friend_request.save()
                return Response({"success": "Friend request sent"}, status=status.HTTP_201_CREATED)
            
            return Response({"error": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"error": "Receiver ID required"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        request_id = request.data.get('request_id')
        status_update = request.data.get('status')
        if request_id and status_update in ['accepted', 'rejected']:
            friend_request = FriendRequest.objects.get(id=request_id, receiver=request.user)
            friend_request.status = status_update
            friend_request.save()
            return Response({"success": f"Friend request {status_update}"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

class ListFriendsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            Q(sent_requests__receiver=self.request.user, sent_requests__status='accepted') |
            Q(received_requests__sender=self.request.user, received_requests__status='accepted')
        )

class PendingRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(receiver=self.request.user, status='pending')

