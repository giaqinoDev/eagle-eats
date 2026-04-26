import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from eagle_eats_backend.data_base import get_db

blue_print = Blueprint('user', __name__, url_prefix='/user')
@blue_print.route('/<int:id>/dashboard', methods=('GET', 'POST'))
def dashboard():
    return None