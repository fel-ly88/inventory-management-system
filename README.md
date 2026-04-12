# 📦 Inventory Management System (Flask REST API + CLI)

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
- Unit tests using pytest
- Covers API endpoints and core logic



##  Tech Stack

- Python 3
- Flask
- Flask-RESTful / Flask routing
- Requests (API calls)
- Pytest (testing)
- JSON (data storage)



##  Installation

### 1. Clone Repository
```bash
git clone <https://github.com/fel-ly88/inventory-management-system>
cd inventory-system
