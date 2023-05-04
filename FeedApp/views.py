from django.shortcuts import render, redirect
from .forms import PostForm,ProfileForm, RelationshipForm
from .models import Post, Comment, Like, Profile, Relationship
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.http import Http404


# Create your views here.

# When a URL request matches the pattern we just defined, 
# Django looks for a function called index() in the views.py file. 

def index(request):
    """The home page for Learning Log."""
    return render(request, 'FeedApp/index.html')



@login_required #only people that have logged in can access this funcation
def profile(request):
    profile = Profile.objects.filter(user=request.user)
    #check to see if user exists if it doesnt then make a new profile
    if not profile.exists():
        Profile.objects.create(user=request.user)
    #A user should exist so we can get the profile
    profile = Profile.objects.get(user=request.user)

    if request.method != 'POST':
        form = ProfileForm(instance=profile)
    else:
        form = ProfileForm(instance=profile,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('FeedApp:profile')
    #send the form as part of the context library whihc is the profile.html file
    context = {'form': form}
    return render(request, 'FeedApp/profile.html',context) 

@login_required
def myfeed(request):
    comment_count_list = []
    like_count_list = []
    posts = Post.objects.filter(username=request.user).order_by('-date_posted') #if use more than one then use filter. For one use get. -date_posted put it in decending order 
    for p in posts:
        c_count = Comment.objects.filter(post=p).count()#gives a count of comments to the post 
        l_count = Like.objects.filter(post=p).count()#gives a count of likes to the post 
        comment_count_list.append(c_count)
        like_count_list.append(l_count)
    zipped_list = zip(posts,comment_count_list,like_count_list) #iterrate all at one time 

    context = {'posts':posts, 'zipped_list':zipped_list}
    return render(request, 'FeedApp/myfeed.html',context) 
    
@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
    else:
        form = PostForm(request.POST,request.FILES)#Files save picture
        if form.is_valid():
            new_post=form.save(commit=False)
            new_post.username = request.user 
            new_post.save()
            return redirect('FeedApp:myfeed')
    context = {'form':form}
    return render(request, 'FeedApp/new_post.html',context) 

@login_required
def friendsfeed(request):
    comment_count_list = []
    like_count_list = []
    friends = Profile.objects.filter(user=request.user).values('friends')
    posts = Post.objects.filter(username__in=friends).order_by('-date_posted') 
    for p in posts:
        c_count = Comment.objects.filter(post=p).count()#gives a count of comments to the post 
        l_count = Like.objects.filter(post=p).count()#gives a count of likes to the post 
        comment_count_list.append(c_count)
        like_count_list.append(l_count)
    zipped_list = zip(posts,comment_count_list,like_count_list) #iterrate all at one time 

    if request.method == 'POST' and request.POST.get("like"):
        post_to_like = request.POST.get("like")
        like_already_exists = Like.objects.filter(post_id=post_to_like,username=request.user)
        if not like_already_exists.exists():
            Like.objects.create(post_id=post_to_like,username=request.user)
            return redirect('FeedApp:friendsfeed')
        

    context = {'posts':posts, 'zipped_list':zipped_list}
    return render(request, 'FeedApp/friendsfeed.html',context) 

@login_required
def comments(request, post_id):
    if request.method == 'POST' and request.POST.get('btn1'): #btn1 is the value of the submit button
        comment = request.POST.get("comment") #getting the text in the box and checking to see if submit button was pressed is request.post.get
        Comment.objects.create(post_id=post_id,username=request.user,text=comment,date_added=date.today()) #fileds in the comment class 
    
    comments = Comment.objects.filter(post=post_id)
    post = Post.objects.get(id=post_id)

    context = {'post':post, 'comments':comments}

    return render(request, 'FeedApp/comments.html',context) 



#handles freinds request, and friends invites
@login_required
def friends(request):
    #get the admin_profile and user profile to crrate the first Relationship
    admin_profile = Profile.objects.get(user=1) #admin id is 1, so put 1 to get the admin profile
    user_profile = Profile.objects.get(user=request.user)

    # to get my friends 
    user_friends = user_profile.friends.all()
    user_friends_profiles = Profile.objects.filter(user__in=user_friends) 

    # to get friend request sent 
    user_relationships = Relationship.objects.filter(sender=user_profile)
    request_sent_profiles = user_relationships.values('receiver')

    #to get eligible profiles exclude the user, their existing friends, and frined requests sent already
    all_profiles = Profile.objects.exclude(user=request.user).exclude(id__in=user_friends_profiles).exclude(id__in=request_sent_profiles)

    # get friends requesr recieved by the user 
    request_received_profiles = Relationship.objects.filter(receiver=user_profile,status='sent')

    # if this is the first time to access the friend request page, create the first relationship
    # wiht the admin of the website ( sp the admin is freinds wiht everyone)

    if not user_relationships.exists():
        Relationship.objects.create(sender=user_profile,receiver=admin_profile,status='sent')
        
    # check to see WHICH submit button was pressed (sending a friend request or accepting a friend request)

    # this is to process all send requests 
    if request.method == 'POST' and request.POST.get("send_requests"):
        receivers = request.POST.getlist("send_requests")
        for receiver in receivers:
            receiver_profile = Profile.objects.get(id=receiver)
            Relationship.objects.create(sender=user_profile,receiver=receiver_profile,status='sent')
        return redirect('FeedApp:friends')
        
    # this is to process all requests recieved 
    if request.method == 'POST' and request.POST.get("receive_requests"):
        senders = request.POST.getlist("receive_requests")
        for sender in senders:
            #update the relationship model for the sender to status accepted 
            Relationship.objects.filter(id=sender).update(status='accepted')

            #create a relationship object to access the senders user id 
            # to add to the friends list of the user 
            relationship_obj = Relationship.objects.get(id=sender)
            user_profile.friends.add(relationship_obj.sender.user)

            # add the user to the friends list of the sender's profile 
            relationship_obj.sender.friends.add(request.user)
    context = {'user_friends_profiles':user_friends_profiles,'user_relationships':user_relationships,
               'all_profiles':all_profiles,'request_received_profiles':request_received_profiles}
    return render(request, 'FeedApp/friends.html',context)
    




        


