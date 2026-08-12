from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class BaseMixin:
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # SEO & Analytics
    meta_title = db.Column(db.String(255), default="Shakil Ahmed | Email Marketing Expert")
    meta_description = db.Column(db.String(500), default="Top-rated Email Marketing expert helping Ecommerce & SaaS brands scale revenue through automation.")
    google_analytics_id = db.Column(db.String(100), default="")
    
    # Hero Content
    hero_title = db.Column(db.String(255), default="Transform Your Business with Data-Driven Email Marketing")
    hero_subtext = db.Column(db.String(500), default="Mailchimp Pro Partner • Klaviyo Partner • UI/UX Design and Development")
    hero_trust_text = db.Column(db.String(255), default="Platforms & tools I work in")
    
    # Links
    cv_link = db.Column(db.String(255), default="#")
    fiverr_link = db.Column(db.String(255), default="#")
    
    # Contact Info
    contact_phone = db.Column(db.String(50), default="+880 1234 567 890")
    contact_email = db.Column(db.String(100), default="hello@theshakil.com")

class SocialLink(db.Model, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False) # linkedin, facebook, twitter, etc.
    icon_name = db.Column(db.String(50), nullable=False) # lucide icon name
    link = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)

class Stat(db.Model, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    suffix = db.Column(db.String(10), default="+")
    order = db.Column(db.Integer, default=0)

class AboutInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), default="Email Marketing That Actually Drives Revenue")
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), default="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=1976&auto=format&fit=crop")

class Service(db.Model, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon_name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    order = db.Column(db.Integer, default=0)

class PortfolioItem(db.Model, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.String(500))
    category = db.Column(db.String(50), nullable=False)
    result_text = db.Column(db.String(100))
    image_path = db.Column(db.String(255))
    link = db.Column(db.String(255), default="#")
    order = db.Column(db.Integer, default=0)

class Testimonial(db.Model, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_role = db.Column(db.String(100)) # e.g., CEO, Marketing Director
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    image_path = db.Column(db.String(255))
    order = db.Column(db.Integer, default=0)

class Partner(db.Model, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo_path = db.Column(db.String(255))
    icon_name = db.Column(db.String(50))
    link = db.Column(db.String(255), default="#")
    order = db.Column(db.Integer, default=0)

class Lead(db.Model, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(50))
    budget = db.Column(db.String(50))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="New") # New, Contacted, Completed
