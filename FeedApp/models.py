from django.db import models
from django.contrib.auth.models import User


# Create your models here. Decribes how the database ir setup. 
class Profile(models.Model):
    first_name = models.CharField(max_length=200,blank=True)
    last_name = models.CharField(max_length=200,blank=True)
    email = models.EmailField(max_length=300,blank=True)
    dob = models.DateField(null=True,blank=True)
    bio = models.TextField(blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE) #asscoaiting each profile to a user
    friends = models.ManyToManyField(User,blank=True,related_name='friends') #a profile can have many friends associated with a user
    created = models.DateTimeField(auto_now=True) #date the profile was created
    updated = models.DateTimeField(auto_now_add=True) #date the profile was updated 

    def __str__(self):
        return f"{self.user.username}"

STATUS_CHOICES = (
    ('sent','sent'),
    ('accepted','accepted')
) 

#allows to establish a relationship between two profiles
class Relationship(models.Model): 
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="sent")
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True) 

#related to any post that the user makes
class Post(models.Model):
    description = models.CharField(max_length=255, blank=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images', blank=True) #blank=True means not required to have an image
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description

#source to the post
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    username = models.ForeignKey(User, related_name='details', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True, blank=True) 

    def __str__(self):
        return self.text 
    
#keep track of the likes of a post
class Like(models.Model):
    username = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)

