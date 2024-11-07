from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.views import View

class AuthLogoutView(View):
    def get(self, request, *args, **kwargs):
        # Log the user out
        logout(request)
        
        messages.success(request, "You have successfully logged out.")
        return redirect('/signin/')