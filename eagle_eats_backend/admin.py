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
        schedules = data_base.execute(
            'select * from schedule'
        ).fetchall()
        schedule_info_list = []
        for schedule in schedules:
            dependents_name_list = ''
            kitchen_dependents = data_base.execute(
                'select username from account join kitchen on account.id = kitchen.account_id join schedule on kitchen.schedule_id = ?',
                (schedule['id'],)
            ).fetchall()
            for dependent in kitchen_dependents:
                dependents_name_list = str(dependent['username']) + ","
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
        #Parse form input and validate
        error = schedule_validation(inputed_schedule)

        if error is None:
            #write to db
            query_schedule(inputed_schedule, name)
            redirect(url_for('admin.schedules'))
        else:
            form_data = request.form
            flash(error)
            return render_template('dashboard/schedule_creation.html', input_schedule=inputed_schedule)
    return render_template('dashboard/schedule_creation.html', input_schedule=None)

def generate_inputed_schedule(input_request):
    monday = {
        "isClosed": 1 if request.form.get('monday_closed') else 0,
        "breakfast_open": input_request.form['mon_b_open'],
        "breakfast_closed": input_request.form['mon_b_closed'],
        "lunch_open": input_request.form['mon_l_open'],
        "lunch_closed": input_request.form['mon_l_closed'],
        "dinner_open": input_request.form['mon_d_open'],
        "dinner_closed": input_request.form['mon_d_closed']
    }
    tuesday = {
        "isClosed": 1 if request.form.get('tuesday_closed') else 0,
        "breakfast_open": input_request.form['tue_b_open'],
        "breakfast_closed": input_request.form['tue_b_closed'],
        "lunch_open": input_request.form['tue_l_open'],
        "lunch_closed": input_request.form['tue_l_closed'],
        "dinner_open": input_request.form['tue_d_open'],
        "dinner_closed": input_request.form['tue_d_closed']
    }
    wednesday = {
        "isClosed": 1 if request.form.get('wednesday_closed') else 0,
        "breakfast_open": input_request.form['wed_b_open'],
        "breakfast_closed": input_request.form['wed_b_closed'],
        "lunch_open": input_request.form['wed_l_open'],
        "lunch_closed": input_request.form['wed_l_closed'],
        "dinner_open": input_request.form['wed_d_open'],
        "dinner_closed": input_request.form['wed_d_closed']
    }
    thursday = {
        "isClosed": 1 if request.form.get('thursday_closed') else 0,
        "breakfast_open": input_request.form['thur_b_open'],
        "breakfast_closed": input_request.form['thur_b_closed'],
        "lunch_open": input_request.form['thur_l_open'],
        "lunch_closed": input_request.form['thur_l_closed'],
        "dinner_open": input_request.form['thur_d_open'],
        "dinner_closed": input_request.form['thur_d_closed']
    }
    friday = {
        "isClosed": 1 if request.form.get('friday_closed') else 0,
        "breakfast_open": input_request.form['fri_b_open'],
        "breakfast_closed": input_request.form['fri_b_closed'],
        "lunch_open": input_request.form['fri_l_open'],
        "lunch_closed": input_request.form['fri_l_closed'],
        "dinner_open": input_request.form['fri_d_open'],
        "dinner_closed": input_request.form['fri_d_closed']
    }
    saturday = {
        "isClosed": 1 if request.form.get('saturday_closed') else 0,
        "breakfast_open": input_request.form['sat_b_open'],
        "breakfast_closed": input_request.form['sat_b_closed'],
        "lunch_open": input_request.form['sat_l_open'],
        "lunch_closed": input_request.form['sat_l_closed'],
        "dinner_open": input_request.form['sat_d_open'],
        "dinner_closed": input_request.form['sat_d_closed']
    }
    sunday = {
        "isClosed": 1 if request.form.get('sunday_closed') else 0,
        "breakfast_open": input_request.form['sun_b_open'],
        "breakfast_closed": input_request.form['sun_b_closed'],
        "lunch_open": input_request.form['sun_l_open'],
        "lunch_closed": input_request.form['sun_l_closed'],
        "dinner_open": input_request.form['sun_d_open'],
        "dinner_closed": input_request.form['sun_d_closed']
    }

    return {
        "2": monday,
        "3": tuesday,
        "4": wednesday,
        "5": thursday,
        "6": friday,
        "7": saturday,
        "1": sunday
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

        day_of_week = None
        match int(key):
            case 1:
                day_of_week = 'Sunday'
            case 2:
                day_of_week = 'Monday'
            case 3:
                day_of_week = 'Tuesday'
            case 4:
                day_of_week = 'Wednsday'
            case 5:
                day_of_week = 'Thursday'
            case 6:
                day_of_week = 'Friday'
            case 7:
                day_of_week = 'Saturday'
        
        if not (breakfast_open_time is None and breakfast_closed_time is None):
            if((breakfast_open_time is None and breakfast_closed_time) or (breakfast_open_time and breakfast_closed_time is None)):
                return errorType_empty + day_of_week + " breakfast."
            elif breakfast_open_time >= breakfast_closed_time:
                return errorType_invalid + day_of_week + " breakfast."
        
        if not (lunch_open_time is None and lunch_closed_time is None):
            if((lunch_open_time is None and lunch_closed_time) or (lunch_open_time and lunch_closed_time is None)):
                return errorType_empty + day_of_week + " lunch."
            elif breakfast_open_time > breakfast_closed_time:
                return errorType_invalid + day_of_week + " lunch."
        
        if not (dinner_open_time is None and dinner_closed_time is None):
            if((dinner_open_time is None and dinner_closed_time) or (dinner_open_time and dinner_closed_time is None)):
                return errorType_empty + day_of_week + " dinner."
            elif breakfast_open_time > breakfast_closed_time:
                return errorType_invalid + day_of_week + " dinner."
        
    return None

def query_schedule(schedule_inputs, schedule_name):
    data_base = get_db()
    execution = data_base.execute(
        'insert into schedule (name) values (?)',
        (schedule_name,)
    )
    schedule_id = execution.lastrowid
    print("Created new scheduel entity")

    for key, value in schedule_inputs.items():
        weekday = schedule_inputs[key]

        isClosed = weekday['isClosed']
        breakfast_open = weekday['breakfast_open']
        breakfast_closed = weekday['breakfast_closed']
        lunch_open = weekday['lunch_open']
        lunch_closed = weekday['lunch_closed']
        dinner_open = weekday['dinner_open']
        dinner_closed = weekday['dinner_closed']

        data_base.execute(
            '''insert into kitchen_weekly_schedule(
            schedule_id, 
            day_of_week, 
            isClosed, 
            breakfast_open, 
            breakfast_closed,
            lunch_open,
            lunch_closed,
            dinner_open,
            dinner_closed)
            values(?,?,?,?,?,?,?,?,?)''',
            (schedule_id,
             int(key),
             isClosed,
             breakfast_open, 
            breakfast_closed,
            lunch_open,
            lunch_closed,
            dinner_open,
            dinner_closed)
        )
    data_base.commit()

@blue_print.route('/cancel', methods = ('POST', ))
def cancel_schedule_creation():
    if request.method == 'POST':
        return redirect(url_for('admin.schedules'))
    
def parse_time(value):
    if value is None or value == "":
        return None
    return datetime.strptime(value, "%H:%M").time()


