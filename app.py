from flask import (Flask, render_template,
request, redirect, url_for, flash, jsonify)

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

# imports for login functionality
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']

app = Flask(__name__)


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    # print "done!"
    return output

 # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("You have been logged out!")
        return redirect(url_for('homepage'))

    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
def homepage():
    session = DBSession()
    category_list = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.id)).limit(5).all()
    return render_template("homepage.html",
                           category_list=category_list,
                           items=items,
                           login_session=login_session)


@app.route('/category/<int:category_id>')
def viewCategory(category_id):
    session = DBSession()
    category_list = session.query(Category).all()
    selected_category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()

    return render_template("category.html",
                           category_list=category_list,
                           selected_category=selected_category,
                           items=items,
                           login_session=login_session)


@app.route('/category/<int:category_id>/item/<int:item_id>')
def viewItem(category_id, item_id):
    session = DBSession()
    category_list = session.query(Category).all()
    selected_category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    selected_item = session.query(Item).filter_by(id=item_id).one()

    return render_template("item.html",
                           category_list=category_list,
                           selected_category=selected_category,
                           items=items,
                           selected_item=selected_item,
                           login_session=login_session)


@app.route('/additem', methods=['GET', 'POST'])
def addItem():
    session = DBSession()
    category_list = session.query(Category).all()

    if 'username' not in login_session:
        flash("You need to login to access this feature!")
        return redirect('/login')

    if request.method == 'POST':
        if request.form['item_name']:
            item_category = request.form['item_category']
            category_id = session.query(Category.id).filter_by(
                name=item_category).one()[0]
            new_item = Item(name=request.form['item_name'],
                            description=request.form['item_description'],
                            category_id=category_id,
                            creator=login_session['email'])
            session.add(new_item)
            session.commit()
            flash("Item Added!")
            return redirect(url_for('homepage'))

    else:
        return render_template("additem.html",
                               category_list=category_list,
                               login_session=login_session)


@app.route('/category/item/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    session = DBSession()
    category_list = session.query(Category).all()
    edited_item = session.query(Item).filter_by(id=item_id).one()

    if 'username' not in login_session:
        flash("You need to login to access this feature!")
        return redirect('/login')

    if login_session['email'] != edited_item.creator:
        flash("Sorry, only the creator of the item is allowed to edit it!!")
        return redirect('/')

    if request.method == 'POST':
        item_category = request.form['item_category']
        category_id = session.query(Category.id).filter_by(name=item_category).one()[0]
        if request.form['item_name']:
            edited_item.name = request.form['item_name']
            edited_item.description = request.form['item_description']
            edited_item.category_id = category_id
            edited_item.creator = login_session['email']
            print edited_item.description
            session.add(edited_item)
            session.commit()
            flash("Item Edited!")
            return redirect(url_for('homepage'))
    else:
        return render_template("edititem.html",
                               edited_item=edited_item,
                               category_list=category_list,
                               login_session=login_session)


@app.route('/deleteitem/<int:item_id>', methods=['GET', 'POST'])
def deleteItem(item_id):
    session = DBSession()
    selected_item = session.query(Item).filter_by(id=item_id).one()

    if 'username' not in login_session:
        flash("You need to login to access this feature!")
        return redirect('/login')

    if login_session['email'] != selected_item.creator:
        flash("Sorry, only the creator of the item is allowed to delete it!!")
        return redirect('/')

    if request.method == 'POST':
        deleted_item = session.query(Item).filter_by(id=item_id).one()
        session.delete(deleted_item)
        session.commit()
        flash("Item Deleted!")
        return redirect(url_for('homepage'))

    else:

        return render_template("deleteitem.html",
                               selected_item=selected_item,
                               login_session=login_session)


@app.route('/JSON')
def JSONCatalog():
    session = DBSession()
    items = session.query(Item).all()

    return jsonify(json_list=[i.serialize for i in items])


@app.route('/category/<int:category_id>/JSON')
def JSONCategory(category_id):
    session = DBSession()
    category_list = session.query(Category).all()
    selected_category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()

    return jsonify(json_list=[i.serialize for i in items])


@app.route('/item/<int:item_id>/JSON')
def JSONItem(item_id):
    session = DBSession()
    selected_item = session.query(Item).filter_by(id=item_id).one()

    return jsonify(json_list=(selected_item.serialize))


if __name__ == "__main__":
    app.secret_key = 'dev key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
