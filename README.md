# Car Rental Platform

A Django web application for a car rental system. This application allows users to browse available cars, make bookings, and submit support requests.

## Features

- User registration and authentication
- Car browsing and searching
- Booking management
- Support request submission
- Responsive design

## Database Schema

The application uses PostgreSQL and includes the following models:

- User: For user authentication and management
- Car: To store car information
- Booking: To manage car bookings
- Payment: To track booking payments
- SupportRequest: To handle customer support inquiries

## Setup Instructions

1. Clone the repository:

```
git clone <repository-url>
cd car_rental_platform
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Database setup:

   - Create a PostgreSQL database named 'car_rental_db'
   - Configure database settings in `settings.py` if needed

4. Run migrations:

```
python manage.py migrate
```

5. Create initial data:

```
python manage.py setupdata
```

6. Run the development server:

```
python manage.py runserver
```

7. Access the application at http://127.0.0.1:8000/

## Demo Accounts

After running the `setupdata` command, you can use the following demo accounts:

- Customer account:

  - Username: customer
  - Password: customer123

- Admin account:
  - Username: admin
  - Password: admin123
  - Note: Admin users cannot log in to the main application as per requirements

## Project Structure

- `car_rental/` - Main application directory
  - `models.py` - Database models
  - `views.py` - View functions
  - `urls.py` - URL patterns
  - `forms.py` - Form definitions
  - `templates/` - HTML templates
  - `static/` - Static files (CSS, JS, images)
  - `management/commands/` - Custom management commands

## Requirements

- Python 3.8+
- Django 4.0+
- PostgreSQL
