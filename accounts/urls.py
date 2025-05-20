from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('create/', BanquetBookingCreateView.as_view(), name='create-booking'),
    path('update/<int:pk>/', BanquetBookingUpdateView.as_view(), name='booking-update'),
    path('delete/<int:pk>/', BanquetBookingDeleteView.as_view(), name='booking-delete'),
    path('bookings/<int:booking_id>/send-code/', SendConfirmationCodeView.as_view(), name='send-confirmation-code'),
    path('bookings/<int:booking_id>/confirm/', ConfirmBookingView.as_view(), name='confirm-booking'),   
    path('bookings/', BanquetBookingListView.as_view(), name='booking-list'),
    path('cafes/', CafeListView.as_view(), name='cafes-list'),
    path('cafes/<int:pk>/', CafeDetailView.as_view(), name='cafe-detail'),
    path('user/', get_current_user, name='current-user'),
    path('users/', user_list, name='user-list'),
    path('users/create/', create_user, name='create-user'),
    path('users/<int:user_id>/', delete_user, name='delete-user'),
    path('users/<int:user_id>/update/', update_user, name='update-user'),
]
