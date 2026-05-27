from django.shortcuts import render

def hello_world(request):
    return render(request, 'pages/hello-world.html')

def pag2(request):
    return render(request, 'pages/pag2.html')