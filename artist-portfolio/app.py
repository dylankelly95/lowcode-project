import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, abort, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-placeholder'
DATABASE = os.path.join(app.root_path, 'portfolio.db')


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    with open(os.path.join(app.root_path, 'schema.sql'), mode='r') as f:
        conn.executescript(f.read())
    conn.close()


@app.route('/')
def index():
    conn = get_db()
    portfolio = conn.execute('SELECT * FROM portfolios LIMIT 1').fetchone()
    
    featured_work = conn.execute(
        'SELECT * FROM work_items WHERE is_featured = 1 ORDER BY created_at DESC'
    ).fetchall()
    
    projects = conn.execute(
        'SELECT * FROM projects ORDER BY created_at DESC'
    ).fetchall()
    
    conn.close()
    return render_template('index.html', portfolio=portfolio, featured_work=featured_work, projects=projects)


@app.route('/projects')
def list_projects():
    conn = get_db()
    projects = conn.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('projects.html', projects=projects)


@app.route('/projects/new', methods=['GET'])
def new_project_form():
    return render_template('project_form.html')


@app.route('/projects', methods=['POST'])
def create_project():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('Project title is required.')
        return render_template('project_form.html', title=title, description=description), 400
        
    if len(title) > 200:
        flash('Project title must be 200 characters or fewer.')
        return render_template('project_form.html', title=title, description=description), 400

    conn = get_db()
    portfolio = conn.execute('SELECT id FROM portfolios LIMIT 1').fetchone()
    portfolio_id = portfolio['id'] if portfolio else 1
    
    conn.execute(
        'INSERT INTO projects (portfolio_id, title, description) VALUES (?, ?, ?)',
        (portfolio_id, title, description)
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for('list_projects'))


@app.route('/projects/<int:project_id>')
def project_detail(project_id):
    conn = get_db()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    
    if project is None:
        conn.close()
        abort(404)
        
    work_items = conn.execute(
        'SELECT * FROM work_items WHERE project_id = ? ORDER BY created_at DESC', (project_id,)
    ).fetchall()
    conn.close()
    
    return render_template('project_detail.html', project=project, work_items=work_items)


@app.route('/work')
def list_work():
    conn = get_db()
    work_items = conn.execute(
        'SELECT w.*, p.title as project_title FROM work_items w LEFT JOIN projects p ON w.project_id = p.id ORDER BY w.created_at DESC'
    ).fetchall()
    conn.close()
    return render_template('work.html', work_items=work_items)


@app.route('/work/new', methods=['GET'])
def new_work_form():
    conn = get_db()
    projects = conn.execute('SELECT id, title FROM projects ORDER BY title ASC').fetchall()
    conn.close()
    return render_template('work_form.html', projects=projects)


@app.route('/work', methods=['POST'])
def create_work():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    media_type = request.form.get('media_type', '').strip()
    media_url = request.form.get('media_url', '').strip()
    project_id_raw = request.form.get('project_id', '').strip()
    is_featured = 1 if request.form.get('is_featured') else 0
    
    project_id = int(project_id_raw) if project_id_raw.isdigit() else None
    
    conn = get_db()
    projects = conn.execute('SELECT id, title FROM projects ORDER BY title ASC').fetchall()
    
    if not title:
        flash('Work item title is required.')
        conn.close()
        return render_template('work_form.html', projects=projects), 400
        
    if len(title) > 200:
        flash('Title must be 200 characters or fewer.')
        conn.close()
        return render_template('work_form.html', projects=projects), 400

    allowed_types = ['image', 'video', 'audio', 'link']
    if media_type and media_type not in allowed_types:
        flash('Invalid media type selected.')
        conn.close()
        return render_template('work_form.html', projects=projects), 400

    conn.execute(
        'INSERT INTO work_items (project_id, title, description, media_type, media_url, is_featured) VALUES (?, ?, ?, ?, ?, ?)',
        (project_id, title, description, media_type, media_url, is_featured)
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for('list_work'))


@app.route('/work/<int:work_id>')
def work_detail(work_id):
    conn = get_db()
    work_item = conn.execute(
        'SELECT w.*, p.title as project_title FROM work_items w LEFT JOIN projects p ON w.project_id = p.id WHERE w.id = ?',
        (work_id,)
    ).fetchone()
    conn.close()
    
    if work_item is None:
        abort(404)
        
    return render_template('work_detail.html', work_item=work_item)


@app.route('/work/<int:work_id>/feature', methods=['POST'])
def toggle_feature(work_id):
    conn = get_db()
    work_item = conn.execute('SELECT * FROM work_items WHERE id = ?', (work_id,)).fetchone()
    
    if work_item is None:
        conn.close()
        abort(404)
        
    new_status = 0 if work_item['is_featured'] == 1 else 1
    conn.execute('UPDATE work_items SET is_featured = ? WHERE id = ?', (new_status, work_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('work_detail', work_id=work_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', content="<h2>404 — Page Not Found</h2><p>The requested resource does not exist.</p>"), 404


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)