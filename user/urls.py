# Import the Django REST framework and views modules
from rest_framework import routers
from .views import UserViewSet


# Create an instance of the DefaultRouter class
router = routers.DefaultRouter()

# Register the UserViewSet with the router
router.register('', UserViewSet)