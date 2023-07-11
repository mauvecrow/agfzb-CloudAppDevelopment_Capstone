from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import CarDealer, CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request, get_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid user or password"
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')
# ...

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'POST':
        # check if user exists
        username = request.POST['username_f']
        password = request.POST['password_f']
        first_name = request.POST['first_f']
        last_name = request.POST['last_f']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("new user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name,
                last_name=last_name, password=password)
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "User already exists"
            return render(request, 'djangoapp/registration.html', context)
    else:
        return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/44afbc3a-4d46-45dc-99c8-72d987e67f82/dealership-package/get-all-dealerships"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        # dealer_names = ', '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        # return HttpResponse(dealer_names)
        context = {}
        context['dealership_list'] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == 'GET':
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/44afbc3a-4d46-45dc-99c8-72d987e67f82/dealership-package/get-review"
        dealer_reviews = get_dealer_reviews_from_cf(url, dealer_id)
        # reviews = '; '.join([', '.join("%s: %s" % item for item in vars(rev).items()) for rev in dealer_reviews])
        # return HttpResponse(reviews)
        context = {}
        context['review_list'] = dealer_reviews
        url2 = "https://us-south.functions.appdomain.cloud/api/v1/web/44afbc3a-4d46-45dc-99c8-72d987e67f82/dealership-package/get-dealership"
        dealership = get_request(url2, id=dealer_id)['docs'][0]
        
        context['dealership'] = dealership
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    context['dealer_id'] = dealer_id
    if request.method == 'POST':
        print("Inside POST add review")

        url = "https://us-south.functions.appdomain.cloud/api/v1/web/44afbc3a-4d46-45dc-99c8-72d987e67f82/dealership-package/post-review"
        # print("User: " + str(request.user))
        if request.user is None:
            return render(request, 'djangoapp/registration.html', context)
        print("User is authenticated")
        content = request.POST['content']
        purchase = request.POST['purchasecheck']
        purchase_date = request.POST['purchasedate']
        car_id = request.POST['car']
        car = CarModel.objects.get(pk=car_id)
        print(str(car))
        make = car.car_make.name
        model = car.name
        year = car.year.strftime("%Y")
        review = {
            # "id": "001",
            "name": "online review",
            "dealership": dealer_id,
            "review": content,
            "purchase": purchase,
            "purchase_date": purchase_date,
            "car_make": make,
            "car_model": model,
            "car_year": int(year)
        }
        json_payload = {}
        json_payload['review'] = review
        print(json_payload)
        result = post_request(url, json_payload)
        print(result)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
    if request.method == 'GET':
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context['cars'] = cars
        url2 = "https://us-south.functions.appdomain.cloud/api/v1/web/44afbc3a-4d46-45dc-99c8-72d987e67f82/dealership-package/get-dealership"
        dealership = get_request(url2, id=dealer_id)['docs'][0]
        context['dealership'] = dealership
        return render(request, 'djangoapp/add_review.html', context)



