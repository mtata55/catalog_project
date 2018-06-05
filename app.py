from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def homepage():
	return render_template("homepage.html")

@app.route('/category')
def viewCategory():
	return render_template("category.html")

@app.route('/category/item')
def viewItem():
	return render_template("item.html")

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


