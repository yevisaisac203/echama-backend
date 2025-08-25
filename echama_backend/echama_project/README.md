# eChama Backend 💰📱

A **Django REST Framework (DRF)** backend for managing **digital chamas (investment groups)**.  
This API provides endpoints for user management, group contributions, loans, and authentication.

---

## 🚀 Features
- User Registration & Authentication (JWT)
- Group Management (Create & Join Chamas)
- Contributions Tracking
- Loan Management
- API Documentation with **Swagger** & **Redoc**
- Role-based Permissions (only members can access their chama data)

---

## 🛠️ Tech Stack
- **Backend Framework**: Django, Django REST Framework (DRF)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: SQLite (default) / PostgreSQL (recommended)
- **API Docs**: drf-yasg (Swagger & Redoc)

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/echama-backend.git
cd echama-backend

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

### 3. Install Dependencies
```bash
pip install -r requirements.txt

### 4. Apply Migrations
```bash
python manage.py migrate

### 5. Create a Superuser (for admin access)
```bash
python manage.py createsuperuser

### 6. Run the Development Server
```bash 
python manage.py runserver
The API will be accessible at `http://127.0.0.1:8000/`
---
🔑Authentication
This project uses JWT (JSON Web Tokens).
obtain token:
POST /api/token/ with {"username": "yourusername", "password": "yourpassword"}
refresh token:  
POST /api/token/refresh/ with {"refresh": "your_refresh_token"}

example usage:
{
    "username": "testuser",
    "password": "testpassword"

}

📖API Documentation
- Swagger UI: `http://127.0.0.1:8000/swagger/`
- Redoc: `http://127.0.0.1:8000/redoc/`
---
✅Running Tests
```bash
python manage.py test
---
📂 Project Structure
echama_project/
│── echama_app/        # Main application
│   ├── models.py      # Database models
│   ├── serializers.py # DRF serializers
│   ├── views.py       # API views
│   ├── urls.py        # App routes
│── echama_project/    # Project settings
│── requirements.txt   # Dependencies
│── manage.py          # Django CLI
---
## 🤝 Contributing
Fork the repo 🍴

Create a new branch (git checkout -b feature-name)

Commit changes (git commit -m "Added new feature")

Push branch (git push origin feature-name)

Open a Pull Request 🚀
---
📬 Contact
Developer: Yevisa Isac

LinkedIn: https://www.linkedin.com/in/yevisa-isac-b1103234b/
Email: isaack.jyevisa@gmail.com

---
## 📜 License
This project is licensed under the MIT License





