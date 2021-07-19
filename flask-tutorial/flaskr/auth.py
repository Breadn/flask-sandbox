import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

'''
Note: the 'g' object is a namespace object that stores data from the app context
        + The data is global within the app context, lives for the duration of context
        + Makes operating on common resources between funcs/requests easier
'''

# Register function for auth URL
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Enter a username.'
        elif not password:
            error = 'Enter a password.'
        elif db.execute(
            'SELECT id FROM user WHERE LOWER(username) = LOWER(?)', (username,)
        ).fetchone() is not None:
            error = f'Username is already registered'

        # Successful register
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()

            return redirect(url_for('auth.login'))
        
        # Unsuccessful register
        flash(error)

    return render_template('auth/register.html')


# Login function for auth URL
@bp.route('/login', methods=('GET', 'POST'))
def login():
    # Process submitted POST requests
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE LOWER(username) = LOWER(?)', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect login.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect login.'
            print(f"LOG: Failed login attempt of user '{username}' with '{password}'")
        
        # Successful login
        if error is None:
            session.clear()
            # user id from PRIMARY KEY
            session['user_id'] = user['id']
            
            return redirect(url_for('index'))
        
        # Unsuccessful login
        flash(error)
    
    # If user already logged in, redir to index
    if g.user:
        return redirect(url_for('index'))

    return render_template('auth/login.html')


# Logout function to clear session to None user_id
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Runs before view func for any URL to load user-specific info
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    # Set no g.user if not user detected in session
    if user_id is None:
        g.user = None
    # If session does have user logged in
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# Function to require login to view, takes in view and wraps it with
# an inner verification func
def login_required(view):
    @functools.wraps(view)
    # Take in variable keyword args that may come with view func
    def wrapped_view(**kwargs):
        # If no user login detected, redir to login
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view