from django.shortcuts import render

def messages(request):
    return render(request, 'chat/messages.html')
