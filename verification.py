from functools import wraps
from flask import session, flash, redirect, url_for, request


def user_session(user, username, remember=False):
    session["user_id"] = user[0][0]
    session["user_name"] = username
    session["user_role"] = user[0][2]

    if remember:
        session['remember'] = True

    session.modified = True

def logout_user():
    del(session["user_id"])
    del(session["user_name"])
    del(session["user_role"])

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Lai apmeklētu šo lapu jums jābūt adminam! ', category='error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_login_required(f):
    print("starts")
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') == 0:
            flash('Lai apmeklētu šo lapu jums jāielogojas')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
