from django.conf.urls import include, url
from api.views import *

urlpatterns = [
    url(r"^get_base_features/", get_base_features, name="get_base_features"),
    url(r"^get_average_face/", get_average_face, name="get_average_face"),
]
