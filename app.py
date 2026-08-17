import os
import random
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, SiteSettings, Stat, AboutInfo, Service, PortfolioItem, Testimonial, SocialLink, Partner, Lead, FaqItem, ProcessStep
from datetime import datetime
import config

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
    return db.session.get(User, int(user_id))

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
        if not hasattr(settings, 'hero_trust_text') or not settings.hero_trust_text: settings.hero_trust_text = "Platforms & tools I work in"
    
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
            Service(title="Email Marketing Strategy", icon_name="bolt", description="Data-driven strategies that turn subscribers into loyal customers.", category="email", order=1),
            Service(title="Advanced Automation", icon_name="robot", description="Sophisticated flows that nurture leads and drive revenue on autopilot.", category="email", order=2),
            Service(title="UI/UX Design", icon_name="pen-nib", description="High-converting landing pages and email designs that wow your audience.", category="uiux", order=3),
            Service(title="Web Development", icon_name="code", description="Modern, responsive websites built with the latest technologies.", category="webdev", order=4),
            Service(title="Analytics & Reporting", icon_name="chart-line", description="Detailed insights and performance tracking for every campaign.", category="email", order=5),
            Service(title="A/B Testing", icon_name="flask", description="Continuous optimization to ensure your emails are always performing.", category="email", order=6)
        ]
        db.session.add_all(services)

    if not PortfolioItem.query.first():
        items = [
            PortfolioItem(title="News Newsletter Performance Overhaul", category="Publishing / Media", result_text="+38% CTR", summary="Redesigned content structure and optimization to drive higher click-through rates.", image_path="https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=1200&auto=format&fit=crop", order=1),
            PortfolioItem(title="Deliverability Rescue for an Irish Retailer", category="E-Commerce", result_text="Inbox Recovery", summary="Identified spam trap issues and rebuilt sender reputation to restore inbox placement.", image_path="https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=1200&auto=format&fit=crop", order=2),
            PortfolioItem(title="Sender Reputation Rebuild — Action Sports Brand", category="DTC / Merch", result_text="70K List", summary="Cleaned up a large list and implemented sunset flows to maintain high engagement.", image_path="https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=1200&auto=format&fit=crop", order=3),
            PortfolioItem(title="Wholesale Plumbing Supplier Campaign Build", category="B2B Wholesale", result_text="Hero Product Campaign", summary="Built high-converting B2B campaigns to drive bulk orders of a hero product.", image_path="https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=1200&auto=format&fit=crop", order=4),
            PortfolioItem(title="Newsletter Programme for a Luxury Studio", category="Beauty / Services", result_text="Multi-Location", summary="Created a unified newsletter template system scalable across multiple locations.", image_path="https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=1200&auto=format&fit=crop", order=5),
            PortfolioItem(title="Corporate Gifting Email Template Build", category="B2B Corporate", result_text="Template System", summary="Developed a modular, responsive template system to accelerate campaign production.", image_path="https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=1200&auto=format&fit=crop", order=6)
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
            SocialLink(platform="LinkedIn", icon_name="linkedin-in", link="#", order=1),
            SocialLink(platform="Twitter", icon_name="x-twitter", link="#", order=2),
            SocialLink(platform="Facebook", icon_name="facebook-f", link="#", order=3)
        ]
        db.session.add_all(socials)
        
    if not Partner.query.first():
        partners = [
            Partner(name="Mailchimp", icon_name="mailchimp", order=1),
            Partner(name="Klaviyo", icon_name="envelope-open-text", order=2),
            Partner(name="Shopify", icon_name="shopify", order=3),
            Partner(name="Amazon", icon_name="amazon", order=4),
            Partner(name="Google", icon_name="google", order=5),
            Partner(name="Meta", icon_name="meta", order=6),
            Partner(name="HubSpot", icon_name="hubspot", order=7),
            Partner(name="Salesforce", icon_name="salesforce", order=8)
        ]
        db.session.add_all(partners)

    if not FaqItem.query.first():
        faqs = [
            FaqItem(question="Why are my emails going to spam?", answer="Usually one of four causes: an unauthenticated sending domain (missing SPF, DKIM, or DMARC), a list with high inactivity, sending volume that spikes unnaturally, or poor engagement signals. An audit identifies which applies to you.", order=1),
            FaqItem(question="Should I use Mailchimp or Klaviyo?", answer="Klaviyo is generally stronger for Shopify and WooCommerce stores that need deep purchase-behaviour automation. Mailchimp is more cost-effective for content newsletters, B2B, and service businesses. I work in both and will recommend based on your setup, not my preference.", order=2),
            FaqItem(question="How much does this cost?", answer="Audits start at $299. Ongoing retainers start at $350/month. Full platform builds are quoted per project after a discovery call.", order=3),
            FaqItem(question="How long does deliverability recovery take?", answer="Typically 4 to 12 weeks. Sender reputation rebuilds gradually through consistent, well-targeted sending — anyone promising a fix in days is not being straight with you.", order=4),
            FaqItem(question="Do you work with my timezone?", answer="Yes. I work with clients across the US, UK, EU, and Middle East, and schedule calls in your local time.", order=5),
            FaqItem(question="Can you take over an existing account?", answer="Yes. I regularly audit and take over accounts built by previous agencies or freelancers.", order=6)
        ]
        db.session.add_all(faqs)

    if not ProcessStep.query.first():
        steps = [
            ProcessStep(step_number="01", label="Audit", title="Find what's actually broken", description="I review your sending domain, authentication records, list health, and campaign history — then tell you plainly which of those is costing you money.", deliverable="a written audit with prioritised fixes", order=1),
            ProcessStep(step_number="02", label="Strategy", title="Agree the plan before any build", description="We settle scope, timeline, and what success looks like in numbers. You approve it in writing, so nothing gets built that you didn't ask for.", deliverable="a scoped plan with fixed dates", order=2),
            ProcessStep(step_number="03", label="Build", title="Ship it, tested everywhere", description="Flows, templates, segments, and domain authentication — built by hand in table-based HTML and checked in Gmail, Outlook, and Apple Mail before it goes live.", deliverable="a live, documented setup you own", order=3),
            ProcessStep(step_number="04", label="Report", title="Know what worked, monthly", description="A plain-English report every month: what performed, what didn't, and the two or three things I'd change next. No dashboards you'll never open.", deliverable="a monthly PDF with next steps", order=4),
        ]
        db.session.add_all(steps)
        
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
    partners = Partner.query.order_by(Partner.order).all()
    faqs = FaqItem.query.order_by(FaqItem.order).all()
    process_steps = ProcessStep.query.order_by(ProcessStep.order).all()
    return render_template('index.html', 
                         settings=settings, 
                         about=about, 
                         stats=stats, 
                         services=services, 
                         portfolio=portfolio,
                         testimonials=testimonials,
                         social_links=social_links,
                         partners=partners,
                         faqs=faqs,
                         process_steps=process_steps)

