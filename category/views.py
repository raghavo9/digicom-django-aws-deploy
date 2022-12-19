from django.shortcuts import render
from django.http import HttpRequest


# Create your views here.

def misc_function(request):
    print("reached here")
    request.session['user_email'] = "raghav"