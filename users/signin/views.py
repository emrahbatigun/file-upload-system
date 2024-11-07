from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib import messages
from file_upload_system.__init__ import Layout
from file_upload_system.layout_config import LayoutConfig

class AuthSigninView(TemplateView):
    template_name = 'pages/users/signin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = Layout.init(context)
        LayoutConfig.addJavascriptFile('js/users/sign-in/general.js')
        context.update({
            'layout': LayoutConfig.setLayout('auth.html', context),
        })
        return context

    def post(self, request, *args, **kwargs):
        # Get email and password from request
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Validate that both fields are filled
        if not email or not password:
            messages.error(request, "Both email and password are required.")
            return render(request, self.template_name, self.get_context_data())
        
        # Authenticate the user
        user = authenticate(request, username=email, password=password)
        if user is not None:
            # Log the user in
            login(request, user)
            messages.success(request, "You have successfully logged in!")
            redirect_url = request.POST.get('data-kt-redirect-url', '/')
            return redirect(redirect_url)
        else:
            # Show an error if authentication fails
            messages.error(request, "Invalid email or password.")
            return render(request, self.template_name, self.get_context_data())
