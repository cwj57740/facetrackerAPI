# -*- coding: utf-8 -*-
import os
import requests
import time
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

API_KEY = 'WRg5cwms3We9MiZV9CHaJZH53kc30VFI'
API_SECRET = 'a1S4bXBNjNZWHFAJRZUclUuYuaIV-aps'
URL = 'https://api-cn.faceplusplus.com/facepp/v3/detect?api_key=%s&api_secret=%s&' \
      'return_attributes=gender,age,eyestatus,emotion,ethnicity,beauty,skinstatus' \
      '&return_landmark=%d' \
      % (API_KEY, API_SECRET, 2)
FILE_PATH = "F://webroot"


@csrf_exempt
def get_base_features(request):
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
    return HttpResponse(r)
