import os
import requests

from flask import Flask, render_template, redirect, session, g, json, request, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError


from forms import UserSignup, LoginForm, WatchlistForm
from models import db, connect_db, User, Watchlist
from keys import api_key, Password

CURR_USER_KEY = "curr_user"


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', f'postgresql://postgres:{Password}@localhost:5432/stocks'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user"""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Create a new user and add it to DB. Redirect to homepage."""

    form = UserSignup()

    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            db.session.commit()

        except IntegrityError:
            # add flash messages for error.
            return render_template('signup.html', form=form)
        
        do_login(user)

        # add flash message for successful signup.
        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Login a user."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            # add flash for login
            return redirect('/')
        
        # add flash for invalid user

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Logout a user."""

    do_logout()
    # add flash for success
    return redirect('/')


##############################################################################
# Stock route

@app.route('/stocks', methods=["POST", "GET"])
def stock_redirect():
    """Data from search bar redirects to stock details page."""
    ticker = request.form.get('search')
    
    return redirect(f'/stocks/{ticker}')

@app.route('/stocks/<stock_ticker>')
def stock_details(stock_ticker):
    """Fetch data from API about stock and display the data."""
    stock_ticker = stock_ticker.upper()
    

    URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-summary"
    querystring = {"symbol":f"{stock_ticker}", "region":"US"}
    headers = {
    'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
    'x-rapidapi-key': api_key
    }
    response = requests.request("GET", URL, headers=headers, params=querystring)
    stock = json.loads(response.text)
    return render_template('stock.html', stock=stock)

##############################################################################
# Routes for logged in 'Users'


@app.route('/create/watchlist', methods=["GET", "POST"])
def watchlists():
    """displays a form to create a watchlist"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = WatchlistForm()
    
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        watch_list = Watchlist(name=name, description=description)
        g.user.watchlists.append(watch_list)
        db.session.commit()

        return redirect(f"/")

    return render_template('create_wl.html', form=form)

@app.route('/watchlists/<watchlist_id>')
def watchlists_details(watchlist_id):
    """Display watchlist details and allow user to add and remove stocks from list."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    data = None

    watchlist = Watchlist.query.get_or_404(watchlist_id)
    if watchlist.stock == None:
        return render_template('watchlist_details.html', watchlist=watchlist, data=data)
    stocks = ",".join(watchlist.stock)

    URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"

    querystring = {"region":"US", "symbols":stocks}
    headers = {
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
        'x-rapidapi-key': api_key
    }
    response = requests.request("GET", URL, headers=headers, params=querystring)
    data = json.loads(response.text)
    

    return render_template('watchlist_details.html', watchlist=watchlist, data=data)

@app.route('/update-watchlist', methods=["POST", "GET"])
def update_watchlist():
    """Called from frontend to add/remove a stock to a watchlist."""

    watchlist_id = request.args.get('watchlist')
    ticker = request.args.get('ticker')
    Watchlist.add_or_remove_stock(watchlist_id, ticker)
    
    # should return a object instead of a string or something
    return "OK"

@app.route('/delete/watchlist/<int:watchlist_id>', methods=["POST", "GET"])
def delete_watchlist(watchlist_id):
    """Delete a watchlist."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    wl = Watchlist.query.get_or_404(watchlist_id)
    if wl.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    db.session.delete(wl)
    db.session.commit()

    return redirect("/")

@app.route('/delete/user', methods=["POST", "GET"])
def delete_user():
    """Delete a user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/")

##############################################################################
# Home route

@app.route('/')
def home():
    return render_template('homepage.html')