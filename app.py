from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

app = Flask(__name__)


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)


@app.route('/')
def homepage():
	session = DBSession()
	category_list = session.query(Category).all()
	items = session.query(Item).order_by(desc(Item.id)).limit(5).all()
	return render_template("homepage.html", category_list = category_list, items=items)

@app.route('/category/<int:category_id>')
def viewCategory(category_id):
	session = DBSession()
	category_list = session.query(Category).all()
	selected_category = session.query(Category).filter_by(id=category_id).one()
	items = session.query(Item).filter_by(category_id=category_id).all()

	return render_template("category.html", category_list = category_list, selected_category=selected_category, items=items)

@app.route('/category/<int:category_id>/item/<int:item_id>')
def viewItem(category_id, item_id):
	session = DBSession()
	category_list = session.query(Category).all()
	selected_category = session.query(Category).filter_by(id=category_id).one()
	items = session.query(Item).filter_by(category_id=category_id).all()
	selected_item = session.query(Item).filter_by(id=item_id).one()

	return render_template("item.html", category_list = category_list, selected_category=selected_category, items=items, selected_item=selected_item)

@app.route('/additem', methods=['GET','POST'])
def addItem():
	session = DBSession()
	category_list = session.query(Category).all()

	if request.method == 'POST':
		if request.form['item_name']:
			item_category = request.form['item_category']
			category_id = session.query(Category.id).filter_by(name=item_category).one()[0]
			new_item = Item(name=request.form['item_name'],
				description=request.form['item_description'],
				category_id=category_id)
			session.add(new_item)
			session.commit()
			flash("Item Added!")
			return redirect(url_for('homepage'))
	else:
		return render_template("additem.html",category_list = category_list )

@app.route('/category/item/<int:item_id>/edit', methods=['GET','POST'])
def editItem(item_id):
	session = DBSession()
	category_list = session.query(Category).all()
	edited_item = session.query(Item).filter_by(id=item_id).one()
	if request.method == 'POST':
		item_category = request.form['item_category']
		category_id = session.query(Category.id).filter_by(name=item_category).one()[0]
		if request.form['item_name']:
			edited_item.name = request.form['item_name']
			edited_item.description = request.form['item_description']
			edited_item.category_id = category_id
			session.add(edited_item)
			session.commit()
			flash("Item Edited!")
			return redirect(url_for('homepage'))
	else:
		return render_template("edititem.html", edited_item=edited_item, category_list=category_list)

@app.route('/deleteitem/<int:item_id>', methods=['GET', 'POST'])
def deleteItem(item_id):
	session = DBSession()
	selected_item = session.query(Item).filter_by(id=item_id).one()

	if request.method == 'POST':
		deleted_item = session.query(Item).filter_by(id=item_id).one()
		session.delete(deleted_item)
		session.commit()
		flash("Item Deleted!")
		return redirect(url_for('homepage'))

	else:

		return render_template("deleteitem.html", selected_item = selected_item )


if __name__ == "__main__":
	app.secret_key = 'dev key'
	app.debug = True
	app.run(host='0.0.0.0', port=8000)


