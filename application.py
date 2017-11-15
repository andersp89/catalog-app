from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# LinkedIn - OAuth 2.0
@app.route('/linkedin')
def linkedin():	
	# Step 1: Authenticate user with OAuth 2.0

	# Settings
	client_id = "863720r8ib2vo6"
	redirect_uri = "http://0.0.0.0:8000/"
	client_secret = "gfaWUCJWGsnqQ54y" # Secret
	state = "sdafa2121r20SADAFl" # Secret, to prevent CSRF
	scope = "r_basicprofile" # LinkedIn permissions

	return redirect("https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={0}&redirect_uri={1}&state={2}&scope={3}".format(client_id, redirect_uri, state, scope))


	# Step 2: Retrieve basic profile data
	code = '' #OAuth 2.0 authorization code
	state = '' #CSRF attacks check



#http://0.0.0.0:8000/?code=AQTs-9oO6-TDLX8mz_8-0AuL3LXkYmvy0Rn7zdQgC0mKY972rfKUm1fLkJkoUqOq5aueXt1yeeA_sGu19H8I1y64b4lV8oYmbqYOmxg2rUdHBNiV1FgJR_NMz-HIeTgvhWoS0NEoQVodpv3lYBA&state=sdafa2121r20SADAFl

	# Step 3: 



# Local Permission System





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