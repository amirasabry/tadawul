from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
import requests
import json
import random

def index(request):
    """ The method that rendering the main page
    where we get the payment gateway & order data
    """
    template = loader.get_template('index.html')
    return HttpResponse(template.render())

def checkout(request):
    """ Get request data, validate & make 
    a Tadawul API Call to initiate the payment process
    """
    if validateFormData(request.POST):
	    store_id       = request.session['store_id']   = request.POST['store_id']
	    auth_token     = request.session['auth_token'] = request.POST['auth_token']
	    custom_ref     = request.session['custom_ref'] = random.randrange(100, 999)

	    customer_email = request.POST['customer_email']
	    customer_phone = request.POST['customer_phone']
	    amount         = request.POST['amount']

	    url  = 'https://c7drkx2ege.execute-api.eu-west-2.amazonaws.com/payment/initiate'
	    payload = "id={}&amount={}&phone={}&email={}&backend_url={}&frontend_url={}&custom_ref={}"
	    payload = payload.format(store_id, 10, customer_phone, customer_email, 'http://www.example.com', ('http://' + request.META.get('HTTP_HOST') + '/handleresponse'),custom_ref)
	    headers = {
	    'Accept': 'application/json',
	    'Content-Type': 'application/x-www-form-urlencoded',
	    'Authorization': ('Bearer ' + auth_token)
	    }

	    response = requests.request("POST", url, headers=headers, data=payload)
	    response = json.loads(response.text)
	    if response['result'] == 'success':
	    	return redirect(response['url'])
	    else:    	
	        template = loader.get_template('checkout.html')
	        return HttpResponse(template.render({'data': response}, request))
    else:
    	# Change the messages level to ensure the debug message is added.
        # request.session['bar'] = 'FooBar'
        # context['bar'] = 'FooBar'
        messages.success(request,'done')
        return redirect(reverse('index'))


def handleresponse(request):
    #Get transaction status
    if 'custom_ref' in request.session and 'store_id' in request.session and 'auth_token' in request.session:
        custom_ref = request.session['custom_ref']
        store_id   = request.session['store_id']
        auth_token   = request.session['auth_token']
        url = 'https://c7drkx2ege.execute-api.eu-west-2.amazonaws.com/receipt/transaction';
        payload = 'store_id={}&custom_ref={}'
        payload = payload.format(store_id, custom_ref)
        headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': ('Bearer ' + auth_token)
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = json.loads(response.text)        
    else:
        custom_ref = 0
        response = {
        'custom_ref' : request.session['custom_ref'],
        'store_id' : request.session['store_id'],
        'auth_token' : request.session['auth_token'],
        }

    template = loader.get_template('response.html')
    return HttpResponse(template.render({'data': response}, request))

def validateFormData(data):
    if 'store_id' not in data or not data['store_id']\
    or 'auth_token' not in data or not data['auth_token']\
    or 'customer_email' not in data or not data['customer_email']\
    or 'customer_phone' not in data or not data['customer_phone']\
    or 'amount' not in data or not data['amount']:
        return False
    else:
    	return True



