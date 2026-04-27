import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from eagle_eats_backend.data_base import get_db
from eagle_eats_backend.auth import login_required

blue_print = Blueprint('user', __name__, url_prefix='/user')
@blue_print.route('/<int:user_id>/dashboard', methods=('GET', 'POST'))
@login_required
def dashboard(user_id):
    return render_template('dashboard/dashboard.html', user_id = 'User')