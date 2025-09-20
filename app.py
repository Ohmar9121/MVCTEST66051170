import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from controllers.crowdfunding_controller import CrowdfundingController
from config import Config
from datetime import datetime  # Add this import

app = Flask(__name__)
app.secret_key = 'crowdfunding_secret'

controller = CrowdfundingController()

if not os.path.exists(Config.PROJECTS_FILE):
    print("Creating sample data...")
    controller.initialize_sample_data()
else:
    print("Loading existing data...")
    controller.project_model.load_data()
    controller.reward_model.load_data()
    controller.user_model.load_data()
    controller.pledge_model.load_data()

# Add template filters
@app.template_filter('to_datetime')
def to_datetime_filter(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except:
        return datetime.now()

@app.context_processor
def utility_processor():
    return dict(now=datetime.now())
        
@app.route('/')
def index():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    sort_by = request.args.get('sort', 'deadline')
    
    projects = controller.get_projects(search, category, sort_by)
    
    return render_template('projects.html', 
                         projects=projects,
                         categories=Config.PROJECT_CATEGORIES,
                         search=search,
                         category=category,
                         sort_by=sort_by)

@app.route('/project/<project_id>')
def project_details(project_id):
    details = controller.get_project_details(project_id)
    if not details:
        flash("Project not found", "danger")
        return redirect(url_for('index'))
    
    return render_template('project_detail.html', **details)

@app.route('/stats')
def stats():
    successful, rejected = controller.get_stats()
    status_counts = controller.get_project_status_counts()
    
    return render_template('stats.html', 
                         successful_pledges=successful,
                         rejected_pledges=rejected,
                         failed_projects_count=status_counts['failed'],
                         successful_projects_count=status_counts['successful'],
                         active_projects_count=status_counts['active'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = controller.authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Login successful", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for('index'))

@app.route('/pledge/<project_id>', methods=['POST'])
def make_pledge(project_id):
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    reward_id = request.form.get('reward_id', '')
    
    try:
        amount = int(request.form.get('amount', 0))
    except:
        flash("Invalid amount", "danger")
        return redirect(url_for('project_details', project_id=project_id))
    
    result = controller.make_pledge(user_id, project_id, reward_id, amount)
    
    if result['success']:
        flash("Pledge successful!", "success")
    else:
        flash(f"Pledge failed: {result['message']}", "danger")
    
    return redirect(url_for('project_details', project_id=project_id))

if __name__ == '__main__':
    app.run(debug=True)