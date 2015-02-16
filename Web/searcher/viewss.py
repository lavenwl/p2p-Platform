# coding=utf-8

from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from searcher.forms import TRegForm, LoginForm
from searcher.models import ThirdLogin
from searcher.models import UserInformation
from searcher.inner_views import user_auth, refresh_header
from django.core.urlresolvers import reverse
import httplib
import json
from string import join
import hashlib

__author__ = 'laven'


def qq_is_first(request):
    resp = 0
    if request.method == 'POST':
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        u_ajax = request.POST.get('name', None)
        if u_ajax:
            response['Content-Type'] = "application/json"
            r_u = request.POST.get('param', None)
            u = User.objects.filter(username=r_u)
            if u.exists():
                response.write('{"info": "用户已存在","status": "n"}')  # 用户已存在
                return response
            else:
                response.write('{"info": "用户可以使用","status": "y"}')
                return response
        openid = request.POST.get('openid', '')
        accesstoken = request.POST.get('accessToken', '')
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        nickname = request.POST.get('nickname', '')
        url = request.POST.get('url', '')
        if openid != "" and accesstoken != "" and username == "" and email == "":
            tl = ThirdLogin.objects.filter(openId=openid)
            if tl.exists():
                if tl[0].qqFlag == "1":
                    u = User.objects.filter(id=(UserInformation.objects.filter(id=tl[0].userInfo_id)[0].user_id))
                    username = u[0].username
                    resp = 1
                else:
                    resp = 0
            else:
                resp = 0
        elif username != "" and email != "" and openid != "" and accesstoken != "":
            u = User.objects.filter(username=username)
            if u.exists():
                resp = 2
            else:
                new_user = User.objects.create_user(username=username, password="openid", email=email)
                new_user.save()
                u = UserInformation(user=new_user, photo_url=url)
                u.save()
                tl = ThirdLogin(openId=openid, accessToken=accesstoken, qqFlag=0)
                tl.userInfo = u
                tl.qqFlag = 1
                tl.save()
                resp = 1
        else:
            print "qq something unhopeful happend!"

        if resp == 1:
            user = User.objects.get(username=username)
            user.is_active = True
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth.login(request, user)
            if user is not None and user.is_active:
                auth.login(request, user)
            return HttpResponseRedirect('/')
        else:
            error = ''
            if resp == 2:
                error = "please input correctly!"
            form = TRegForm({'username': nickname, 'openid': openid, 'accessToken': accesstoken, 'url': url})
            return render_to_response("register.html", {'form': form, 'error': error, 'openid': openid}, context_instance=RequestContext(request))
    else:
        print "qq something unhopeful happend2!"
        # nickname = 'testqq'
        # openid = 'testqq_openid'
        # accesstoken = 'testqq_accessToken'
        # url = 'testqq_url'
        # form = TRegForm({'username': nickname, 'openid': openid, 'accessToken': accesstoken, 'url': url})
        # return render_to_response("register.html", {'form': form, 'openid': openid}, context_instance=RequestContext(request))

def wb_is_first(request):
    resp = 0
    if request.method == 'POST':
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        wbid = request.POST.get('wbid', '')
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        nickname = request.POST.get('nickname', '')
        url = request.POST.get('url', '')
        if wbid != "" and username == "" and email == "":
            tl = ThirdLogin.objects.filter(wbId=wbid)
            if tl.exists():
                if tl[0].wbFlag == "1":
                    u = User.objects.filter(id=(UserInformation.objects.filter(id=tl[0].userInfo_id)[0].user_id))
                    username = u[0].username
                    password = "wbid"
                    resp = 1
                else:
                    resp = 0
            else:
                resp = 0
        elif username != "" and email != "":
            u = User.objects.filter(username=username)
            if u.exists():
                resp = 2
            else:
                new_user = User.objects.create_user(username=username, password="wbid", email=email)
                new_user.save()
                u = UserInformation(user=new_user, photo_url=url)
                u.save()
                tl = ThirdLogin(wbId=wbid, wbFlag=0)
                tl.userInfo = u
                tl.wbFlag = 1
                tl.save()
                resp = 1
        else:
            print " wb something unhopeful happend!"

        if resp == 1:
            user = User.objects.get(username=username)
            user.is_active = True
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth.login(request, user)
            if user is not None and user.is_active:
                auth.login(request, user)
            return HttpResponseRedirect('/')
        else:
            error = ''
            if resp == 2:
                error = "please input correctly!"
            form = TRegForm({'username': nickname, 'wbid': wbid, 'url': url})
            return render_to_response("register.html", {'form': form, 'error': error, 'wbid': wbid}, context_instance=RequestContext(request))
    else:
        print " wb something unhopeful happend2!"
        # nickname = 'testwb'
        # wbid = 'testwb_id'
        # url = 'testwb_url'
        # form = TRegForm({'username': nickname, 'wbid': wbid, 'url': url})
        # return render_to_response("register.html", {'form': form}, context_instance=RequestContext(request))

