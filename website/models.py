from django.db import models
import random

def random_reference():
    reference = []
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    # now I know my abc, come along and sing with me.
    for i in range(0, 9):
        reference.append(alphabet[random.randint(0, len(alphabet) - 1)])
        reference.append(str(random.randint(1, 9)))

    return ''.join(reference)

# Create your models here.
class Order(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.CharField(max_length=20)
    business_name = models.CharField(max_length=100, null=True)
    service = models.CharField(max_length=100)
    message = models.TextField()
    completed = models.BooleanField(default=False)
    in_progress = models.BooleanField(default=False)
    invoice = models.CharField(max_length=100, blank=True, null=True)
    reference = models.CharField(max_length=100, default=random_reference, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.CharField(max_length=20, default=False, null=False)
    subject = models.CharField(max_length=200)
    order_ref = models.CharField(max_length=25, default=None, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Reviews(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    main_content = models.TextField()
    rating = models.IntegerField()


class CustomerProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    business_name = models.CharField(max_length=150, blank=True)
