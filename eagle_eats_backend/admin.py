from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from eagle_eats_backend.data_base import get_db
from eagle_eats_backend.auth import login_required
from eagle_eats_backend.db_utils.kitchens_util import update_kitchen_statuses
from eagle_eats_backend.db_utils.schedules_util import get_organized_schedule_info
from datetime import datetime

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
        inputed_schedule = generate_inputed_schedule(request)
        error = schedule_validation(inputed_schedule)

        if error is None:
            #write to db
            return None
        flash(error)
    return render_template('dashboard/schedule_creation.html')

def generate_inputed_schedule(request):
    monday = {
        "isClosed": request.form['monday_closed'],
        "breakfast_open": request.form['mon_b_open'],
        "breakfast_closed": request.form['mon_b_closed'],
        "lunch_open": request.form['mon_l_open'],
        "lunch_closed": request.form['mon_l_closed'],
        "dinner_open": request.form['mon_d_open'],
        "dinner_closed": request.form['mon_d_closed']
    }
    tuesday = {
        "isClosed": request.form['tuesday_closed'],
        "breakfast_open": request.form['tue_b_open'],
        "breakfast_closed": request.form['tue_b_closed'],
        "lunch_open": request.form['tue_l_open'],
        "lunch_closed": request.form['tue_l_closed'],
        "dinner_open": request.form['tue_d_open'],
        "dinner_closed": request.form['tue_d_closed']
    }
    wednesday = {
        "isClosed": request.form['wednesday_closed'],
        "breakfast_open": request.form['wed_b_open'],
        "breakfast_closed": request.form['wed_b_closed'],
        "lunch_open": request.form['wed_l_open'],
        "lunch_closed": request.form['wed_l_closed'],
        "dinner_open": request.form['wed_d_open'],
        "dinner_closed": request.form['wed_d_closed']
    }
    thursday = {
        "isClosed": request.form['thursday_closed'],
        "breakfast_open": request.form['thur_b_open'],
        "breakfast_closed": request.form['thur_b_closed'],
        "lunch_open": request.form['thur_l_open'],
        "lunch_closed": request.form['thur_l_closed'],
        "dinner_open": request.form['thur_d_open'],
        "dinner_closed": request.form['thur_d_closed']
    }
    friday = {
        "isClosed": request.form['friday_closed'],
        "breakfast_open": request.form['fri_b_open'],
        "breakfast_closed": request.form['fri_b_closed'],
        "lunch_open": request.form['fri_l_open'],
        "lunch_closed": request.form['fri_l_closed'],
        "dinner_open": request.form['fri_d_open'],
        "dinner_closed": request.form['fri_d_closed']
    }
    saturday = {
        "isClosed": request.form['sat_closed'],
        "breakfast_open": request.form['sat_b_open'],
        "breakfast_closed": request.form['sat_b_closed'],
        "lunch_open": request.form['sat_l_open'],
        "lunch_closed": request.form['sat_l_closed'],
        "dinner_open": request.form['sat_d_open'],
        "dinner_closed": request.form['sat_d_closed']
    }
    sunday = {
        "isClosed": request.form['sun_closed'],
        "breakfast_open": request.form['sun_b_open'],
        "breakfast_closed": request.form['sun_b_closed'],
        "lunch_open": request.form['sun_l_open'],
        "lunch_closed": request.form['sun_l_closed'],
        "dinner_open": request.form['sun_d_open'],
        "dinner_closed": request.form['sun_d_closed']
    }

    return {
        "monday": monday,
        "tuesday": tuesday,
        "wednesday": wednesday,
        "thursday": thursday,
        "friday": friday,
        "saturday": saturday,
        "sunday": sunday
    }

def schedule_validation(schedule):
    errorType_empty = "Please set both start and end times to either none or concrete times for "
    errorType_invalid = "Invalid hours: start time must be before end time for "
    for key, value in schedule.items():
        week_day = schedule[key]
        breakfast_open_time = parse_time(week_day['breakfast_open'])
        breakfast_closed_time = parse_time(week_day['breakfast_closed'])
        lunch_open_time = parse_time(week_day['lunch_open'])
        lunch_closed_time = parse_time(week_day['lunch_closed'])
        dinner_open_time = parse_time(week_day['dinner_open'])
        dinner_closed_time = parse_time(week_day['dinner_closed'])

        if not (breakfast_open_time is None and breakfast_closed_time is None):
            if((breakfast_open_time is None and breakfast_closed_time) or (breakfast_open_time and breakfast_closed_time is None)):
                return errorType_empty + str(key) + "breakfast."
            elif breakfast_open_time >= breakfast_closed_time:
                return errorType_invalid + str(key) + "breakfast."
        
        if not (lunch_open_time is None and lunch_closed_time is None):
            if((lunch_open_time is None and lunch_closed_time) or (lunch_open_time and lunch_closed_time is None)):
                return errorType_empty + str(key) + "lunch."
            elif breakfast_open_time > breakfast_closed_time:
                return errorType_invalid + str(key) + "lunch."
        
        if not (dinner_open_time is None and dinner_closed_time is None):
            if((dinner_open_time is None and dinner_closed_time) or (dinner_open_time and dinner_closed_time is None)):
                return errorType_empty + str(key) + "dinner."
            elif breakfast_open_time > breakfast_closed_time:
                return errorType_invalid + str(key) + "dinner."
        
    return None
        

def parse_time(value):
    if value is None or value == "":
        return None
    return datetime.strptime(value, "%H:%M").time()


