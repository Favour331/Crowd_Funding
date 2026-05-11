import os
import mysql.connector
import random
import datetime
from flask import Flask, Blueprint, flash, render_template, jsonify, request, session, redirect, url_for, send_file, current_app
from functools import wraps
from werkzeug.utils import secure_filename
from routes.decorators import login_required
from routes.backings import new_pledge
from services.project_service import get_dashboard_data,get_each_projects,get_all_projects
from services.backing_service import create_backing, get_backings_for_project, fetch_user_profile

projects_bp = Blueprint("project", __name__)
projects_bp.secret_key = 'Project_key'

#########CREATOR SIDE###################

def project_owner_required(f):
    @wraps(f)
    def decorated_function(project_id, *args, **kwargs):
        conn = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
        cur = conn.cursor(dictionary=True)
        cur.execute("Select Creator_Id From Projects Where id = %s", (project_id,))
        project = cur.fetchone()
        cur.close()
        conn.close()
        if not project or project['Creator_Id'] != session.get('user_id'):
            return jsonify({"Error": "Access Denied"}), 403
        return f(project_id, *args, **kwargs)
    return decorated_function


@login_required
@projects_bp.route('/projects/create_project')
def to_creator():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please login first")
        return render_template("auth/login.html")
    
    return render_template('projects/create.html')
    
@projects_bp.route('/projects/explore')
def explore():
    return redirect('/projects')
    
@projects_bp.route('/projects/my_projects')
def list_projects():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login first')
        return render_template('auth/login.html')
    
    # Get complete dashboard data
    data = get_dashboard_data(user_id)
    
    if not data:
        flash('User not found')
        return redirect('/login')
    
    return render_template('projects/list.html', datas=data)

