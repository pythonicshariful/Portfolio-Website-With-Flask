import sqlite3
import os

# 1. Update schema via raw sqlite3 BEFORE importing app
# This prevents app.py from crashing on startup when it queries the DB
db_path = 'instance/portfolio.db'
if not os.path.exists(db_path):
    db_path = 'portfolio.db'

print(f"Applying schema updates to {db_path}...")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('ALTER TABLE site_settings ADD COLUMN hero_trust_text VARCHAR(255) DEFAULT "Platforms & tools I work in"')
        print("- Added hero_trust_text column.")
    except sqlite3.OperationalError as e:
        print("- hero_trust_text:", e)

    try:
        cursor.execute('ALTER TABLE portfolio_item ADD COLUMN summary VARCHAR(500)')
        print("- Added summary column.")
    except sqlite3.OperationalError as e:
        print("- summary:", e)

    conn.commit()
    conn.close()
except Exception as e:
    print(f"Error updating schema: {e}")

print("Schema updated. Now loading Flask app to seed data...")

# 2. Now it's safe to import app and models
from app import app, db
from models import SiteSettings, PortfolioItem

with app.app_context():
    # Update existing settings
    settings = SiteSettings.query.first()
    if settings and not settings.hero_trust_text:
        settings.hero_trust_text = "Platforms & tools I work in"
        db.session.commit()
        
    # Replace Portfolio Items
    PortfolioItem.query.delete()
    
    items = [
        PortfolioItem(title="News Newsletter Performance Overhaul", category="Publishing / Media", result_text="+38% CTR", summary="Redesigned content structure and optimization to drive higher click-through rates.", image_path="https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=1200&auto=format&fit=crop", order=1),
        PortfolioItem(title="Deliverability Rescue for an Irish Retailer", category="E-Commerce", result_text="Inbox Recovery", summary="Identified spam trap issues and rebuilt sender reputation to restore inbox placement.", image_path="https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=1200&auto=format&fit=crop", order=2),
        PortfolioItem(title="Sender Reputation Rebuild — Action Sports Brand", category="DTC / Merch", result_text="70K List", summary="Cleaned up a large list and implemented sunset flows to maintain high engagement.", image_path="https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=1200&auto=format&fit=crop", order=3),
        PortfolioItem(title="Wholesale Plumbing Supplier Campaign Build", category="B2B Wholesale", result_text="Hero Product Campaign", summary="Built high-converting B2B campaigns to drive bulk orders of a hero product.", image_path="https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=1200&auto=format&fit=crop", order=4),
        PortfolioItem(title="Newsletter Programme for a Luxury Studio", category="Beauty / Services", result_text="Multi-Location", summary="Created a unified newsletter template system scalable across multiple locations.", image_path="https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=1200&auto=format&fit=crop", order=5),
        PortfolioItem(title="Corporate Gifting Email Template Build", category="B2B Corporate", result_text="Template System", summary="Developed a modular, responsive template system to accelerate campaign production.", image_path="https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=1200&auto=format&fit=crop", order=6)
    ]
    db.session.add_all(items)
    db.session.commit()
    
    print("Migration and data seeding completed successfully!")
