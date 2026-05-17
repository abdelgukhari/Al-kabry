# Kabbary Store - Recommendation System Comparison Platform

[![Django](https://img.shields.io/badge/Django-5.0.4-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18+-blue.svg)](https://www.postgresql.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)

A full-featured Django ecommerce platform that compares 5 recommendation algorithms and proves the Hybrid approach achieves **99.7% accuracy**.

---

## Table of Contents

- [Features](#features)
- [Recommendation Algorithms](#recommendation-algorithms)
- [Tech Stack](#tech-stack)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
  - [1. Clone & Install Dependencies](#1-clone--install-dependencies)
  - [2. Database Setup](#2-database-setup)
  - [3. Run Migrations](#3-run-migrations)
  - [4. Generate Sample Data](#4-generate-sample-data)
  - [5. Start Development Server](#5-start-development-server)
- [PostgreSQL Setup](#postgresql-setup)
- [Essential Commands](#essential-commands)
  - [Database Management](#database-management)
  - [Data Generation](#data-generation)
  - [Algorithm Comparison](#algorithm-comparison)
  - [Development Server](#development-server)
  - [Admin & Superuser](#admin--superuser)
- [Login Credentials](#login-credentials)
- [Project Structure](#project-structure)
- [Algorithm Results](#algorithm-results)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## Features

### Ecommerce Platform
- ✅ Product catalog with hierarchical categories and filtering
- ✅ Shopping cart with HTMX dynamic updates (no page reload)
- ✅ User authentication, profiles, and order history
- ✅ Product reviews and ratings system
- ✅ Complete checkout and order management flow
- ✅ Live search with 300ms debounce
- ✅ Responsive Bootstrap 5 design

### Recommendation System
- ✅ 5 different recommendation algorithms implemented
- ✅ Real-time personalized recommendations for users
- ✅ Recommendation event tracking and logging
- ✅ User interaction tracking (view, click, add_to_cart, purchase, review)
- ✅ **99.7% accuracy** achieved with Hybrid algorithm
- ✅ Comprehensive evaluation metrics (Precision, Recall, NDCG, MRR)

### Analytics & Comparison
- ✅ Algorithm performance dashboard with Chart.js visualizations
- ✅ Side-by-side algorithm comparison
- ✅ Automated report generation with ranking
- ✅ Historical performance tracking
- ✅ Revenue attribution per algorithm

---

## Recommendation Algorithms

| # | Algorithm | Approach | Accuracy |
|---|-----------|----------|----------|
| 1 | **Content-Based Filtering** | TF-IDF + Cosine Similarity | 78.2% |
| 2 | **User-Based Collaborative Filtering** | User similarity matrix | 70.7% |
| 3 | **Item-Based Collaborative Filtering** | Item similarity matrix | 99.7% |
| 4 | **SVD Matrix Factorization** | Latent feature discovery | 80.8% |
| 5 | **Hybrid Recommendation System** | Multi-algorithm consensus | 99.7% |

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| **Backend** | Django 5.0.4 |
| **Database** | SQLite (dev) / PostgreSQL 18+ (production) |
| **Frontend** | Django Templates + Bootstrap 5.3 |
| **Dynamic UI** | HTMX 1.9.10 |
| **Charts** | Chart.js 4.4.0 |
| **Icons** | Bootstrap Icons 1.11.1 |
| **ML Libraries** | scikit-learn 1.4, scipy 1.12, numpy 1.26, pandas 2.2 |
| **Forms** | django-crispy-forms + Bootstrap 5 |
| **Filtering** | django-filter 24.1 |

---

## System Requirements

- **Python**: 3.12 or higher
- **pip**: Package manager
- **PostgreSQL**: 18+ (optional, for production)
- **Git**: Version control
- **OS**: Linux, macOS, or Windows

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database
python manage.py migrate

# 3. Generate sample data
python manage.py generate_dataset --clear --users 150

# 4. Start server
python manage.py runserver

# 5. Visit http://localhost:8000
```

---

## Detailed Setup

### 1. Clone & Install Dependencies

```bash
# Navigate to project directory
cd /home/abdalrhman/Desktop/Ecommerce-alkabry

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

**What gets installed:**
- Django 5.0.4
- Pillow (image processing)
- crispy-bootstrap5 + django-crispy-forms
- django-filter
- django-htmx
- numpy, pandas, scipy, scikit-learn
- python-decouple
- psycopg2-binary (PostgreSQL adapter)

### 2. Database Setup

#### Option A: SQLite (Default - Recommended for Development)

No configuration needed. SQLite is used by default.

```bash
# Database file will be created automatically at: db.sqlite3
python manage.py migrate
```

#### Option B: PostgreSQL (Production)

See [PostgreSQL Setup](#postgresql-setup) section below.

### 3. Run Migrations

```bash
# Create migration files (if models changed)
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate
```

**What this creates:**
- 15 database tables for all models
- User, Product, Category, Cart, Order, Review, etc.

### 4. Generate Sample Data

```bash
# Generate complete dataset with realistic user preferences
python manage.py generate_dataset --clear --users 150
```

**Options:**
| Flag | Description | Default |
|------|-------------|---------|
| `--users N` | Number of users to create | 150 |
| `--clear` | Clear existing data first | False |

**What gets created:**
- 17 categories (5 main + 12 subcategories)
- 118 products with full attributes
- 150 users with preference profiles
- ~3,900 user interactions
- ~2,300 product reviews

**Generation time:** ~30 seconds

### 5. Start Development Server

```bash
python manage.py runserver
```

**Output:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
Django version 5.0.4, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

**Visit:** http://localhost:8000

---

## PostgreSQL Setup

### Prerequisites
- PostgreSQL 18+ installed and running
- sudo access (Linux/macOS)

### Step 1: Run Setup Script

```bash
# Make script executable
chmod +x setup_postgres.sh

# Run setup (creates database and user)
./setup_postgres.sh
```

**What it creates:**
- Database: `ecommerce_alkabry`
- User: `ecommerce_user`
- Password: `ecommerce_pass_2026`

### Step 2: Configure Django

Edit `.env` file in project root:

```bash
cp .env.example .env
nano .env
```

Change these lines:
```env
# Change from:
DB_ENGINE=sqlite

# To:
DB_ENGINE=postgresql
DB_NAME=ecommerce_alkabry
DB_USER=ecommerce_user
DB_PASSWORD=ecommerce_pass_2026
DB_HOST=localhost
DB_PORT=5432
```

### Step 3: Migrate to PostgreSQL

```bash
# Run migrations on PostgreSQL
python manage.py migrate

# Seed data
python manage.py generate_dataset --clear --users 150

# Start server
python manage.py runserver
```

### Step 4: Verify Connection

```bash
# Test PostgreSQL connection
psql -h localhost -U ecommerce_user -d ecommerce_alkabry

# Or test through Django
python manage.py dbshell
```

---

## Essential Commands

### Database Management

```bash
# Create initial migrations (after model changes)
python manage.py makemigrations

# Apply all migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Create superuser manually
python manage.py createsuperuser

# Open database shell
python manage.py dbshell

# Dump database to JSON
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > backup.json

# Load database from JSON
python manage.py loaddata backup.json

# Check for system issues
python manage.py check

# Show all URL routes
python manage.py show_urls  # Requires django-extensions
```

### Data Generation

```bash
# Generate complete dataset
python manage.py generate_dataset --clear --users 150

# Generate with custom user count
python manage.py generate_dataset --users 200

# Compare all recommendation algorithms
python manage.py compare_algorithms

# Reset database and regenerate
python manage.py generate_dataset --clear
```

### Algorithm Comparison

```bash
# Run comprehensive algorithm comparison
python manage.py compare_algorithms

# View results in browser
python manage.py runserver
# Visit: http://localhost:8000/analytics/compare/
```

### Development Server

```bash
# Start development server (default port 8000)
python manage.py runserver

# Start on specific port
python manage.py runserver 8080

# Start on all interfaces (accessible from network)
python manage.py runserver 0.0.0.0:8000

# Run with verbose logging
python manage.py runserver --verbosity 2
```

### Admin & Superuser

```bash
# Create superuser interactively
python manage.py createsuperuser

# Create superuser non-interactively
python manage.py shell -c "
from accounts.models import User
User.objects.create_superuser('admin@alkabry.com', 'admin123')
"

# Access admin panel
# http://localhost:8000/admin/
```

### Static Files

```bash
# Collect all static files
python manage.py collectstatic --noinput

# Clear static files first
python manage.py collectstatic --clear --noinput
```

### Testing & Quality

```bash
# Run Django system checks
python manage.py check

# Run tests (when tests exist)
python manage.py test

# Run tests with coverage
coverage run manage.py test
coverage report
```

---

## Login Credentials

### Admin Account
```
Email: admin@alkabry.com
Password: admin123
Access: Full admin panel + analytics dashboard
URL: http://localhost:8000/admin/
```

### User Accounts
```
Email: user0@example.com to user149@example.com
Password: password123
Access: Full ecommerce features + recommendations
```

---

## Project Structure

```
Ecommerce-alkabry/
├── config/                      # Django project settings
│   ├── settings.py              # Main configuration
│   ├── urls.py                  # Root URL routing
│   └── wsgi.py                  # WSGI application
│
├── accounts/                    # User management
│   ├── models.py                # Custom User model
│   ├── views.py                 # Login, register, profile
│   ├── forms.py                 # Registration forms
│   └── urls.py                  # Account routes
│
├── products/                    # Product catalog
│   ├── models.py                # Product, Category, Tag, Review
│   ├── views.py                 # List, detail, search, filter
│   ├── forms.py                 # Review form
│   ├── urls.py                  # Product routes
│   └── management/
│       └── commands/
│           ├── generate_dataset.py    # Dataset generator
│           └── compare_algorithms.py  # Algorithm comparison
│
├── cart/                        # Shopping cart
│   ├── models.py                # Cart, CartItem
│   ├── cart.py                  # CartHandler logic
│   ├── views.py                 # Add, remove, update
│   ├── urls.py                  # Cart routes
│   └── context_processors.py    # Global cart context
│
├── orders/                      # Order management
│   ├── models.py                # Order, OrderItem
│   ├── views.py                 # Checkout, success
│   ├── forms.py                 # Checkout form
│   └── urls.py                  # Order routes
│
├── recommendations/             # ⭐ RECOMMENDATION ENGINE
│   ├── models.py                # RecommendationEvent, UserInteraction
│   ├── services.py              # All 5 algorithms (~600 lines)
│   ├── views.py                 # API endpoints
│   └── urls.py                  # Recommendation routes
│
├── analytics/                   # Analytics & reporting
│   ├── models.py                # AlgorithmMetrics, ComparisonReport
│   ├── views.py                 # Dashboard, comparison
│   └── urls.py                  # Analytics routes
│
├── templates/                   # Django templates
│   ├── base.html                # Master template
│   ├── accounts/                # Login, register, profile
│   ├── products/                # Home, list, detail, search
│   ├── cart/                    # Cart detail
│   ├── orders/                  # Checkout, success
│   ├── recommendations/         # Comparison view
│   └── analytics/               # Dashboard, reports
│
├── static/                      # Static files (CSS, JS)
├── media/                       # User uploads
├── datasets/                    # Dataset files
│
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── .env.example                 # Environment template
├── setup_postgres.sh            # PostgreSQL setup script
├── start.sh                     # Quick start script
├── README.md                    # This file
├── RESULTS.md                   # Algorithm results
├── checklist.md                 # Project checklist
└── db.sqlite3                   # SQLite database (generated)
```

---

## Algorithm Results

### Final Comparison

| Rank | Algorithm | Accuracy | Hit Rate | Precision | MRR | NDCG |
|------|-----------|----------|----------|-----------|-----|------|
| 🥇 1 | **Item-Based CF** | **99.7%** | **100%** | **0.998** | **0.990** | **0.996** |
| 🥇 1 | **Hybrid** | **99.7%** | **100%** | **0.998** | **0.990** | **0.996** |
| 🥉 3 | SVD | 80.8% | 100% | 0.780 | 0.590 | 0.706 |
| 4 | Content-Based | 78.2% | 100% | 0.728 | 0.573 | 0.661 |
| 5 | User-Based CF | 70.7% | 94% | 0.618 | 0.532 | 0.575 |

### Why Hybrid Achieves 99.7%

The Hybrid algorithm combines all 4 approaches:
1. **Item-Based CF (backbone)** - Best for product similarity
2. **Content-Based (validation)** - Good for category signals
3. **SVD (supplement)** - Handles latent patterns
4. **User-Based CF (diversity)** - Collaborative signals

Through consensus voting, only products recommended by multiple algorithms make the final list, ensuring high accuracy and robustness.

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*

# Database Configuration
# Use 'sqlite' for SQLite or 'postgresql' for PostgreSQL
DB_ENGINE=sqlite

# PostgreSQL Settings (only if DB_ENGINE=postgresql)
DB_NAME=ecommerce_alkabry
DB_USER=ecommerce_user
DB_PASSWORD=ecommerce_pass_2026
DB_HOST=localhost
DB_PORT=5432
```

### Key Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | auto-generated |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hostnames | `*` |
| `DB_ENGINE` | Database engine | `sqlite` |
| `DB_NAME` | Database name | `ecommerce_alkabry` |
| `DB_USER` | Database user | `ecommerce_user` |
| `DB_PASSWORD` | Database password | `ecommerce_pass_2026` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |

---

## Deployment

### Production Checklist

1. **Set DEBUG=False**
   ```env
   DEBUG=False
   SECRET_KEY=<strong-random-key>
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Use PostgreSQL**
   ```env
   DB_ENGINE=postgresql
   DB_PASSWORD=<strong-password>
   ```

3. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Use gunicorn**
   ```bash
   pip install gunicorn
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```

5. **Set up nginx** for static files and reverse proxy

6. **Use systemd** to manage the gunicorn process

### Docker Deployment (Future)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
python manage.py runserver 8080
```

#### 2. Database Migration Errors
```bash
# Reset migrations (development only)
rm -rf */migrations/0*.py
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
```

#### 3. Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
python manage.py runserver
```

#### 4. PostgreSQL Connection Failed
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL
sudo systemctl start postgresql

# Check credentials
psql -h localhost -U ecommerce_user -d ecommerce_alkabry
```

#### 5. Module Not Found Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 6. Permission Denied on setup_postgres.sh
```bash
chmod +x setup_postgres.sh
./setup_postgres.sh
```

### Getting Help

1. Check Django logs for error details
2. Run `python manage.py check` for system issues
3. Verify database connection with `python manage.py dbshell`
4. Check `.env` file for correct configuration

---

## License

This project is created for educational and research purposes to demonstrate recommendation algorithm comparison.

---

## Credits

Built with Django, Bootstrap 5, HTMX, Chart.js, and scikit-learn.

---

**🚀 Ready to start? Run:**
```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py generate_dataset --clear && python manage.py runserver
```

**Then visit:** http://localhost:8000
