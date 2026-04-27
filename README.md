# Inventory Management System (Flask REST API + CLI)

A full-stack backend system built with Flask that allows administrators to manage inventory items, integrate external product data, and interact through both REST API endpoints and a CLI tool.

## ✨ Features

###  Inventory Management (CRUD)
- Create new inventory items  
- View all items or a single item by ID  
- Update item details (price, quantity)  
- Delete items from inventory  

###  External API Integration
- Fetch real-time product data from OpenFoodFacts  
- Import fetched products directly into your inventory  

###  REST API
- Built using Flask  
- JSON-based responses  
- Clean and RESTful routing structure  

###  CLI Interface
- Manage inventory directly from the terminal  
- Perform CRUD operations via CLI  
- Fetch and import external product data  

###  Testing
- Unit tests implemented using `pytest`  
- Run tests with:
```bash
python -m pytest
```

---

## 🛠️ Tech Stack

| Technology   | Purpose                          |
|-------------|----------------------------------|
| Python 3    | Core programming language        |
| Flask       | Web framework / REST API         |
| Flask-CORS  | Handle cross-origin requests     |
| Requests    | External API communication       |
| Pytest      | Unit testing                     |
| JSON        | In-memory data storage           |

---

##  Project Structure

```
inventory-management-system/
├── server/
│   ├── __init__.py
│   └── app.py
├── cli/
│   └── cli.py
├── tests/
│   └── test_app.py
└── README.md
```

---

##  Installation

### 1. Clone the Repository
```bash
git clone https://github.com/fel-ly88/inventory-management-system
cd inventory-management-system
```

### 2. Create & Activate a Virtual Environment
```bash
python3 -m venv venv
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install flask flask-cors requests pytest
```

---

## 🚀 Running the Application

### Start the Flask Server
```bash
cd server
python app.py
```

Server runs at: http://localhost:5000

### Start the CLI
```bash
cd cli
python cli.py
```

---

## 📡 API Endpoints

| Method | Endpoint               | Description                      |
|--------|-----------------------|----------------------------------|
| GET    | /inventory            | Get all inventory items          |
| GET    | /inventory/<id>       | Get item by ID                   |
| POST   | /inventory            | Create a new item                |
| PATCH  | /inventory/<id>       | Update an item                   |
| DELETE | /inventory/<id>       | Delete an item                   |
| GET    | /search               | Search items (requires params)   |
| POST   | /inventory/import     | Import from OpenFoodFacts        |

---

## 🧪 Running Tests

```bash
python -m pytest
```

### Test Coverage Includes:
- GET /inventory  
- GET /inventory/<id>  
- POST /inventory  
- PATCH /inventory/<id>  
- DELETE /inventory/<id>  
- GET /search  
- POST /inventory/import  