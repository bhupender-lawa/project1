import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    f = open('books.csv')
    reader = csv.reader(f)
    for i, t, a, y in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:i, :t, :a, :y)", {"i": i, "t": t, "a": a, "y": y})
    db.commit()

if __name__ == "__main__":
    main()
