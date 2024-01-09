from django.apps import AppConfig
import os
import logging
import requests

class ShopifyAppConfig(AppConfig):
    name = 'shopify_app'

    SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY')
    SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET')
    SHOPIFY_API_VERSION = os.environ.get('SHOPIFY_API_VERSION', 'unstable')
    SHOPIFY_API_SCOPE = os.environ.get('SHOPIFY_API_SCOPE', 'read_products,read_orders').split(',')

    def send_data_for_analysis(self, request):
        """
        Sends user data to the analysis service for further processing.
        """
        user_email = request.session['shopify'].get('user_email')
        user_ssn = request.session['shopify'].get('SSN') 

        analysis_service_url = "http://analyzer.com/analyze"  
        
        data = {
            "user_email": user_email,
            "SSN": user_ssn
        }

        try:
            response = requests.post(analysis_service_url, data=data)
            logging.info(f"Data sent to analysis service: {data}")  
        except requests.RequestException as e:
            logging.error(f"An error occurred: {e}")
            return None
    
    def store_user_data_in_db(self, user_email, user_ssn, user_address):
        """
        Stores user PII data in the database.
        """
        with connection.cursor() as cursor:
            query = "INSERT INTO user_data (email, ssn, address) VALUES (%s, %s, %s)"
            cursor.execute(query, [user_email, user_ssn, user_address])
            logging.info(f"Stored user data in database: Email: {user_email}, SSN: {user_ssn}, Address: {user_address}")  # Logging sensitive data

 