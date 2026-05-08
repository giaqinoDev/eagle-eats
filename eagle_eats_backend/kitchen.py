from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from eagle_eats_backend.data_base import get_db
from eagle_eats_backend.auth import login_required

blue_print = Blueprint('kitchen', __name__, url_prefix='/kitchen')
@blue_print.route("/dashboard", methods=('GET', 'POST'))
@login_required
def dashboard():
    db = get_db()
    account_id = session['account_id']
    kitchen = db.execute(
        'select id, location from kitchen where account_id=?',
        (account_id,)
    ).fetchone()

    if kitchen is None:
        return "Kitchen not found"

    orders = db.execute(
        '''select id, status, total_price, delivery_location from orders where kitchen_id=?
        and status in ('pending', 'ready') order by id desc''',
        (kitchen['id'],)
    ).fetchall()

    enriched_orders = []

    for order in orders:
        items = db.execute(
            'select item_name, quantity from order_item where order_id = ?',
            (order['id'],)
        ).fetchall()

        enriched_orders.append({
            "id": order['id'],
            "status": order['status'],
            "total_price": order['total_price'],
            "delivery_location": order['delivery_location'],
            "items": items
        })

    return render_template('dashboard/kitchen_dashboard.html', kitchen=kitchen, orders=enriched_orders)

@blue_print.route('/orders/<int:order_id>/ready', methods=('POST',))
@login_required
def mark_ready(order_id):

    db = get_db()

    db.execute(
        'update orders set status="ready" where id = ?',
        (order_id,)
    )
    db.commit()

    return redirect(url_for('kitchen.dashboard'))