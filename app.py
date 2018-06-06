from flask import Flask, render_template

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

app = Flask(__name__)


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def homepage():
	category_list = session.query(Category).all()
	return render_template("homepage.html", category_list = category_list)

@app.route('/category/<int:category_id>')
def viewCategory(category_id):
	category_list = session.query(Category).all()
	selected_category = session.query(Category).filter_by(id=category_id).one()
	items = session.query(Item).filter_by(category_id=category_id).all()
	return render_template("category.html", category_list = category_list, selected_category=selected_category, items=items)

@app.route('/category/<int:category_id>/item/<int:item_id>')
def viewItem(category_id, item_id):
	category_list = session.query(Category).all()
	selected_category = session.query(Category).filter_by(id=category_id).one()
	items = session.query(Item).filter_by(category_id=category_id).all()
	selected_item = session.query(Item).filter_by(id=item_id).one()
	return render_template("item.html", category_list = category_list, selected_category=selected_category, items=items, selected_item=selected_item)

@app.route('/additem')
def addItem():
	return render_template("additem.html")

@app.route('/category/item/edit')
def editItem():
	return render_template("edititem.html")

@app.route('/deleteitem')
def deleteItem():
	return render_template("deleteitem.html")


if __name__ == "__main__":
	app.debug = True
	app.run(host='0.0.0.0', port=8000)


