from oauth2_provider.backends import OAuth2Backend
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

UserModel = get_user_model()

class CustomOAuth2Backend(OAuth2Backend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            # Try to fetch the user by username
            user = UserModel.objects.get(username=username)
        except ObjectDoesNotExist:
            try:
                # If user with the username does not exist, try fetching by email
                user = UserModel.objects.get(email=username)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None
