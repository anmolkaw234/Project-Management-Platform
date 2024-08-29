import traceback
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist

from .models import *


# Create your views here.
def Home(request):
    data = {}
    
    try:
        user = get_object_or_404(User, id=request.user.id)
        user = authenticate(request, username=user.email, password=user.password)
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(status='Active').count()
        ongoing_p = total_projects - active_projects
        total_users = User.objects.count()
        
        data = {
            "user" : request.user,
            "ongoing_projects": ongoing_p,
            "active_projects": active_projects,
            "total_users": total_users
            }
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
    
    return render(
        request,
        "home/index.html",
        data
    )


@csrf_exempt
def Login(request):
    data = {}
    
    try:
        if request.method == "POST":
            user = authenticate(request, email=request.POST.get('email'), password=request.POST.get('password'))
            
            if user is not None:
                auth_login(request, user)
                
                return redirect('/')
            else:
                messages.error(request, 'Invalid email or password.')
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
    
    return render(request, 'login/index.html', data)


@csrf_exempt
def Register(request):
    data = {}
    
    try:
        if request.method == "POST":
            if request.POST.get('password') != request.POST.get('confirm_password'):
                messages.error(request, 'Passwords do not match.')
            elif User.objects.filter(email=request.POST.get('email')).exists():
                messages.error(request, 'Email is already registered.')
            else:
                User.objects.create_user(username=request.POST.get("username"), name=f"{request.POST.get('f_name')} {request.POST.get('l_name')}", f_name=request.POST.get('f_name'), l_name=request.POST.get('l_name'), email=request.POST.get('email'), password=request.POST.get('password')).save()
                messages.success(request, 'Account created successfully.')
                
                return redirect('/login')
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
    
    return render(request, 'register/index.html', data)


def SendNotification(tos, by, title, description, date):
    try:
        tos = list(tos)
        
        for to in tos:
            notification = Notification(to=User.objects.get(id=to.id), by=User.objects.get(id=by.id), title=title, description=description, date=date, is_viewed=False)
            notification.save()
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()


@csrf_exempt
def Projects(request):
    data = {}
    
    try:
        if not request.user.is_authenticated:
            return redirect("/login")
        
        data = {"projects" : Project.objects.all(), "user" : User.objects.get(id=request.user.id)}
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
    
    return render(request, "projects/index.html", data)


def JoinProject(project, user):
    if user in project.invited.all():
        project.user.add(User.objects.get(id=user.id))
        SendNotification(project.host.all(), user, f"User: {user.name} joined the project.")
    else:
        project.potential_user.add(User.objects.get(id=user.id))
        SendNotification(project.host.all(), user, "Request to Join.", f"Hey, I am {user.name}. I want to join your project.", now())


@csrf_exempt
def CreateProject(request):
    data = {}
    
    try:
        if not request.user.is_authenticated:
            return redirect("/login")
        
        if request.method == "POST":
            project = Project(title=request.POST.get('title'), description=request.POST.get('description'), tags=list(request.POST.getlist('tags')), skills=list(request.POST.getlist('skills')), start_date=now(), end_date=now(), progress=request.POST.get('progress'), rating=0.0, status="Ongoing")
            project.save()
            project.host.add(User.objects.get(id=request.user.id))
            project.user.add(User.objects.get(id=request.user.id))
            user = get_object_or_404(User, id=request.user.id)
            user.projects.add(Project.objects.get(id=project.id))
            
            return redirect("/projects")
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
    
    return render(request, "addproject/index.html", data)


