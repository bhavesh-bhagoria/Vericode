from django.shortcuts import render


def home(request):
    return render(request, "frontend/index.html")



def login_page(request):
    return render(
        request,
        "frontend/login.html"
    )