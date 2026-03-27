# Calorie Tracker

A full-stack web application built with Django and Django REST Framework that helps users track daily calorie intake and expenditure. Users can log food consumption and physical activities, and the app calculates net calories (surplus or deficit) using the Harris-Benedict BMR equation and standard MET formulas.

## Features

- **User Profiles** — Create profiles with biometric data (weight, height, age, sex) to calculate personalized BMR
- **Food Logging** — Search from 14,000+ food items across multiple food groups, log meals with servings
- **Activity Logging** — Choose from 800+ activities with MET values, log duration
- **Daily Summary** — View net calories = Food Intake - BMR - Calories Burned
- **Trends View** — See all daily logs for a user with calorie breakdown
- **REST API** — Full API endpoints for programmatic access

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0.3 |
| API | Django REST Framework 3.17.1 |
| Database | SQLite3 |
| Frontend | Django Templates, Bootstrap 4.6.2, jQuery 3.6.0 |
| Data Import | OpenPyXL 3.1.5 |

## Project Structure

```
calorie_tracker/
├── calorie_project/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── tracker/                  # Main app
│   ├── models.py             # UserProfile, Food, Activity, DailyLog, FoodEntry, ActivityEntry
│   ├── views.py              # DRF ViewSets + Django template views
│   ├── serializers.py        # DRF serializers with computed fields
│   ├── urls.py               # API and template URL routing
│   ├── utils.py              # BMR and calorie calculation helpers
│   ├── admin.py              # Django admin registration
│   └── management/commands/
│       └── load_data.py      # Custom command to import Excel data
├── templates/                # HTML templates
│   ├── base.html             # Base layout (header, footer, CDN imports)
│   ├── signup.html           # User registration form
│   ├── user_list.html        # Dashboard with user table + add data modal
│   ├── user_data.html        # User's all daily logs with calorie stats
│   └── user_details.html     # Single day breakdown (food, activity, net calories)
├── static/css/               # Custom CSS
├── data-excels-for-db/       # Source Excel files
│   ├── food-calories.xlsx    # 14,000+ food items
│   └── MET-values.xlsx       # 800+ activities with MET values
├── manage.py
└── requirements.txt
```

## Database Schema

```
UserProfile ──┐
              │ ForeignKey (one-to-many)
           DailyLog ──┬── FoodEntry ──── Food
              │       │
  (unique: user+date) └── ActivityEntry ── Activity
```

- **UserProfile** — name, weight, height, age, sex + `bmr()` method
- **Food** — name, food_group, calories, fat, protein, carbohydrate, serving_description
- **Activity** — activity_name, specific_motion, met_value
- **DailyLog** — one per user per day, computes `total_calories_in()`, `total_calories_out()`, `net_calories()`
- **FoodEntry** — links Food to DailyLog with servings and meal_type
- **ActivityEntry** — links Activity to DailyLog with duration_minutes

## Formulas Used

**BMR (Harris-Benedict Equation):**
- Male: `66.47 + (13.75 x weight_kg) + (5.00 x height_cm) - (6.76 x age)`
- Female: `655.10 + (9.56 x weight_kg) + (1.85 x height_cm) - (4.68 x age)`

**Activity Calories:** `MET_value x weight_kg x (duration_minutes / 60)`

**Net Calories:** `Calories In - BMR - Calories Burned`
- Negative = calorie deficit (weight loss)
- Positive = calorie surplus (weight gain)

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vaibhavagarwal19/calorie_tracker.git
   cd calorie_tracker
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS/Linux
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Load food and activity data from Excel files**
   ```bash
   python manage.py load_data
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Open in browser**
   - Signup: http://127.0.0.1:8000/
   - Dashboard: http://127.0.0.1:8000/users/
   - Admin: http://127.0.0.1:8000/admin/

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | List all users |
| POST | `/api/users/` | Create a user |
| GET | `/api/foods/?search=&food_group=` | Search foods (max 50 results) |
| GET | `/api/activities/?search=` | Search activities (max 50 results) |
| GET | `/api/daily-log/<user_id>/` | Get all daily logs for a user |
| GET | `/api/daily-log/<user_id>/<date>/` | Get specific day's log |
| POST | `/api/add-food-entry/` | Add a food entry |
| POST | `/api/add-activity-entry/` | Add an activity entry |
| GET | `/api/food-groups/` | List all distinct food groups |
| GET | `/api/activity-names/` | List all distinct activity names |
