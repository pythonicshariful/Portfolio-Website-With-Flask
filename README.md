# Portfolio-Website-With-Flask

A premium, fully dynamic portfolio website built with Flask, SQLAlchemy, and Tailwind CSS. Features a comprehensive admin dashboard for managing all site content.

## Features
- **Dynamic Content**: Manage Hero, About, Stats, Services, and Portfolio via Admin Hub.
- **Admin Dashboard**: Secure login to update all site settings, including SEO and Analytics.
- **Testimonials**: Add and manage client reviews with image uploads.
- **Social Media Hub**: Dynamically update social links across the site.
- **SEO Optimized**: Built-in fields for Meta Tags and Google Analytics.
- **Premium Design**: Modern, responsive UI with glassmorphism and smooth animations.

## Tech Stack
- **Backend**: Flask, Flask-SQLAlchemy, Flask-Login
- **Frontend**: Jinja2, Tailwind CSS, Lucide Icons, Font Awesome, AOS
- **Database**: SQLite

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/pythonicshariful/Portfolio-Website-With-Flask.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup Configuration:
   - Rename `config.example.py` to `config.py`.
   - Add your Gmail address and App Password to `config.py`.

4. Run the application:
   ```bash
   python app.py
   ```
4. Access the site at `http://127.0.0.1:5000` and admin at `/admin`.

## Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`
