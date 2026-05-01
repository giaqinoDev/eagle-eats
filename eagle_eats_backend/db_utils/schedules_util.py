from eagle_eats_backend.data_base import get_db

def get_organized_schedule_info(schedule_id):
    database_ref = get_db()

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
        "week": organize_schedule(weekly_schedule)
    }

def organize_schedule(weekly_schedule):
    if weekly_schedule is None:
        return None
    
    dayofweek_keys = ["1", "2", "3", "4", "5", "6", "7"]
    org_schedule = dict.fromkeys(dayofweek_keys)

    for weekday_schedule in weekly_schedule:
        org_schedule[str(weekday_schedule["day_of_week"])] = weekday_schedule
    
    return org_schedule