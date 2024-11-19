# Currency Exchange DRF Project

## Introduction

Welcome to the Currency Exchange Django DRF project. This README provides step-by-step instructions to set up and run the project on your local development machine. Please ensure you go through all the instructions and files before executing the steps described here.

## Prerequisites

Before you proceed, make sure you have the following requirements met:
* Python 3.11 installed on your system.
* Familiarity with Python virtual environments.
* Basic understanding of Django and Django REST Framework operation.

## Installation

Follow these steps to set up your development environment:

1. **Install virtualenv Python package:**

   Open your terminal and execute the following command:
   ```bash
   pip install virtualenv
2. **Create a Python virtual environment:**

   Open your terminal and execute the following command:
   ```bash
   python3.11 -m venv env
3. **Activate the Python virtual environment:**
   
   For macOS/Linux:
   ```bash
   source env/bin/activate
4. **Install the required packages:**

   Ensure you are in the project's root directory where the `requirements.txt` file is located, then run:
   ```bash
   pip install -r requirements.txt
## Running the Project

Once the setup is complete, you can run the Django server:

1. **Navigate to the `currency_exchange` directory:**

   Change to the directory containing your `manage.py` file:
   ```bash   
   cd currency_exchange
2. **Database migrations:**

   Perform database migrations with the following commands:
   
   ```bash
   python manage.py makemigrations 
   python manage.py migrate
3. **Start the Django development server:**

   Launch your server using:
   
   ```bash
   python manage.py runserver
4. **Backoffice Currency Converter:**
    
    Launch backoffice  currency converter:
    ```bash
    http://127.0.0.1:8000/mycurrency/currency/backoffice-dashboard/
## Additional Information
- The Postman collection for the API endpoints is available in the currency_exchange directory
- If you encounter issues with migrations, check your database configuration in the `settings.py` file and ensure the database server is running.
- Remember to create new migrations and apply them whenever you make changes to your models.

Thank you for using our Django DRF Project. If you have any questions or need further assistance, please feel free to reach out
