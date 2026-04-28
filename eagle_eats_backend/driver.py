from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from eagle_eats_backend.data_base import get_db
from eagle_eats_backend.auth import login_required

blue_print = Blueprint('driver', __name__, url_prefix = '/driver')

@blue_print.route('/dashboard', methods = ('GET', 'POST'))
@login_required
def dashboard():
    return render_template('dashboard/dashboard.html', user_id = 'Driver')