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
        cart = session.get('cart', {})
        user_info = get_logged_in_user(session['account_id'])
        print(user_info['username'])
        #Get open kitchens
        open_kitchens = data_base.execute(
            'select id, menu_id, location, operation from kitchen where operation !=?',
            ('Closed',)
        ).fetchall()

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
    return render_template('dashboard/user_dashboard.html', cart=cart, user_name=user_info['username'], open_kitchens_offerings = open_kitchens_offerings)

def get_logged_in_user(user_id):
    data_base = get_db()
    user_info = data_base.execute(
        'select id, username from account where id=?',
        (user_id,)
    ).fetchone()
    return user_info


#------------------------Cart/Order System-----------------------------------------------------------
@blue_print.route('/cart/add/<int:kitchen_id>/<int:item_id>', methods = ('GET', 'POST'))
@login_required
def add_to_cart(kitchen_id, item_id):
    db = get_db()

    item = db.execute(
        'SELECT id, name, price FROM item WHERE id = ?',
        (item_id,)
    ).fetchone()

    if item is None:
        return redirect(url_for('user.dashboard'))

    cart = session.get('cart', {})
    existing_kitchen_ids = {
        item['kitchen_id']
        for item in cart.values()
    }

    if kitchen_id not in existing_kitchen_ids and len(existing_kitchen_ids) > 0:
        flash("Can only order from the same kitchen")
    else:
        item_id = str(item_id)
        cart_key = f"{kitchen_id}:{item_id}"

        # increment quantity
        if cart_key in cart:
            cart[cart_key]['quantity'] += 1
        else:
            cart[cart_key] = {
                "kitchen_id": kitchen_id,
                "item_id": item_id,
                "name": item['name'],
                "price": float(item['price']),
                "quantity": 1
            }

    #update session with mutated cart
    session['cart'] = cart

    return redirect(url_for('user.dashboard'))

@blue_print.route('/cart/remove/<int:kitchen_id>/<int:item_id>', methods=('GET', 'POST'))
@login_required
def remove_from_cart(kitchen_id, item_id):
    cart = session.get('cart', {})
    item_id = str(item_id)
    cart_key = f"{kitchen_id}:{item_id}"

    if cart_key in cart:
        cart[cart_key]['quantity'] -= 1
        if cart[cart_key]['quantity'] <= 0:
            del cart[cart_key]

    session['cart'] = cart

    return redirect(url_for('user.dashboard'))

@blue_print.route('/cart/set-location', methods=['POST'])
@login_required
def set_delivery_location():
    location = request.form.get('delivery_location')

    if location:
        session['delivery_location'] = location

    return redirect(url_for('user.dashboard'))

@blue_print.route('/cart/checkout', methods=('POST',))
@login_required
def checkout():

    db = get_db()

    cart = session.get('cart', {})
    delivery_location = session.get('delivery_location')

    # validation
    if not cart:
        return "Cart is empty"

    if not delivery_location:
        return "Please select a delivery location"

    user_id = session['account_id']

    first_cart_item = next(iter(cart.values()))
    kitchen_id = first_cart_item['kitchen_id']

    total_price = 0

    # calculate order total
    for cart_item in cart.values():

        quantity = cart_item['quantity']
        price = cart_item['price']

        total_price += quantity * price

    # create ONE order
    order_cursor = db.execute(
        '''insert into orders
        (
            user_id,
            kitchen_id,
            status,
            total_price,
            delivery_location
        )
        values (?, ?, ?, ?, ?)''',
        (
            user_id,
            kitchen_id,
            'pending',
            total_price,
            delivery_location
        )
    )

    order_id = order_cursor.lastrowid

    # create order items
    for cart_item in cart.values():

        db.execute(
            '''insert into order_item
            (
                order_id,
                item_id,
                quantity,
                item_name,
                item_price
            )
            values(?, ?, ?, ?, ?)''',
            (
                order_id,
                cart_item['item_id'],
                cart_item['quantity'],
                cart_item['name'],
                cart_item['price']
            )
        )

    db.commit()

    # clear cart after successful checkout
    session['cart'] = {}

    return redirect(url_for('user.dashboard'))