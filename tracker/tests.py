from django.test import TestCase, Client
from .models import UserProfile, Food, Activity, DailyLog, FoodEntry, ActivityEntry


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            name='Test User', weight=70, height=175, age=25, sex='male'
        )

    def test_bmr_male(self):
        expected = round(66.4730 + (13.7516 * 70) + (5.0033 * 175) - (6.7550 * 25), 3)
        self.assertEqual(self.user.bmr(), expected)

    def test_bmr_female(self):
        user = UserProfile.objects.create(
            name='Female User', weight=60, height=165, age=30, sex='female'
        )
        expected = round(655.0955 + (9.5634 * 60) + (1.8496 * 165) - (4.6756 * 30), 3)
        self.assertEqual(user.bmr(), expected)

    def test_str(self):
        self.assertEqual(str(self.user), 'Test User')


class FoodEntryModelTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            name='Test User', weight=70, height=175, age=25, sex='male'
        )
        self.food = Food.objects.create(
            food_id=1, name='Apple', food_group='Fruits', calories=95
        )
        self.log = DailyLog.objects.create(user=self.user, date='2026-03-29')

    def test_calories_consumed(self):
        entry = FoodEntry.objects.create(
            daily_log=self.log, food=self.food, servings=2, meal_type='snack'
        )
        self.assertEqual(entry.calories_consumed(), 190.0)

    def test_daily_log_total_calories_in(self):
        FoodEntry.objects.create(daily_log=self.log, food=self.food, servings=1, meal_type='breakfast')
        FoodEntry.objects.create(daily_log=self.log, food=self.food, servings=2, meal_type='lunch')
        self.assertEqual(self.log.total_calories_in(), 285.0)


class ActivityEntryModelTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            name='Test User', weight=70, height=175, age=25, sex='male'
        )
        self.activity = Activity.objects.create(
            activity_name='Running', specific_motion='Jogging', met_value=7.0
        )
        self.log = DailyLog.objects.create(user=self.user, date='2026-03-29')

    def test_calories_burned(self):
        entry = ActivityEntry.objects.create(
            daily_log=self.log, activity=self.activity, duration_minutes=60
        )
        # MET * weight * (duration / 60) = 7.0 * 70 * 1 = 490
        self.assertEqual(entry.calories_burned(), 490.0)

    def test_daily_log_net_calories(self):
        food = Food.objects.create(food_id=1, name='Apple', food_group='Fruits', calories=500)
        FoodEntry.objects.create(daily_log=self.log, food=food, servings=1, meal_type='lunch')
        ActivityEntry.objects.create(daily_log=self.log, activity=self.activity, duration_minutes=30)
        # net = calories_in - bmr - calories_out
        # net = 500 - user.bmr() - (7.0 * 70 * 0.5)
        expected = round(500 - self.user.bmr() - 245, 2)
        self.assertEqual(self.log.net_calories(), expected)


class DailyLogModelTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            name='Test User', weight=70, height=175, age=25, sex='male'
        )

    def test_unique_together(self):
        DailyLog.objects.create(user=self.user, date='2026-03-29')
        with self.assertRaises(Exception):
            DailyLog.objects.create(user=self.user, date='2026-03-29')

    def test_empty_log_totals(self):
        log = DailyLog.objects.create(user=self.user, date='2026-03-29')
        self.assertEqual(log.total_calories_in(), 0)
        self.assertEqual(log.total_calories_out(), 0)


class TemplateViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserProfile.objects.create(
            name='Test User', weight=70, height=175, age=25, sex='male'
        )

    def test_signup_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_user_list_page(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)

    def test_user_data_page(self):
        response = self.client.get(f'/users/{self.user.id}/data/')
        self.assertEqual(response.status_code, 200)

    def test_user_details_page(self):
        response = self.client.get(f'/users/{self.user.id}/details/')
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user(self):
        response = self.client.post('/', {
            'name': 'New User', 'weight': 65, 'height': 170, 'age': 30, 'sex': 'female'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserProfile.objects.filter(name='New User').exists())


class APIEndpointsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserProfile.objects.create(
            name='Test User', weight=70, height=175, age=25, sex='male'
        )
        self.food = Food.objects.create(
            food_id=1, name='Apple', food_group='Fruits', calories=95
        )
        self.activity = Activity.objects.create(
            activity_name='Running', specific_motion='Jogging', met_value=7.0
        )

    def test_list_users(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 200)

    def test_search_foods(self):
        response = self.client.get('/api/foods/?search=Apple')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_search_activities(self):
        response = self.client.get('/api/activities/?search=Jogging')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_food_groups(self):
        response = self.client.get('/api/food-groups/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Fruits', response.json())

    def test_add_food_entry(self):
        response = self.client.post('/api/add-food-entry/',
            data={'user_id': self.user.id, 'date': '2026-03-29', 'food_id': self.food.id, 'servings': 1, 'meal_type': 'lunch'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(FoodEntry.objects.exists())

    def test_add_food_entry_missing_fields(self):
        response = self.client.post('/api/add-food-entry/',
            data={'user_id': self.user.id},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_add_food_entry_invalid_servings(self):
        response = self.client.post('/api/add-food-entry/',
            data={'user_id': self.user.id, 'date': '2026-03-29', 'food_id': self.food.id, 'servings': -1},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_add_activity_entry(self):
        response = self.client.post('/api/add-activity-entry/',
            data={'user_id': self.user.id, 'date': '2026-03-29', 'activity_id': self.activity.id, 'duration_minutes': 30},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ActivityEntry.objects.exists())

    def test_delete_food_entry(self):
        log = DailyLog.objects.create(user=self.user, date='2026-03-29')
        entry = FoodEntry.objects.create(daily_log=log, food=self.food, servings=1, meal_type='lunch')
        response = self.client.delete(f'/api/delete-food-entry/{entry.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(FoodEntry.objects.filter(id=entry.id).exists())

    def test_delete_activity_entry(self):
        log = DailyLog.objects.create(user=self.user, date='2026-03-29')
        entry = ActivityEntry.objects.create(daily_log=log, activity=self.activity, duration_minutes=30)
        response = self.client.delete(f'/api/delete-activity-entry/{entry.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(ActivityEntry.objects.filter(id=entry.id).exists())

    def test_delete_user(self):
        response = self.client.delete(f'/users/{self.user.id}/delete/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(UserProfile.objects.filter(id=self.user.id).exists())
