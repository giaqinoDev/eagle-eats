from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from eagle_eats_backend.data_base import get_db
from eagle_eats_backend.auth import login_required

blue_print = Blueprint('admin', __name__, url_prefix="/admin")

@blue_print.route('dashboard', methods = ('GET', 'POST'))
@login_required
def dashboard():
    database_ref = get_db()
    if request.method == 'GET':
        kitchens = database_ref.execute(
            'select * from account join kitchen on account.id = kitchen.account_id'
        ).fetchall()
    return render_template('dashboard/admin_dashboard.html', kitchens=kitchens)