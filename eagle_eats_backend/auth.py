import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from eagle_eats_backend.data_base import get_db

blue_print = Blueprint('auth', __name__, url_prefix = '/auth')
@blue_print.route('/register/user', methods=('GET', 'POST'))
def register_user():
    if(request.method == 'POST'):
        student_id = request.form['student_id']
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        database_ref = get_db()
        error = None

        if not student_id:
            error = 'A Boston College student ID is requried'
        elif not first_name:
            error = 'Your first name is required'
        elif not last_name:
            error = 'Your last name is required'
        elif not username:
            error = 'A username is required'
        elif not password:
            error = 'A password is required'
        
        if error is None:
            try:
                database_ref.execute(
                    'insert into user(student_id, first_name, last_name, user_name, hashed_password)'
                    ' values(?, ?, ?, ?, ?)',
                    (student_id, first_name, last_name, username, generate_password_hash(password))
                )
                database_ref.commit()
            except database_ref.IntegrityError:
                error = f'An account with the ID or username is already registered'
        
        flash(error)
    return render_template('auth/register.html')