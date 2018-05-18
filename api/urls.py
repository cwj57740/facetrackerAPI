from django.conf.urls import include, url
from api.views import *

urlpatterns = [
    url(r"^get_base_features/", get_base_features, name="get_base_features"),
    url(r"^get_stick_pic/", get_stick_pic, name="get_stick_pic"),
    url(r"^get_average_face/", get_average_face, name="get_average_face"),
    url(r"^change_features/", change_features, name="change_features"),
]
