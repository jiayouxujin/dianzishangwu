import pymysql
from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.


def fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    data = [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
    return data


def helloworld(request):
    return JsonResponse({"name": "xujin"})


def hello(request):
    return render(request, 'hello.html')

def erp(request):
    return render(request,'erp.html')


def getrecommend(request):
    taglist = request.GET.getlist('tag[]')
    db = pymysql.connect("127.0.0.1", "root", "123456", "dianzishangwu")
    cursor = db.cursor()
    data = []
    for item in taglist:
        cursor.execute("select * from temp2 where item1tag=%s", item)
        data = data + fetchall(cursor)
    return JsonResponse(data=data, safe=False)
