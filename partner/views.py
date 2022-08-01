import json
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import redirect, render

from partner.friend_request_status import FriendRequestStatus
from partner.models import User, ActivitiesTest, FriendList, ActivityList, FriendRequest
from django.contrib import messages
import hashlib


# Create your views here.
from partner.utils import get_friend_request_or_false


def activities(request):
    if request.session.get('is_login') == True:
        user = User.objects.get(id=request.session.get('uid'))
        activity = ActivitiesTest.objects.filter(initiator=user.username)
        # test
        now_time = datetime.now()
        activities_right_time = []
        for ac in activity:
            # activities_right_time.append(ac.startTime)
            ac.startTime = ac.startTime.replace(tzinfo=None)
            if ac.startTime > now_time:  # 这里是大于才可以
                activities_right_time.append(ac)

        context = {}
        context['now_time'] = now_time
        context['activity'] = activities_right_time  # 用户发起的活动
        # context['activity'] = activity
        # context['activities_right_time'] = activities_right_time

        # 好友列表
        try:
            friend_list = FriendList.objects.get(user=user)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=user)
            friend_list.save()
        friends = friend_list.friends.all()
        activities = []  # 好友发起的活动
        for friend in friends:
            friend_activities = ActivitiesTest.objects.filter(initiator=friend.username)
            for friend_activity in friend_activities:
                if friend_activity.startTime > now_time:
                    activities.append(friend_activity)
        context['activities'] = activities
        return render(request, 'activities.html', context)
    else:
        return render(request, 'activities.html')



def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, '两次密码输入不一致')
        elif User.objects.filter(username=username):
            messages.error(request, '该用户名已被注册')
        elif username == ' ':
            messages.error(request, '用户名不能为空')
        else:
            md5 = hashlib.md5()
            md5.update(password1.encode('utf-8'))
            password1 = md5.hexdigest()
            user = User.objects.create(username=username, password=password1)
            user.save()
            messages.success(request, '注册成功')
            return redirect('/login')
    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        password = md5.hexdigest()
        if User.objects.filter(username=username):
            if User.objects.filter(username=username)[0].password == password:
                messages.success(request, '登录成功！')
                request.session["is_login"] = True
                request.session["username"] = username
                request.session["uid"] = User.objects.get(username=username).id
                return redirect('/home')
            else:
                messages.error(request, '密码错误，请重新登录')
        else:
            messages.error(request, '用户不存在，请重新登录')
    return render(request, 'login.html')


def logout(request):
    request.session.flush()
    return redirect('/')


def home(request):
    return render(request, 'home.html')


def create(request):
    if request.method == 'POST':
        # initiator = User.objects.get('username')
        initiator = User.objects.get(id=request.session.get('uid')).username
        title = request.POST.get('activitiesName')
        nums = request.POST.get('activitiesNumP')
        startTime = request.POST.get('startTime')
        endTime = request.POST.get('endTime')
        img = request.FILES['img']
        location = request.POST.get('activitiesLocation')
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        if startTime>endTime:
            messages.error(request, '日期设置错误')
        else :
            activity = ActivitiesTest.objects.create(initiator=initiator, title=title, nums=nums, startTime=startTime, endTime=endTime, location=location, img=img, lat=lat, lng=lng)
            activity.save()
            messages.success(request, '创建成功')
            return redirect('/activities/')
    return render(request, 'create_activities.html')




def details(request, id):
    context = {}
    activity = ActivitiesTest.objects.get(id=id)  # 本页活动
    initiator = User.objects.get(username=activity.initiator)  # 活动发起人
    user = User.objects.get(id=request.session.get('uid'))  # 用户本人
    context['activity'] = activity
    context['initiator'] = initiator
    context['user'] = user

    # 活动功能
    if activity:
        try:
            activities_list = ActivityList.objects.get(initiator=user)
        except ActivityList.DoesNotExist:
            activities_list = ActivityList(initiator=user)
            activities_list.save()
        activities = activities_list.activities.all()

        # 初始化
        is_in = False
        is_myActivity = True

        if user != initiator:
            is_myActivity = False
            for activity2 in activities:
                if activity2 == activity:
                    is_in = True

        nums = 1  # 参与该活动的人数
        query = ActivityList.objects.all()
        participants = []
        for person in range(0, query.count()):
            testuser = User.objects.get(username=query[person])
            oneactivities_list = ActivityList.objects.get(initiator=testuser)
            oneactivities = oneactivities_list.activities.all()
            for oneactivity in oneactivities:
                if oneactivity == activity:
                    nums = nums + 1
                    participants.append(testuser)

    context['participants'] = participants
    context['nums'] = nums
    context['is_in'] = is_in
    context['is_myActivity'] = is_myActivity
    return render(request, 'details.html', context)


