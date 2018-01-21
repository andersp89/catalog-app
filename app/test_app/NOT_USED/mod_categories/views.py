from . import category
#from app import db

from flask import render_template, current_app
from models import function1

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

'''
def checkIfLoggedIn():
    if 'name' not in login_session:
        return False
    else:
        return True
'''


@category.route('/')
def allCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    logged_in = function1.checkIfLoggedIn()
    return render_template('catalog.html', categories=categories,
                           logged_in=logged_in)

'''
def allCategories():
    # Do some stuff
    return render_template('catalog.html')

'''