# CPS510 A9: University Enrollment (Django)

Quick instructions to build and run this Django webapp on localhost.

Prerequisites
- Python 3.10+ (same major used for development)
- pip

## Setup
Run the following CLI command to get django package:

    pip install django

## How to Run Program

**1. Apply DB Migrations**

    python3 manage.py migrate

**2. Seed Mock User Data**

    python3 manage.py seed_mock_data

**3. Run the web server**

    python3 manage.py runserver

## Usage/Testing
- Head to [localhost:8000](http://localhost:8000) and login with a Student/Instructor/Admin account
- To login with a Student Account, use the following email/password credentials:
    - `john.jason@torontomu.ca`
    - `jason1234`
- To login with a Instructor Account, use the following email/password credentials:
    - `abhari@torontomu.ca`
    - `abdolreza1234`
- To login with a Admin Account, use the following username/password credentials:
    - `admin1`
    - `adminpass`