def send_friend_request(request):
    user = User.objects.get(id=request.session.get('uid'))
    payload = {}
    if request.method == "POST" and request.session.get('is_login') == True:
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            receiver = User.objects.get(pk=user_id)
            try:
                # Get any friend requests (active and not-active)
                friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver)
                # find if any of them are active
                try:
                    for request in friend_requests:
                        if request.is_active:
                            raise Exception("你已经发送过好友申请")
                    # if none are active, then create a new friend request
                    friend_request = FriendRequest(sender=user, receiver=receiver)
                    friend_request.save()
                    payload['response'] = "已发送好友申请"
                except Exception as e:
                    payload['response'] = str(e)
            except FriendRequest.DoesNotExist:
                # There are no friend requests so create one
                friend_request = FriendRequest(sender=user, receiver=receiver)
                friend_request.save()
                payload['response'] = "已发送好友申请"

            if payload['response'] == None:
                payload['response'] = "Something went wrong"
        else:
            payload['response'] = "无法发送好友申请"
    else:
        payload['response'] = "请先登录账号"
    return HttpResponse(json.dumps(payload), content_type="application/json")


def accept_friend_request(request, *arg, **kwargs):
    user = User.objects.get(id=request.session.get('uid'))
    payload = {}
    if request.method == "GET" and request.session.get('is_login') == True:
        friend_request_id = kwargs.get("friend_request_id")
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            # confirm that is the correct request
            if friend_request.receiver == user:
                if friend_request:
                    # found the request. Not accept it.
                    friend_request.accept()
                    payload['response'] = "已接受好友申请"
                else:
                    payload['response'] = "Something went wrong"
            else:
                payload['response'] = "That is not your request to accept"
        else:
            payload['response'] = "无法接受该好友申请"
    else:
        payload['response'] = "请先登录账号"
    return HttpResponse(json.dumps(payload), content_type="application/json")


def decline_friend_request(request, *args, **kwargs):
    user = User.objects.get(id=request.session.get('uid'))
    payload = {}
    if request.method == "GET" and request.session.get('is_login') == True:
        friend_request_id = kwargs.get("friend_request_id")
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            # confirm that it is the correct request
            if friend_request.receiver == user:
                if friend_request:
                    # found the request. Now decline it
                    friend_request.decline()
                    payload['response'] = "已拒绝好友申请"
                else:
                    payload['response'] = "Something went wrong"
            else:
                payload['response'] = "That is not your friend request to decline"
        else:
            payload['response'] = "无法拒绝该好友申请"
    else:
        payload['response'] = "请先登录账号"
    return HttpResponse(json.dumps(payload), content_type="application/json")


def remove_friend(request, *args, **kwargs):
    user = User.objects.get(id=request.session.get('uid'))
    payload = {}
    if request.method == "POST" and request.session.get('is_login') == True:
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            try:
                removee = User.objects.get(pk=user_id)
                friend_list = FriendList.objects.get(user=user)
                friend_list.unfriend(removee)
                payload['response'] = "已删除该好友"
            except Exception as e:
                payload['response'] = f"Something went wrong: {str(e)}"
        else:
            payload['response'] = "无法删除该好友"
    else:
        payload['response'] = "请先登录账号"
    return HttpResponse(json.dumps(payload), content_type="application/json")


def cancel_friend_request(request, *arg, **kwargs):
    user = User.objects.get(id=request.session.get('uid'))
    payload = {}
    if request.method == "POST" and request.session.get('is_login') == True:
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            receiver = User.objects.get(pk=user_id)
            try:
                friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver, is_active=True)
            except Exception as e:
                payload['response'] = "好友申请不存在"
            # There should only ever be a single active friend request at any given time. Cancel them all just in case
            if len(friend_requests) > 1: #基本不会发生
                for req in friend_requests:
                    req.cancel()
                payload['response'] = "已取消好友申请"
            else:
                # found the request. Now cancel it
                friend_requests.first().cancel()
                payload['response'] = "已取消好友申请"
        else:
            payload['response'] = "无法取消好友申请"
    else:
        payload['response'] = "请先登录账号"
    return HttpResponse(json.dumps(payload), content_type="application/json")


