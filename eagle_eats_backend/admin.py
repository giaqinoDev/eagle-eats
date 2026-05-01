from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from eagle_eats_backend.data_base import get_db
from eagle_eats_backend.auth import login_required
from eagle_eats_backend.db_utils.kitchens_util import update_kitchen_statuses
from eagle_eats_backend.db_utils.schedules_util import get_organized_schedule_info

blue_print = Blueprint('admin', __name__, url_prefix="/admin")
class kitchen_info:
    def __init__(self, operation, info, schedule, menu):
        self.operation = operation
        self.info = info
        self.schedule =schedule
        self.menu = menu

class schedule_info:
    def __init__(self, id, name, dependents, schedule):
        self.id = id
        self.name = name
        self.dependents = dependents
        self.schedule = schedule

@blue_print.route('dashboard/kitchens', methods = ('GET', 'POST'))
@login_required
def kitchens():
    database_ref = get_db()
    if request.method == 'GET':
        update_kitchen_statuses()
        kitchens = database_ref.execute(
            'select * from kitchen join account on account.id = kitchen.account_id'
        ).fetchall()

        kitchen_info_list = []
        for kitchen in kitchens:
            schedule_id = kitchen['schedule_id']
            if schedule_id is None:
                kitchen_info_list.append(kitchen_info("Closed", kitchen, None, None))
            else:
                weekly_schedule = get_organized_schedule_info(schedule_id)
                operation = kitchen["operation"]
                kitchen_info_list.append(kitchen_info(operation, kitchen, weekly_schedule, None))

    return render_template('dashboard/admin_dashboard.html', kitchens=kitchen_info_list)

@blue_print.route('dashboard/schedules', methods=('GET', 'POST'))
@login_required
def schedules():
    data_base = get_db()
    if request.method == "GET":
        dependents_name_list = ''
        schedules = data_base.execute(
            'select * from schedule'
        ).fetchall()
        kitchen_dependents = data_base.execute(
            'select username from account join kitchen on account.id = kitchen.account_id join schedule on kitchen.schedule_id = schedule.id'
        ).fetchall()
        for dependent in kitchen_dependents:
            dependents_name_list = str(dependent['username']) + ","
        schedule_info_list = []
        for schedule in schedules:
            weekly_schedule = get_organized_schedule_info(schedule['id'])
            schedule_info_list.append(schedule_info(schedule['id'], schedule['name'], dependents_name_list, weekly_schedule))

    return render_template('dashboard/admin_dashboard.html', schedules_list = schedule_info_list)