@app.route('/privacy-policy')
def privacy_policy():
    settings = SiteSettings.query.first()
    social_links = SocialLink.query.order_by(SocialLink.order).all()
    return render_template('privacy_policy.html', settings=settings, social_links=social_links)

@app.context_processor
def inject_global_data():
    settings = SiteSettings.query.first()
    social_links = SocialLink.query.order_by(SocialLink.order).all()
    return dict(settings=settings, social_links=social_links)

# --- Email Helper ---
def send_email(subject, body, to_email):
    sender_email = config.EMAIL_USER
    sender_password = config.EMAIL_PASS
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))
    
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# --- Admin Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            # Generate 6-digit OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            session['otp'] = otp
            session['pending_user_id'] = user.id
            
            settings = SiteSettings.query.first()
            target_email = settings.contact_email if settings and settings.contact_email else "skahmed0912@gmail.com"
            
            email_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                <h2 style="color: #008080; text-align: center;">Login Verification Code</h2>
                <p>Hello,</p>
                <p>You are receiving this email because a login attempt was made to your portfolio admin dashboard.</p>
                <div style="background-color: #f9f9f9; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #333;">{otp}</span>
                </div>
                <p>This code will expire shortly. If you did not make this request, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #888; text-align: center;">&copy; {datetime.now().year} Shakil Ahmed Portfolio</p>
            </div>
            """
            
            if send_email("Your Admin Login OTP", email_body, target_email):
                flash('An OTP has been sent to your contact email.', 'info')
                return redirect(url_for('verify_otp'))
            else:
                flash('Error sending OTP. Please check your email configuration.', 'danger')
        else:
            flash('Invalid username or password', 'danger')
    return render_template('admin/login.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'pending_user_id' not in session or 'otp' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        input_otp = request.form.get('otp')
        if input_otp == session.get('otp'):
            user = db.session.get(User, session.get('pending_user_id'))
            if user:
                login_user(user)
                session.pop('otp', None)
                session.pop('pending_user_id', None)
                return redirect(url_for('admin_dashboard'))
        flash('Invalid OTP. Please try again.', 'danger')
        
    return render_template('admin/verify_otp.html')

@app.route('/submit_lead', methods=['POST'])
def submit_lead():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    whatsapp = request.form.get('whatsapp')
    budget = request.form.get('budget')
    details = request.form.get('details')
    
    if not full_name or not email:
        return jsonify({"success": False, "message": "Name and Email are required"}), 400
        
    new_lead = Lead(
        full_name=full_name,
        email=email,
        whatsapp=whatsapp,
        budget=budget,
        details=details
    )
    db.session.add(new_lead)
    db.session.commit()
    
    # Send Notification Email
    target_email = "info@zeplostudio.com"
    
    lead_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h2 style="color: #008080;">New Lead Received!</h2>
        <p>A new potential client has contacted you through your portfolio website.</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold; width: 30%;">Full Name:</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{full_name}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Email:</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{email}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Budget:</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{budget}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Details:</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{details}</td>
            </tr>
        </table>
        <p style="margin-top: 20px;">Check your admin dashboard for more details.</p>
    </div>
    """
    send_email(f"New Lead: {full_name}", lead_body, target_email)
    
    return jsonify({"success": True, "message": "We have received your message!"})

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
    partners = Partner.query.all()
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    faqs = FaqItem.query.order_by(FaqItem.order).all()
    process_steps = ProcessStep.query.order_by(ProcessStep.order).all()
    return render_template('admin/dashboard.html', 
                         settings=settings, 
                         stats=stats, 
                         about=about, 
                         services=services, 
                         portfolio=portfolio,
                         testimonials=testimonials,
                         social_links=social_links,
                         partners=partners,
                         leads=leads,
                         faqs=faqs,
                         process_steps=process_steps)

