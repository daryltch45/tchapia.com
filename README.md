# Tchapia.com

A handyman marketplace connecting Cameroonians with skilled artisans for projects of any size.

## About

Tchapia is a web platform that bridges the gap between customers and local handymen across Cameroon. Whether you need help with a small repair or a major renovation, our platform makes it simple to:

- **For Customers:** Post projects, browse qualified artisans, and receive competitive offers
- **For Artisans:** Discover new opportunities, showcase your skills, and grow your business

Everything is streamlined and transparent for both parties, from project posting to offer submission and completion.

## Why Tchapia?

- Connect with verified local artisans in your city
- Post projects in minutes
- Receive multiple competitive offers
- Secure and transparent process
- Support local Cameroonian businesses

## Features

- **Dual User Roles:** Separate dashboards for customers and artisans
- **Project Management:** Create, edit, and track project status
- **Smart Matching:** Find artisans by service type and location
- **Offer System:** Artisans submit competitive bids on projects
- **Rating & Reviews:** Build trust through community feedback
- **City Coverage:** Support for major Cameroonian cities (Douala, Yaoundé, Bafoussam, and more)
- **Responsive Design:** Works seamlessly on mobile and desktop

## Technologies Used

- **Backend:** Django 5.0
- **Frontend:** Bootstrap 5, Font Awesome
- **Database:** PostgreSQL
- **Package Manager:** UV

## Installation
```bash
# Clone repository
git clone https://github.com/daryltch45/tchapia.com.git
cd tchapia.com

# Install dependencies (with uv)
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver