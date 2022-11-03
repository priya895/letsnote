from django.contrib.auth import authenticate,login,logout
# from django.shortcuts import render
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import *
from cryptography.fernet import MultiFernet,Fernet
from django.conf import settings
from django.core.mail import send_mail
import random
def encryption(str1,key):
    mf=Fernet(key)
    enctex = mf.encrypt(str1.encode())
    return enctex
def decryption(str1,key):
    key.encode()
    mf= Fernet(key)
    dectex = mf.decrypt(str1.encode())
    return dectex.decode('utf-8')
# Create your views here.
def index(request):
    return render(request,"mynotes/index.html")
def active(request):
    return render (request, "mynotes/index.html")
def login_view(request):
    if request.method=="POST":
        username=request.POST["username"]
        password=request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return HttpResponseRedirect(reverse("homepage"))
        else:
            return render(request, "mynotes/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request,"mynotes/login.html")
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "mynotes/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "mynotes/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return render(request,"mynotes/homepage.html")
    else:
        return render(request, "mynotes/register.html")
def homepage(request):
    return render(request,"mynotes/homepage.html")
def about(request):
    return render(request,"mynotes/about.html")
def contact(request):
    return render(request,"mynotes/contact.html")
@login_required(login_url='/login')
def create(request):
    if request.method== "POST":
        note= Notes()
        note.content=request.POST["content"]
        note.Title=request.POST["Title"]
        note.owner= request.user
        note.save()
        return redirect(fnotes)
    else:
        return render(request,"mynotes/create.html",{
            "list":Notes.objects.all()
        })
@login_required(login_url="/login")
def remnotes(request,id):
    current=request.user
    p=Notes.objects.get(id=id)
    p.delete()
    return redirect(fnotes)
@login_required(login_url='/login')
def fnotes(request):
    current=request.user
    try:
        return render(request, "mynotes/notes.html",{
            
            "p":Notes.objects.filter(owner=current).all(),
            "wishlist": True,
        })
    except Notes.DoesNotExist:
        return HttpResponse("No saved files in your notes!!!")
@login_required(login_url='/login')
def create_pwd(request):
    if request.method== "POST":
        pwd=Passwords() 
        pwd.Website=request.POST["website"]
        pwd.Username=request.POST["username"]
        psd=request.POST["password"]
        k=Fernet.generate_key()
        pwd.Key= k.decode("utf-8")
        pwd.Password=encryption(psd,pwd.Key).decode('utf-8')
        pwd.Owner= request.user
        pwd.save()
        return redirect(retrieve)
    else:
        return render(request,"mynotes/create_p.html",{
            "list":Notes.objects.all()
        })
@login_required(login_url='/login')
def rempassword(request,id):
    current=request.user
    p=Passwords.objects.get(id=id)
    p.delete()
    return redirect(retrieve)
@login_required(login_url='/login')
def retrieve(request):
    current=request.user
    try:
        return render(request, "mynotes/passwords.html",{
            
            "p":Passwords.objects.filter(Owner=current).all(),
        })
    except Notes.DoesNotExist:
        return HttpResponse("No saved files in your Passwords!!!")
@login_required(login_url='/login')
def decrypter(request,id):
    current = request.user
    p= Passwords.objects.get(id=id)
    g= p.Key
    h=p.Password
    t= decryption(h,g)
    try:
        return render(request, "mynotes/pwd.html",{
            "a":p,
            "g":t,
        })
    except Passwords.DoesNotExist:
        return HttpResponse("Unable to decrypt")
@login_required(login_url='/login')
def nlogin(request,id): 
    current=request.user
    global r
    r=random.randrange(1,10000,4)
    send_mail(
        'otp for your password access',
        str(r),
        settings.EMAIL_HOST_USER,
        [current.email, ],
    )
    return render(request,"mynotes/smail.html",{
        "id":id,
    }) 

@login_required (login_url = '/login')
def blogin(request,id):
    if request.method=='POST':
        passw=request.POST['fpass']
        if passw==str(r):
            return redirect(decrypter,id=id)
        else:
            return HttpResponse(r)
    return render(request,"mynotes/homepage.html") 
@login_required(login_url='/login')
def fshow(request,id):
    current=request.user
    return render(request, "mynotes/show.html",{
            "p":Notes.objects.filter(owner=current).all(),
            "pi":Notes.objects.filter(id=id),
            
    })
@login_required(login_url='/login')
def pshow(request,id):
    current=request.user
    return render(request, "mynotes/pshow.html",{
            "p":Passwords.objects.filter(Owner=current).all(),
            "pi":Passwords.objects.filter(id=id),     
    })
def delete_notes(request,id):
    current=request.user
    queryset= Notes.objects.get(id=id)
    if request.method=="POST":
        queryset.delete()
        return redirect('/notes')
    return render(request,'mynotes/delete.html')
def delete_password(request,id):
    current=request.user
    queryset= Passwords.objects.get(id=id)
    if request.method=="POST":
        queryset.delete()
        return redirect('/retrieve')
    return render(request,'mynotes/delete_pass.html')
