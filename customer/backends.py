from customer.models import Customer


class CustomerAuthBackend(object):
    """
    Email Authentication Backend

    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """
    @staticmethod
    def authenticate(password=None, email=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = Customer.objects.get(email=email)
            if password is None or user.check_password(password):
                return user
            else:
                return None
        except Customer.DoesNotExist:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return Customer.objects.get(pk=user_id)
        except Customer.DoesNotExist:
            return None