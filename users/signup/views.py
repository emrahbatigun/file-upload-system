# views.py
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
from file_upload_system.__init__ import Layout
from file_upload_system.layout_config import LayoutConfig

class AuthSignupView(TemplateView):
    template_name = 'pages/users/signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = Layout.init(context)
        LayoutConfig.addJavascriptFile('js/users/sign-up/general.js')
        context.update({
            'layout': LayoutConfig.setLayout('auth.html', context),
        })
        return context

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        
        if not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, self.template_name, self.get_context_data())

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, self.template_name, self.get_context_data())

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, self.template_name, self.get_context_data())

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return render(request, self.template_name, self.get_context_data())

        user = User.objects.create_user(username=email, email=email, password=password)
        messages.success(request, "Account created successfully.")
        return redirect('/signin')