@csrf_exempt
def ProjectView(request, ProjectID, tab):
    peers = [
        {'id': 101, 'username': "John", 'profile': SET_NULL},
        {'id': 102, 'username': "Jane", 'profile': SET_NULL},
        {'id': 103, 'username': "Fred", 'profile': SET_NULL},
    ]
    data = {
        'tab' : tab,
        'peers': peers
        }
    
    try:
        if not request.user.is_authenticated:
            return redirect("/login")
        
        project = get_object_or_404(Project, id=ProjectID)
        data.update({"user" : User.objects.get(id=request.user.id)})
        print(project.invited.all())
        data.update({'tab' : tab, 'project': project, 'users': project.user.all(), 'potential_users': project.potential_user.all(), 
                     'assignments': project.assignments.all(), 'comments': project.comments.all(), 'tags': project.tags, 
                     'languages': project.languages, 'skills': project.skills})
        
        if request.method == "POST":
            req = request.POST
            
            if "discussions" in req:
                if "add":
                    comment = Discussion(title=request.POST.get("title"), description=request.POST.get("description"), project=Project.objects.get(id=ProjectID), reply_to=None, date=now(), files=request.POST.get("files"), by=request.user)
                elif "reply" in req:
                    comment = Discussion(title=request.POST.get("title"), description=request.POST.get("description"), project=Project.objects.get(id=ProjectID), reply_to=request.POST.get("reply_to"), date=now(), files=request.POST.get("files"), by=request.user)
                
                comment.save()
                project.comments.add(Discussion.objects.get(id=comment.id))
                
                return redirect(f"/project/{ProjectID}/discussions")
            elif "join" in req:
                JoinProject(project, User.objects.get(id=request.user.id))
            elif "members" in req:
                if "add" in req:
                    # invite = User.objects.get(email=request.POST.get("invited"))
                    invited_name = request.POST.get("invited")
                    try:
                        invite = User.objects.get(username=invited_name) 
                    except ObjectDoesNotExist:
                        invite = User.objects.create_user(
                            username=invited_name, 
                            email=request.POST.get("invited_email", ""), 
                            password='defaultpassword'
                        )
                    project.invited.add(invite)
                    # send notification
                elif "hire" in req:
                    print("hire")
                    hire = User.objects.get(id=request.POST.get("hire"))
                    project.user.add(hire)
                    project.potential_user.remove(hire)
                    hire.projects.add(project)
                    # send notification
                elif "delete" in req:
                    print("del")
                    hire = User.objects.get(id=request.POST.get("delete"))
                    project.potential_user.remove(hire)
                    # send notification
                elif "remove" in req:
                    if request.user in project.host.all():
                        member = User.objects.get(id=request.POST.get("member"))
                        project.user.remove(member)
                        project.host.remove(member)
                        project.save()
                        # send notification
                elif "makehost" in req:
                    if request.user in project.host.all():
                        member = User.objects.get(id=request.POST.get("member"))
                        project.host.add(member)
                        project.save()
                        SendNotification(member, request.user, f"Host: {project.title}", f"{request.user.name} added you to host for the project {project.title}.", now())
                elif "drophost" in req:
                    if len(project.host.all()) > 2 and request.user in project.host.all():
                        member = User.objects.get(id=request.POST.get("member"))
                        project.host.remove(member)
                        project.save()
                        SendNotification(member, request.user, f"No longer host", f"You are no longer host of the project {project.title}. Removed by {request.user.name}", now())
            elif "assignment" in req:
                if "add" in req:
                    # print(req.POST)
                    if request.user in project.host.all():
                        assignment = Assignment(title=request.POST.get("title"), description=request.POST.get("description"), start_date=now(), end_date=now(), files=None, by=request.user, project=Project.objects.get(id=project.id))
                        assignment.save()
                        project.assignments.add(Assignment.objects.get(id=assignment.id))
                        # send_to = list(project.user.all())
                        # send_to.remove(request.user)
                        # SendNotification(send_to, request.user, f"New Assignment published.", f"New assignment made by {request.user.name} on date {now()} of the project {project.title()} submit it by {assignment.end_date}.", now())
                elif "submit" in req:
                    assignment = request.POST.get("assignment")
                    submission = Submission(title=request.POST.get("title"), description=request.POST.get("description"), files=request.POST.get("files"), assignment = assignment, by=request.user)
                    submission.save()
                    SendNotification(assignment.by, request.user, f"Assignment-{title} Submitted", f"Assignment-{title} submitted by {request.user.name} on date {now()}.", now())
                elif "delete" in req:
                    assignment = get_object_or_404(Assignment, id=request.POST.get["assignment"])
                    title = assignment.title
                    assignment.delete()
                    send_to = project.user.all()
                    send_to.remove(request.user)
                    SendNotification(send_to, request.user, f"Assignment-{title} deleted", f"Assignment-{title} deleted by {request.user.name} on date {now()}.", now())
            elif 'mark_as_completed' in request.POST:
                project.status = 'Completed'  # Update status to 'Completed'
                project.save()
                return redirect('projects')
            elif 'suspend_project' in request.POST:
                project.status = 'Suspended'  # Update status to 'Suspended'
                project.save()
                return redirect('projects')
            
            elif 'delete' in request.POST:
                print(request.POST)
                project.delete()
                return redirect('projects')
            elif "settings" in req:
                title = request.POST.get('title')
                description = request.POST.get('description')
                objectives = request.POST.get('objectives')
                tags = request.POST.get('tags')
                start_date = request.POST.get('start_date')
                open_for_hire = request.POST.get('open_for_hire') == 'yes'

                # Create a new project
                Project.objects.create(
                    title=title,
                    description=description,
                    objectives=objectives,
                    tags=[tag.strip() for tag in tags.split(',')],
                    start_date=start_date,
                    open_for_hire=open_for_hire,
                )

                return redirect('projects')

        else:
            pass
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
    
    return render(request, "project/index.html", data)

