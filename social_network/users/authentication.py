import logging

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        logging.debug(f"Authenticating user with email: {email}")
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                logging.debug(f"User {user} authenticated successfully")
                return user
            logging.debug("Password does not match")
        except User.DoesNotExist:
            logging.debug("User does not exist")
        
        return None