@projects_bp.route('/projects/list/active/<int:id>')
def active_projects(id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login first')
        return render_template('auth/login.html')
        
    conn1 = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    conn2 = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    cur1.execute("SELECT * FROM projects where creator_id = %s",(id,))
    cur2.execute("SELECT * FROM users WHERE Id = %s", (user_id,))
    rose = cur1.fetchall()
    rows = cur2.fetchall()
    cur1.close()
    cur2.close()
    conn1.close()
    return render_template('projects/active.html',roll=rose,row=rows)
    
    
@projects_bp.route('/projects/view/<int:Id>')
def view_projects(Id):
    user_id =  session.get('user_id')
    if not user_id:
        flash("Please Log in First")
        return render_template('auth/login.html')

    projects = projects_view(Id)
    return render_template('projects/view.html', projects=projects)

@projects_bp.route('/projects/edit')
def edit_project():
    user_id =  session.get('user_id')
    if not user_id:
        flash("Please Log in First")
        return render_template('auth/login.html')

    conn = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
    conn1 = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
    cur = conn.cursor()
    cur1 = conn1.cursor()
    cur.execute("SELECT * FROM projects LEFT JOIN users ON projects.creator_id = users.Id WHERE creator_id = %s", (user_id,))
    cur1.execute("SELECT * FROM users WHERE Id = %s", (user_id,))
    rose = cur.fetchall()
    curly = cur1.fetchall()
    cur.close()
    conn.close()
    return render_template('projects/edit.html', roll=rose, row=curly)

@projects_bp.route('/project/create', methods=['GET','POST'])
def new_project():
    creator_id = session.get('user_id')
    if not creator_id:
        flash('Please login first')
        return render_template('auth/login.html')

    if request.method == 'GET':
        return redirect(url_for('project.to_creator'))

    # POST: create project
    proj_id = random.randint(1, 1000000)
    title = (request.form.get('title') or '').strip()
    select = (request.form.get('select') or '').strip()
    short = (request.form.get('short') or '').strip()
    more = (request.form.get('more') or '').strip()
    goal = (request.form.get('goal') or '').strip()
    image_file = request.files.get('image')
    end = (request.form.get('end_date') or '').strip()
    risk = (request.form.get('risks') or '').strip()
    reward = (request.form.get('reward') or '').strip()

    def respond_error(message, status_code=400):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': message}), status_code
        flash(message)
        return render_template('projects/create.html')

    if not (title and more and goal and short and end and risk and reward):
        return respond_error('Missing form data')

    if not image_file or not image_file.filename:
        return respond_error('Please upload an image file')

    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    filename = secure_filename(image_file.filename)
    if '.' not in filename:
        return respond_error('Invalid image file name')

    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return respond_error('Only image files are allowed (png, jpg, jpeg, gif, webp)')

    try:
        if int(goal) <= 0:
            return respond_error('Funding goal must be a positive number')
    except ValueError:
        return respond_error('Invalid funding goal')

    try:
        deadline = datetime.datetime.strptime(end, '%Y-%m-%d').date()
        if deadline <= datetime.date.today(): 
            return respond_error('Deadline must be in the future')
    except ValueError:
        return respond_error('Invalid deadline format')

    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    image_name = f"project_{proj_id}_{int(datetime.datetime.now().timestamp())}.{extension}"
    image_path = os.path.join(upload_folder, image_name)
    image_url = f"/static/uploads/{image_name}"

    try:
        image_file.save(image_path)
    except Exception as e:
        return respond_error(f'Unable to save image: {str(e)}')

    try:
        conn = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO Projects(Id, Creator_Id, title, description, short_desc, category, funding_goal, main_image_url, risk_challenges, rewards, deadline, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (proj_id, creator_id, title, more, short, select, goal, image_url, risk, reward, deadline, 'Pending_review')
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return respond_error(f'Unable to save project: {str(e)}', 500)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Project submitted for review', 'redirect': url_for('project.list_projects')})

    flash('Project submitted for review')
    return redirect('/projects/my_projects')

@projects_bp.route('/projects/<int:project_id>/update', methods=['POST'])
@project_owner_required
def Update_project(project_id):
    data = request.get_json()
    allowed = ['title','description','short_desc','funding_goal','risks_challenges','rewards']
    fields = []
    values = []
    
    for field in allowed:
        if field in data:
            fields.append(f'{field} = %s')
            values.append(data[field])
            
    if not fields:
        flash('No Valid field to update')
        return jsonify({"message": "No fields to update"}), 400
    
    values.append(project_id)
    values.append(session['user_id'])
    
    conn = mysql.connector.connect(host='localhost', user='root', passwd='',database='crowd_funding')
    curs = conn.cursor()
    curs.execute(f"""UPDATE projects SET {', '.join(fields)} WHERE id = %s AND creator_id = %s AND status = 'draft'""", values)
    if curs.rowcount == 0:
        flash('Project not found or cannot be modified')
    conn.commit()
    curs.close()
    conn.close()
    flash('Project Updated successfully')
    return jsonify({"message": "Project updated"}), 200

########## USERS SIDE ##################3
@projects_bp.route('/projects')
def projects_see():

    user_id = session.get('user_id')

    if not user_id:
        flash("Please Login first")
        return render_template('auth/login.html')

    projects = get_all_projects()

    return render_template('user/utilities/projects.html',jects=projects, backer=user_id)

@projects_bp.route('/backers/projects/see/<int:id>')
def backer_get_each_projects(id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please Login first")
        return render_template('auth/login.html')
    
    row = get_each_projects(id)
    
    return render_template('user/utilities/more.html', roll=row, backer=user_id, ject=id)
    
@projects_bp.route("/like/<int:pid>", methods=['POST', 'DELETE'])    
def like_project(pid):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Please login first"}), 401
    
    connect = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    curry = connect.cursor()
    curry.execute("Select * from likes where backers_id = %s and project_id = %s",(user_id,pid))
    existing_like = curry.fetchall()
    curry.close()
    connect.close()
    
    # POST - Like the project
    if request.method == 'POST':
        if not existing_like:
            conn = mysql.connector.connect(host='localhost', user='root', passwd='',database='crowd_funding')
            cur = conn.cursor()
            cur.execute("Insert into likes (backers_id,project_id) Values(%s, %s)", (user_id,pid))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"success": True, "message": "Project liked successfully", "liked": True}), 200
        else:
            return jsonify({"success": False, "message": "You already liked this project", "liked": True}), 400
    
    # DELETE - Unlike the project
    elif request.method == 'DELETE':
        if existing_like:
            conn = mysql.connector.connect(host='localhost', user='root', passwd='',database='crowd_funding')
            cur = conn.cursor()
            cur.execute("Delete from likes where backers_id = %s and project_id = %s", (user_id,pid))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"success": True, "message": "Project unliked successfully", "liked": False}), 200
        else:
            return jsonify({"success": False, "message": "You haven't liked this project", "liked": False}), 400

