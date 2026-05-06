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
    def __init__(self, operation, info, schedule, menu_name):
        self.operation = operation
        self.info = info
        self.schedule =schedule
        self.menu_name = menu_name

class schedule_info:
    def __init__(self, id, name, dependents, schedule):
        self.id = id
        self.name = name
        self.dependents = dependents
        self.schedule = schedule

class menu_info:
    def __init__(self, id, name, breakfast_items, lunch_items, dinner_items):
        self.id = id
        self.name = name
        self.breakfast_items = breakfast_items
        self.lunch_items = lunch_items
        self.dinner_items = dinner_items

#-----------------Kitchen Stuff----------------------------------------------------------------------------------------------------
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
            menu_id = kitchen['menu_id']
            if(menu_id is None):
                menu_name = None
            else:
                menu = database_ref.execute(
                    'select name from menu where id=?',
                    (menu_id,)
                ).fetchone()
                menu_name = menu['name']
                print(menu_name)

            if schedule_id is None:
                weekly_schedule = None
                operation = 'Closed'
                #kitchen_info_list.append(kitchen_info("Closed", kitchen, None, None))
            else:
                weekly_schedule = get_organized_schedule_info(schedule_id)
                operation = kitchen["operation"]
            kitchen_info_list.append(kitchen_info(operation, kitchen, weekly_schedule, menu_name))

    return render_template('dashboard/admin_dashboard.html', kitchens=kitchen_info_list)

@blue_print.route('dashboard/kitchens/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update_kitchen_logistics(id):
    data_base = get_db()

    active_schedule = data_base.execute(
        'select schedule_id from kitchen where id=?',
        (id,)
    ).fetchone()
    active_schedule_id = active_schedule['schedule_id']

    active_menu = data_base.execute(
        'select menu_id from kitchen where id=?',
        (id,)
    ).fetchone()
    active_menu_id = active_menu['menu_id']

    if active_schedule_id is not None and active_schedule_id != '':
        print("Active schedule ID AHNWHDUBNWDHBUWDBUWNDU: " + str(active_schedule_id))
        active_schedule_info = data_base.execute(
            'select * from schedule where id=?',
            (active_schedule_id, )
        ).fetchone()
        active_schedule_name = active_schedule_info['name']

        schedules_list = data_base.execute(
            'select * from schedule where id!=?',
            (active_schedule_id,)
        ).fetchall()
    else:
        active_schedule_name = None
        schedules_list = data_base.execute(
            'select * from schedule'
        ).fetchall()

    if active_menu_id is not None and active_menu_id != '':
        active_menu_info = data_base.execute(
            'select * from menu where id=?',
            (active_menu_id, )
        ).fetchone()
        active_menu_name = active_menu_info['name']

        menus_list = data_base.execute(
            'select * from menu where id !=?',
            (active_menu_id,)
        ).fetchall()
    else:
        active_menu_name = None
        menus_list = data_base.execute(
            'select * from menu'
        ).fetchall()

    if request.method == 'POST':
        schedule_selected = request.form['schedule_dropdown']
        menu_selected = request.form['menu_dropdown']
        if schedule_selected == '':
            schedule_selected = None
        if menu_selected == '':
            menu_selected == None
        #Future Menu drop down
        #menu_selected = request.form['menu_dropdown]

        if schedule_selected != active_schedule_id:
            print("UPDATE THE ACTIVE SCHEDULE!")
            data_base.execute(
                'update kitchen set schedule_id=? where id=?',
                (schedule_selected, id)
            )
            data_base.commit()
        if menu_selected != active_menu_id:
            print('UPDATE KITCHENS MENU!')
            data_base.execute(
                'update kitchen set menu_id=? where id=?',
                (menu_selected, id)
            )
            data_base.commit()
        return redirect(url_for('admin.kitchens'))
    
    return render_template('dashboard/kitchen_info_updating.html', 
                           schedules=schedules_list , 
                           active_schedule_name=active_schedule_name, 
                           active_schedule_id=active_schedule_id,
                           menus = menus_list,
                           active_menu_name = active_menu_name,
                           active_menu_id = active_menu_id
                           )

#-----------------Schedule Stuff---------------------------------------------------------------------------------------------------
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
                'select username from account join kitchen on account.id = kitchen.account_id where kitchen.schedule_id = ?',
                (schedule['id'],)
            ).fetchall()
            for dependent in kitchen_dependents:
                print('wdhwduhd')
                dependents_name_list += str(dependent['username']) + ", "
            weekly_schedule = get_organized_schedule_info(schedule['id'])
            schedule_info_list.append(schedule_info(schedule['id'], schedule['name'], dependents_name_list, weekly_schedule))

    return render_template('dashboard/admin_dashboard.html', schedules_list = schedule_info_list)

