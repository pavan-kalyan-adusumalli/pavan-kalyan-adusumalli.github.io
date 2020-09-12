# Project 1

Web Programming with Python and JavaScript

about Home page:
Home page itself containg a form for login from which a user can log in to the session by giving right username and password.

about login page:
login page contains login form which makes user to log in to session only if usernme and password match each other

about register page:
register page contains user registration form which allow user to create an account.
The username should be unique and more than 5 letters.
The password should also be more than 5 letters.

about search page:
The search page contains an input field by which a book can be searched.
one can search for a book by its name, author name, isbn number.

about results page:
The results page shows the relevent results matching to the submitted book name or author name or isbn number.
user can click on the individual book results to know more about books and submit their reviews.

about bookpage:
bookpage contains the information about book such as book title, author name, year of publicaiton, isbn number.
The cover of book also has been displayed by using covers.openlibrary api.
And the average ratings, average number of reviews for this book on goodreads also have been displayed.

at the bottom of page the reviews submitted by users for this book have displayed.
And there is also facility to submit your own rating and review on top of this.

about api page:
api page returns the json response containing details of the book.
The json response will be in the following format>
{
    "title": "Memory",
    "author": "Doug Lloyd",
    "year": 2015,
    "isbn": "1632168146",
    "review_count": 28,
    "average_score": 5.0
}