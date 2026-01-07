
from django.contrib import admin
from django.urls import path
from .views import home, register_view, login_view, logout_view, book_service, master_detail, profile_view
urlpatterns = [path('admin/', admin.site.urls), path('', home), path('register/', register_view), path('login/', login_view), path('logout/', logout_view), path('book/', book_service), path('master/<int:master_id>/', master_detail), path('profile/', profile_view)]
