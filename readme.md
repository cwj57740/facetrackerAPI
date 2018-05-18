# FaceTracker backend api
### environment:python 3.6.5, [redis 3.2](https://redis.io/download) ([windows-redis](https://github.com/MicrosoftArchive/redis/releases))
`pip install django==1.11.13 django-cors-headers requests django-redis-sessions chainer opencv-python Pillow`

修改api/views.py中FILE_PATH为图片路径

在facetrackerAPI目录下执行git clone https://github.com/AlongWY/FaceGen.git

执行`python manage.py runserver`开启服务器

开启redis(windows为powershell下执行./redis-server.exe)


| 接口                    | 参数                | 方法 | 结果     |
| ----------------------- | -----------------  | ---- | -------- |
| /api/get_base_features/ | img:图片           | post | landmark |
| /api/get_stick_pic/     | json_str:json数据  | post | 简笔画图片|
| /api/get_average_face/  |                    | get  | 平均脸图片|
| /api/change_features/   | list:[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] | post | 平均脸图片|
| /api/get_similar_face/  |                    | get  | 相似图片  |