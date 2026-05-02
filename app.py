import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, SiteSettings, Stat, AboutInfo, Service, PortfolioItem, Testimonial, SocialLink

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'))
        db.session.add(admin)
    
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
    
    # Ensure new columns have defaults if they exist but are null
    if settings:
        if not settings.meta_title: settings.meta_title = "Shakil Ahmed | Email Marketing Expert"
        if not settings.meta_description: settings.meta_description = "Top-rated Email Marketing expert helping Ecommerce & SaaS brands scale revenue through automation."
    
    if not AboutInfo.query.first():
        about = AboutInfo(content="With years of expertise in e-commerce and SaaS, I help businesses turn their email lists into revenue-generating machines. My process combines data analysis, creative design, and technical automation.")
        db.session.add(about)
        
    if not Stat.query.first():
        stats = [
            Stat(label="Happy Clients", value=700, suffix="+", order=1),
            Stat(label="Projects Delivered", value=1000, suffix="+", order=2),
            Stat(label="5★ Reviews", value=490, suffix="+", order=3),
            Stat(label="Deliverability Focus", value=100, suffix="%", order=4)
        ]
        db.session.add_all(stats)
    
    if not Service.query.first():
        services = [
            Service(title="Automation Workflows", description="Sophisticated welcome, abandoned cart, and post-purchase sequences that convert.", icon_name="zap", category="email", order=1),
            Service(title="Newsletter Design", description="Beautiful, high-converting newsletter templates tailored to your brand voice.", icon_name="mail", category="email", order=2),
            Service(title="Audience Segmentation", description="Advanced list segmentation to ensure the right message reaches the right person.", icon_name="users", category="email", order=3)
        ]
        db.session.add_all(services)

    if not PortfolioItem.query.first():
        items = [
            PortfolioItem(title="Fashion Brand Retention Flow", category="Ecommerce", result_text="+47% REVENUE", image_path="https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=1200&auto=format&fit=crop", order=1),
            PortfolioItem(title="SaaS Onboarding Sequence", category="SaaS", result_text="24% CONVERSION", image_path="https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=1200&auto=format&fit=crop", order=2),
            PortfolioItem(title="Real Estate Lead Gen", category="Real Estate", result_text="$12k PROFIT", image_path="https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=1200&auto=format&fit=crop", order=3)
        ]
        db.session.add_all(items)

    if not Testimonial.query.first():
        testimonials = [
            Testimonial(client_name="Sarah Johnson", client_role="CEO, Bloom Decor", content="Shakil transformed our email marketing. Our revenue from automated flows jumped by 45% in just two months.", image_path="https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=150&h=150&fit=crop", order=1),
            Testimonial(client_name="Marcus Chen", client_role="Marketing Director, TechFlow", content="The most technical email marketer I've worked with. His setup is clean, professional, and delivers results.", image_path="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=150&h=150&fit=crop", order=2)
        ]
        db.session.add_all(testimonials)

    if not SocialLink.query.first():
        socials = [
            SocialLink(platform="LinkedIn", icon_name="linkedin", link="#", order=1),
            SocialLink(platform="Twitter", icon_name="twitter", link="#", order=2),
            SocialLink(platform="Facebook", icon_name="facebook", link="#", order=3)
        ]
        db.session.add_all(socials)
        
    db.session.commit()

# --- Public Routes ---

@app.route('/')
def index():
    settings = SiteSettings.query.first()
    about = AboutInfo.query.first()
    stats = Stat.query.order_by(Stat.order).all()
    services = Service.query.order_by(Service.order).all()
    portfolio = PortfolioItem.query.order_by(PortfolioItem.order).all()
    testimonials = Testimonial.query.order_by(Testimonial.order).all()
    social_links = SocialLink.query.order_by(SocialLink.order).all()
    return render_template('index.html', 
                         settings=settings, 
                         about=about, 
                         stats=stats, 
                         services=services, 
                         portfolio=portfolio,
                         testimonials=testimonials,
                         social_links=social_links)

@app.context_processor
def inject_global_data():
    settings = SiteSettings.query.first()
    social_links = SocialLink.query.order_by(SocialLink.order).all()
    return dict(settings=settings, social_links=social_links)

# --- Admin Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password')
    return render_template('admin/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    settings = SiteSettings.query.first()
    stats = Stat.query.all()
    about = AboutInfo.query.first()
    services = Service.query.all()
    portfolio = PortfolioItem.query.all()
    testimonials = Testimonial.query.all()
    social_links = SocialLink.query.all()
    return render_template('admin/dashboard.html', 
                         settings=settings, 
                         stats=stats, 
                         about=about, 
                         services=services, 
                         portfolio=portfolio,
                         testimonials=testimonials,
                         social_links=social_links)

# --- CRUD Routes ---

@app.route('/admin/update_settings', methods=['POST'])
@login_required
def update_settings():
    settings = SiteSettings.query.first()
    settings.hero_title = request.form.get('hero_title')
    settings.hero_subtext = request.form.get('hero_subtext')
    settings.cv_link = request.form.get('cv_link')
    settings.fiverr_link = request.form.get('fiverr_link')
    settings.contact_phone = request.form.get('contact_phone')
    settings.contact_email = request.form.get('contact_email')
    settings.meta_title = request.form.get('meta_title')
    settings.meta_description = request.form.get('meta_description')
    settings.google_analytics_id = request.form.get('google_analytics_id')
    db.session.commit()
    flash('Settings updated successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_about', methods=['POST'])
@login_required
def update_about():
    about = AboutInfo.query.first()
    about.title = request.form.get('title')
    about.content = request.form.get('content')
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            about.image_path = url_for('static', filename='uploads/' + filename)
    db.session.commit()
    flash('About section updated successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/stat/add', methods=['POST'])
@login_required
def add_stat():
    stat = Stat(label=request.form.get('label'), value=request.form.get('value'), suffix=request.form.get('suffix'), order=request.form.get('order'))
    db.session.add(stat)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/stat/delete/<int:id>')
@login_required
def delete_stat(id):
    stat = Stat.query.get_or_404(id)
    db.session.delete(stat)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/service/add', methods=['POST'])
@login_required
def add_service():
    service = Service(title=request.form.get('title'), description=request.form.get('description'), icon_name=request.form.get('icon_name'), category=request.form.get('category'), order=request.form.get('order'))
    db.session.add(service)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/service/delete/<int:id>')
@login_required
def delete_service(id):
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/portfolio/add', methods=['POST'])
@login_required
def add_portfolio():
    item = PortfolioItem(title=request.form.get('title'), category=request.form.get('category'), result_text=request.form.get('result_text'), link=request.form.get('link'), order=request.form.get('order'))
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image_path = url_for('static', filename='uploads/' + filename)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/portfolio/delete/<int:id>')
@login_required
def delete_portfolio(id):
    item = PortfolioItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/testimonial/add', methods=['POST'])
@login_required
def add_testimonial():
    t = Testimonial(client_name=request.form.get('client_name'), client_role=request.form.get('client_role'), content=request.form.get('content'), order=request.form.get('order'))
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            t.image_path = url_for('static', filename='uploads/' + filename)
    db.session.add(t)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/testimonial/delete/<int:id>')
@login_required
def delete_testimonial(id):
    t = Testimonial.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/social/add', methods=['POST'])
@login_required
def add_social():
    s = SocialLink(platform=request.form.get('platform'), icon_name=request.form.get('icon_name'), link=request.form.get('link'), order=request.form.get('order'))
    db.session.add(s)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/social/delete/<int:id>')
@login_required
def delete_social(id):
    s = SocialLink.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