@blue_print.route('dashboard/schedules/create', methods=('GET', 'POST'))
@login_required
def create_schedule():
    if request.method == 'POST':
        name = request.form['name']
        inputed_schedule = generate_inputed_schedule(request)
        #Parse form input and validate
        error = schedule_validation(inputed_schedule)

        if error is None:
            #write to db
            query_schedule(inputed_schedule, name)
            return redirect(url_for('admin.schedules'))
        else:
            flash(error)
            return render_template('dashboard/schedule_creation.html', input_schedule=inputed_schedule)
    return render_template('dashboard/schedule_creation.html', input_schedule=None)

def generate_inputed_schedule(input_request):
    monday = {
        "isClosed": 1 if input_request.form.get('monday_closed') else 0,
        "breakfast_open": input_request.form['mon_b_open'],
        "breakfast_closed": input_request.form['mon_b_closed'],
        "lunch_open": input_request.form['mon_l_open'],
        "lunch_closed": input_request.form['mon_l_closed'],
        "dinner_open": input_request.form['mon_d_open'],
        "dinner_closed": input_request.form['mon_d_closed']
    }
    tuesday = {
        "isClosed": 1 if input_request.form.get('tuesday_closed') else 0,
        "breakfast_open": input_request.form['tue_b_open'],
        "breakfast_closed": input_request.form['tue_b_closed'],
        "lunch_open": input_request.form['tue_l_open'],
        "lunch_closed": input_request.form['tue_l_closed'],
        "dinner_open": input_request.form['tue_d_open'],
        "dinner_closed": input_request.form['tue_d_closed']
    }
    wednesday = {
        "isClosed": 1 if input_request.form.get('wednesday_closed') else 0,
        "breakfast_open": input_request.form['wed_b_open'],
        "breakfast_closed": input_request.form['wed_b_closed'],
        "lunch_open": input_request.form['wed_l_open'],
        "lunch_closed": input_request.form['wed_l_closed'],
        "dinner_open": input_request.form['wed_d_open'],
        "dinner_closed": input_request.form['wed_d_closed']
    }
    thursday = {
        "isClosed": 1 if input_request.form.get('thursday_closed') else 0,
        "breakfast_open": input_request.form['thur_b_open'],
        "breakfast_closed": input_request.form['thur_b_closed'],
        "lunch_open": input_request.form['thur_l_open'],
        "lunch_closed": input_request.form['thur_l_closed'],
        "dinner_open": input_request.form['thur_d_open'],
        "dinner_closed": input_request.form['thur_d_closed']
    }
    friday = {
        "isClosed": 1 if input_request.form.get('friday_closed') else 0,
        "breakfast_open": input_request.form['fri_b_open'],
        "breakfast_closed": input_request.form['fri_b_closed'],
        "lunch_open": input_request.form['fri_l_open'],
        "lunch_closed": input_request.form['fri_l_closed'],
        "dinner_open": input_request.form['fri_d_open'],
        "dinner_closed": input_request.form['fri_d_closed']
    }
    saturday = {
        "isClosed": 1 if input_request.form.get('saturday_closed') else 0,
        "breakfast_open": input_request.form['sat_b_open'],
        "breakfast_closed": input_request.form['sat_b_closed'],
        "lunch_open": input_request.form['sat_l_open'],
        "lunch_closed": input_request.form['sat_l_closed'],
        "dinner_open": input_request.form['sat_d_open'],
        "dinner_closed": input_request.form['sat_d_closed']
    }
    sunday = {
        "isClosed": 1 if input_request.form.get('sunday_closed') else 0,
        "breakfast_open": input_request.form['sun_b_open'],
        "breakfast_closed": input_request.form['sun_b_closed'],
        "lunch_open": input_request.form['sun_l_open'],
        "lunch_closed": input_request.form['sun_l_closed'],
        "dinner_open": input_request.form['sun_d_open'],
        "dinner_closed": input_request.form['sun_d_closed']
    }

    return {
        "1": sunday,
        "2": monday,
        "3": tuesday,
        "4": wednesday,
        "5": thursday,
        "6": friday,
        "7": saturday
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
            elif lunch_open_time > lunch_closed_time:
                return errorType_invalid + day_of_week + " lunch."
        
        if not (dinner_open_time is None and dinner_closed_time is None):
            if((dinner_open_time is None and dinner_closed_time) or (dinner_open_time and dinner_closed_time is None)):
                return errorType_empty + day_of_week + " dinner."
            elif dinner_open_time > dinner_closed_time:
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

@blue_print.route('dashboard/schedules/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update_schedule(id):
    initial_schedule = get_organized_schedule_info(id)
    if request.method == 'POST':
        name = request.form['name']
        inputed_schedule = generate_inputed_schedule(request)
        error = schedule_validation(inputed_schedule)

        if error is None:
            #update db
            query_schedule_update(id, name, inputed_schedule, initial_schedule)
            return redirect(url_for('admin.schedules'))
        else:
            flash(error)
            return render_template('dashboard/schedule_creation.html', input_schedule=inputed_schedule, schedule_name=name)
    return render_template('dashboard/schedule_creation.html', input_schedule=initial_schedule['week'], schedule_name=initial_schedule['name'])

def query_schedule_update(schedule_id, input_name, schedule_input, original_schedule):
    data_base = get_db()
    #Check if name was changed
    if input_name != original_schedule['name']:
        data_base.execute(
            'update schedule set name=? where id=?',
            (input_name, schedule_id)
        )
    
    for key, value in schedule_input.items():
        weekday = schedule_input[key]

        #inputed schedule data
        isClosed = weekday['isClosed']
        breakfast_open = weekday['breakfast_open']
        breakfast_closed = weekday['breakfast_closed']
        lunch_open = weekday['lunch_open']
        lunch_closed = weekday['lunch_closed']
        dinner_open = weekday['dinner_open']
        dinner_closed = weekday['dinner_closed']

        #original schedule data
        isClosed_orig = original_schedule['week'][key]['isClosed']
        breakfast_open_orig = original_schedule['week'][key]['breakfast_open']
        breakfast_closed_orig = original_schedule['week'][key]['breakfast_closed']
        lunch_open_orig = original_schedule['week'][key]['lunch_open']
        lunch_closed_orig = original_schedule['week'][key]['lunch_closed']
        dinner_open_orig = original_schedule['week'][key]['dinner_open']
        dinner_closed_orig = original_schedule['week'][key]['dinner_closed']

        if(isClosed != isClosed_orig):
            data_base.execute(
                'update kitchen_weekly_schedule set isClosed=? where schedule_id=? and day_of_week=?',
                (isClosed, schedule_id, key)
            )
        if(breakfast_open != breakfast_open_orig):
            data_base.execute(
                'update kitchen_weekly_schedule set breakfast_open=? where schedule_id=? and day_of_week=?',
                (breakfast_open, schedule_id, key)
            )
        if(breakfast_closed != breakfast_closed_orig):
            data_base.execute(
                'update kitchen_weekly_schedule set breakfast_closed=? where schedule_id=? and day_of_week=?',
                (breakfast_closed, schedule_id, key)
            )
        if(lunch_open != lunch_open_orig):
            data_base.execute(
                'update kitchen_weekly_schedule set lunch_open=? where schedule_id=? and day_of_week=?',
                (lunch_open, schedule_id, key)
            )
        if(lunch_closed != lunch_closed_orig):
            data_base.execute(
                'update kitchen_weekly_schedule set lunch_closed=? where schedule_id=? and day_of_week=?',
                (lunch_closed, schedule_id, key)
            )
        if(dinner_open != dinner_open_orig):
            data_base.execute(
                'update kitchen_weekly_schedule set dinner_open=? where schedule_id=? and day_of_week=?',
                (dinner_open, schedule_id, key)
            )
        if(dinner_closed != dinner_closed_orig):
            data_base.execute(
                'update kitchen_weekly_schedule set dinner_closed=? where schedule_id=? and day_of_week=?',
                (dinner_closed, schedule_id, key)
            )
    
    data_base.commit()
    
@blue_print.route('/cancel', methods = ('POST', ))
@login_required
def cancel_schedule_creation():
    if request.method == 'POST':
        return redirect(url_for('admin.schedules'))

@blue_print.route('/cancel/kitchen_update', methods = ('POST', ))
@login_required
def cancel_kitchen_info_update():
    if request.method == 'POST':
        return redirect(url_for('admin.kitchens'))

#-----------Menu Stuff----------------------------------------------------------------------------------------
@blue_print.route('dashboard/menus', methods = ('GET', 'POST'))
@login_required
def menus():
    data_base = get_db()
    if request.method == 'GET':
        menus = data_base.execute(
            'select * from menu'
        ).fetchall()

        menus_list = []
        for menu in menus:
            menu_name = menu['name']
            menu_id = menu['id']
            menu_items = data_base.execute(
                'select * from item where menu_id=?',
                (menu_id,)
            ).fetchall()
            breakfast_items = []
            lunch_items = []
            dinner_items = []
            for item in menu_items:
                if(item['availability'] == 'Breakfast'):
                    breakfast_items.append(item)
                elif(item['availability'] == 'Lunch'):
                    lunch_items.append(item)
                elif(item['availability'] == 'Dinner'):
                    dinner_items.append(item)
            print(len(breakfast_items))
            info = menu_info(menu_id, menu_name, breakfast_items, lunch_items, dinner_items)
            menus_list.append(info)
    return render_template('dashboard/admin_dashboard.html', menus_info = menus_list)

@blue_print.route('dashboard/menus/create', methods = ('GET', 'POST'))
def create_menu():
    return None


#--------------------Helper functions--------------------------------------------------------------------------
def parse_time(value):
    if value == "":
        print("EMPTY!!")
        return None
    return datetime.strptime(value, "%H:%M").time()
