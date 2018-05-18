# -*- coding: utf-8 -*-
import cv2
import json
import os
import time

import requests
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from PIL import Image

from FaceGen import face_features
from FaceGen import PixMain
from FaceGen import StarMain

API_KEY = 'WRg5cwms3We9MiZV9CHaJZH53kc30VFI'
API_SECRET = 'a1S4bXBNjNZWHFAJRZUclUuYuaIV-aps'
URL = 'https://api-cn.faceplusplus.com/facepp/v3/detect?api_key=%s&api_secret=%s&' \
      'return_attributes=gender,age,eyestatus,emotion,ethnicity,beauty,skinstatus' \
      '&return_landmark=%d' \
      % (API_KEY, API_SECRET, 2)
FILE_PATH = "./api/static/pictures"


@csrf_exempt
def get_base_features(request):
    if request.method == "POST":
        if "img" in request.POST:
            img = request.POST["img"]
        else:
            return JsonResponse({"msg": "no img upload"})
    else:
        return JsonResponse({"msg": "method is not allowed "})
    file_name = img
    ext = ".png"
    img_path = os.path.join(FILE_PATH, file_name+ext)
    # destination = open(img_path, 'wb+')
    # for chunk in img.chunks():  # 分块写入文件
    #     destination.write(chunk)
    # destination.close()
    files = {'image_file': open(img_path, 'rb')}
    json_str = "null"
    t = 0
    while json_str == "null":
        r = requests.post(url=URL, files=files).json().get('faces')
        json_str = json.dumps(r)
        t += 1
        if t >= 10:
            return JsonResponse({"msg": "timeout"})

    request.session["img_path"] = img_path

    return HttpResponse(json_str)


@csrf_exempt
def get_stick_pic(request):
    if request.method == "POST":
        if "json_str" in request.POST:
            json_str = request.POST["json_str"]
        else:
            return JsonResponse({"msg": "no json"})
    else:
        return JsonResponse({"msg": "method is not allowed "})
    if "img_path" not in request.session:
        return JsonResponse({"msg": "use get_base_features first"})
    img_path = request.session["img_path"]
    print("img_path:"+img_path)
    img_path = request.session["img_path"]
    image = cv2.imread(img_path)
    image = face_features.convert(image)
    json_object = json.loads(json_str)
    result = face_features.gen_src(image, json_object)
    result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    file_name = str(int(time.time()))
    ext = ".png"
    stick_pic_path = os.path.join(FILE_PATH, file_name + ext)
    cv2.imwrite(stick_pic_path, result)
    print("stick_pic_path", stick_pic_path)
    request.session["stick_pic_path"] = stick_pic_path

    # image_data = open(stick_pic_path, "rb").read()
    # return HttpResponse(image_data, content_type="image/png")

    # 简笔画透明化
    img = Image.open(stick_pic_path)
    img = img.convert("RGBA")
    data = img.getdata()
    new_Data = list()
    for item in data:
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            new_Data.append((255, 255, 255, 0))
        else:
            new_Data.append(item)
    img_name = str(int(time.time())) + ext
    transparent_stick_pic = os.path.join(FILE_PATH, img_name)
    img.putdata(new_Data)
    img.save(transparent_stick_pic, "PNG")

    data = {"image_path": img_name}
    return HttpResponse(json.dumps(data))


@csrf_exempt
def get_average_face(request):
    if "stick_pic_path" not in request.session:
        return JsonResponse({"msg": "use get_stick_pic first"})
    stick_pic_path = request.session["stick_pic_path"]
    print("stick_pic_path:"+stick_pic_path)

    stick_image = PixMain.Image.open(stick_pic_path)
    stick_image = PixMain.preprocess_img(stick_image, crop_to=256, resize_to=256, P=True)

    gen_image = PixMain.get_generator(enc_model="FaceGen/model/pix_enc.npz", dec_model="FaceGen/model/pix_dec.npz")
    name = str(int(time.time()))
    gen_image(stick_image, FILE_PATH, name)
    path = 'image_{}_{}.png'.format(name, "pix")
    average_face_path = FILE_PATH + '\\' + path
    # average_face_path = FILE_PATH + '\image_{}_{}.png'.format(name, "pix")
    print("average_face_path:"+average_face_path)

    request.session["average_face_path"] = average_face_path

    # image_data = open(average_face_path, "rb").read()
    # return HttpResponse(image_data, content_type="image/png")

    print(path)

    data = {"image_path": path}
    return HttpResponse(json.dumps(data))


@csrf_exempt
def change_features(request):
    if request.method == "POST":
        if "list" in request.POST:
            list_str = request.POST["list"]
        else:
            return JsonResponse({"msg": "no list"})
    else:
        return JsonResponse({"msg": "method is not allowed "})
    if "average_face_path" not in request.session:
        return JsonResponse({"msg": "use get_average_face first"})
    average_face_path = request.session["average_face_path"]

    list = json.loads(list_str)

    print("list_str:"+str(list))

    gen_image = StarMain.get_generator(model_path="FaceGen/model/star_gen.npz")
    image = StarMain.Image.open(average_face_path)
    image = StarMain.preprocess_img(image)

    pictures = []
    paths = []

    for i in range(5):
        name = str(int(time.time()))
        image = gen_image(image, list, FILE_PATH, name=name)
        image = StarMain.transpose(image)
        paths.append('image_{}_{}.png'.format(name, str(list)))
        pictures.append(FILE_PATH + '\\' + paths[i])

    print("result_img:"+paths[4])

    data = {"image_path": paths[4]}
    return HttpResponse(json.dumps(data))
