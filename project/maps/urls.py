from django.urls import path

from . import views

app_name = 'maps'

urlpatterns = [
    path('', views.index, name='first'),
    path('test/', views.test, name='test'),
    path('<slug:trip>/', views.GenerateMaps.as_view(), name='index'),
    path('<slug:trip>/up/', views.UpdateMaps.as_view(), name='update'),
    path('<slug:trip>/recalc/', views.RecalcMaps.as_view(), name='recalc'),
    path('<slug:trip>/qty/', views.CommentQty.as_view(), name='comment_qty'),
    path('<slug:trip>/<slug:post>/comments/', views.Comments.as_view(), name='comments'),
]