@login_required
def add_task(request):
    p_id = 1
    if request.method == 'POST':
        name = request.POST.get('name')
        deadline = request.POST.get('deadline')
        description = request.POST.get('description')
        p_id = request.POST.get('project')
        
        project = Project.objects.get(id=p_id)
        
        # Create and save the new task
        Assignment.objects.create(
            title=name,
            project=project,
            end_date=deadline,
            description=description,
            by=request.user
        )
        
        return redirect('project', project_id=p_id)
    
    return render(request, 'addtask/index.html', {
        'p_id': p_id
    })
    
@login_required
def add_peer(request):
    peers = [
        {'id': 1, 'username': "John", 'profile': SET_NULL},
        {'id': 2, 'username': "Jane", 'profile': SET_NULL},
        {'id': 3, 'username': "Fred", 'profile': SET_NULL},
    ]
    p_id = request.POST.get('project_id', None) 
    
    if request.method == 'POST':
        peer_id = request.POST.get('peer_id')
        project = get_object_or_404(Project, id=p_id)
        peer = get_object_or_404(User, id=peer_id)
        project.invited.add(peer)
        # project.save()
        
        return redirect('project', project_id=p_id)

    return render(request, 'project/index.html', {
        'p_id': p_id,
        'peers': peers
    })


@csrf_exempt
def Profile(request, tab="profile"):
    data = {'tab' : tab}
    
    try:
        if not request.user.is_authenticated:
            return redirect("/login")
        
        data.update({"user" : User.objects.get(id=request.user.id)})
        
        if request.method == "POST":
            req = request.POST
            
            if "Profile" in req:
                pass
            elif "Billing" in req:
                pass
            elif "Security" in req:
                pass
            elif "Notifications" in req:
                data.update({"notifications" : get_object_or_404(Notification, to=request.user)})
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
    
    return render(request, "profile/index.html", data)


def Colab(request):
    data = {}
    
    try:
        if not request.user.is_authenticated:
            return redirect("/login")
        
        data = {"user" : User.objects.get(id=request.user.id)}
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
    
    return render(request, 'colab/index.html', data)


