from flask import render_template
from . import category

@category.route('/')
def allCategories():
    # Do some stuff
    return render_template('catalog.html')