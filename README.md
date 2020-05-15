#project1

This is a simple Books Review website where User can see a Books ratings and reviews.

In the application file there are several app.routes URL's:
1. index
2. signup
3. login
4. profile
5. search
6. logout
7. book
8. rare
9. api

Below I explain all these routes.
1. index: This is the home page till the User logs in. Here a simple discription of website with signin and signup links.
2. signup: This link helps user create a new account with BookSniffer(the website).
3. login: Directs to the login page where user can enter username and password to login.
4. profile: This is home page once user logs in. And from here user can search for the Book they like to see rating and reviews.
5. search: This is a POST method. When the user searches for the book request goes to "search" route and return to a page where we see all the results related to the search query or error if the search is invalid.
6. logout: It pops up the user_id from the session and logs out the user. Directs to index.
7. book: It collects all the data from the database about the book and shows it to the user.
8. rare: It records the users rating and review for the book and updates the database.
9. api: Anyone can go to /api/<isbn> route to get a json file of the book.
