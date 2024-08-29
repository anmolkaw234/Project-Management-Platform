from django.db.models import *
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


def user_profile_path(instance, filename):
    return f'user_{instance.id}/{filename}'


class User(AbstractUser):
    email = EmailField(unique=True)
    password = CharField(max_length=120)
    name = CharField(max_length=120)
    f_name = CharField(max_length=120)
    l_name = CharField(max_length=120)
    doe = DateField(default=now)
    rating = FloatField(default=0.0)
    languages = JSONField(default=list)
    profile = ImageField(upload_to=user_profile_path, null=True, blank=True)
    projects = ManyToManyField('Project', related_name='UserProjects')
    submissions = ManyToManyField('Submission', related_name='UserSubmissions')
    groups = ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = ManyToManyField(Permission, related_name='custom_user_set_permissions')
    files = FileField(upload_to='user_files/', null=True, blank=True)
    #######################
    objects = UserManager()


class Project(Model):
    title = CharField(max_length=120)
    description = TextField()
    start_date = DateTimeField(default=now)
    end_date = DateTimeField(null=True, blank=True)
    rating = FloatField()
    progress = IntegerField(default=0)
    host = ManyToManyField(User, related_name='hosts', blank=True)
    user = ManyToManyField(User, related_name='users', blank=True)
    invited = ManyToManyField('User', related_name='invited', blank=True)
    potential_user = ManyToManyField('User', related_name='PotentialUser', blank=True)
    assignments = ManyToManyField('Assignment', related_name='ProjectAssignment', blank=True)
    status = CharField(max_length=120)
    files = FileField(upload_to='project_files/', null=True, blank=True)
    comments = ManyToManyField('Discussion', related_name='ProjectDiscussion', blank=True)
    tags = JSONField(default=list, blank=True)
    objectives = JSONField(default=list, blank=True)
    languages = JSONField(default=list, blank=True)
    skills = JSONField(default=list, blank=True)
    hiring = BooleanField(default=True)
    # add links
    github_link = CharField(max_length=200)
    twitter_link = CharField(max_length=200)
    facebook_link = CharField(max_length=200)
    instagram_link = CharField(max_length=200)
    web_link = CharField(max_length=200)


class Team(Model):
    name = CharField(max_length=120)
    project = ForeignKey('Project', related_name='TeamProject', on_delete=CASCADE)
    users = ManyToManyField('User', related_name='TeamUser')


class Discussion(Model):
    title = CharField(max_length=120)
    description = TextField()
    project = ForeignKey('Project', related_name='projectdiscuss', on_delete=CASCADE)
    reply_to = ForeignKey('Discussion', related_name='Comments', on_delete=CASCADE, null=True, blank=True)
    files = FileField(upload_to='discussion_files/', null=True, blank=True)
    date = DateTimeField(default=now)
    by = ForeignKey('User', related_name='UserDiscussion', on_delete=CASCADE)



class Assignment(Model):
    title = CharField(max_length=120, null=True, blank=True)
    description = TextField()
    start_date = DateTimeField(default=now)
    end_date = DateTimeField()
    files = FileField(upload_to='assignment_files/', null=True, blank=True)
    by = ForeignKey('User', related_name='HostAssignment', on_delete=CASCADE)
    comments = ManyToManyField('Discussion', related_name='AssignmentDiscussion', blank=True)
    project = ForeignKey('Project', related_name='AssignmentProject', on_delete=CASCADE)
    doneby = ManyToManyField('User', related_name='AssignmentUser', blank=True)


class Submission(Model):
    title = CharField(max_length=120)
    description = TextField()
    files = FileField(upload_to='submission_files/', null=True, blank=True)
    date = DateTimeField(default=now)
    by = ForeignKey('User', related_name='SubmissionUser', on_delete=CASCADE)
    assignment = ForeignKey('Assignment', related_name='SubmissionAssignment', on_delete=CASCADE)


class Notification(Model):
    type = CharField(max_length=120)
    title = CharField(max_length=120)
    description = TextField()
    date = DateTimeField(default=now)
    is_viewed = BooleanField(default=False)
    by = ForeignKey('User', related_name='tempNotification', on_delete=CASCADE)
    to = ForeignKey('User', related_name='UserNotification', on_delete=CASCADE)
    
class Task(Model):
    project = ForeignKey(Project, on_delete=CASCADE)
    name = CharField(max_length=255)
    deadline = DateTimeField()
    description = TextField()
    status = TextField(default="Active")