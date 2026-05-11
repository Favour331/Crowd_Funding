from flask import Flask, request, render_template, Blueprint, flash, jsonify, session, redirect, url_for
from services.backing_service import create_backing, get_backings_for_project, fetch_user_profile

backings_blueprint = Blueprint('Backings', __name__)
backings_blueprint.secret_key = "Backings+key"

@backings_blueprint.route('/backings/new_pledge', methods=['POST'])
def new_pledge():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login first')
        return redirect('/login')

    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    project_id = data.get('project_id')
    email = data.get('email')
    amount_value = data.get('amount')
        # return redirect(request.referrer or url_for('project.list_projects'))

    if not project_id or not email or not amount_value:
        flash('Missing required fields')
        return redirect(request.referrer or url_for('project.list_projects'))

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
