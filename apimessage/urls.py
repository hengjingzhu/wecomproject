from django.urls import path
from apimessage.views import *

urlpatterns = [
    path('receive',RECEIVE_MESSAGE.as_view()),
    
]
