from flask import Blueprint, render_template


blueprint = Blueprint('dashboard', __name__)


@blueprint.route('/')
def home():
    return render_template('dashboard/home.html')
