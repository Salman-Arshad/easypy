from django.shortcuts import render


def test(request):
    return render(request, 'ws/test.html')


def test_broadcast(request):
    return render(request, 'ws/test_broadcast.html')
