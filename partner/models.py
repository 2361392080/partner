from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    headimg = models.ImageField(upload_to='headimages/', default="default/TooLazyToChangeImage.png")
    personalSign = models.TextField(max_length=500, default="这个人太懒了，什么也没有留下")


class ActivitiesTest(models.Model):
    # initiator = models.ForeignKey(User, on_delete=models.CASCADE)
    initiator = models.CharField(max_length=32)
    title = models.CharField(max_length=32)
    nums = models.IntegerField(null = True)
    startTime = models.DateTimeField(null = True)
    endTime = models.DateTimeField(null = True)
    location = models.CharField(max_length=100, null = True)
    lat = models.CharField(max_length=20, null = True)
    lng = models.CharField(max_length=20, null = True)
    img = models.ImageField(upload_to='images/', blank = True, null = True)

class ActivityList(models.Model):
    initiator = models.OneToOneField(User, on_delete=models.CASCADE, related_name="initiator", default="")
    activities = models.ManyToManyField(ActivitiesTest, blank=True, related_name="activities")

    def __str__(self):
        return self.initiator.username

    def add_activity(self, activity):
        # add a new activity
        if not activity in self.activities.all():
            self.activities.add(activity)

    def remove_activity(self, activity):
        # remove a activity
        if activity in self.activities.all():
            self.activities.remove(activity)



class FriendList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
    friends = models.ManyToManyField(User, blank=True, related_name="friends")

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        # add a new friend
        if not account in self.friends.all():
            self.friends.add(account)

    def remove_friend(self, account):
        # remove a friend
        if account in self.friends.all():
            self.friends.remove(account)

    def unfriend(self, removee):
        # initiate the action of unfriending someone
        remover_friends_list = self  # person terminating the friendship ;(

        # remove friend from remover friend list
        remover_friends_list.remove_friend(removee)

        # remove friend from removee friend list
        friends_list = FriendList.objects.get(user=removee)
        friends_list.remove_friend(self.user)

    def is_mutual_friend(self, friend):
        # is this a friend?
        if friend in self.friends.all():
            return True
        return False


class FriendRequest(models.Model):
    """
    A friend request consists of two main parts:
        1. SENDER:
            - Person sending/initiating the friend request
        2. RECEIVER:
            - Person receiving the friend request
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    is_active = models.BooleanField(blank=True, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.username

    def accept(self):
        """
        Accept a friend request
        Update both SENDER and RECEIVER friend lists
        """
        receiver_friend_list = FriendList.objects.get(user=self.receiver)
        if receiver_friend_list:
            receiver_friend_list.add_friend(self.sender)
            self.is_active = False
            sender_friend_list = FriendList.objects.get(user=self.sender)
            if sender_friend_list:
                sender_friend_list.add_friend(self.receiver)
                self.save()

    def decline(self):
        """
        Decline a friend request
        It is "declined" by setting the "is_active" field to False
        """
        self.is_active = False
        self.save()

    def cancel(self):
        """
        Cancel a friend request
        It is "cancelled" by setting the "is_active" field to False
        This is only different with respect to "declining" through the notification that is generated
        """
        self.is_active = False
        self.save()
