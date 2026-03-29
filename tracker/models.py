from django.db import models

# Create your models here.
class UserProfile(models.Model):
    SEX_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    name = models.CharField(max_length=100)
    weight = models.FloatField(help_text="Weight in kg")
    height = models.FloatField(help_text="Height in cm")
    age = models.IntegerField(help_text="Age in years")
    sex = models.CharField(max_length=6, choices=SEX_CHOICES)

    def bmr(self):
        if self.sex == 'male':
            return round(
                66.4730 + (13.7516 * self.weight) + (5.0033 * self.height) - (6.7550 * self.age), 3
            )
        return round(
            655.0955 + (9.5634 * self.weight) + (1.8496 * self.height) - (4.6756 * self.age), 3
        )

    def __str__(self):
        return self.name


class Food(models.Model):
    food_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=300)
    food_group = models.CharField(max_length=100)
    calories = models.FloatField()
    fat = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    carbohydrate = models.FloatField(default=0)
    serving_description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Activity(models.Model):
    activity_name = models.CharField(max_length=200)
    specific_motion = models.CharField(max_length=300)
    met_value = models.FloatField()

    class Meta:
        verbose_name_plural = "activities"

    def __str__(self):
        return f"{self.activity_name} - {self.specific_motion}"


class DailyLog(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='daily_logs')
    date = models.DateField()

    class Meta:
        unique_together = ('user', 'date')

    def total_calories_in(self):
        return sum(entry.calories_consumed() for entry in self.food_entries.all())

    def total_calories_out(self):
        return sum(entry.calories_burned() for entry in self.activity_entries.all())

    def bmr(self):
        return self.user.bmr()

    def net_calories(self):
        return round(self.total_calories_in() - self.bmr() - self.total_calories_out(), 2)

    def __str__(self):
        return f"{self.user.name} - {self.date}"


class FoodEntry(models.Model):
    MEAL_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, related_name='food_entries')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    servings = models.FloatField(default=1)
    meal_type = models.CharField(max_length=10, choices=MEAL_CHOICES)

    def calories_consumed(self):
        return round(self.food.calories * self.servings, 2)

    def __str__(self):
        return f"{self.food.name} x{self.servings} ({self.meal_type})"


class ActivityEntry(models.Model):
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, related_name='activity_entries')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    duration_minutes = models.FloatField()

    def calories_burned(self):
        weight = self.daily_log.user.weight
        return round(self.activity.met_value * weight * (self.duration_minutes / 60), 2)

    def __str__(self):
        return f"{self.activity.specific_motion} - {self.duration_minutes} min"