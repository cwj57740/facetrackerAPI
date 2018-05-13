# FaceTracker backend api
### environment:python 3.6.5
`pip install django==1.11.13,django-cors-headers,requests`

修改api/views.py中FILE_PATH为图片路径

执行`python manage.py runserver`开启服务器



| 接口                    | 参数     | 方法 | 结果     |
| ----------------------- | -------- | ---- | -------- |
| /api/get_base_features/ | img:图片 | post | landmark |
|                         |          |      |          |
|                         |          |      |          |