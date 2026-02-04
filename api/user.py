from flask import Flask,request,Blueprint, jsonify, render_template,flash,redirect,session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import random

user_bp = Blueprint("user", __name__)
user_bp.secret_key = "Yoursecretkey"

@user_bp.route('/register_users', methods=['POST', 'GET'])
def registered_users():
    if request.method == 'POST':
        try:
            Id = random.randint(0,100000000)
            user = request.form.get('user_name')
            fess_name = request.form.get('firstname')
            last_name = request.form.get('lastname')
            email = request.form.get('email')
            password = request.form.get('passwd')
            if not (fess_name and last_name and email and password):
                flash('You must fill all the entry')
                return
            hashed = generate_password_hash(password)
            role = request.form.get('role') or 'user'

            conn = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (Id, username,First_name, Last_name, Email, Password, Role) VALUES (%s,%s,%s, %s, %s, %s,%s)",
                (Id,user,fess_name, last_name, email, hashed, role)
            )
            conn.commit()
            cur.close()
            conn.close()
            if role == "Creator":
                return render_template('auth/bio.html')
            flash('User Inserted Sucessfully')
            return render_template('auth/bio.html')
        except Exception as e:
            return jsonify({'message': str(e)}), 400
    return render_template('auth/register.html') 

@user_bp.route('/login', methods=['GET', 'POST'])
def login_users():
    if request.method == 'GET':
        return render_template('auth/login.html')

    email = request.form.get('mail')
    passwd = request.form.get('word')
    if not (email and passwd):
        flash("Missing credentials")
        return render_template('sec.html')
    try:
        conn = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE Email = %s", (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row and check_password_hash(row['Password'], passwd):
            session['user_id'] = row['Id']
            session['user_role'] = row['Role']
            creator_id = session.get('user_id')
            role = row.get('Role', '')
            
            # Use the authenticated user dict directly to avoid template indexing issues
            if role == "Creator":
                # Render a creator landing (could be a dashboard or base page)
                return render_template('base.html', user=row)

            # For non-creators render dashboard and provide initial empty collections
            return render_template('user/utilities/dashboard.html', user=row, projects=[], backings=[], notifications=[], recent=[])

        flash("Incorrect Email or Password")
        return render_template('auth/login.html')
    except Exception as e:
        flash(str(e))
        return render_template('auth/login.html')

@user_bp.route('/bio', methods=['POST','GET'])
def tel():
    if request.method == 'POST':
        number = request.form.get('telle')
        if number:
            # store verification code in session (avoid module-global name collisions)
            code = random.randint(0,100000)
            session['verify_code'] = code
            return render_template('auth/verify.html', ver=code)
        return render_template('auth/bio.html')
    return render_template('bio.html')
     
@user_bp.route('/verify', methods=['POST','GET'])
def verify():
    # show verify form on GET
    if request.method == 'GET':
        code = session.get('verify_code')
        return render_template('verify.html', ver=code)

    # POST: check submitted code
    submitted = request.form.get('numb')
    code = session.get('verify_code')
    if not submitted:
        flash('Please enter the verification code')
        return render_template('verify.html', ver=code)

    if str(submitted).strip() != str(code):
        flash('Verification code does not match')
        return render_template('auth/verify.html', ver=code)

    # verification succeeded
    session.pop('verify_code', None)
    return render_template('auth/login.html')

##################      PROFILE     ########### ###
@user_bp.route('/user/profile/<int:user_id>')
def user_profile(user_id):
    # Single DB connection and cursor
    conn = mysql.connector.connect(host='localhost', user='root',passwd='',database='crowd_funding')
    cur = conn.cursor(dictionary=True)

    # Fetch user once
    cur.execute("SELECT * FROM users WHERE Id = %s", (user_id,))
    user = cur.fetchone()

    projects = []
    backings = []
    role = (user.get('Role') or user.get('role') or '').lower() if user else ''

    if role == 'creator':
        cur.execute(
            "SELECT p.*, COUNT(DISTINCT p.backer_count) AS backers, COUNT(DISTINCT p.amount_raised) AS amount "
            "FROM projects p WHERE p.creator_id = %s GROUP BY p.Id",
            (user_id,)
        )
        projects = cur.fetchall()

    elif role == 'backer':
        cur.execute(
            "SELECT b.*, p.title AS project_title, p.status AS project_status, p.Id AS project_id "
            "FROM BACKINGS b JOIN projects p ON p.Id = b.Project_Id WHERE b.Backer_id = %s",
            (user_id,)
        )
        backings = cur.fetchall()

    cur.close()
    conn.close()

    # Render the same template for both roles; template branches based on `role`
    return render_template('user/profile/profile.html', user_id=user_id, user=user, projects=projects, backings=backings, role=role)

@user_bp.route('/user/profile/edit')
def user_profile_edit():
    return render_template('user/profile/edit.html')

###################     ADMIN API       #####################
@user_bp.route('/admin/register', methods=['POST','GET'])
def reg_admin():
    if request.method == 'POST':
        try:
            name = request.form.get('fess_name')
            last = request.form.get('last')
            email = request.form.get('email')
            number = request.form.get('number')
            if not (name and last and email and number):
                flash('All entries must be filled')
                return render_template('admin/auth/register.html')
            try:
                conn = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
                cur = conn.cursor()
                cur.execute("Create Table if not exists Admin(Id int Primary Key Auto_increment, First_name Varchar(250) not null,Last_name Varchar(250) not null, Email varchar(50) not null, Phone_number int(11) not null, Password Varchar(250))")
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                flash(str(e))
            conn = mysql.connector.connect(host='localhost', user='root',passwd='', database='crowd_funding')
            cur = conn.cursor()
            cur.execute('Insert into admin(First_name, Last_name, Email, Phone_number) Values(%s,%s,%s,%s)', (name,last,email,number))
            conn.commit()
            cur.close()
            conn.close()
            return render_template('admin/auth/verify.html')
        except Exception as e:
            flash(str(e))
    return render_template('admin/auth/login.html')


@user_bp.route('/admin/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'GET':
        return render_template('admin/auth/login.html')

    email = request.form.get('mail')
    passwd = request.form.get('word')
    if not (email and passwd):
        flash("Missing credentials")
        return render_template('sec.html')
    try:
        conn = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM admin WHERE Email = %s", (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row and check_password_hash(row['Password'], passwd):
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

        flash("Incorrect Email or Password")
        print("Incorrect password")
        return render_template('admin/auth/login.html')
    except Exception as e:
        flash(str(e))
        return render_template('admin/auth/login.html')

@user_bp.route('/admin/verify', methods=['POST','GET'])
def admin_verify():
    if request.method == 'POST':
        try:
            passwd = request.form.get('passwd')
            confirm = request.form.get('confirm')
            if not(passwd and confirm):
                flash("All entries must be filled")
                return render_template('admin/auth/verify.html')
            if confirm != passwd:
                flash('password does not match')
                return render_template('admin/auth/verify.html')
            hashed = generate_password_hash(confirm)
            conn = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')
            cur = conn.cursor()
            cur.execute("Update admin set Password = %s where Password is Null",(hashed,))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('user.login_admin'))    
        except Exception as e:
            flash(str(e))
            return render_template('admin/auth/verify.html')
    return render_template('admin/auth/login.html')

@user_bp.route('/admin/creators/view')
def view_creators():
    conn = mysql.connector.connect(host='localhost', user='root',passwd='',database='crowd_funding')
    cur = conn.cursor()
    cur.execute("Select * FROM users where role = 'creator'")
    row = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('admin/users/creators.html',row=row)