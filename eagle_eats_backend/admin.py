from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from eagle_eats_backend.data_base import get_db
from eagle_eats_backend.auth import login_required

blue_print = Blueprint('admin', __name__, url_prefix="/admin")
class kitchen_info:
    def __init__(self, kitchen, schedule, menu):
        self.kitchen = kitchen
        self.schedule =schedule
        self.menu = menu

@blue_print.route('dashboard', methods = ('GET', 'POST'))
@login_required
def dashboard():
    database_ref = get_db()
    if request.method == 'GET':
        kitchens = database_ref.execute(
            'select * from account, kitchen where account.id = kitchen.account_id'
        ).fetchall()
        kitchen_list = []
        for kitchen in kitchens:
            kitchen_list.append(kitchen_info(kitchen, get_schedule(kitchen), None))
    return render_template('dashboard/admin_dashboard.html', kitchens=kitchen_list)

def get_schedule(kitchen):
    database_ref = get_db()
    error = None
    schedule_id = kitchen['schedule_id']
    if schedule_id is None:
        return None
    
    try:
        schedule_name = database_ref.execute(
            'select name from schedule where schedule.id=?',
            (schedule_id,)
        ).fetchone()
        weekly_schedule = database_ref.execute(
            'select day_of_week, isClosed, breakfast_open,breakfast_closed,lunch_open,lunch_closed,dinner_open,dinner_closed'
            ' from kitchen_weekly_schedule where kitchen_weekly_schedule.schedule_id=?',
            (schedule_id,)
        ).fetchall()
        return {
            "name": schedule_name['name'],
            "schedule": weekly_schedule
        }
    except:
        error = "GET erorr on kitchen info level"
        flash(error)
        return None
