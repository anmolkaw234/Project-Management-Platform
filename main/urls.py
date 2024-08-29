from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import *


urlpatterns = [
    path('', Home, name='home'),
    path('login', Login, name='login'),
    path('logout', Logout, name='logout'),
    path('register', Register, name='register'),
    
    path('project/<slug:ProjectID>/<slug:tab>', ProjectView, name='project'),
    # path('addtask', Projects, name='addtask'),
    path('add_peer', add_peer, name='add_peer'),
    
    path('projects', Projects, name='projects'),
    path('addproject', CreateProject, name='addproject'),
    
    path('profile', Profile, name='profile'),
    
    path('colab', Colab, name='colab'),
    
    path('dashboard', Dashboard, name='dashboard'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)