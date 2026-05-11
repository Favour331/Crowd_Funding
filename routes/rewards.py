from flask import Flask,render_template,redirect,url_for,Blueprint,request,flash
from werkzeug.security import generate_password_hash,check_password_hash
from models.rewards import rewards_table

rewards_blueprint = Blueprint("rewards", __name__)
rewards_blueprint.secret_key = 'Yoursecretkey'

@rewards_blueprint.route('/save_rewards', methods=['POST'])
def save_reward():
    pass