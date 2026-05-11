from flask import Flask,request,Blueprint, jsonify, render_template,flash,redirect,session, url_for, g,json,current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import random
import mysql.connector
from services.user_service import authenticate_user,create_one_user,save_profile_image,get_user_details,get_user_by_id,get_user_profile_by_id,get_user_profile_and_projects,get_results
from db.connection import initialize_database

user_bp = Blueprint("user", __name__)
user_bp.secret_key = "Yoursecretkey"

@user_bp.route('/choose_plan')
def choose_plan():
    return render_template('auth/choose.html')

@user_bp.route('/before_request')
def before_request():
    g.user = None
    user_id = session.get('user_id')
    if user_id:
        g.user = get_user_by_id(user_id)

@user_bp.route('/register', methods=['POST', 'GET'])
def registered_users():
    if request.method == 'POST':
        try:
            # Initialize database on first registration attempt
            initialize_database()
            
            Id = random.randint(0,100000000)
            first = request.form.get('firstname')
            last = request.form.get('lastname')
            email = request.form.get('email')
            password = request.form.get('passwd')
            role = request.form.get('role', 'backer').capitalize()
            
            if not (first and last and email and password):
                flash('You must fill all the entry')
                return render_template('auth/register.html', role=role.lower())
            
            user = create_one_user(first,last,email,password,role)
            if not user:
                flash("Registration Failed")
                return render_template('auth/register.html', role=role.lower())
            if user['Role'] == "Creator":
                session['pending_user_id'] = user['id']
                return render_template('auth/bio.html')
            elif user['Role'] == "Backer":
                session['pending_user_id'] = user['id']
                return render_template('auth/bio.html')
            return "Invalid Role Selected"
        except Exception as e:
            return "Error: " + str(e)
    
    role = request.args.get('role', 'backer')
    return render_template('auth/register.html', role=role)
 
@user_bp.route('/login', methods=['GET', 'POST'])
def login_users():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    email = request.form.get('email')
    passwd = request.form.get('passwd')

    user = authenticate_user(email,passwd)
    
    if not user:
        flash("Invalid Credentials")
        return render_template('auth/login.html')
    
    session['user_id'] = user["id"]
    session['user_email'] = user["Email"]

    if user:
        return redirect(url_for("user.dashboard"))
    else:
        return "Unauthorised Access"
    
@user_bp.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to access the dashboard")
        return redirect(url_for('user.login_users'))

    person = get_user_by_id(user_id)

    if not person:
        flash("User not found")
        return redirect(url_for('user.login_users'))
    if not person.get('profile_image_url'):
        return redirect(url_for('user.tel'))

    return render_template('user/utilities/dashboard.html', stats=person, user_id=user_id)


def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
    )


@user_bp.route('/bio', methods=['POST','GET'])
def tel():
    if request.method == 'POST':
        number = request.form.get('telle')
        upload = request.files.get('profile_picture')

        if not number:
            flash('Phone number is required.')
            return render_template('auth/bio.html')
        if not upload or upload.filename == '':
            flash('Profile picture is required.')
            return render_template('auth/bio.html')
        if not allowed_file(upload.filename):
            flash('Allowed image types: png, jpg, jpeg, gif.')
            return render_template('auth/bio.html')

        pending_user_id = session.get('pending_user_id')
        if not pending_user_id:
            flash('Session expired. Please register again.')
            return redirect(url_for('user.registered_users'))

        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        os.makedirs(upload_folder, exist_ok=True)
        filename = secure_filename(upload.filename)
        filename = f"profile_{pending_user_id}_{random.randint(100000,999999)}_{filename}"
        upload.save(os.path.join(upload_folder, filename))

        profile_image_url = url_for('static', filename=f'uploads/{filename}')
        save_profile_image(pending_user_id, profile_image_url)

        code = random.randint(0,100000)
        session['verify_code'] = code
        return render_template('auth/verify.html', ver=code)

    return render_template('auth/bio.html')
     
@user_bp.route('/verify', methods=['POST','GET'])
def verify():
    # show verify form on GET
    if request.method == 'GET':
        code = session.get('verify_code')
        return render_template('auth/verify.html', ver=code)

    # POST: check submitted code
    submitted = request.form.get('numb')
    code = session.get('verify_code')
    if not submitted:
        flash('Please enter the verification code')
        return render_template('auth/verify.html', ver=code)

    if str(submitted).strip() != str(code):
        flash('Verification code does not match')
        return render_template('auth/verify.html', ver=code)

    # verification succeeded
    session.pop('verify_code', None)
    session.pop('pending_user_id', None)
    return render_template('auth/login.html')

@user_bp.route('/search', methods=['GET'])
def search():
    query = request.form.get('q') or request.args.get('q', '').strip()
    if not query:
        flash('Please enter a search term')
        return redirect(url_for('main.home'))
    
    get_search = get_results(query)
    if get_search is None:
        flash('No results found')

    # Implement search logic here (e.g., search projects and creators)
    # For now, just return the search query
    return render_template('search_results.html', results=get_search, query=query)

@user_bp.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    return redirect("/login")   

##################      PROFILE     ########### ###
@user_bp.route('/user/profile/<int:user_id>')
def user_profile(user_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('User not logged in')
        return redirect(url_for('user.login_users'))

    user = get_user_profile_by_id(user_id)
    if not user:
        flash('User not found')
        return redirect(url_for('user.login_users'))
    projects = []
    backings = []
    get_projects = get_user_profile_and_projects(user_id)
    role = user['Role'].lower()

    # Render the same template for both roles; template branches based on `role`
    return render_template('user/profile/profile.html',role=role,projects=get_projects,user=user)

@user_bp.route('/user/profile/edit')
def user_profile_edit():
    return render_template('user/profile/edit.html')

###################     ADMIN API       #####################
@user_bp.route('/admin/register', methods=['POST','GET'])
def reg_admin():
    if request.method == 'POST':
        try:
            name = request.form.get('first')
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

        flash("Incorrect Email or Password")
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
    cur.execute("Select * FROM users where role = 'Creator'")
    row = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('admin/users/creators.html',row=row)