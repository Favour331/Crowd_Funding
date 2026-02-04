from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, jsonify,session
import mysql.connector
from werkzeug.security import check_password_hash
from models.users import table_name
from models.backings import create_backing_table
from models.projects import create_projects_table
from models.updates import create_updates_table
from models.rewards import create_rewards_table
from models.sessions import create_sessions_table
from config import my_db
from api.user import user_bp
from api.projects import projects_bp, project_owner_required
import time

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key_here'

conn = mysql.connector.connect(host='localhost',user='root',passwd='',database='crowd_funding')

@app.route('/')
def fess():
    user_id = session.get('user_id')
    if user_id:
        flash('Please login first')
        return render_template('auth/register.html')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE Id = %s", (user_id,))
    row = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('base.html')

@app.route('/lohin')
def tosec():
    return render_template('auth/login.html')

@app.route('/to_admin')
def admin():
    return render_template('admin/auth/register.html')

app.register_blueprint(user_bp)
app.register_blueprint(projects_bp)

if __name__ == '__main__':
    app.run(debug=True)