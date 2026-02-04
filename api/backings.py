from flask import Flask,request,render_template,Blueprint,flash,jsonify,session
import mysql.connector
# import random
from api.user import login_users

backings_blueprint = Blueprint('Backings', __name__)
backings_blueprint.secret_key = "Backings+key"

@backings_blueprint.route('/backings/new_pledge', methods=['GET','POST'])
@login_users
def new_pledge(project_id):
    data = request.get_json()
    conn = mysql.connector.connect(host='localhost', user='root', passwd='',database='crowd_funding')
    cur = conn.commit()
    cur.execute("Select id, creator_id, goal, deadline, status from projects where id =%s",(project_id))
    project = cur.fetchone()
    if not project:
        flash("Project not found")
    if project['creator_id'] == session['user_id']:
        flash('Cannot pledge to your own project')
    try:
        amount = float(data['amount'])
        if amount <= 0:
            flash('Pledge amount must be postive')
    except (ValueError, KeyError):
        flash('Invalid pledge amount')
        
    cur.execute('Insert Into backings(backer_id, project_id, amount, reward_tier, rewadr_desc,estimated_delivery, is_anonymous) VALUES(%s,%s,%s,%s,%s,%s,%s)',(session['user_id'],project_id, amount,data.get('reward_tier'),data.get('reward_desc'),data.get('estimated_delivery'),data.get('is_anonymous', False)))
    
    cur.execute('Update projects SET amount_raised = amount_raised + %s Where id = %s',(amount, project_id))
    conn.commit()
    cur.close()
    conn.close()
    flash('Pledge successfull',cur.lastrowid)
    return render_template('backer.html')