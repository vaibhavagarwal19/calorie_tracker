from rest_framework import serializers
from .models import UserProfile, Food, Activity, DailyLog, FoodEntry, ActivityEntry


class UserProfileSerializer(serializers.ModelSerializer):
    bmr = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'weight', 'height', 'age', 'sex', 'bmr']

    def get_bmr(self, obj):
        return obj.bmr()


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'


class FoodEntrySerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source='food.name', read_only=True)
    food_group = serializers.CharField(source='food.food_group', read_only=True)
    calories_consumed = serializers.SerializerMethodField()

    class Meta:
        model = FoodEntry
        fields = ['id', 'food', 'food_name', 'food_group', 'servings', 'meal_type', 'calories_consumed']

    def get_calories_consumed(self, obj):
        return obj.calories_consumed()


class ActivityEntrySerializer(serializers.ModelSerializer):
    activity_name = serializers.CharField(source='activity.activity_name', read_only=True)
    specific_motion = serializers.CharField(source='activity.specific_motion', read_only=True)
    met_value = serializers.FloatField(source='activity.met_value', read_only=True)
    calories_burned = serializers.SerializerMethodField()

    class Meta:
        model = ActivityEntry
        fields = ['id', 'activity', 'activity_name', 'specific_motion', 'met_value', 'duration_minutes', 'calories_burned']

    def get_calories_burned(self, obj):
        return obj.calories_burned()


class DailyLogSerializer(serializers.ModelSerializer):
    food_entries = FoodEntrySerializer(many=True, read_only=True)
    activity_entries = ActivityEntrySerializer(many=True, read_only=True)
    total_calories_in = serializers.SerializerMethodField()
    total_calories_out = serializers.SerializerMethodField()
    bmr = serializers.SerializerMethodField()
    net_calories = serializers.SerializerMethodField()

    class Meta:
        model = DailyLog
        fields = ['id', 'user', 'date', 'food_entries', 'activity_entries',
                  'total_calories_in', 'total_calories_out', 'bmr', 'net_calories']

    def get_total_calories_in(self, obj):
        return obj.total_calories_in()

    def get_total_calories_out(self, obj):
        return obj.total_calories_out()

    def get_bmr(self, obj):
        return obj.bmr()

    def get_net_calories(self, obj):
        return obj.net_calories()
