# Stock Watch

http://stock-watch-news.herokuapp.com/
Stock Watch is a web app that allows users to view information about stocks and create customized watchlists to track all
of their stocks on one page.

## Features

- Search bar
  - The search bar will suggest valid stock listings in a dropdown menu based on user input. This data is requested from the API I use.
- Stock details page
  - This page features various information about the stock and company as well as recent news listings.
- Watchlist page
  - Each user created watchlist has its own page where a short summary of the stocks daily performance is displayed.

These are the three main features I chose for my website. Overall these were the most basic and important features
to include in a website like this.

## User flow / Structure

- '/' Homepage for the website with a basic title/greeting and a navbar. The navbar remains consistent throughout the site.
  From here a user can search for stocks, login and signup. If already logged in they can view watchlist, delete account, or sign out.
- '/stocks/<stock_ticker>' This is the stock details page which displays stock information and news. Anyone can view this page,
  but only users will have the option to add or remove the stock from their watchlist.
- '/create/watchlist' Registered users can create watchlists with a title and descrption. Each new watchlist is empty.
- '/watchlists/<watchlist_id>' This is the watchlist details page which displays a short daily summary of each stock and allows for removal.

## API - Yahoo Finance API https://rapidapi.com/apidojo/api/yahoo-finance1/

This API is very thorough and contains a multitude of endpoints. I chose this api because it is free and also very easy to use
despite being very information dense.

## Project Tools and Dependencies

- Html
- CSS
- Javascript
- Jquery
- Flask - Python
  - Flask_sqlalchemy
  - Flask_CORS
  - jinja
  - WTForms
  - Bcrypt
- Postgresql

## Testing

If you would like to explore and test my website without making an account you can use a test user account.
- username: testuser
- password: testuser