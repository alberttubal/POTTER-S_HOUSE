from django.urls import path 
from .views import GalleryPublic 
 
urlpatterns = [ 
    path('', GalleryPublic.as_view(), name='gallery'), 
]
