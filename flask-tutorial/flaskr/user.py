from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

# User imports
from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint('user', __name__, url_prefix='/user')


# Returns profile data
def get_profile_info(user_id):
    db = get_db()
    user_info = db.execute(
        'SELECT u.id, u.joined, u.username'
        ' FROM user u'
        ' WHERE u.id = ?',
        (user_id,)
    ).fetchone()

    user_posts = db.execute(
        'SELECT p.title'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (user_id,)
    ).fetchall()
    user_posts = len(user_posts)

    return user_info, user_posts


@bp.route('/profile')
@login_required
def profile():
    profile_info = get_profile_info(g.user['id'])

    return render_template('user/profile.html', 
                            user_info=profile_info[0], 
                            user_posts=profile_info[1])

