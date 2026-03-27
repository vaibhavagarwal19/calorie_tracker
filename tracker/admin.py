from django.contrib import admin
from .models import UserProfile, Food, Activity, DailyLog, FoodEntry, ActivityEntry

admin.site.register(UserProfile)
admin.site.register(Food)
admin.site.register(Activity)
admin.site.register(DailyLog)
admin.site.register(FoodEntry)
admin.site.register(ActivityEntry)
