from django.urls import path
from .views import SignupView, SearchUserView, FriendRequestView, ListFriendsView, PendingRequestsView, CustomTokenObtainPairView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('search/', SearchUserView.as_view(), name='search-user'),
    path('friend-request/', FriendRequestView.as_view(), name='friend-request'),
    path('friends/', ListFriendsView.as_view(), name='list-friends'),
    path('pending-requests/', PendingRequestsView.as_view(), name='pending-requests'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair')
]