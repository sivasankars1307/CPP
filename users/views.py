from django.shortcuts import render, HttpResponse
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserRegistrationModel, TokenCountModel
from django.conf import settings
from datetime import datetime, timedelta
import jwt
import os
import pandas as pd

SECRET_KEY = "ce9941882f6e044f9809bcee90a2992b4d9d9c21235ab7c537ad56517050f26b"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HttpResponse(
            status=204,
            content="Could not validate credentials",
        )

def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            loginId = form.cleaned_data['loginid']
            TokenCountModel.objects.create(loginid=loginId, count=0)
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            messages.error(request, 'Email or Mobile Already Exists')
            print("Invalid form")
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})

def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                data = {'loginid': loginid}
                token_jwt = create_access_token(data)
                request.session['token'] = token_jwt
                print("User id At", check.id, status)
                return render(request, 'users/UserHomePage.html', {})
            else:
                messages.error(request, 'Your Account is Not Activated')
                return render(request, 'UserLogin.html')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'Invalid Login ID or Password')
            print('Exception: Invalid credentials')
    return render(request, 'UserLogin.html', {})

def UserHome(request):
    return render(request, 'users/UserHomePage.html', {})

def ViewDataset(request):
    dataset = os.path.join(settings.MEDIA_ROOT, 'nist_risk_management_policy_dataset.csv')
    df = pd.read_csv(dataset)
    df = df.to_html(index=None)
    return render(request, 'users/viewData.html', {'data': df})

def cyResults(request):
    from .utility.modelTest import startResults
    results = startResults()
    return render(request, 'users/results.html', {'rf': results.to_html})

# def GPTTest(request):
#     if request.method == 'POST':
#         query = request.POST.get('yourquery')
#         API_KEY = request.POST.get("API_KEY")
        
#         try:
#             import google.generativeai as genai
#             genai.configure(api_key=API_KEY)
            
#             # Try without the models/ prefix
#             model = genai.GenerativeModel('gemini-pro')
            
#             response = model.generate_content(query)
#             data = response.text
#             return render(request, 'users/gptResponse.html', {'data': data})
            
#         except Exception as e:
#             error_message = f"Error: {str(e)}"
#             return render(request, 'users/gptResponse.html', {
#                 'data': error_message,
#                 'error': True
#             })
#     else:
#         return render(request, 'users/gptTestForm.html', {})

from django.shortcuts import render
from google import genai
from google.genai import types

def GPTTest(request):
    if request.method == "POST":
        query = request.POST.get("yourquery")
        api_key = request.POST.get("API_KEY")

        try:
            # 👇 Tell it to use API version v1 (newer endpoint)
            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(api_version="v1")
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",   # 🚀 modern supported model
                contents=query
            )

            return render(request, "users/gptResponse.html", {
                "data": response.text
            })

        except Exception as e:
            return render(request, "users/gptResponse.html", {
                "data": f"Error: {str(e)}",
                "error": True
            })

    return render(request, "users/gptTestForm.html")




