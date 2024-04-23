from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    user_type_choices = (
        ('Admin', 'Admin'),
        ('Lead', 'Lead'),
        ('Employee', 'Employee')
    )
    user_type = models.CharField(max_length=20, choices=user_type_choices,default="Employee",null=False)
    first_name=models.CharField(max_length=20,null=False)
    last_name=models.CharField(max_length=20,null=False)
    email=models.EmailField(max_length=255,null=False)
    password=models.CharField(max_length=100,null=False)
    
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    
class Task(models.Model):
    task_priority_choice = (
        ('Normal', 'Normal'),
        ('Intermediate', 'Intermediate'),
        ('Critical', 'Critical')
    )
    task_status_choice = (
        ('Pending', 'Pending'),
        ('Acknowledge', 'Acknowledge'),
        ('Completed', 'Completed')
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    priority = models.CharField(max_length=20, choices=task_priority_choice,default="Normal")
    status = models.CharField(max_length=20, choices=task_status_choice,default="Pending")
    assignee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_by')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_to')

    def __str__(self):
        return self.title
    
class Lead(models.Model):
    id=models.BigAutoField(primary_key=True)
    lead_assignee = models.ForeignKey(CustomUser,null=True,blank=True,on_delete=models.CASCADE,related_name='lead_assigned_by')
    employee_assigned = models.ForeignKey(CustomUser,null=True,blank=True,on_delete=models.CASCADE,related_name='employee_assigned_to')

    def __str__(self):
        
        return self.lead_assignee.first_name + " " + self.lead_assignee.last_name




