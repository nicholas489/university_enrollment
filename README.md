# University Enrollment (Django) — Build & Run

Quick instructions to build and run this Django webapp.

Prerequisites
- Python 3.10+ (same major used for development)
- pip
- (optional) virtualenv

Recommended Django version: 5.2.8 (project migrations were generated with this).

### How to Run Program

**1. Apply DB Migrations**

    python3 manage.py migrate

**2. Seed Mock User Data (Optional as should already be in SqlLite file)**

    python3 manage.py seed_mock_data

**3. Run the web server**

    python3 manage.py runserver