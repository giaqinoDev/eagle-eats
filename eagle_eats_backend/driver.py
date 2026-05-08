from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from eagle_eats_backend.data_base import get_db
from eagle_eats_backend.auth import login_required

blue_print = Blueprint('driver', __name__, url_prefix = '/driver')

@blue_print.route('/dashboard', methods=('GET',))
@login_required
def dashboard():
    db = get_db()
    driver_id = session['account_id']

    #orders that are ready and not picked up
    orders = db.execute(
        'select id, kitchen_id, total_price, delivery_location from orders where status = "ready" and driver_id is null order by id asc'
    ).fetchall()

    #drivers active deliveries
    active_orders = db.execute(
        'select id, kitchen_id, total_price, delivery_location from orders where status = "delivering" and driver_id = ?',
        (driver_id,)
    ).fetchall()

    return render_template('dashboard/drivers_dashboard.html', orders=orders, active_orders=active_orders)

@blue_print.route('/orders/<int:order_id>/claim', methods=('POST',))
@login_required
def claim_order(order_id):

    db = get_db()
    driver_id = session['account_id']

    #claim available orders
    result = db.execute(
        'update orders set status = "delivering", driver_id = ? where id = ? and status = "ready" and driver_id is null',
        (driver_id, order_id)
    )

    if result.rowcount == 0:
        flash("Order already claimed")
    else:
        db.commit()

    return redirect(url_for('driver.dashboard'))

@blue_print.route('/orders/<int:order_id>/complete', methods=('POST',))
@login_required
def complete_order(order_id):
    db = get_db()
    driver_id = session['account_id']

    #owner of order can complete order
    result = db.execute(
        'update orders set status = "completed" where id = ? and driver_id = ? and status = "delivering"',
        (order_id, driver_id)
    )
    db.commit()

    if result.rowcount == 0:
        flash("Cannot complete this order")

    return redirect(url_for('driver.dashboard'))