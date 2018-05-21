# -*- coding: utf-8 -*-
import cv2
import json
import os
import time
import shutil

import requests
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from PIL import Image

from FaceGen import face_features
from FaceGen import PixMain
from FaceGen import StarMain

# face++ api_key与api_secret
API_KEY = 'WRg5cwms3We9MiZV9CHaJZH53kc30VFI'
API_SECRET = 'a1S4bXBNjNZWHFAJRZUclUuYuaIV-aps'

# face++ detect api
URL = 'https://api-cn.faceplusplus.com/facepp/v3/detect?api_key=%s&api_secret=%s&' \
      'return_attributes=gender,age,eyestatus,emotion,ethnicity,beauty,skinstatus' \
      '&return_landmark=%d' \
      % (API_KEY, API_SECRET, 2)

#face++ search api
SEARCH_URL = 'https://api-cn.faceplusplus.com/facepp/v3/search'
# search api 提交参数
params = {
    'api_key': API_KEY,
    'api_secret': API_SECRET,
    'faceset_token': 'db6d9ea50feea6b8ff17470b122c50cd',
    'return_result_count': '3'
}

# token与图片匹配数据文件
DATA_FILE = "data.txt"

# 项目图片路径
FILE_PATH = "E:\webroot"


@csrf_exempt
def get_base_features(request):
    """
    获取基本特征
    :param request:
    :return:
    """
    # 错误处理
    if request.method == "POST":
        if "img" in request.POST:
            img = request.POST["img"]
        else:
            return JsonResponse({"msg": "no img upload"})
    else:
        return JsonResponse({"msg": "method is not allowed "})

    # 文件路径生成
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
        # face++ detect api 调用
        r = requests.post(url=URL, files=files).json().get('faces')
        json_str = json.dumps(r)
        t += 1
        if t >= 10:
            return JsonResponse({"msg": "timeout"})

    request.session["img_path"] = img_path

    return HttpResponse(json_str)


@csrf_exempt
def get_stick_pic(request):
    """
    获取生成简笔画路径
    :param request:
    :return:
    """
    # 错误处理
    if request.method == "POST":
        if "json_str" in request.POST:
            json_str = request.POST["json_str"]
        else:
            return JsonResponse({"msg": "no json"})
    else:
        return JsonResponse({"msg": "method is not allowed "})
    if "img_path" not in request.session:
        return JsonResponse({"msg": "use get_base_features first"})

    # session 读取路径
    img_path = request.session["img_path"]
    print("img_path:"+img_path)

    # 简笔画生成
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
    img_name = "trans-"+str(int(time.time())) + ext
    transparent_stick_pic = os.path.join(FILE_PATH, img_name)
    shutil.copy(stick_pic_path, transparent_stick_pic)
    img = Image.open(transparent_stick_pic)
    img = img.convert("RGBA")
    data = img.getdata()
    new_Data = list()
    for item in data:
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            new_Data.append((255, 255, 255, 0))
        else:
            new_Data.append(item)

    img.putdata(new_Data)
    img.save(transparent_stick_pic, "PNG")

    data = {"image_path": img_name}
    return HttpResponse(json.dumps(data))


@csrf_exempt
def get_average_face(request):
    """
    根据简笔画生成平均脸
    :param request:
    :return:
    """
    # 错误处理
    if "stick_pic_path" not in request.session:
        return JsonResponse({"msg": "use get_stick_pic first"})
    stick_pic_path = request.session["stick_pic_path"]
    print("stick_pic_path:"+stick_pic_path)

    # 获取简笔画
    stick_image = PixMain.Image.open(stick_pic_path)
    stick_image = PixMain.preprocess_img(stick_image, crop_to=256, resize_to=256, P=True)

    # pix处理
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
    """
    通过StarGens进一步根据特征生成人脸
    :param request:
    :return:
    """
    # 错误处理
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

    # 获取参数
    list = json.loads(list_str)

    print("list_str:"+str(list))

    # StarGen处理
    gen_image = StarMain.get_generator(model_path="FaceGen/model/star_gen.npz", att_num=5, image_size=128)
    image = StarMain.Image.open(average_face_path)
    image = StarMain.preprocess_img(image)

    pictures = []
    paths = []

    for i in range(1):
        name = str(int(time.time()))
        image = gen_image(image, list, FILE_PATH, name=name)
        image = StarMain.transpose(image)
        paths.append('image_{}_{}.png'.format(name, str(list)))
        pictures.append(FILE_PATH + '\\' + paths[i])

    print("result_img:"+paths[0])
    request.session["result_img"] = pictures[0]
    data = {"image_path": paths[0]}
    return HttpResponse(json.dumps(data))


@csrf_exempt
def get_similar_face(request):
    """
    找到图片库中相似人脸
    :param request:
    :return:
    """
    # 最终结果人脸路径获取
    result_img = request.session["result_img"]
    print("result_img:" + result_img)

    i=0
    while True:
        # face++ search api 调用
        files = {'image_file': open(result_img, 'rb')}
        r = requests.post(SEARCH_URL, data=params, files=files).json()

        if r is not None:
            print(r)
            print(r.get("results"))
            if "results" in r:
                results = r.get("results")
                break
        i += 1
        if i > 10:
            return JsonResponse({"msg": "timeout"})
    pitures = []
    # 获取图片路径
    for item in results:
        if "face_token" in item:
            face_token = item["face_token"]
            pitures.append(get_pic_from_token(face_token))

    data = {"pictures": pitures}
    return HttpResponse(json.dumps(pitures))


def get_pic_from_token(token):
    """
    根据token值获取图片名
    :param token:
    :return:
    """
    path = FILE_PATH + "\\" + DATA_FILE
    f = open(path)
    lines = f.readlines()
    for line in lines:
        if token == line.split()[1]:
            print(line.split()[1])
            return line.split()[0]
