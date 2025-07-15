import os
from math import ceil
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, abort, session
from app.models import db
from datetime import datetime, timedelta

views = Blueprint('views', __name__)

DESIGNER_FOLDER = r"C:\Users\ASUS\Downloads\designs_loc"
USERNAME = 'admin'
PASSWORD = 'pass123'

# ---------------------------
# Auth Middleware
# ---------------------------
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("views.login"))
        return func(*args, **kwargs)
    return wrapper

# ---------------------------
# Login & Logout
# ---------------------------
@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('views.dashboard'))
        return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@views.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('views.login'))

# ---------------------------
# Dashboard
# ---------------------------
@views.route('/')
@login_required
def dashboard():
    designers = [
        name for name in os.listdir(DESIGNER_FOLDER)
        if os.path.isdir(os.path.join(DESIGNER_FOLDER, name))
    ]
    return render_template('dashboard.html', designers=designers)

# ---------------------------
# Designer Summary with KPIs + Chart
# ---------------------------
@views.route('/designer/<designer_name>/summary')
@login_required
def designer_summary(designer_name):
    filter_type = request.args.get('filter', '')  # "", "weekly", "monthly"
    folder_path = os.path.join(DESIGNER_FOLDER, designer_name)
    if not os.path.exists(folder_path):
        return abort(404)

    now = datetime.now()
    time_cutoff = None

    if filter_type == 'weekly':
        time_cutoff = now - timedelta(days=7)
    elif filter_type == 'monthly':
        time_cutoff = now - timedelta(days=30)

    subfolder_stats = {}

    for root, _, files in os.walk(folder_path):
        rel_path = os.path.relpath(root, folder_path)
        subfolder = rel_path if rel_path != '.' else 'Root'

        for file in files:
            if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            file_path = os.path.join(root, file)
            created_at = datetime.fromtimestamp(os.path.getctime(file_path))
            
            # ⛔ Skip files outside the time window
            if time_cutoff and created_at < time_cutoff:
                continue

            suit_status, dupatta_status = db.get_status(designer_name, file)

            if subfolder not in subfolder_stats:
                subfolder_stats[subfolder] = {'total': 0, 'passed': 0, 'pending': 0}

            subfolder_stats[subfolder]['total'] += 1
            if suit_status == 'All ok' and dupatta_status == 'All ok':
                subfolder_stats[subfolder]['passed'] += 1
            else:
                subfolder_stats[subfolder]['pending'] += 1

    total = sum(v['total'] for v in subfolder_stats.values())
    passed = sum(v['passed'] for v in subfolder_stats.values())
    pending = sum(v['pending'] for v in subfolder_stats.values())

    return render_template(
        'designer_summary.html',
        designer=designer_name,
        subfolder_stats=subfolder_stats,
        total=total,
        passed=passed,
        pending=pending,
        filter=filter_type  
    )

# ---------------------------
# Gallery View for Any Subfolder (Root or Nested)
# ---------------------------
@views.route('/designer/<designer_name>/', defaults={'subfolder': ''})
@views.route('/designer/<designer_name>/<path:subfolder>')
@login_required
def designer_gallery(designer_name, subfolder):
    folder_path = os.path.normpath(os.path.join(DESIGNER_FOLDER, designer_name, subfolder))
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return abort(404)


    search_query = request.args.get('q', '').lower()
    suit_filter = request.args.get('suit_filter', '')
    dupatta_filter = request.args.get('dupatta_filter', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    status_options = ['All ok', '1 colour ok', '2 colour ok', '3 colour ok', '4 colour ok', 'all pending']

    images = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            if search_query and search_query not in file.lower():
                continue

            suit_status, dupatta_status = db.get_status(designer_name, file)
            if suit_filter and suit_status != suit_filter:
                continue
            if dupatta_filter and dupatta_status != dupatta_filter:
                continue

            file_path = os.path.join(folder_path, file)
            created_at = os.path.getctime(file_path)
            upload_date = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d')

            images.append({
                'name': file,
                'suit_status': suit_status,
                'dupatta_status': dupatta_status,
                'upload_date': upload_date
            })

    total = len(images)
    total_pages = ceil(total / per_page)
    paginated_images = images[(page - 1) * per_page: page * per_page]

    return render_template('designer_gallery.html',
                           designer=designer_name,
                           subfolder=subfolder,
                           images=paginated_images,
                           search_query=search_query,
                           suit_filter=suit_filter,
                           dupatta_filter=dupatta_filter,
                           page=page,
                           total_pages=total_pages,
                           status_options=status_options)

# ---------------------------
# Serve Individual Images
# ---------------------------
@views.route('/images/<designer>/<path:filename>')
@login_required
def image(designer, filename):
    base_path = os.path.join(DESIGNER_FOLDER, designer)
    full_path = os.path.join(base_path, filename)
    if os.path.exists(full_path):
        return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path))
    return abort(404)

# ---------------------------
# Update Suit/Dupatta Status
# ---------------------------
@views.route('/update_status/<designer_name>/<image_name>', methods=['POST'])
@login_required
def update_image_status(designer_name, image_name):
    suit_status = request.form.get('suit_status')
    dupatta_status = request.form.get('dupatta_status')
    db.update_status(designer_name, image_name, suit_status, dupatta_status)
    return redirect(request.referrer or url_for('views.dashboard'))

@views.route('/api/upload', methods=['POST'])
def api_upload():
    auth_token = request.headers.get('Authorization')
    if auth_token != 'secret_api_key':
        return {'error': 'Unauthorized'}, 401

    designer = request.form['designer']
    subfolder = request.form.get('subfolder', 'Root')
    image = request.files['image']

    save_path = os.path.join(DESIGNER_FOLDER, designer, subfolder)
    os.makedirs(save_path, exist_ok=True)

    image.save(os.path.join(save_path, image.filename))
    return {'status': 'success'}, 200
