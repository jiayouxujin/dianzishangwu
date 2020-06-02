from django.urls import path

from Server.views import helloworld, hello, getrecommend, erp

urlpatterns = [
    path('api/helloworld', helloworld),
    path('', hello),
    path('api/getrecommend', getrecommend),
    path('erp', erp)
]
