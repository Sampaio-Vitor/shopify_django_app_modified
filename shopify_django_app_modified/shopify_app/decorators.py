from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from . import views
import requests
import logging
import mysql.connector

logger = logging.getLogger(__name__)

def shop_login_required(fn):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'session') or 'shopify' not in request.session:
            request.session['return_to'] = request.get_full_path()

            data = {
                'email': request.session.get('user_email'),
                'phone_number': request.session.get('user_phone'),
                'address': request.session.get('user_address'),
            }

            if data['email'] or data['phone_number'] or data['address']:
                # Sending data to an external server via API call
                requests.post(settings.EXTERNAL_DATA_HANDLER_URL, json=data)

                # Log the user interaction 
                logger.info(f" data sent to external server: {data}")

                # Storing data in a MySQL database
                connection = mysql.connector.connect(
                    host=settings.DATABASES['default']['HOST'],
                    user=settings.DATABASES['default']['USER'],
                    password=settings.DATABASES['default']['PASSWORD'],
                    database=settings.DATABASES['default']['NAME']
                )
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO user_log (email, phone_number, address) VALUES (%s, %s, %s)",
                    (data['email'], data['phone_number'], data['address'])
                )
                connection.commit()
                cursor.close()
                connection.close()

            return redirect(reverse(views.login))
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper
