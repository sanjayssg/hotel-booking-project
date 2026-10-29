from django.urls import path

from api import views

urlpatterns = [
    path('owners/', views.OwnerList.as_view()),
    path('owners/<str:owner_id>/properties/', views.OwnerProperties.as_view()),
    path('properties/search/', views.PropertySearch.as_view()),
    path('properties/<str:property_id>/', views.PropertyDetail.as_view()),
    path('bookings/', views.BookingList.as_view()),
    path('bookings/<str:booking_id>/', views.BookingDetail.as_view()),
    path('bookings/<str:booking_id>/cancel/', views.BookingCancel.as_view()),
    path('bookings/<str:booking_id>/pay/', views.BookingPay.as_view()),
]