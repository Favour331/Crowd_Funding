from flask import Flask,Blueprint,flash,render_template,jsonify,request,session,redirect,url_for,send_file
import mysql.connector
import random
from functools import wraps
import datetime

projects_bp = Blueprint("project", __name__)
projects_bp.secret_key = 'Project_key'

#########CREATOR SIDE###################

def project_owner_required(f):
    @wraps(f)
    def decorated_function(project_id, *args, **kwargs):
        conn = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
        cur = conn.cursor()
        cur.execute("Select Creator_Id From Projects Where id = %s",(project_id))
        project = cur.fetchone()
        if not project or project['Creator_Id'] != session.get('user_id'):
            return jsonify({"Error": "Access Denied"}), 403
        return f(project_id, *args, **kwargs)
    return decorated_function

@projects_bp.route('/projects/to_creator')
def to_creator():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login first')
        return render_template('auth/register.html')
    
    conn1 = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    cur1 = conn1.cursor()
    cur1.execute("SELECT * FROM users WHERE Id = %s", (user_id,))
    rows = cur1.fetchall()
    cur1.close()
    conn1.close()
    return render_template('projects/create.html', row=rows)

@projects_bp.route('/projects/list')
def list_projects():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login first')
        return render_template('auth/login.html')
    
    conn2 = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    conn3 = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    conn4 = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    conn1 = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    den = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    cur2 = conn2.cursor()
    cur3 = conn3.cursor()
    cur4 = conn4.cursor()
    cur1 = conn1.cursor()
    selt = den.cursor()
    cur2.execute("Select COUNT(*) from projects where status = 'active' and creator_id = %s",(user_id,))
    cur3.execute("Select COUNT(*) from projects where status = 'rejected' and creator_id = %s", (user_id,))
    cur4.execute("Select COUNT(*) from projects where status ='pending_review' and creator_id = %s", (user_id,))
    cur1.execute("SELECT * FROM users WHERE Id = %s", (user_id,))
    selt.execute("Select * from projects where status = 'active' and creator_id = %s", (user_id,))
    curt = cur2.fetchall()
    pels = cur3.fetchall()
    thrd = cur4.fetchall()
    rows = cur1.fetchall()
    slet = selt.fetchall()
    conn2.commit()
    conn3.commit()
    conn4.commit()
    cur2.close()
    cur3.close()
    cur4.close()
    return render_template('projects/list.html',curts=curt,pels=pels,thrd=thrd,row=rows,slet=slet)


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

    conn = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
    conn1 = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
    cur = conn.cursor()
    cur1 = conn1.cursor()
    cur.execute("SELECT * FROM projects WHERE id = %s", (Id,))
    cur1.execute("SELECT * FROM users WHERE Id = %s", (user_id,))
    rose = cur.fetchall()
    curly = cur1.fetchall()
    cur.close()
    conn.close()
    return render_template('projects/view.html', roll=rose, row=curly)

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
    rows = []
    if request.method == "POST":
        
        if not creator_id:
            flash('Please login first')
            return render_template('auth/login.html')

        proj_id = random.randint(0,1000000)
        title = request.form.get('title')
        select = request.form.get('select')
        short = request.form.get('short')
        more = request.form.get('more')
        goal = request.form.get('goal')
        image_file = request.files.get('image') 
        end = request.form.get('end_date')
        risk = request.form.get("risks")
        reward = request.form.get('reward')
        
        if not (title and more and goal and short and end and risk and reward):
            flash('Missing form data')
            return render_template('creator.html', row=rows)
            
            # Handle image file
        image_data = None
        if image_file and image_file.filename:
            try:
                image_data = image_file.read()
            except Exception as e:
                flash(f"Error reading image: {str(e)}")
                return render_template('creator.html', row=rows)
        else:
            flash('Please upload an image')
            return render_template('creator.html', row=rows)

            # Validate Funding Goal
        try:
            if int(goal) <= 0:
                flash("Funding must be positive")
                return render_template('creator.html', row=rows)
        except(ValueError, KeyError) as e:
            flash("Invalid funding goal")
            print(e)
            return render_template('creator.html', row=rows)
            
            # Validate Deadline
        try:
            deadline = datetime.datetime.strptime(end,'%Y-%m-%d').date()
            if deadline <= datetime.date.today():
                flash("Deadline must be in the future")
                return render_template('creator.html', row=rows)
        except(ValueError, KeyError) as e:
            print(e)
            flash('Invalid Deadline')
            return render_template('creator.html', row=rows)
                
            # Insert Projects Into Database
        conn = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO Projects(Id, Creator_Id, title, description, short_desc, category, funding_goal, main_image_url, risk_challenges, rewards, deadline, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (proj_id, creator_id, title, more, short, select, goal, image_data, risk, reward, deadline, "Pending_review")
        )
        conn.commit()
        cur.close()
        conn.close()
        flash('Project Submitted for review')
        return redirect('/projects/list')
    
    # GET: fetch projects
    try:
        if creator_id:
            conn = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
            cur = conn.cursor()
            cur.execute("SELECT * FROM projects WHERE Creator_Id = %s", (creator_id,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return render_template('projects/list.html', row=rows)
    except Exception as e:
        flash(str(e))
    
    return render_template('projects/list.html')

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
@projects_bp.route('/projects/see')
def projects_see():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please Login first")
        return render_template('auth/login.html')

    conn = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT p.*,COUNT(DISTINCT c.Id) AS comment_count,COUNT(DISTINCT l.Id) AS like_count, u.username AS creator_name FROM projects p LEFT JOIN comments c ON c.project_id = p.Id LEFT JOIN likes l ON l.project_id = p.Id left join users u on u.Id = p.creator_id WHERE p.status = 'active' GROUP BY p.Id")

    projects = cur.fetchall()

    cur.close()
    conn.close()

    if not projects:
        flash("No active projects yet")

    return render_template('user/utilities/projects.html', jects=projects)

@projects_bp.route('/backers/projects/see/<int:id>')
def backer_get_each_projects(id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please Login first")
        return render_template('auth/login.html')
    conn = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    cur = conn.cursor(dictionary=True)
    cur.execute("Select p.*,u.* From projects p left join users u on u.Id = p.creator_id where p.Id = %s group by p.creator_id",(id,))
    row = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('user/utilities/more.html', roll=row, backer=user_id, ject=id)
    
@projects_bp.route("/backers/projects/see/<int:bid>/like/<int:pid>")    
def like_project(bid,pid):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please Login first")
        return render_template('auth/login.html')
    connect = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
    curry = connect.cursor()
    curry.execute("Select * from likes where backers_id = %s and project_id = %s",(bid,pid))
    goat = curry.fetchall()
    if not goat:
        conn = mysql.connector.connect(host='localhost', user='root', passwd='',database='crowd_funding')
        cur = conn.cursor()
        cur.execute("Insert into likes (backers_id,project_id) Values(%s, %s)", (bid,pid))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(f'/backers/projects/see/{pid}')
    connect.commit()
    curry.close()
    connect.close()
    return redirect(f'/backers/projects/see/{pid}')

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
    cur1.execute("Select COUNT(*) from users where role = 'creator'")
    cur2.execute("Select COUNT(*) from users where role = 'backer'")
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
