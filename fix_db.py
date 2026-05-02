from app import app, db
from models import SiteSettings, AboutInfo, Stat, Service, PortfolioItem, Testimonial, SocialLink

with app.app_context():
    db.create_all()
    
    if not SiteSettings.query.first():
        s = SiteSettings(
            meta_title='Shakil Ahmed | Email Marketing Expert',
            meta_description='Professional email marketing expert.',
            hero_title="I Help Brands Scale with <span class='text-teal'>Email Marketing</span>",
            hero_subtext='Expert strategies and high-performance designs to turn your subscribers into loyal customers.',
            contact_phone='+880 1234 567 890',
            contact_email='hello@theshakil.com',
            cv_link='#',
            fiverr_link='#'
        )
        db.session.add(s)
        print("Created SiteSettings")

    if not AboutInfo.query.first():
        a = AboutInfo(
            title='Passionate About Results',
            content='I specialize in building email marketing ecosystems that don’t just look good, but drive significant revenue growth.',
            image_path='/static/images/profile.png'
        )
        db.session.add(a)
        print("Created AboutInfo")

    db.session.commit()
    print("Database fix completed")
