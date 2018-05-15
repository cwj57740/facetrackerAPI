# -*- coding: utf-8 -*-
import os
import requests
import time
import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from FaceGen import *

API_KEY = 'WRg5cwms3We9MiZV9CHaJZH53kc30VFI'
API_SECRET = 'a1S4bXBNjNZWHFAJRZUclUuYuaIV-aps'
URL = 'https://api-cn.faceplusplus.com/facepp/v3/detect?api_key=%s&api_secret=%s&' \
      'return_attributes=gender,age,eyestatus,emotion,ethnicity,beauty,skinstatus' \
      '&return_landmark=%d' \
      % (API_KEY, API_SECRET, 2)
FILE_PATH = "D:\webroot"


@csrf_exempt
def get_base_features(request):
    ip = get_ip(request)

    if request.method == "POST":
        img = request.FILES.get("img", None)
        if not img:
            return JsonResponse({"msg": "no img upload"})
    file_name = str(int(time.time()))
    ext = os.path.splitext(img.name)[1]
    img_path = os.path.join(FILE_PATH, file_name+ext)
    destination = open(img_path, 'wb+')
    for chunk in img.chunks():  # 分块写入文件
        destination.write(chunk)
    destination.close()
    files = {'image_file': open(img_path, 'rb')}
    r = requests.post(url=URL, files=files).json().get('faces')

    if ip not in request.session:
        value = {"img_path": img_path}
        request.session["ip"] = value
    else:
        request.session["ip"]["img_path"] = img_path

    json_str = json.dumps(r)
    return HttpResponse(json_str)


def get_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip