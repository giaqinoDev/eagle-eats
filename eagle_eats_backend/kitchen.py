from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from eagle_eats_backend.data_base import get_db
from eagle_eats_backend.auth import login_required

blue_print = Blueprint('kitchen', __name__, url_prefix='/kitchen')
@blue_print.route("/dashboard", methods=('GET', 'POST'))
@login_required
def dashboard():
    return render_template('dashboard/dashboard.html', user_id = session.get('account_id'))