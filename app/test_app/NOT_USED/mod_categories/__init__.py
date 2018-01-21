from flask import Blueprint

category = Blueprint('category', __name__, template_folder='templates')

from . import views