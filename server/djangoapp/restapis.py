import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if "api_key" in kwargs:
            params = dict()
            params['text'] = kwargs['text']
            params['version'] = kwargs['version']
            params['features'] = kwargs['featuers']
            params['return_analyzed_text'] = kwargs['return_analyzed_text']
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=params, auth=HTTPBasicAuth('apikey', kwargs['api_key']))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    response = requests.post(url, params=kwargs, json=json_payload)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    print("POst to url {}".format(url))
    json_data = json.loads(response.text)
    return json_data



# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    json_result = get_request(url, dealerId=dealerId)
    
    if json_result:
        reviews = json_result["docs"]
        for review in reviews:
            try:
                watson = analyze_review_sentiments("Future-proofed foreground capability")
                print("watson: " + watson)
            except:
                print("watson failed")

            review_id = review['id'] if 'id' in review else "-1"
            purchase_date = review['purchase_date'] if 'purchase_date' in review else None
            car_make = review['car_make'] if 'car_make' in review else None
            car_model = review['car_model'] if 'car_model' in review else None
            car_year = review['car_year'] if 'car_year' in review else None 
            purchase = review['purchase'] if 'purchase' in review else False
            rev_obj = DealerReview(review['dealership'], review['name'], purchase,
            review['review'], purchase_date, car_make, 
            car_model, car_year, watson, review_id)
            results.append(rev_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    authenticator = IAMAuthenticator('ys7vnsi5flQ8K0UBuGh3tKRR1UGQ3g2XHZdTDBHBMP2V')
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/a0983f67-18bb-4ddd-b103-2c63f26e167f"
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze(
        text=text,
        features=Features(sentiment=SentimentOptions(targets=[text]))
    ).get_result()

    label=json.dumps(response, indent=2) 

    label = response['sentiment']['document']['label'] 

    return(label) 
    # response = get_request(url,
    #     api_key="ys7vnsi5flQ8K0UBuGh3tKRR1UGQ3g2XHZdTDBHBMP2V",text=text, version='2022-04-07',features=)
    # return response


