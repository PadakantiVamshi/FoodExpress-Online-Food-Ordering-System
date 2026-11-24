# FoodExpress - Online Food Ordering System

## Project Overview
FoodExpress is a full-stack web application that allows
customers to browse food items, add items to a shopping
cart and place orders. Administrators can monitor orders,
view dashboard statistics and update order statuses.

## Technologies Used
- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- Database: MySQL
- API: REST API
- Database Connector: MySQL Connector Python
- Development Tool: Visual Studio Code
- Version Control: Git and GitHub

## Features
- Dynamic food menu
- Shopping cart management
- Customer selection
- Order placement
- Automatic order total calculation
- Admin dashboard
- Order status management
- REST API CRUD operations
- Relational database integration

## Database Tables
1. customers
2. categories
3. menu_items
4. orders
5. order_items

## Database Concepts
- Primary Keys
- Foreign Keys
- Table Relationships
- SQL JOINs
- Aggregate Functions
- CRUD Operations
- Database Transactions

## Installation Instructions

### 1. Create a virtual environment
    python -m venv venv

### 2. Activate the virtual environment on Windows
    .\venv\Scripts\Activate.ps1

### 3. Install dependencies
    pip install -r requirements.txt

### 4. Configure the database
Create a MySQL database named foodexpress_db.
Import database/foodexpress_db.sql into MySQL.

### 5. Configure environment variables
Copy .env.example to .env and enter your MySQL
connection details.

### 6. Run the application
    python app.py

## Application URLs
- Customer Page: http://127.0.0.1:5000/
- Admin Dashboard: http://127.0.0.1:5000/admin
- Menu API: http://127.0.0.1:5000/api/menu
- Dashboard API: http://127.0.0.1:5000/api/admin/dashboard

## Future Enhancements
- Customer login and registration
- Admin authentication
- Online payment integration
- Real-time order tracking
- Cloud deployment

## Academic Project
Master of Science in Computer Science
Fairleigh Dickinson University