def homepage(request):
    # if request.method == 'POST':
    #     user = User.objects.get(username=request.session.get('username'))
    #     if request.FILES['headimg']!=None:
    #         headimg = request.FILES['headimg']
    #         user.headimg = headimg
    #     if request.request.POST.get('userName')!=None:
    #         username = request.POST.get('userName')
    #         personalSign = request.POST.get('personalSign')
    #         user.username = username
    #         user.personalSign = personalSign
    #     user.save()
    if request.session.get('is_login') == True:
        home = User.objects.get(id=request.session.get('uid'))
        activities1 = ActivitiesTest.objects.filter(initiator=home.username)
        now_time = datetime.now()
        length = activities1.count()
        # 好友列表
        try:
            friend_list = FriendList.objects.get(user=home)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=home)
            friend_list.save()
        friends = friend_list.friends.all()
        # 好友申请
        friend_requests = None
        try:
            friend_requests = FriendRequest.objects.filter(receiver=home, is_active=True)
        except:
            pass

        # 参与的活动列表
        try:
            activities_list = ActivityList.objects.get(initiator=home)
        except ActivityList.DoesNotExist:
            activities_list = ActivityList(initiator=home)
            activities_list.save()
        activities2 = activities_list.activities.all()

        return render(request, 'personalpage.html',
                      {'home': home, 'activities1': activities1, 'length': length, 'friends': friends,
                       'friend_requests': friend_requests, 'activities2': activities2, 'now_time': now_time})
    else:
        messages.error(request, '请先登录账号')
        return render(request, 'home.html')


def friendpage(request, id):
    # user_id = kwargs.get("user_id")
    # try:
    #     user = User.objects.get(id=request.session.get('uid'))
    # except:
    #     HttpResponse("出错了")
    user = User.objects.get(id=request.session.get('uid'))
    account = User.objects.get(id=id)
    activities1 = ActivitiesTest.objects.filter(initiator=account.username)
    length = activities1.count()
    now_time = datetime.now()
    context = {}
    context['friend'] = account
    context['activities1'] = activities1
    context['length'] = length
    context['now_time'] = now_time
    # 好友功能
    if account:
        try:
            friend_list = FriendList.objects.get(user=account)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=account)
            friend_list.save()
        friends = friend_list.friends.all()

        # "初始化"
        is_self = True
        is_friend = False
        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

        # 好友申请
        friend_request = None
        try:
            friend_request = FriendRequest.objects.get(sender=account, receiver=user, is_active=True)
        except:
            pass

        if user != account:
            is_self = False
            if friends.filter(pk=user.id):
                is_friend = True
            else:
                is_friend = False
                # case1: request has beem sent from them to you:
                if get_friend_request_or_false(sender=account, receiver=user) != False:
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                    context['pending_friend_request_id'] = get_friend_request_or_false(sender=account, receiver=user).id
                # case2: request has been sent from you to them:
                elif get_friend_request_or_false(sender=user, receiver=account) != False:
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
                # case3: no requests has been sent:
                else:
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
        # 参与的活动列表
        try:
            activities_list = ActivityList.objects.get(initiator=account)
        except ActivityList.DoesNotExist:
            activities_list = ActivityList(initiator=account)
            activities_list.save()
        activities2 = activities_list.activities.all()
        context['activities2'] = activities2

        context['is_self'] = is_self
        context['is_friend'] = is_friend
        context['request_sent'] = request_sent
        context['friend_request'] = friend_request

        return render(request, 'friendpage.html', context)


def changeHeadimg(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.session.get('uid'))
        headimg = request.FILES['headimg']
        user.headimg = headimg
        user.save()
    return redirect('/home/')


def changeDetails(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.session.get('uid'))
        username2 = request.POST.get('userName2')
        activities1 = ActivitiesTest.objects.filter(initiator=username2)
        username = request.POST.get('userName')
        request.session["username"] = username
        personalSign = request.POST.get('personalSign')
        for p in activities1:
            p.initiator = username
            p.save()
        user.username = username
        user.personalSign = personalSign
        user.save()
    return redirect('/homepage/')


def searchAccount(request):
    context = {}
    if request.method == 'GET':
        search_query = request.GET.get('q')
        if len(search_query) > 0:
            search_results = User.objects.filter(username__icontains=search_query)
            user = User.objects.get(id=request.session.get('uid'))
            friend_list = FriendList.objects.get(user=user)
            friends = friend_list.friends.all()
            accounts = []  # [(account1, True), {account2, False}, ...]
            for account in search_results:
                t = False
                for friend in friends:
                    if account == friend:
                        t = True
                accounts.append((account, t))
            context['accounts'] = accounts
            context['search_query'] = search_query
            context['user'] = user
    return render(request, 'searchResults.html', context)