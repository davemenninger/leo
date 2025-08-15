from flask import Blueprint, render_template, request, flash, redirect, session, g
from werkzeug.security import check_password_hash

from db import get_db

auth = Blueprint('auth', __name__)

@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@auth.route('/logout')
def logout():
    session.clear()
    flash("bye")
    return redirect("/")

@auth.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        print(user)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            flash("nice")
            return redirect("/")

        flash(error)
    return render_template('login.html')
