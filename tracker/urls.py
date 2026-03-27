from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserProfileViewSet)
router.register(r'foods', views.FoodViewSet)
router.register(r'activities', views.ActivityViewSet)

# API-only URLs (included under /api/)
api_urlpatterns = [
    path('', include(router.urls)),
    path('daily-log/<int:user_id>/<str:log_date>/', views.daily_log_detail, name='daily_log_detail'),
    path('daily-log/<int:user_id>/', views.user_all_logs, name='user_all_logs'),
    path('add-food-entry/', views.add_food_entry, name='add_food_entry'),
    path('add-activity-entry/', views.add_activity_entry, name='add_activity_entry'),
    path('food-groups/', views.food_groups, name='food_groups'),
    path('activity-names/', views.activity_names, name='activity_names'),
]

# Template views (included under /)
template_urlpatterns = [
    path('', views.signup_view, name='signup'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/<int:user_id>/data/', views.user_data_view, name='user_data'),
    path('users/<int:user_id>/details/', views.user_details_view, name='user_details'),
    path('users/<int:user_id>/delete/', views.delete_user_view, name='delete_user'),
]
