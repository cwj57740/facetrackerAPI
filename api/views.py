# -*- coding: utf-8 -*-

import time
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from FaceGen.face_features import *
from FaceGen.PixMain import *

API_KEY = 'WRg5cwms3We9MiZV9CHaJZH53kc30VFI'
API_SECRET = 'a1S4bXBNjNZWHFAJRZUclUuYuaIV-aps'
URL = 'https://api-cn.faceplusplus.com/facepp/v3/detect?api_key=%s&api_secret=%s&' \
      'return_attributes=gender,age,eyestatus,emotion,ethnicity,beauty,skinstatus' \
      '&return_landmark=%d' \
      % (API_KEY, API_SECRET, 2)
FILE_PATH = "D:\webroot"


@csrf_exempt
def get_base_features(request):
    if request.method == "POST":
        img = request.FILES.get("img", None)
        if not img:
            return JsonResponse({"msg": "no img upload"})
    else:
        return JsonResponse({"msg": "method is not allowed "})
    file_name = str(int(time.time()))
    ext = os.path.splitext(img.name)[1]
    img_path = os.path.join(FILE_PATH, file_name+ext)
    destination = open(img_path, 'wb+')
    for chunk in img.chunks():  # 分块写入文件
        destination.write(chunk)
    destination.close()
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
def get_average_face(request):
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

    image = cv2.imread(img_path)
    image = convert(image)
    json_object = json.loads(json_str)
    result = gen_src(image, json_object)
    result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    file_name = str(int(time.time()))
    ext = ".png"
    stick_pic_path = os.path.join(FILE_PATH, file_name+ext)
    cv2.imwrite(stick_pic_path, result)
    print("stick_pic_path",stick_pic_path)

    stick_image = Image.open(stick_pic_path)
    stick_image = preprocess_img(stick_image, crop_to=256, resize_to=256, P=True)

    gen_image = get_generator(enc_model="FaceGen/model/pix_enc.npz", dec_model="FaceGen/model/pix_dec.npz")
    name = str(int(time.time()))
    gen_image(stick_image, FILE_PATH, name)
    average_face_path = FILE_PATH + '\image_{}_{}.png'.format(name, "pix")
    print("average_face_path:"+average_face_path)

    image_data = open(average_face_path, "rb").read()
    return HttpResponse(image_data, content_type="image/png")

