from rest_framework import status
from .models import *
from rest_framework.response import Response
from .serializers import RegisterUserSerializer,UserLoginSerializer,AdminUserhirarchyupdateSerializer,TaskSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login,logout


# Create your views here.
@api_view(['POST'])
def Registration(request):
    if request.method == 'POST':
        username = request.data.get('username')
        first_name=request.data.get('first_name')
        last_name=request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password')
        user_type=request.data.get('user_type')
        
         # Check if username is already taken
        if CustomUser.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        # Create the user
        user = CustomUser.objects.create_user(username=username,first_name=first_name,last_name=last_name, password=password, email=email,user_type=user_type)
        # Serialize the user
        serializer = RegisterUserSerializer(user)
        return Response({'user': serializer.data, 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response({'error':'Give required inputs'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            serializer = UserLoginSerializer(user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key,'user': serializer.data,'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid login'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        token = Token.objects.get(user=request.user)
        token.delete()
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

#------------------Admin section------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def adminpageusersview(request):
    # Check if the user is authenticated and is an admin
    if not request.user.is_authenticated or request.user.user_type != 'Admin':
        return Response({"error": "Authentication required or user is not an admin"}, status=status.HTTP_401_UNAUTHORIZED)
    
    #get registered users under employee and lead,get assignee and also assigned_to
    employees = CustomUser.objects.filter(user_type='Employee').values('id', 'first_name', 'last_name', 'email')
    leads = CustomUser.objects.filter(user_type='Lead').values('id', 'first_name', 'last_name', 'email')
    Assignee_Assigned_to = Lead.objects.all().values('id', 'lead_assignee__first_name','employee_assigned__first_name')
    return Response({'employees': list(employees), 'leads': list(leads),'Assignee_Assigned_to': list(Assignee_Assigned_to)})
    
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def adminchangeuser_type(request):
    # Check if the user is authenticated and is an admin
    if not request.user.is_authenticated or request.user.user_type != 'Admin':
        return Response({"error": "Authentication required or user is not an admin"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        data = request.data
        user_id = data.get('user_id')
        new_user_type = data.get('new_user_type')
        # Check if user_id and new_user_type are provided
        if not user_id or not new_user_type:
            return Response({'error': 'User ID and new user type are required.'}, status=status.HTTP_400_BAD_REQUEST)
        # Retrieve the user 
        user = CustomUser.objects.get(id=user_id)
        # Update the user_type if the user exists
        user.user_type = new_user_type
        user.save()
        # Serialize and return the updated user
        serializer = AdminUserhirarchyupdateSerializer(user)
        return Response({'user': serializer.data, 'message': 'User type updated successfully.'})
    except CustomUser.DoesNotExist:
        return Response({'error': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception :
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Adminassign_employee_to_lead(request):
    if request.user.user_type == 'Admin':
        if request.method == 'POST':
            user_id = request.data.get('user_id')
            employee_id = request.data.get('employees', [])
        # Retrieve the CustomUser object corresponding to the provided user ID
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'The provided user ID does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is a Lead
        if user.user_type == 'Lead':
            # Get or create the Lead object for the provided user
            lead, _ = Lead.objects.get_or_create(lead_assignee=user)
            # Check if any employee ID is provided
            if not employee_id:
                return Response({'error': 'No employees provided to assign'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the employee ID exists for provided employee ID
            try:
                employee = CustomUser.objects.get(id=employee_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'The provided employee ID does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            # Assign the employee to the lead
            lead.employee_assigned=employee
            lead.save()
            # print("*****")
            # print(lead.employee_assigned)
            return Response({'message': 'Employee assigned successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'The provided user ID does not belong to a Lead'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def adminview_tasks(request):
    if request.user.user_type == 'Admin': 
        if request.method == 'GET':
            username = request.data.get('username')
        # Retrieve the user using username
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        # Retrieve all tasks assigned to the user
        tasks_assigned = Task.objects.filter(assigned_to=user)
        # Serialize the tasks
        serializer = TaskSerializer(tasks_assigned,many=True)
        return Response({'tasks_assigned': serializer.data}, status=status.HTTP_200_OK)
    
#-------------------lead section-------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def leadview_employees_and_tasks(request):
    # Check if the user is authenticated and is a lead
    if not request.user.is_authenticated or request.user.user_type != 'Lead':
        return Response({"error": "Authentication required or user is not a lead"}, status=status.HTTP_403_FORBIDDEN)

    # Get the lead object
    lead = request.user  # logged-in user is the lead

    if request.method == 'GET':
        # Retrieve IDs of employees assigned to the lead
        assigned_employee_ids = Lead.objects.filter(lead_assignee=lead).values_list('employee_assigned', flat=True)

        # Retrieve tasks assigned to those employees
        assigned_tasks = Task.objects.filter(assigned_to__in=assigned_employee_ids)

        # Serialize the tasks for each employee
        employee_tasks = {}
        for employee_id in assigned_employee_ids:
            employee_tasks[employee_id] = TaskSerializer(assigned_tasks.filter(assigned_to=employee_id), many=True).data

        return Response({'employee_id_tasks': employee_tasks})

    elif request.method == 'POST':
        # Check if the provided data is valid
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            # Assign the task to employees under the lead
            assigned_employee_ids = Lead.objects.filter(lead_assignee=lead).values_list('employee_assigned', flat=True)
            for employee_id in assigned_employee_ids:
                serializer.save(assignee=lead, assigned_to_id=employee_id)
            return Response({'message': 'Task added successfully to employees under the lead'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def leadupdate_task(request, task_id):
    if not request.user.user_type == 'Lead':
        return Response({"error": "User is not a lead"}, status=status.HTTP_403_FORBIDDEN)

    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return Response({"error": "Task does not exist"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = TaskSerializer(instance=task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#-------------------Employee section-------------    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employeeview_task(request):
    if not request.user.is_authenticated or request.user.user_type != 'Employee':
        return Response({"error": "Authentication required or user is not an Employee"}, status=status.HTTP_401_UNAUTHORIZED)
    user = request.user
    # Retrieve tasks assigned to the authenticated user (employee)
    tasks = Task.objects.filter(assigned_to=user).order_by('priority', 'start_date')
    serializer = TaskSerializer(tasks, many=True)
    return Response({"tasks":serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def employeeupdate_taskstatus(request, task_id):
    # Check if the user is authenticated and is an Employee
    if not request.user.is_authenticated or request.user.user_type != 'Employee':
        return Response({"error": "Authentication required or user is not an Employee"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        # Retrieve the task
        task = Task.objects.get(id=task_id, assigned_to=request.user)
    except Task.DoesNotExist:
        return Response({"error": "Task not found or you are not assigned to this task"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Serialize and return the task data
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Check if the provided status transition is valid
        new_status = request.data.get('status')
        if new_status == 'Acknowledge' and task.status != 'Pending':
            return Response({"error": "Invalid status transition"}, status=status.HTTP_400_BAD_REQUEST)
        elif new_status == 'Completed' and task.status != 'Acknowledge':
            return Response({"error": "Invalid status transition"}, status=status.HTTP_400_BAD_REQUEST)
        # Serialize and update the task_status data
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employeefilter_taskpriority(request):
    if not request.user.is_authenticated or request.user.user_type != 'Employee':
        return Response({"error": "Authentication required or user is not an Employee"}, status=status.HTTP_401_UNAUTHORIZED)
    
    user = request.user
    priority = request.data.get('priority')
    # Retrieve tasks assigned to the employee filtered by priority
    if priority:
        tasks = Task.objects.filter(assigned_to=user, priority=priority).order_by('start_date')
    else:
        tasks = Task.objects.filter(assigned_to=user).order_by('start_date')

    serializer = TaskSerializer(tasks, many=True)
    return Response({"tasks":serializer.data}, status=status.HTTP_200_OK)