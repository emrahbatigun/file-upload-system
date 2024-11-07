from django.urls import path
from users.signin.views import AuthSigninView
from users.signup.views import AuthSignupView
from users.logout.views import AuthLogoutView

app_name = 'users'

urlpatterns = [
    path('signup/', AuthSignupView.as_view(template_name='pages/users/signup.html'), name='signup'),
    path('signin/', AuthSigninView.as_view(template_name='pages/users/signin.html'), name='signin'),
    path('logout/', AuthLogoutView.as_view(), name='logout')
]