from django.conf.urls import include, url
from api.views import *

urlpatterns = [
    url(r"^get_base_features/", get_base_features, name="get_base_features"),
]
