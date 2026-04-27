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
                account_id = create_account(database_ref, error, first_name, last_name, username, password, 'user')
                if account_id is not None:
                    database_ref.execute(
                        'insert into user(account_id, student_id)'
                        ' values(?, ?)',
                        (account_id, student_id)
                    )
                    database_ref.commit()
            except database_ref.IntegrityError:
                if error is None:
                    error = f'An account with the ID is already registered'
        flash(error)
    return render_template('auth/user_registration.html')

@blue_print.route('/register/driver', methods=('GET', 'POST'))
def register_driver():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        state = request.form['state']
        license_id = request.form['license']
        database_ref = get_db()
        error = None

        if first_name is None:
            error = 'Your first name is required'
        elif last_name is None:
            error = 'Your last name is required'
        elif username is None:
            error = 'A username is required'
        elif password is None:
            error = 'A password is required'

        if error == None:
            try:
                account_id = create_account(database_ref, error, first_name, last_name, username, password, 'driver')
                if account_id is not None:
                    database_ref.execute(
                        'insert into driver(account_id, state, license_id)'
                        ' values(?, ?, ?)',
                        (account_id, state, license_id)
                    )
                    database_ref.commit()
            except database_ref.IntegrityError:
                if error is None:
                    error = f'An account with this license in {state} is already registered'
            
        flash(error)
    return render_template('auth/driver_registration.html')

def create_account(db, error, first_name, last_name, username, password, role):
    try:
        execution = db.execute(
            'insert into account(username, hashed_password, first_name, last_name, role)'
            ' values(?, ?, ?, ?, ?)',
            (username, generate_password_hash(password), first_name, last_name, role)
        )
        return execution.lastrowid #return id
    except db.IntegrityError:
        error = f'User {username} is already registered'
        flash(error)
        return None

@blue_print.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        database_ref = get_db()
        error = None

        account = database_ref.execute(
            f'select * from account where username = ?',
            (username,)
        ).fetchone()

        if username is None:
            error = 'Incorrect username'
        elif not check_password_hash(account['hashed_password'], password):
            error = 'Incorrect password'
        
        if error is None:
            session.clear()
            session['account_id'] = account['id']
            session['role'] = account['role']
            if account['role'] == 'user':
                return redirect(url_for('user.dashboard', user_id=session['account_id']))
            return redirect(url_for(''))
        
        flash(error)
    return render_template('auth/login.html')

@blue_print.before_app_request
def load_logged_in_user():
    account_id = session.get('account_id')
    role = session.get('role')
    if account_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            f'select * from account join {role} on account.id = {role}.account_id'
        ).fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view