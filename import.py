import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine("DATABASE_URL")
db = scoped_session(sessionmaker(bind=engine))


f = open(r"C:\Users\Pavan Kalyan\Desktop\project1\project1\books.csv")
reader = csv.reader(f)
for isbn,title,author,year in reader:
    db.execute("INSERT INTO books2(isbn, title, author, year) VALUES(:isbn, :title, :author, :year)",
    {'isbn':isbn,'title':title,'author':author,'year':year})
    db.commit()