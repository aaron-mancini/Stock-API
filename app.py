import os
import re
import requests

from flask import Flask, render_template, redirect, session, g, json, request, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from jinja2.exceptions import UndefinedError
from werkzeug.wrappers import response


from forms import UserSignup, LoginForm, WatchlistForm
from models import db, connect_db, User, Watchlist
# from keys import api_key, Password


CURR_USER_KEY = "curr_user"


app = Flask(__name__)

uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
api_key = os.getenv("api_key")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
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
            flash(f"Invalid signup! Please try again", "red")
            return render_template('signup.html', form=form)
        
        do_login(user)

        flash(f"Welcome {user.username}! Thanks for joining!", "green")
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
            flash(f"Welcome back {user.username}!", "green")
            return redirect('/')
        flash("Incorrect username or password", "red")
        
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Logout a user."""

    do_logout()
    flash(f"Logged Out! Thanks for visiting!", "green")
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
    

    URL = "https://yh-finance.p.rapidapi.com/stock/v2/get-summary"
    querystring = {"symbol":f"{stock_ticker}", "region":"US"}
    headers = {
    'x-rapidapi-host': "yh-finance.p.rapidapi.com",
    'x-rapidapi-key': api_key
    }
    try: 
        response = requests.request("GET", URL, headers=headers, params=querystring)
    except:
        flash("Error. API is down or invallid search term!", "red")

    newsResponse = requests.request("GET", 'https://yh-finance.p.rapidapi.com/auto-complete', headers=headers, params={"q":f"{stock_ticker}", "region":"US"})
    news = json.loads(newsResponse.text)
                                

    stock = json.loads(response.text)
    return render_template('stock.html', stock=stock, news=news)

##############################################################################
# Routes for logged in 'Users'


@app.route('/create/watchlist', methods=["GET", "POST"])
def watchlists():
    """displays a form to create a watchlist"""
    if not g.user:
        flash("Access unauthorized.", "red")
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
        flash("Access unauthorized.", "red")
        return redirect("/")
    
    data = None

    watchlist = Watchlist.query.get_or_404(watchlist_id)

    if watchlist.user_id != g.user.id:
        flash("Access unauthorized.", "red")
        return redirect("/")

    if watchlist.stock == None or watchlist.stock == []:
        return render_template('watchlist_details.html', watchlist=watchlist, data=data)
    stocks = ",".join(watchlist.stock)

    URL = "https://yh-finance.p.rapidapi.com/market/v2/get-quotes"

    querystring = {"region":"US", "symbols":stocks}
    headers = {
        'x-rapidapi-host': "yh-finance.p.rapidapi.com",
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
    # watchlist = Watchlist.query.get_or_404(watchlist_id)
    # if ticker in watchlist.stock:
    #     flash(f"Added '{ticker}' to {watchlist.name}!")
    # else: flash(f"Removed {ticker} from {watchlist.name}")
    
    
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

    flash("Successfully deleted your watchlist!", "green")
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
    flash("Successfully deleted your account!", "green")
    return redirect("/")

##############################################################################
# Home route

@app.route('/')
def home():
    return render_template('homepage.html')

# Search bar

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")

    url = "https://yh-finance.p.rapidapi.com/auto-complete"
    querystring = {"q":query,"region":"US"}
    headers = {
        'x-rapidapi-host': "yh-finance.p.rapidapi.com",
        'x-rapidapi-key': api_key
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    return data

##############################################################################
# Errors

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404

# @app.errorhandler(UndefinedError)
# def undefinded_error(e):
#     flash("Server is down or you entered an invalid term!", "red")
#     return redirect("/")