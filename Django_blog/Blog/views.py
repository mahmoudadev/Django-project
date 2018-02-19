
from distutils.command import register
from django.contrib.sessions import serializers
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
from .models import *
from .forms import commentform,replyform, UserLogin,RegistrationForm
from django.http import HttpResponseRedirect, JsonResponse
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re
from django.db.models import Q
from .models import *
from django.template import RequestContext
from django.contrib.auth import authenticate,get_user_model,login,logout

def allPosts(request):
    all_posts = Post.objects.all()
    page = request.GET.get('page',1)
    paginator = Paginator(all_posts, 5)
    try:
        posts=paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(page)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    all_cat = getCat()
    sub_cat = sub(request)
    context = {"allPosts": posts, "allCat": all_cat, "subcat": sub_cat}
    return render(request, "blog/home.html", context)


def search(request):

    try:
        tag = Tag.objects.get(name__icontains=request.GET['term'])
        byTag = Post.objects.filter(tag=tag.id).order_by('created_at')
    except Tag.DoesNotExist:
        byTag = None
    try:
        found_entries = Post.objects.filter(title__icontains=request.GET['term']).order_by('created_at')

    except Post.DoesNotExist:
        found_entries = None
    all_cat = getCat()
    sub_cat = sub(request)
    context = {"allPosts": found_entries, "tags": byTag, "allCat": all_cat, "subcat": sub_cat}
    return render(request, "blog/search.html", context)




def getCat():

    cat=Category.objects.all()
    return cat


def getPostsCat(request, cat_id):
    all_posts = Post.objects.filter(cat_id= cat_id).order_by('created_at')
    all_cat = getCat()
    sub_cat = sub(request)
    context = {"allPosts": all_posts, "allCat": all_cat, "subcat": sub_cat}
    return render(request, "blog/home.html", context)




def subscribe(request):
    cat_id = request.GET.get('catid', None)
    status = Category.subscribe.through.objects.filter(category_id=cat_id, user_id=request.user.id).exists()

    if status:
        #remove
        Category.subscribe.through.objects.filter(category_id=cat_id, user_id=request.user.id).delete()
        data = {
            'x': 1

        }

    else:
		Category.subscribe.through.objects.create(category_id=cat_id, user_id=request.user.id)
		data = {
			'x': 2

		}

		return JsonResponse(data)

# Create your views here.

def filterwithoutbadwords(comment):
	commentsplitted=comment.split()
	ob2 = BadWord.objects.all() 
	counter=0
	for c in commentsplitted:
		c=c.lower()
		for o in ob2:
			o=o.name.lower()
			if c == o:
				size=len(c)
				cnew=""
				for cindex in c:
					cnew=cnew+"*"
					cnew=str(cnew)
				commentsplitted[counter]=cnew
		counter+=1
	mylists=""
	for uu in commentsplitted:
		mylists = mylists + uu
		mylist2=str(mylists)
	return mylist2

def postPage(request,post_id,user_id):
	form = commentform()
	form1=replyform()
	ob = Post.objects.get(id=post_id)
	obb = Tag.objects.all()
	ob1 = Comment.objects.raw("select * from Blog_comment where post_id=post_id")
	xx=[]
	xx1=[]
	for x in ob1:
		varg =filterwithoutbadwords(x.body)
		xx.append(varg)
		ob5 = User.objects.get(id=x.user_id)
		xx1.append(ob5)
	zipped_data= zip(ob1,xx,xx1)	
	xx1=[]
	xx11=[]
	ob2 = Reply.objects.all()  
	for x1 in ob2:
		varg =filterwithoutbadwords(x1.body)
		xx1.append(varg)
		ob5 = User.objects.get(id=x1.user_id)
		xx11.append(ob5)
	zipped_data1= zip(ob2,xx1,xx11)
	context = {'post_list':ob,
	'tag_list':obb,
	'comment_list':ob1,
	'comment_body':xx,
	'zipped_data':zipped_data,
	'zipped_data1':zipped_data1,
	}
	#if request.method=="POST":
	#	varf=request.POST.get('body')
	#	vare=filterwithoutbadwords(varf)
	#	ob1= form.save(commit=False)
	#	ob1.user_id=user_id
	#	ob1.post_id=post_id
	#	ob1.body=varf
	#	ob1.save()

	
	return render(request, 'postpage.html', context)

def new_comment(request):
	form = commentform()
	ob1= form.save(commit=False)
	ob1.post_id=request.GET.get('post_id',None)
	ob1.user_id=1
	ob1.body=request.GET.get('body',None)
	ob1.save()
	username_calculated = User.objects.get(id=ob1.user_id)
	data = {
	'idd' :ob1.id,
	'username':ob1.user_id,
	'createdat':ob1.created_at
	}
	
	return JsonResponse(data)

def new_reply(request):
	form1 = replyform()
	ob1= form1.save(commit=False)
	ob1.comment_id=request.GET.get('comment_id_reply',None)
	#print ob1.comment_id
	ob1.user_id=1
	ob1.body=request.GET.get('bodyreply',None)
	#print ob1.body
	ob1.save()
	data = {
	'idd' :ob1.id,
	'username':ob1.user_id,
	'createdat':ob1.created_at 
	}
	return JsonResponse(data)



#	messages.info(request,"geeet")
#	form= commentform()
#	print "get new_comment"
#	if request.method=="POST":
#		print "method b post"
#		form=commentform(request.POST)
#		if form.is_valid():
#			form.save()
#			return JsonResponse(serializers.serialize('json',Comment.objects.all()),safe=False)
	#return render(request, 'postpage.html')
	
	#return render(request, 'postpage.html',context1)



def comment_delete(request):
	comment_id=request.GET.get('comment_id',None)
	comm=Comment.objects.get(id=comment_id)
	comm.delete()
	data = {
	'x' :1
	}
	
	return JsonResponse(data)









def sub(request):
    catsub=Category.objects.filter(subscribe=request.user.id)
    cat_sub=[]
    for i in catsub:
        cat_sub.append(i.id)
    return cat_sub


User = get_user_model()
def login(request):
	form = UserLogin(request.POST or None)
	if form.is_valid():
		username = form.cleaned_data.get("username")
		password = form.cleaned_data.get("password")
	return render(request, "blog/login_page.html", {"form" : form})


def register(request):
	if request.method == "POST":
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("/home")
	else:
		form = RegistrationForm()

	return render(request, "blog/register.html", {"form": form})


def logout(request):
	return render(request, "logout_page.html", {})



















