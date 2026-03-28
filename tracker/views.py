from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserProfile, Food, Activity, DailyLog, FoodEntry, ActivityEntry
from .serializers import (
    UserProfileSerializer, FoodSerializer, ActivitySerializer,
    DailyLogSerializer, FoodEntrySerializer, ActivityEntrySerializer
)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class FoodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        food_group = self.request.query_params.get('food_group')
        if search:
            qs = qs.filter(name__icontains=search)
        if food_group:
            qs = qs.filter(food_group__iexact=food_group)
        return qs.order_by('name')[:50]


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(specific_motion__icontains=search)
        return qs.order_by('activity_name', 'specific_motion')[:50]


@api_view(['GET'])
def daily_log_detail(request, user_id, log_date):
    user = get_object_or_404(UserProfile, pk=user_id)
    try:
        log = DailyLog.objects.get(user=user, date=log_date)
    except DailyLog.DoesNotExist:
        return Response({'detail': 'No data for this date.'}, status=404)
    serializer = DailyLogSerializer(log)
    return Response(serializer.data)


@api_view(['GET'])
def user_all_logs(request, user_id):
    user = get_object_or_404(UserProfile, pk=user_id)
    logs = DailyLog.objects.filter(user=user).order_by('-date')
    serializer = DailyLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_food_entry(request):
    user_id = request.data.get('user_id')
    log_date = request.data.get('date')
    food_id = request.data.get('food_id')
    servings = float(request.data.get('servings', 1))
    meal_type = request.data.get('meal_type', 'lunch')

    user = get_object_or_404(UserProfile, pk=user_id)
    food = get_object_or_404(Food, pk=food_id)
    daily_log, _ = DailyLog.objects.get_or_create(user=user, date=log_date)

    entry = FoodEntry.objects.create(
        daily_log=daily_log, food=food, servings=servings, meal_type=meal_type
    )
    return Response(FoodEntrySerializer(entry).data, status=201)


@api_view(['POST'])
def add_activity_entry(request):
    user_id = request.data.get('user_id')
    log_date = request.data.get('date')
    activity_id = request.data.get('activity_id')
    duration_minutes = float(request.data.get('duration_minutes', 30))

    user = get_object_or_404(UserProfile, pk=user_id)
    activity = get_object_or_404(Activity, pk=activity_id)
    daily_log, _ = DailyLog.objects.get_or_create(user=user, date=log_date)

    entry = ActivityEntry.objects.create(
        daily_log=daily_log, activity=activity, duration_minutes=duration_minutes
    )
    return Response(ActivityEntrySerializer(entry).data, status=201)


@api_view(['DELETE'])
def delete_food_entry(request, entry_id):
    entry = get_object_or_404(FoodEntry, pk=entry_id)
    entry.delete()
    return Response(status=204)


@api_view(['DELETE'])
def delete_activity_entry(request, entry_id):
    entry = get_object_or_404(ActivityEntry, pk=entry_id)
    entry.delete()
    return Response(status=204)


@api_view(['GET'])
def food_groups(request):
    groups = Food.objects.values_list('food_group', flat=True).distinct().order_by('food_group')
    return Response(list(groups))


@api_view(['GET'])
def activity_names(request):
    names = Activity.objects.values_list('activity_name', flat=True).distinct().order_by('activity_name')
    return Response(list(names))


# ==================== Template Views ====================

def signup_view(request):
    if request.method == 'POST':
        UserProfile.objects.create(
            name=request.POST['name'],
            weight=float(request.POST['weight']),
            height=float(request.POST['height']),
            age=int(request.POST['age']),
            sex=request.POST['sex'],
        )
        return redirect('user_list')
    return render(request, 'signup.html')


def user_list_view(request):
    users = UserProfile.objects.all()
    food_groups_list = Food.objects.values_list('food_group', flat=True).distinct().order_by('food_group')
    activity_names_list = Activity.objects.values_list('activity_name', flat=True).distinct().order_by('activity_name')
    today = date.today()
    min_date = today - timedelta(days=30)
    context = {
        'users': users,
        'food_groups': food_groups_list,
        'activity_names': activity_names_list,
        'today': today.isoformat(),
        'min_date': min_date.isoformat(),
    }
    return render(request, 'user_list.html', context)


def user_data_view(request, user_id):
    user = get_object_or_404(UserProfile, pk=user_id)
    logs = DailyLog.objects.filter(user=user).order_by('-date')
    food_groups_list = Food.objects.values_list('food_group', flat=True).distinct().order_by('food_group')
    activity_names_list = Activity.objects.values_list('activity_name', flat=True).distinct().order_by('activity_name')
    today = date.today()
    min_date = today - timedelta(days=30)

    log_data = []
    for log in logs:
        log_data.append({
            'date': log.date,
            'bmr': log.bmr(),
            'calories_in': log.total_calories_in(),
            'calories_out': log.total_calories_out(),
            'net_calories': log.net_calories(),
        })

    context = {
        'user': user,
        'logs': log_data,
        'food_groups': food_groups_list,
        'activity_names': activity_names_list,
        'today': today.isoformat(),
        'min_date': min_date.isoformat(),
    }
    return render(request, 'user_data.html', context)


def user_details_view(request, user_id):
    user = get_object_or_404(UserProfile, pk=user_id)
    selected_date = request.GET.get('date', date.today().isoformat())
    food_groups_list = Food.objects.values_list('food_group', flat=True).distinct().order_by('food_group')
    activity_names_list = Activity.objects.values_list('activity_name', flat=True).distinct().order_by('activity_name')
    today = date.today()
    min_date = today - timedelta(days=30)

    try:
        log = DailyLog.objects.get(user=user, date=selected_date)
        food_entries = log.food_entries.select_related('food').all()
        activity_entries = log.activity_entries.select_related('activity').all()
        total_in = log.total_calories_in()
        total_out = log.total_calories_out()
        bmr = log.bmr()
        net = log.net_calories()
    except DailyLog.DoesNotExist:
        food_entries = []
        activity_entries = []
        total_in = 0
        total_out = 0
        bmr = user.bmr()
        net = 0 - bmr

    context = {
        'user': user,
        'selected_date': selected_date,
        'food_entries': food_entries,
        'activity_entries': activity_entries,
        'total_in': total_in,
        'total_out': total_out,
        'bmr': bmr,
        'net': round(net, 2),
        'food_groups': food_groups_list,
        'activity_names': activity_names_list,
        'today': today.isoformat(),
        'min_date': min_date.isoformat(),
    }
    return render(request, 'user_details.html', context)


def delete_user_view(request, user_id):
    user = get_object_or_404(UserProfile, pk=user_id)
    user.delete()
    return redirect('user_list')
