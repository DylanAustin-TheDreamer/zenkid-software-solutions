from django.contrib import admin
from .models import Order, Message, Reviews

# Register your models here.
admin.site.register(Order)
admin.site.register(Message)
admin.site.register(Reviews)