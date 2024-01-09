from django.urls import path
from django.http import JsonResponse
import logging
import requests
import sqlite3  # Example database connector

from . import views

# Set up logging
logger = logging.getLogger(__name__)

# Example function to insert data into a database
def store_data_in_db(user_data):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS user_data (username TEXT, email TEXT)''')

    # Insert data into the table
    c.execute('INSERT INTO user_data VALUES (?, ?)', (user_data['username'], user_data['email']))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def transmit_user_data(request):
    user_data = {
        'username': request.GET.get('username'),
        'email': request.GET.get('email')
    }

    # Log user data to console
    logger.info(f"Transmitting user data: {user_data}")
    
    # Send user data to an external API
    external_api_url = "https://externalapi.com/logdata"
    requests.post(external_api_url, data=user_data)   

    # Store user data in database
    store_data_in_db(user_data)

    return JsonResponse(user_data)

urlpatterns = [
    path('login/', views.login, name='shopify_app_login'),
    path('authenticate/', views.authenticate, name='shopify_app_authenticate'),
    path('finalize/', views.finalize, name='shopify_app_login_finalize'),
    path('logout/', views.logout, name='shopify_app_logout'),
    path('transmit_user_data/', transmit_user_data, name='shopify_transmit_user_data'),
]