# --- CRUD Routes ---

@app.route('/admin/update_settings', methods=['POST'])
@login_required
def update_settings():
    settings = SiteSettings.query.first()
    settings.hero_eyebrow = request.form.get('hero_eyebrow')
    settings.hero_title = request.form.get('hero_title')
    settings.hero_subtext = request.form.get('hero_subtext')
    settings.hero_trust_text = request.form.get('hero_trust_text')
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
    item = PortfolioItem(title=request.form.get('title'), category=request.form.get('category'), result_text=request.form.get('result_text'), summary=request.form.get('summary'), link=request.form.get('link'), order=request.form.get('order'))
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

@app.route('/admin/partner/add', methods=['POST'])
@login_required
def add_partner():
    p = Partner(name=request.form.get('name'), icon_name=request.form.get('icon_name'), link=request.form.get('link'), order=request.form.get('order'))
    if 'logo' in request.files:
        file = request.files['logo']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            p.logo_path = url_for('static', filename='uploads/' + filename)
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/partner/delete/<int:id>')
@login_required
def delete_partner(id):
    p = Partner.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/stat/update/<int:id>', methods=['POST'])
@login_required
def update_stat(id):
    stat = Stat.query.get_or_404(id)
    stat.label = request.form.get('label')
    stat.value = request.form.get('value')
    stat.suffix = request.form.get('suffix')
    stat.order = request.form.get('order')
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/service/update/<int:id>', methods=['POST'])
@login_required
def update_service(id):
    service = Service.query.get_or_404(id)
    service.title = request.form.get('title')
    service.description = request.form.get('description')
    service.icon_name = request.form.get('icon_name')
    service.category = request.form.get('category')
    service.order = request.form.get('order')
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/portfolio/update/<int:id>', methods=['POST'])
@login_required
def update_portfolio(id):
    item = PortfolioItem.query.get_or_404(id)
    item.title = request.form.get('title')
    item.category = request.form.get('category')
    item.result_text = request.form.get('result_text')
    item.summary = request.form.get('summary')
    item.link = request.form.get('link')
    item.order = request.form.get('order')
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image_path = url_for('static', filename='uploads/' + filename)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/testimonial/update/<int:id>', methods=['POST'])
@login_required
def update_testimonial(id):
    t = Testimonial.query.get_or_404(id)
    t.client_name = request.form.get('client_name')
    t.client_role = request.form.get('client_role')
    t.content = request.form.get('content')
    t.order = request.form.get('order')
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            t.image_path = url_for('static', filename='uploads/' + filename)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/social/update/<int:id>', methods=['POST'])
@login_required
def update_social(id):
    s = SocialLink.query.get_or_404(id)
    s.platform = request.form.get('platform')
    s.icon_name = request.form.get('icon_name')
    s.link = request.form.get('link')
    s.order = request.form.get('order')
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/partner/update/<int:id>', methods=['POST'])
@login_required
def update_partner(id):
    p = Partner.query.get_or_404(id)
    p.name = request.form.get('name')
    p.icon_name = request.form.get('icon_name')
    p.link = request.form.get('link')
    p.order = request.form.get('order')
    if 'logo' in request.files:
        file = request.files['logo']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            p.logo_path = url_for('static', filename='uploads/' + filename)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/lead/delete/<int:id>')
