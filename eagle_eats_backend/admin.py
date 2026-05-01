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

@blue_print.route('dashboard/schedules/create', methods=('GET', 'POST'))
@login_required
def create_schedule():
    print("Create a new Schedule")
    if request.method == 'POST':
        name = request.form['name']

        #Breakfast
        mon_b_open = request.form['mon_b_open']
        mon_b_closed = request.form['mon_b_closed']
        tue_b_open = request.form['tue_b_open']
        tue_b_closed = request.form['tue_b_closed']
        wed_b_open = request.form['wed_b_open']
        web_b_closed = request.form['wed_b_closed']
        thur_b_open = request.form['thur_b_open']
        thur_b_closed = request.form['thur_b_closed']
        fri_b_open = request.form['fri_b_open']
        fri_b_closed = request.form['fri_b_closed']
        sat_b_open = request.form['sat_b_open']
        sat_b_closed = request.form['sat_b_closed']
        sun_b_open = request.form['sun_b_open']
        sun_b_closed = request.form['sun_b_closed']

        #Lunch
        mon_l_open = request.form['mon_l_open']
        mon_l_closed = request.form['mon_l_closed']
        tue_l_open = request.form['tue_l_open']
        tue_l_closed = request.form['tue_l_closed']
        wed_l_open = request.form['wed_l_open']
        web_l_closed = request.form['wed_l_closed']
        thur_l_open = request.form['thur_l_open']
        thur_l_closed = request.form['thur_l_closed']
        fri_l_open = request.form['fri_l_open']
        fri_l_closed = request.form['fri_l_closed']
        sat_l_open = request.form['sat_l_open']
        sat_l_closed = request.form['sat_l_closed']
        sun_l_open = request.form['sun_l_open']
        sun_l_closed = request.form['sun_l_closed']

        #Dinner
        mon_d_open = request.form['mon_d_open']
        mon_d_closed = request.form['mon_d_closed']
        tue_d_open = request.form['tue_d_open']
        tue_d_closed = request.form['tue_d_closed']
        wed_d_open = request.form['wed_d_open']
        web_d_closed = request.form['wed_d_closed']
        thur_d_open = request.form['thur_d_open']
        thur_d_closed = request.form['thur_d_closed']
        fri_d_open = request.form['fri_d_open']
        fri_d_closed = request.form['fri_d_closed']
        sat_d_open = request.form['sat_d_open']
        sat_d_closed = request.form['sat_d_closed']
        sun_d_open = request.form['sun_d_open']
        sun_d_closed = request.form['sun_d_closed']

    return render_template('dashboard/schedule_creation.html')




