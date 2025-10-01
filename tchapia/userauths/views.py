from django.contrib import messages
from userauths import forms as userauths_forms
from django.contrib.auth import authenticate, login, logout
from handyman import models as handyman_models
from customer import models as customer_models

from userauths import models as user_auths_models
from django.shortcuts import render, redirect
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)




# Create views here 
# Create views here
def register_view(request):
    if request.user.is_authenticated:
        print("####### Already logged In !")
        messages.success(request, "You are already logged in")
        return redirect("/")

    if request.method == "POST":
        form = userauths_forms.UserRegisterForm(request.POST)

        if form.is_valid():
            # Save the user
            user = form.save()

            # Get user type to create appropriate profile
            user_type = form.cleaned_data.get("user_type")
            password = form.cleaned_data.get("password1")

            # Authenticate and login the user
            user = authenticate(request, username=user.email, password=password)
            if user is not None:
                login(request, user)

                # Create user-specific profile based on type
                if user_type == "artisan":
                    handyman_models.Handyman.objects.create(user=user)
                    messages.success(request, "Compte artisan créé avec succès!")
                elif user_type == "client":
                    customer_models.Customer.objects.create(user=user)
                    messages.success(request, "Compte client créé avec succès!")
                
                return redirect("base:home")
            else:
                messages.error(request, "Erreur d'authentification, veuillez réessayer")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous")
    else:
        form = userauths_forms.UserRegisterForm()

    context = {"register_form": form}
    return render(request, "userauths/register.html", context)

def login_view(request):
      print("####### Inside Login !")
      if request.user.is_authenticated:
        print("####### User Authenticated !:", request.user)
        messages.success(request, "You are already logged in")
        return redirect("/")

      if request.method == "POST":
          form = userauths_forms.LoginForm(request.POST)

          email = request.POST.get("username")  # LoginForm uses 'username' field for email
          password = request.POST.get("password")

          user = authenticate(request, username=email, password=password)

          if user is not None:
                login(request, user)
                return redirect("/")
          else:
              messages.error(request, "Email ou mot de passe incorrect")
      else:
          form = userauths_forms.LoginForm()

      context = {"login_form": form}
      return render(request, "userauths/login.html", context)

def logout_view(request):
    print("####### Inside LOGOUT !")
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès")
    return redirect("/")