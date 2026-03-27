from django.urls import path, include
from . import views

urlpatterns = [
    path('api/assistant/', views.assistant_api, name='assistant-api'),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('apps/', views.apps, name='apps'),
    path('contact/', views.contact, name='contact'),
    path('user-account/', views.account, name='user-account'),
    path('logout-confirm/', views.logout_confirm, name='logout-confirm'),
    path('orders/', views.orders, name='orders'),
    path('make-order/', views.make_order, name='make-order'),
    path('send-message/', views.make_message, name='send-message'),
    path('account/signup/', views.signup, name='signup'),  # Custom signup view
    path("account/login/", views.CustomLoginView.as_view(), name="login"),
    path('account/', include('django.contrib.auth.urls')),  # For login/logout/password reset
    path('reviews/', views.reviews, name='reviews'),
    path('make-review/', views.make_review, name='make-review'),
    path("logout-user/", views.logout_user, name="logout-user"),
]