def wx_is_first(request):
    resp = 0
    if request.method == 'GET':
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        code = request.GET.get("code")
        data = initData(code)
        wxopenid = data['openid']
        wxaccesstoken = data['access_token']
        info = initInfo(wxopenid, wxaccesstoken)
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        nickname = info['nickname']
        url = info['headimgurl']
        if wxopenid != "" and wxaccesstoken != "" and username == "" and email == "":
            tl = ThirdLogin.objects.filter(wxopenId=wxopenid)
            if tl.exists():
                if tl[0].wxFlag == "1":
                    u = User.objects.filter(id=(UserInformation.objects.filter(id=tl[0].userInfo_id)[0].user_id))
                    username = u[0].username
                    resp = 1
                else:
                    resp = 0
            else:
                resp = 0
        else:
            print "wx something unhopeful happend!"

        if resp == 1:
            user = User.objects.get(username=username)
            user.is_active = True
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth.login(request, user)
            if user is not None and user.is_active:
                auth.login(request, user)
            return HttpResponseRedirect('/')
        else:
            error = ''
            if resp == 2:
                error = "please input correctly!"
            form = TRegForm({'username': nickname, 'openid': wxopenid, 'accessToken': wxaccesstoken, 'url': url})
            return render_to_response("register.html", {'form': form, 'error': error, 'wxopenid': wxopenid}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        wxopenid = request.POST.get('openid', '')
        wxaccesstoken = request.POST.get('accessToken', '')
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        nickname = request.POST.get('nickname', '')
        url = request.POST.get('url', '')
        if username != "" and email != "" and wxopenid != "" and wxaccesstoken != "":
            u = User.objects.filter(username=username)
            if u.exists():
                resp = 2
            else:
                new_user = User.objects.create_user(username=username, password="wxopenid", email=email)
                new_user.save()
                u = UserInformation(user=new_user, photo_url=url)
                u.save()
                tl = ThirdLogin(wxopenId=wxopenid, wxaccessToken=wxaccesstoken, wxFlag=0)
                tl.userInfo = u
                tl.wxFlag = 1
                tl.save()
                resp = 1
        else:
            print "wx something unhopeful happend!"

        if resp == 1:
            user = User.objects.get(username=username)
            user.is_active = True
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth.login(request, user)
            if user is not None and user.is_active:
                auth.login(request, user)
            return HttpResponseRedirect('/')
        else:
            error = ''
            if resp == 2:
                error = "please input correctly!"
            form = TRegForm({'username': nickname, 'openid': wxopenid, 'accessToken': wxaccesstoken, 'url': url})
            return render_to_response("register.html", {'form': form, 'error': error, 'wxopenid': wxopenid}, context_instance=RequestContext(request))

    else:
        print "wx something unhopeful happend2!"

def initData(code):
    httpClient = None
    try:
        httpClient = httplib.HTTPSConnection('api.weixin.qq.com', timeout=30)
        httpClient.request('GET', '/sns/oauth2/access_token?appid=wx5705d3f981443fb8&secret=46f37dba35e5b57b5b98cc2437296f6b&code='+code+'&grant_type=authorization_code')
        response = httpClient.getresponse()
        if response.status == 200 and response.reason == 'OK':
            url = response.read()
            print "url:|||:", url
            time = json.loads(url)
        return time
    except Exception, e:
        print "httpClient to 'api.weixin.qq.com' initData get an error!", e
    finally:
        if httpClient:
            httpClient.close()

def initInfo(openid, access_token):
    httpClient = None
    try:
        httpClient = httplib.HTTPSConnection('api.weixin.qq.com', timeout=30)
        httpClient.request('GET', '/sns/userinfo?access_token='+access_token+'&openid='+openid)
        response = httpClient.getresponse()
        if response.status == 200 and response.reason == 'OK':
            url = response.read()
            print "url:|||:", url
            time = json.loads(url)
        return time
    except Exception, e:
        print "httpClient to 'api.weixin.qq.com' initInfo get an error!", e
    finally:
        if httpClient:
            httpClient.close()

def wxcheck(request):
    print "get a request!"
    response = HttpResponse()

    response['Content-Type'] = "text/javascript"
    if request.method == "GET":
        print "get a get request!"
        signature = request.GET.get('signature', None)
        timestamp = request.GET.get('timestamp', None)
        nonce = request.GET.get('nonce', None)
        echostr = request.GET.get('echostr', None)
        li = ['999ddbid', timestamp, nonce]
        while lexicographically_next_permutation(li):
            1
        if timestamp != None and nonce != None and echostr != None and signature != None:
            li.reverse()
            str = join(li).replace(' ', '')
            str2 = hashlib.sha1(str).hexdigest()
            if str2 == signature:
                print "wxcheck is okokokokokokokok"
                response.write(echostr)  # 用户已存在
        else:
            response.write("get none")

        #return response
    else:
        print "wxcheck get a post request"
        print "wxcheck use post method:"+request.method
        response.write("post none")
    return response

def lexicographically_next_permutation(a):
    i = len(a) - 2
    while not (i < 0 or a[i] < a[i+1]):
        i -= 1
    if i < 0:
        return False
    j = len(a) - 1
    while not (a[j] > a[i]):
        j -= 1
    a[i], a[j] = a[j], a[i]
    a[i+1:] = reversed(a[i+1:])
    return True


def wx_binding(request):
    print "get a request in wx_binding"
    print "method is :"+request.method
    if request.method == 'POST':
        username = request.REQUEST.get('log_un', None)
        pwd = request.REQUEST.get('log_pwd', None)
        code = request.REQUEST.get('log_code', None)
        if username is None:
            form = LoginForm(request.POST)
            print(form)
            if form.is_valid():
                cd = form.clean()
                print(cd)
                username = cd['username']
                pwd = cd['password']
                code = cd['vcode']
                i = user_auth(request, username, pwd, code)
                if i == 1:
                    a = request.REQUEST.get('next', None)
                    if a:
                        return HttpResponseRedirect(a)
                    else:
                        return HttpResponseRedirect(reverse('searchindex'))
                else:
                    form.valiatetype(i)
                    return render_to_response('login.html', {'form': form, },
                                              context_instance=RequestContext(request))
            else:
                return render_to_response('login.html', {'form': form, },
                                          context_instance=RequestContext(request))

        return refresh_header(request, user_auth(request, username, pwd, code))
    else:
        form = LoginForm()
        next = request.GET.get('next', None)
        return render_to_response('login.html', {'form': form, 'next': next},
                                  context_instance=RequestContext(request))
