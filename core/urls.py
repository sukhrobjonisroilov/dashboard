from django.urls import path
from core.service.view import login, register, otp, re_opt,chiqish,ishchi_list,form_emp,ishchi_edit,info,xodim_delete
from core.views import index
urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('regis/', register, name='register'),
    path('otp/', otp, name='otp'),
    path('resent/', re_opt, name='reotp'),

    path('logout/',chiqish,name = 'logout'),


    #xodimlar
    path('ishchi/',ishchi_list,name='ishchi_emp'),#xodimlar umumiy royxati
    path('add/',form_emp,name='add_emp'),#xodim qoshish
    path('edit/',ishchi_edit,name='edit_emp'),#xodim edit qilish
    path('info/<int:pk>/',info,name ='info'),#malumot
    path('del/<int:pk>/<int:conf>/',xodim_delete,name='xodim_delete')
]
