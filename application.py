from flask import Flask, render_template, redirect, url_for, request, flash, jsonify # request: receiving HTTP requests <-
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

# Imports for oauth
# from oauth2client.client import flow_from_clientsecrets
# from oauth2client.client import FlowExchangeError
# import httplib2
import json # python -> JSON
from flask import make_response # Making HTTP responses
import requests # Making HTTP requests server ->
from flask import session as login_session # Login session management server side


app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# LinkedIn - OAuth 2.0 - Server side implementation
@app.route('/login-linkedin')
def linkedin_connect():	
	# Step 1: Authenticate user with OAuth 2.0

	# Settings
	base_url = 'https://www.linkedin.com/oauth/v2/authorization?response_type=code'
	client_id = "863720r8ib2vo6"
	redirect_uri = "http://0.0.0.0:8000/licode"
	client_secret = "gfaWUCJWGsnqQ54y" # Secret
	state = "sdafa2121r20SADAFl" # Secret, to prevent CSRF, TODO make a random function instead!
	scope = "r_basicprofile" # LinkedIn permissions
	login_session['state'] = state

	return redirect('{0}&client_id={1}&redirect_uri={2}&state={3}&scope={4}'.format(base_url, client_id, redirect_uri, state, scope))

#=<path:string_value>
@app.route('/licode', methods=['GET', 'POST'])
def linkedin_login():	
	# Step 2: Retrieve basic profile data
	# Retrieve values from redirect_uri:
	state = request.args.get('state', None)
	
	# match state, if not send 404 error
	# if error, redirect_uri has additional parameters:
	# error: user_cancelled_login user_cancelled_authorize
	# error_description
	# state
	if login_session['state'] != state:
		response = make_response(json.dumps('Invalid state parameter.'), 401) # WHY: use JSON format in make_response?
		response.headers['Content-Type'] = 'application/json'
		return response

	

	# Step 3: exchange code for access token
	
	# Settings
	data = {}
	data['code'] = request.args.get('code', None)
	data['grant_type'] = 'authorization_code'
	data['redirect_uri'] = "http://0.0.0.0:8000/licode"
	data['client_id'] = "863720r8ib2vo6"
	data['client_secret'] = "gfaWUCJWGsnqQ54y" # Secret
	url = 'https://www.linkedin.com/oauth/v2/accessToken'

	#data = 'grant_type={0}&code={1}&redirect_uri={2}&client_id={3}&client_secret={4}'.format(grant_type, code, redirect_uri, client_id, client_secret)
	request_linkedin = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data=data).json()
	
	try:	
		access_token = request_linkedin["access_token"]
		expires_in = request_linkedin["expires_in"]
	except ValueError:
		response = make_response(json.dumps('Failed to get access token and expires in.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	
	#access_token = json.dumps(request_linkedin)['access_token']


	
	#access_token = json.loads(access)['access_token']
	#access_json = json.loads(status)['post']['access_token']
	#print('JSON FORMAT FTW!!!!: ' + access_json)
	#access_token = access_json['access_token']
	#expires_in = access_json['expires_in']
	
	# Acess token response
	# A successful access token request will return a JSON object containing the following:
	#access_token = access.access_token
	#expires_in = access.expires_in # 60 days

	return 'my code: ' + data['code'] + '<br> my state: ' + state + '<br> post: ' + str(request_linkedin) + '<br> access token:' + str(access_token) + '<br>' + str(expires_in)

	# access token, allow for 1000 chars
	expires_in = '' # 60 days

	# Step 4: Make authenticated requests
	# GET /v1/people/~ HTTP/1.1
	# Host: api.linkedin.com
	# Connection: Keep-Alive
	# Authorization: Bearer AQXdSP_W41_UPs5ioT_t8HESyODB4FqbkJ8LrV_5mff4gPODzOYR

	# If 401 Unaurthorized" response; redirect user back to the start of the auth flow.

	# Refresh your Access Tokens
	# If expires_in is outdated, then redirect user back to the start of the auth flow, but skip the part of accepting the dialog box.


	## Step 2 - retreieve basic profile data (optional)

# Categories
@app.route('/')
def allCategories():
	categories = session.query(Category).order_by(asc(Category.name))
	return render_template('catalog.html', categories=categories)

@app.route('/new', methods=['GET', 'POST'])
def newCategory():
	if request.method == 'POST':
		newCategory = Category(name=request.form['name'])
		session.add(newCategory)
		session.commit()
		return redirect(url_for('allCategories'))
	else:
		return render_template('newcategory.html')	

@app.route('/<category_name>/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_name, category_id):
	if request.method == 'POST':
		editCategoryName = session.query(Category).filter_by(id=category_id).one()
		editCategoryName.name = request.form['name']
		session.add(editCategoryName)
		session.commit()
		return redirect(url_for('allCategories'))
	return render_template('editcategory.html', category_name=category_name, category_id=category_id)

@app.route('/<category_name>/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_name, category_id):
	if request.method == 'POST':
		deleteCategory = session.query(Category).filter_by(id=category_id).one()
		session.delete(deleteCategory)
		session.commit()
		deleteItems = session.query(Item).filter_by(category_id=category_id).all()
		for i in deleteItems:
			session.delete(i)
			session.commit()
		return redirect(url_for('allCategories'))
	else:
		return render_template('deletecategory.html', category_name=category_name, category_id=category_id)


# Items
@app.route('/<category_name>/<int:category_id>')
def allItems(category_name, category_id):
	items = session.query(Item).filter_by(category_id=category_id).order_by(asc(Item.name))
	return render_template('allitems.html', category_name=category_name, category_id=category_id, items=items)

@app.route('/<category_name>/<int:category_id>/<item_name>/<int:item_id>')
def singleItem(category_name, category_id, item_name, item_id):
	item = session.query(Item).filter_by(id=item_id).one()
	return render_template('singleitem.html', category_name=category_name, category_id=category_id, item=item)

@app.route('/<category_name>/<int:category_id>/new', methods=['GET', 'POST'])
def newItem(category_name, category_id):
	if request.method == 'POST':
		newItem = Item(name=request.form['name'], description=request.form['description'], price=request.form['price'], category_id=category_id)
		session.add(newItem)
		session.commit()
		return redirect(url_for('allItems', category_name=category_name, category_id=category_id))
	return render_template('newitem.html', category_name=category_name, category_id=category_id)

@app.route('/<category_name>/<int:category_id>/<item_name>/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(category_name, category_id, item_name, item_id):
	editItem = session.query(Item).filter_by(id=item_id).one()
	if request.method == 'POST':
		editItem.name = request.form['name']
		editItem.description = request.form['description']
		editItem.price = request.form['price']
		session.add(editItem)
		session.commit()
		return redirect(url_for('allItems', category_name=category_name, category_id=category_id))
	return render_template('edititem.html', category_name=category_name, category_id=category_id, item_name=item_name, item_id=item_id, item=editItem)

@app.route('/<category_name>/<int:category_id>/<item_name>/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(category_name, category_id, item_name, item_id):
	if request.method == 'POST':
		deleteItem = session.query(Item).filter_by(id=item_id).one()
		session.delete(deleteItem)
		session.commit()
		return redirect(url_for('allItems', category_name=category_name, category_id=category_id))
	return render_template('deleteitem.html', category_name=category_name, category_id=category_id, item_name=item_name, item_id=item_id)

if __name__ == '__main__':
    app.secret_key = '\x82\x0cq:\x12\xbe\x18\xeb\xb3F\xf1\xc5\x9e\xd8\xdd\xaf\xb5/\x90\xd2\xebbR' # SECRET IN PRODUCTION!
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