def Dashboard(request):
    projects = list(Project.objects.all().values())
    user1, created = User.objects.get_or_create(
        username='user1',
        defaults={
            'email': 'user1@example.com',
            'password': 'password123',
            # 'role': 'Developer'
        }
    )
    user2, created = User.objects.get_or_create(
        username='user2',
        defaults={
            'email': 'user2@example.com',
            'password': 'password123',
            # 'role': 'Manager'
        }
    )

    projects = list(Project.objects.all())
    
    # reviews = list(NetworkReview.objects.all().values())
    notifications = list(Notification.objects.all().values())
    # todo_list = list(ToDoList.objects.all().values())
    example_reviews = [
        {
            "user": {"username": 'john_doe'},
            "peer": {"username": 'jane_smith'},
            "engagement_level": 8,
            "rating": 4.5
        },
        {
            "user": {"username": 'alice_johnson'},
            "peer": {"username": 'charlie_black'},
            "engagement_level": 9,
            "rating": 4.8
        },
        {
            "user": {"username": 'bob_brown'},
            "peer": {"username": 'diana_white'},
            "engagement_level": 7,
            "rating": 4.2
        }
    ]

    # Example Notifications (as dictionaries)
    example_notifications = [
        {
            "user": {"username": 'john_doe'},
            "content": 'You have a new task assigned.',
            "timestamp": now()
        },
        {
            "user": {"username": 'jane_smith'},
            "content": 'Project meeting scheduled for tomorrow.',
            "timestamp": now()
        },
        {
            "user": {"username": 'alice_johnson'},
            "content": 'Your task deadline is approaching.',
            "timestamp": now()
        }
    ]

    # Example To-Do List Items (as dictionaries)
    example_todo_list = [
        {
            "name": 'Complete project proposal',
            "deadline": timezone.datetime(2024, 8, 10, 12, 0),
            "description": 'http://example.com/proposal',
            "status": 'Active'
        },
        {
            "name": 'Review codebase',
            "deadline": timezone.datetime(2024, 8, 15, 15, 0),
            "description": 'http://example.com/codebase',
            "status": 'Active'
        },
        {
            "name": 'Update project documentation',
            "deadline": timezone.datetime(2024, 8, 20, 10, 0),
            "description": 'http://example.com/documentation',
            "status": 'Active'
        }
    ]
    reviews = []
    todo_list = []
    reviews.extend(example_reviews)
    notifications.extend(example_notifications)
    todo_list.extend(example_todo_list)
    # Calculate metrics
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status='Active').count()
    completed_projects = Project.objects.filter(status='Completed').count()
    pending_projects = Project.objects.filter(status='Pending').count()
    
    # Assuming you have a way to get followers, adjust as needed
    followers = User.objects.count()
    
    tasks_done = Assignment.objects.all().count()  # Adjust Task model as necessary

    # Calculate percentage changes (dummy data used here; replace with actual calculation)
    last_week_total_projects = 100  # Replace with actual data
    last_week_active_projects = 50  # Replace with actual data
    last_week_completed_projects = 30  # Replace with actual data
    last_week_pending_projects = 20  # Replace with actual data
    last_week_followers = 200  # Replace with actual data
    last_week_tasks_done = 150  # Replace with actual data

    percentage_changes = {
        'total_projects': ((total_projects - last_week_total_projects) / last_week_total_projects * 100) if last_week_total_projects else 0,
        'active_projects': ((active_projects - last_week_active_projects) / last_week_active_projects * 100) if last_week_active_projects else 0,
        'completed_projects': ((completed_projects - last_week_completed_projects) / last_week_completed_projects * 100) if last_week_completed_projects else 0,
        'pending_projects': ((pending_projects - last_week_pending_projects) / last_week_pending_projects * 100) if last_week_pending_projects else 0,
        'followers': ((followers - last_week_followers) / last_week_followers * 100) if last_week_followers else 0,
        'tasks_completed': ((tasks_done - last_week_tasks_done) / last_week_tasks_done * 100) if last_week_tasks_done else 0,
    }


    data = {
        'projects': projects,
        'reviews':reviews,
        'notifications': notifications,
        'todo_list': todo_list,
        'active_page': 'dashb',
        'users_total_projects': total_projects,
        'user_active_projects': active_projects,
        'user_completed_proj': completed_projects,
        'user_pending_proj': pending_projects,
        'followers': followers,
        'tasks_done': tasks_done,
        'percentage_changes': percentage_changes,

    }

    try:
        if not request.user.is_authenticated:
            return redirect("/login")
        
        data = {"user" : User.objects.get(id=request.user.id)}
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
    
    return render(request, 'dashboard/index.html', data)


def Logout(request):
    auth_logout(request)
    
    return redirect('login')
