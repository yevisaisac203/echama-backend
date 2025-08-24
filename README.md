 eChama Backend API

A backend system for managing digital chamas (informal savings & investment groups). Built with Django REST Framework, this API supports:

Member registration & authentication (JWT)

Group management

Contributions tracking

Loan requests & approvals

Role-based access & permissions

Features

.User authentication & authorization (JWT)

. CRUD operations for Members, Groups, Contributions, Loans

.Validation rules for chama operations

.API documentation (Swagger & Redoc)

. Unit tests for core functionality

.Configurable with PostgreSQL (production) or SQLite (development)

Tech Stack

Backend Framework: Django 5 + Django REST Framework

✓Database: SQLite (dev) / PostgreSQL (prod)

Authentication: JSON Web Tokens (djangorestframework-simplejwt)

Documentation: drf-yasg (Swagger & ReDoc)

Testing: Django Test Framework + Pytest (optional)

Deployment Ready: Docker + Gunicorn + Nginx  
  Project Structure
eChama-backend/
│── api/                # Core app (users, groups, contributions, loans)
│── echama/             # Project settings & configurations
│── tests/              # Unit tests
│── requirements.txt    # Dependencies
│── manage.py           # Django entry point
│── README.md           # Project documentation

 Installation & Setup
1 Clone the Repository
git clone https://github.com/<your-username>/echama-backend.git
cd echama-backend

2 Create a Virtual Environment & Install Dependencies
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows
pip install -r requirements.txt

3 Run Migrations
python manage.py migrate

4 Create a Superuser
python manage.py createsuperuser

5 Run Development Server
python manage.py runserver


Your API will be available at:
 http://127.0.0.1:8000/api/

Authentication

This project uses JWT authentication.

Obtain a token:
POST /api/token/ with username & password.

Refresh a token:
POST /api/token/refresh/

Example Request:

{
  "username": "testuser",
  "password": "password123"
}

 API Documentation

Swagger UI:
 http://127.0.0.1:8000/swagger/

Redoc UI:
 http://127.0.0.1:8000/redoc/

Running Tests
python manage.py test

 Docker Setup (Optional)
Build & Run with Docker Compose
docker-compose up --build


This will start:

Django backend

PostgreSQL database

Roadmap

 Add business rules (loan limits, interest rates, deadlines)

 Implement group roles (admin, treasurer, member)

 Add notifications (email/SMS)

 Add CI/CD pipeline with GitHub Actions

 Deploy to cloud (Railway, Render, or AWS)

 Contributing

Contributions are welcome!

Fork the project

Create a new branch (feature/xyz)

Commit changes (git commit -m "Add feature xyz")

Push to branch (git push origin feature/xyz)

Create a Pull Request

Author

Yevisa Isac

Computer Science Student @ University of Embu

Backend Developer | Django REST Framework Enthusiast

🔗 LinkedIn:https://www.linkedin.com/in/yevisa-isac-b1103234b/

License

This project is licensed under the MIT License.
