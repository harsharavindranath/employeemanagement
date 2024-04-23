from django.urls import path
from  .views import *

urlpatterns = [
    path('Registration/',Registration),
    path('Login/',user_login),
    path('Logout/',user_logout),
    path('adminpageusersview/',adminpageusersview),
    path('adminchangeuser_type/',adminchangeuser_type),
    path('Adminassign_employee_to_lead/',Adminassign_employee_to_lead),
    path('adminview_tasks/',adminview_tasks),
    path('leadview_employees_and_tasks/',leadview_employees_and_tasks),
    path('leadupdate_task/<int:task_id>/',leadupdate_task),
    path('employeeview_task/',employeeview_task),
    path('employeeupdate_taskstatus/<int:task_id>/',employeeupdate_taskstatus),
     path('employeefilter_taskpriority/',employeefilter_taskpriority),
]