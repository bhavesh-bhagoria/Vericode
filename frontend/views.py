from django.shortcuts import render


def home(request):
    return render(request, "frontend/index.html")



def login_page(request):
    return render(
        request,
        "frontend/login.html")

def register_page(request):
    return render(
        request,
        "frontend/register.html"
    )


def verify_email_page(request, token):
    return render(
        request,
        "frontend/verify_email.html",
        {"token": token}
    )