@projects_bp.route("/backers/projects/see/comment/<int:id>")
def comments(id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please Login first")
        return render_template('auth/login.html')
    conx = mysql.connector.connect(host='localhost',user='root',passwd="",database='crowd_funding')
    curx = conx.cursor(dictionary=True)
    curx.execute('SELECT users.Id,users.username,comments.backers_id,comments.project_id,comments.Comments,comments.time_and_date FROM users LEFT JOIN comments ON users.Id = comments.backers_id where comments.project_id = %s',(id,))
    let = curx.fetchall()
    conx.commit()
    conx.close()
    return render_template('user/utilities/comments.html', comments=let, project_id=id,user=user_id)


@projects_bp.route('/backers/projects/see/comment/post/<int:id>', methods=['GET','POST'])
def post_comment(id):
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash("Please Login first")
            return render_template('auth/login.html')
        fer = 1
        comment = request.form.get('comment')
        if  str(comment).strip() < str(fer):
            flash('Comments cannot be empty')
            return redirect(f'/backers/projects/see/comment/{id}')

        conn = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
        cur = conn.cursor()
        cur.execute("Insert Into comments(backers_id,project_id,Comments) Values(%s,%s,%s)",(user_id,id,comment))
        conn.commit()
        cur.close()
        conn.commit()
        return redirect(f'/backers/projects/see/comment/{id}')
    return render_template('user/utilities/more.html')

@projects_bp.route('/backers/projects/new_pledge', methods=['POST'])
def back_project():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login first')
        return redirect('/login')

    email = request.form.get('email')
    amount_value = request.form.get('amount')
    project_id = request.form.get('project_id')

    # if not project_id or email or amount_value:
    #     flash('Missing required fields')
        # return redirect(request.referrer or url_for('project.list_projects'))

    try:
        project_id = int(project_id)
        amount = float(amount_value)
        if amount <= 0:
            raise ValueError('Amount must be positive')
    except (ValueError, TypeError) as e:
        flash('Invalid project ID or amount')
        return redirect(request.referrer or url_for('project.list_projects'))

    user_project = fetch_user_profile(user_id)
    if not user_project:
        flash('User not found')
        return redirect(request.referrer or url_for('project.list_projects'))

    if user_project.get('creator_id') == user_id:
            flash('Cannot pledge to your own project')
            return redirect(request.referrer or url_for('project.list_projects'))

    try:
        success = create_backing(user_id, project_id, amount, email)
        if not success:
            flash('Failed to create backing')
            return redirect(request.referrer or url_for('project.list_projects'))

        flash('Pledge successful')
        return redirect(request.referrer or url_for('project.list_projects'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash('Database error: ' + str(e))
        return redirect(request.referrer or url_for('project.list_projects'))



##################     ADMIN SIDE    #########################
@projects_bp.route('/admin/projects/view')
def get_projects():
    conn = mysql.connector.connect(host='localhost', user='root',passwd='',database='crowd_funding')
    cur = conn.cursor()
    cur.execute("Select * FROM projects where Status = %s",('pending_review',))
    row = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('admin/projects/projects.html',row=row)

@projects_bp.route('/admin/projects/view/<int:id>')
def one(id):
    conn = mysql.connector.connect(host='localhost', user='root',passwd='',database='crowd_funding')
    cur = conn.cursor()
    cur.execute("Select * FROM projects where Id = %s",(id,))
    row = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('admin/projects/view.html',roll=row)


@projects_bp.route('/admin/projects/view/<int:id>/approve')
def approve(id):
    conn = mysql.connector.connect(host='localhost', user='root',passwd='',database='crowd_funding')
    cur = conn.cursor()
    cur.execute("Update projects set Status = 'Active' where Id = %s",(id,))
    conn.commit()
    cur.close()
    conn.close()
    conn1 = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    conn2 = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    conn3 = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    conn4 = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    cur3 = conn3.cursor()
    cur4 = conn4.cursor()
    cur1.execute("Select COUNT(*) from users where role = 'Creator'")
    cur2.execute("Select COUNT(*) from users where role = 'Backer'")
    cur3.execute("Select COUNT(*) from projects where status ='pending_review'")
    cur4.execute("Select COUNT(*)from projects where status = 'active'")
    curt = cur1.fetchall()
    pels = cur2.fetchall()
    thrd = cur3.fetchall()
    frth = cur4.fetchall()
    conn1.commit()
    conn2.commit()
    conn3.commit()
    conn4.commit()
    cur1.close()
    cur2.close()
    cur3.close()
    cur4.close()
    conn1.close()
    conn2.close()
    conn3.close()
    conn4.close()
    cur.close()
    conn.close()
    return render_template('admin/projects/all.html',curls=curt, felt=pels, thrd=thrd,frth=frth)