@login_required
def delete_lead(id):
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    flash('Lead deleted successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/faq/add', methods=['POST'])
@login_required
def add_faq():
    faq = FaqItem(question=request.form.get('question'), answer=request.form.get('answer'), order=request.form.get('order'))
    db.session.add(faq)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/faq/delete/<int:id>')
@login_required
def delete_faq(id):
    faq = FaqItem.query.get_or_404(id)
    db.session.delete(faq)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/faq/update/<int:id>', methods=['POST'])
@login_required
def update_faq(id):
    faq = FaqItem.query.get_or_404(id)
    faq.question = request.form.get('question')
    faq.answer = request.form.get('answer')
    faq.order = request.form.get('order')
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/process/add', methods=['POST'])
@login_required
def add_process_step():
    step = ProcessStep(
        step_number=request.form.get('step_number'),
        label=request.form.get('label'),
        title=request.form.get('title'),
        description=request.form.get('description'),
        deliverable=request.form.get('deliverable'),
        order=request.form.get('order', 0)
    )
    db.session.add(step)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/process/delete/<int:id>')
@login_required
def delete_process_step(id):
    step = ProcessStep.query.get_or_404(id)
    db.session.delete(step)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/process/update/<int:id>', methods=['POST'])
@login_required
def update_process_step(id):
    step = ProcessStep.query.get_or_404(id)
    step.step_number = request.form.get('step_number')
    step.label = request.form.get('label')
    step.title = request.form.get('title')
    step.description = request.form.get('description')
    step.deliverable = request.form.get('deliverable')
    step.order = request.form.get('order', 0)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/sitemap.xml')
def sitemap():
    settings = SiteSettings.query.first()
    # Simple dynamic sitemap
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Homepage
    xml += '  <url>\n'
    xml += '    <loc>https://zeplostudio.com/</loc>\n'
    xml += '    <changefreq>weekly</changefreq>\n'
    xml += '    <priority>1.0</priority>\n'
    xml += '  </url>\n'
    
    # Services section
    xml += '  <url>\n'
    xml += '    <loc>https://zeplostudio.com/#services</loc>\n'
    xml += '    <changefreq>monthly</changefreq>\n'
    xml += '    <priority>0.8</priority>\n'
    xml += '  </url>\n'
    
    xml += '</urlset>'
    return app.response_class(xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: https://zeplostudio.com/sitemap.xml\n"
    return app.response_class(content, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
