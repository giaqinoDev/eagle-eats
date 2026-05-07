from eagle_eats_backend.data_base import get_db
from datetime import datetime, date
import pytz

from eagle_eats_backend.db_utils.schedules_util import get_organized_schedule_info

def update_kitchen_statuses():
    data_base = get_db()
    kitchens = data_base.execute(
        'select * from kitchen join account on account.id = kitchen.account_id'
    ).fetchall()

    for kitchen in kitchens:
        print(kitchen['id'])
        schedule_id = kitchen['schedule_id']
        print("Schedule ID: " + str(schedule_id))
        if schedule_id is None or schedule_id == 'None':
            data_base.execute(
                'update kitchen set operation = ? where id =?',
                ('Closed', kitchen['id'])
            )
            data_base.commit()
        elif schedule_id is not None:
            update_kitchen_operations(schedule_id, kitchen)

def update_kitchen_operations(schedule_id, kitchen):
    data_base = get_db()

    organized_schedule = get_organized_schedule_info(schedule_id)
    update_operation(organized_schedule['week'], kitchen)
    #organize_schedule = organize_schedule(weekly_schedule)


def update_operation(weekly_schedule, kitchen):
    kitchen_id = kitchen['id']
    data_base = get_db()

    time_zone = pytz.timezone('America/New_York')
    east_coast_time = datetime.now(time_zone).time()
    dayOfWeek_today = date.today().isoweekday() #1: Monday, #7: Sunday

    if dayOfWeek_today == 7:
        dayOfWeek_calibrated = 1
    else:
        dayOfWeek_calibrated = dayOfWeek_today + 1
    
    days_schedule = weekly_schedule[str(dayOfWeek_calibrated)]
    operation = "Closed"

    if days_schedule['isClosed'] == 0:
        breakfast_accounted_for = False
        lunch_acounted_for = False
        dinner_accounted_for = False
        if(days_schedule['breakfast_open'] != '' and days_schedule['breakfast_closed'] != ''):
            breakfast_accounted_for = True
            breakfast_open = datetime.strptime(days_schedule['breakfast_open'], "%H:%M").time()
            breakfast_closed = datetime.strptime(days_schedule['breakfast_closed'], "%H:%M").time()
        
        if(days_schedule['lunch_open'] != '' and days_schedule['lunch_closed'] != ''):
            lunch_acounted_for = True
            lunch_open = datetime.strptime(days_schedule['lunch_open'], "%H:%M").time()
            lunch_closed = datetime.strptime(days_schedule['lunch_closed'], "%H:%M").time()
        
        if(days_schedule['dinner_open'] != '' and days_schedule['dinner_closed'] != ''):
            dinner_accounted_for = True
            dinner_open = datetime.strptime(days_schedule['dinner_open'], "%H:%M").time()
            dinner_closed = datetime.strptime(days_schedule['dinner_closed'], "%H:%M").time()

        """print(breakfast_open)
        print(breakfast_closed)
        print(lunch_open)
        print(lunch_closed)
        print(dinner_open)
        print(dinner_closed)
        print(east_coast_time)"""

        if(breakfast_accounted_for and (breakfast_open <= east_coast_time <= breakfast_closed)):
            #print("Breakfast!")
            operation = 'Breakfast'
        
        elif(lunch_acounted_for and (lunch_open <= east_coast_time <= lunch_closed)):
            #print("Lunch!")
            operation = 'Lunch'

        elif(dinner_accounted_for and (dinner_open <= east_coast_time <= dinner_closed)):
            #print("Dinenr")
            operation = 'Dinner'
    
    if operation != kitchen['operation']:
        data_base.execute(
            'update kitchen set operation = ? where id=?',
            (operation, kitchen_id)
        )
        data_base.commit()