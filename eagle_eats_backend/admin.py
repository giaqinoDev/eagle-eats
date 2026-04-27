from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from eagle_eats_backend.data_base import get_db
from eagle_eats_backend.auth import admin_login_required

blue_print = Blueprint('admin', __name__, url_prefix="/admin")
@blue_print.route('dashboard', methods = ('GET', 'POST'))
@admin_login_required
def dashboard():
    return render_template('dashboard/admin_dashboard.html')