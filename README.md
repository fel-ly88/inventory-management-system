# Inventory Management System (Flask REST API + CLI)

A full-stack backend system built with Flask that allows administrators to manage inventory items, integrate external product data, and interact through both REST API endpoints and a CLI tool.

##  Features

###  Inventory Management (CRUD)
- Create new inventory items
- View all items or single items
- Update existing items
- Delete items

###  External API Integration
- Fetch real-time product data using the OpenFoodFacts API
- Add fetched products directly into the inventory database

###  REST API
- Built using Flask
- JSON-based responses
- Clean RESTful routing

###  CLI Interface
- Interact with the system via terminal commands
- Add, view, update, delete inventory items
- Fetch external product data from CLI

###  Testing
- Unit tests using python -m pytest


##  Tech Stack

- Python 3
- Flask
- Flask-CORS
- Requests (API calls)
- Pytest (testing)
- JSON (in-memory data storage)



##  Installation

### 1. Clone Repository
git clone <https://github.com/fel-ly88/inventory-management-system>
cd inventory-system

###  Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install flask-cors
