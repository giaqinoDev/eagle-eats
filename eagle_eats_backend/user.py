import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from eagle_eats_backend.data_base import get_db
from eagle_eats_backend.auth import login_required
from eagle_eats_backend.db_utils.kitchens_util import update_kitchen_statuses

class curr_open_kitchens:
    def __init__(self, id, location, operation, menu_id):
        self.id = id
        self.location = location
        self.operation = operation
        self.menu_id = menu_id

blue_print = Blueprint('user', __name__, url_prefix='/user')
@blue_print.route('/dashboard', methods=('GET', 'POST'))
@login_required
def dashboard():
    update_kitchen_statuses()
    data_base = get_db()
    open_kitchens_offerings = []
    if request.method == 'GET':
        user_info = get_logged_in_user(session['account_id'])
        print(user_info['username'])
        #Get open kitchens
        open_kitchens = data_base.execute(
            'select id, menu_id, location, operation from kitchen where operation !=?',
            ('Closed',)
        ).fetchall()

        if open_kitchens:
            for kitchen in open_kitchens:
                kitchen_menu_id = kitchen['menu_id']
                if kitchen_menu_id is None:
                    open_kitchens_offerings.append(curr_open_kitchens(kitchen['id'], kitchen['location'], kitchen['operation'], None))
                    continue
                else:
                    menu_items = data_base.execute(
                        'select id, name, price from item where menu_id=? and availability=?',
                        (kitchen_menu_id, kitchen['operation'])
                    ).fetchall()
                    open_kitchens_offerings.append(curr_open_kitchens(kitchen['id'], kitchen['location'], kitchen['operation'], menu_items))
    #Get open kitchens
    return render_template('dashboard/user_dashboard.html', user_name=user_info['username'], open_kitchens_offerings = open_kitchens_offerings)

def get_logged_in_user(user_id):
    data_base = get_db()
    user_info = data_base.execute(
        'select id, username from account where id=?',
        (user_id,)
    ).fetchone()
    return user_info