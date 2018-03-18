#!/usr/bin/python
# Framework and DB
from flask import Flask, render_template, redirect, url_for, request, flash, \
    jsonify

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

# OAuth
import json
from flask import make_response
import requests
from flask import session as login_session
import random
import string

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# LinkedIn - OAuth 2.0 - Server side implementation
@app.route('/login-linkedin')
def linkedin_login():
    # Request Authorization code
    base_url = 'https://www.linkedin.com/oauth/v2/authorization?' + \
        'response_type=code'
    client_id = "863720r8ib2vo6"
    redirect_uri = "http://0.0.0.0:8000/licode"
    # Secret in production
    client_secret = "gfaWUCJWGsnqQ54y"
    # Secret, to prevent CSRF
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state

    scope = 'r_basicprofile,r_emailaddress'  # LinkedIn permissions

    return redirect('{0}&client_id={1}&redirect_uri={2}&state={3}&scope={4}'
                    .format(base_url, client_id, redirect_uri, state, scope))


@app.route('/licode', methods=['GET', 'POST'])
def linkedin_connect():
    # Get state and match with my state (to prevent CSRF)
    try:
        state = request.args.get('state', None)
    except:
        response = make_response(json.dumps('Failed to get state from ' +
                                            'LinkedIn.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if login_session['state'] != state:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get authorization code
    try:
        code = request.args.get('code', None)
    except:
        response = make_response(json.dumps('Failed to get authorization ' +
                                            'code from LinkedIn.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get access token and expires in to make requests
    data = {}
    data['code'] = code
    data['grant_type'] = 'authorization_code'
    data['redirect_uri'] = "http://0.0.0.0:8000/licode"
    data['client_id'] = "863720r8ib2vo6"
    data['client_secret'] = "gfaWUCJWGsnqQ54y"  # Secret in production
    url = 'https://www.linkedin.com/oauth/v2/accessToken'

    request_linkedin = requests.post('https://www.linkedin.com/oauth/v2/' +
                                     'accessToken', data=data).json()

    try:
        login_session['access_token'] = request_linkedin["access_token"]
        login_session['expires_in'] = request_linkedin["expires_in"]
    except:
        response = make_response(json.dumps('''Failed to get access_token and
             expires_in from LinkedIn.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get basic LinkedIn profile data
    parameters = 'first-name,email-address,picture-url'
    uri = 'https://api.linkedin.com/v1/people/~:(%s)?format=json' \
        % (parameters)
    headers = {}
    headers['Authorization'] = 'Bearer ' + login_session['access_token']
    get_profile = requests.get(uri, headers=headers).json()

    try:
        login_session['name'] = get_profile['firstName']
        login_session['email'] = get_profile['emailAddress']
        login_session['picture'] = get_profile['pictureUrl']
    except:
        response = make_response(json.dumps('''Failed to get retrieve LinkedIn
             profile data.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if user exists, if not, then create it
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    flash("You are now logged in as %s" % login_session['name'])
    return redirect(url_for('allCategories'))


# Log-out of LinkedIn sign-in
@app.route('/logout-linkedin')
def linkedin_logout():
    # Check if user is logged out already
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('''Current user not
             connected.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if user is valid linkedin user
    uri = 'https://api.linkedin.com/v1/people/~?format=json'
    headers = {}
    headers['Authorization'] = 'Bearer ' + login_session['access_token']
    request_linkedin = requests.get(uri, headers=headers)

    if request_linkedin.status_code == 200:
        del login_session['access_token']
        del login_session['name']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['expires_in']
        return redirect(url_for('allCategories'))
    else:
        response = make_response(json.dumps('''Failed to revoke token for
             given user.''', 401))
        response.headers['Content-Type'] = 'application/json'
        return response


# Helper Functions to authorization
def createUser(login_session):
    newUser = User(name=login_session['name'], email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def checkIfLoggedIn():
    if 'name' not in login_session:
        return False
    else:
        return True


# Categories
@app.route('/')
def allCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    logged_in = checkIfLoggedIn()
    return render_template('catalog.html', categories=categories,
                           logged_in=logged_in)


@app.route('/new', methods=['GET', 'POST'])
def newCategory():
    if 'name' not in login_session:
        return redirect(url_for('allCategories'))
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('allCategories'))
    else:
        logged_in = checkIfLoggedIn()
        return render_template('newcategory.html', logged_in=logged_in)


@app.route('/<category_name>/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_name, category_id):
    if 'name' not in login_session:
        return redirect(url_for('allCategories'))
    if request.method == 'POST':
        editCategoryName = session.query(Category).\
            filter_by(id=category_id).one()
        editCategoryName.name = request.form['name']
        session.add(editCategoryName)
        session.commit()
        return redirect(url_for('allCategories'))
    logged_in = checkIfLoggedIn()
    return render_template('editcategory.html', category_name=category_name,
                           category_id=category_id, logged_in=logged_in)


@app.route('/<category_name>/<int:category_id>/delete',
           methods=['GET', 'POST'])
def deleteCategory(category_name, category_id):
    if 'name' not in login_session:
        return redirect(url_for('allCategories'))
    if request.method == 'POST':
        deleteCategory = session.query(Category).\
            filter_by(id=category_id).one()
        session.delete(deleteCategory)
        session.commit()
        deleteItems = session.query(Item).\
            filter_by(category_id=category_id).all()
        for i in deleteItems:
            session.delete(i)
            session.commit()
        return redirect(url_for('allCategories'))
    else:
        logged_in = checkIfLoggedIn()
        return render_template('deletecategory.html',
                               category_name=category_name,
                               category_id=category_id,
                               logged_in=logged_in)


# Items
@app.route('/<category_name>/<int:category_id>')
def allItems(category_name, category_id):
    items = session.query(Item).filter_by(category_id=category_id).\
        order_by(asc(Item.name))
    logged_in = checkIfLoggedIn()
    return render_template('allitems.html', category_name=category_name,
                           category_id=category_id, items=items,
                           logged_in=logged_in)


@app.route('/<category_name>/<int:category_id>/<item_name>/<int:item_id>')
def singleItem(category_name, category_id, item_name, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    logged_in = checkIfLoggedIn()
    return render_template('singleitem.html', category_name=category_name,
                           category_id=category_id,
                           item=item,
                           logged_in=logged_in)


@app.route('/<category_name>/<int:category_id>/new', methods=['GET', 'POST'])
def newItem(category_name, category_id):
    if 'name' not in login_session:
        return redirect(url_for('allCategories'))
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       price=request.form['price'],
                       category_id=category_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('allItems', category_name=category_name,
                                category_id=category_id))
    logged_in = checkIfLoggedIn()
    return render_template('newitem.html', category_name=category_name,
                           category_id=category_id,
                           logged_in=logged_in)


@app.route('/<category_name>/<int:category_id>/<item_name>/' +
           '<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(category_name, category_id, item_name, item_id):
    if 'name' not in login_session:
        return redirect(url_for('allCategories'))
    editItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        editItem.name = request.form['name']
        editItem.description = request.form['description']
        editItem.price = request.form['price']
        session.add(editItem)
        session.commit()
        return redirect(url_for('allItems', category_name=category_name,
                        category_id=category_id))
    logged_in = checkIfLoggedIn()
    return render_template('edititem.html', category_name=category_name,
                           category_id=category_id,
                           item_name=item_name,
                           item_id=item_id,
                           item=editItem,
                           logged_in=logged_in)


@app.route('/<category_name>/<int:category_id>/<item_name>/<int:item_id>' +
           '/delete', methods=['GET', 'POST'])
def deleteItem(category_name, category_id, item_name, item_id):
    if 'name' not in login_session:
        return redirect(url_for('allCategories'))
    if request.method == 'POST':
        deleteItem = session.query(Item).filter_by(id=item_id).one()
        session.delete(deleteItem)
        session.commit()
        return redirect(url_for('allItems', category_name=category_name,
                                category_id=category_id))
    logged_in = checkIfLoggedIn()
    return render_template('deleteitem.html', category_name=category_name,
                           category_id=category_id, item_name=item_name,
                           item_id=item_id, logged_in=logged_in)


# JSON APIs
@app.route('/<category_name>/<int:category_id>/<item_name>/<int:item_id>/JSON')
def singleItemJSON(category_name, category_id, item_name, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)

if __name__ == '__main__':
    print "hallo med dig"
    app.secret_key = "secret_in_production123"  # SECRET IN PRODUCTION!
    app.debug = True
    app.run(host='18.195.163.63', port=80)
