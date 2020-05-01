CREATE TABLE books(
  id SERIAL PRIMARY KEY,
  isbn VARCHAR NOT NULL UNIQUE,
  title VARCHAR NOT NULL,
  author VARCHAR NOT NULL,
  year INTEGER NOT NULL
);

CREATE TABLE users(
  id  SERIAL PRIMARY KEY,
  name VARCHAR ,
  username  VARCHAR UNIQUE,
  password  VARCHAR
);

CREATE TABLE ratereview(
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users,
  book_id INTEGER REFERENCES books,
  rating INTEGER,
  review VARCHAR
);