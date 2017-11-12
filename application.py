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
		#flash("New category created!")
		return redirect(url_for('allCategories'))
	else:
		return render_template('newcategory.html')	

@app.route('/<category_name>/edit')
def editCategory(category_name):
	return "Here to edit an existing category"

@app.route('/<category_name>/delete', methods=['GET', 'POST'])
def deleteCategory(category_name):
	if request.method == 'POST':
		deleteCategory = session.query(Category).filter_by(name=category_name).one()
		session.delete(deleteCategory)
		session.commit()
		#flash('Category Successfully Deleted')
		return redirect(url_for('allCategories'))
	else:
		return render_template('deletecategory.html', category=category_name)


# Items
@app.route('/<category_name>')
def allItems(category_name):
	return "All items in category"

@app.route('/<category_name>/<item_name>')
def singleItem(category_name, item_name):
	return "Show single item"

@app.route('/<category_name>/new')
def newItem(category_name):
	return "New item"

@app.route('/<category_name>/<item_name>/edit')
def editItem(category_name, item_name):
	return "Edit a menu item"

@app.route('/<category_name>/<item_name>/delete')
def deleteItem(category_name, item_name):
	return "Delete a menu item"

if __name__ == '__main__':
    app.secret_key = '\x82\x0cq:\x12\xbe\x18\xeb\xb3F\xf1\xc5\x9e\xd8\xdd\xaf\xb5/\x90\xd2\xebbR' # SECRET IN PRODUCTION!
    app.debug = True
    app.run(host='0.0.0.0', port=8000)