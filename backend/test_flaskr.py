#------------------------------------------------------------------------#
# Imports.
#------------------------------------------------------------------------#
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import false
from flaskr import create_app
from models import setup_db, Book

#------------------------------------------------------------------------#
# Start the test.
#------------------------------------------------------------------------#
class BookTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app()
    self.client = self.app.test_client
    self.database_name = "bookshelf_test"
    self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', '12', 'localhost:5432', self.database_name)
    setup_db(self.app, self.database_path)

    self.new_book = {
      "title": "O'tgan kunlar", 
      "author": 'Abdulla Qodiriy',
      "rating": 5
    }

    with self.app.app_context():
      self.db = SQLAlchemy()
      self.db.init_app(self.app)
      self.db.create_all()
  def tearDown(self):
      pass
  
  #------------------------------------------------------------------------#
  # Get all books.
  #------------------------------------------------------------------------#
  def test_get_all_books(self):
    res = self.client().get('/books')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(data['books'])
    self.assertTrue(data['total_books'])

  #------------------------------------------------------------------------#
  # Get all books. (error)
  #------------------------------------------------------------------------#
  def test_get_all_books_for_404(self):
    res = self.client().get('/books?page=123456')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 404)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'], 'Resource not found')

  #------------------------------------------------------------------------#
  # Search book.
  #------------------------------------------------------------------------#
  def test_for_search_book(self):
    res = self.client().post('/books', json={'search': 'Novel'})
    data = json.loads(res.data)
    
    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(data['books'])
    self.assertTrue(data['total_books'])

  #------------------------------------------------------------------------#
  # Updata book.
  #------------------------------------------------------------------------#
  def test_update_book(self):
    res = self.client().patch('/books/1', json={'rating': 1})
    data = json.loads(res.data)

    book = Book.query.filter(Book.id == 5).one_or_none()

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertEqual(book.format()['rating'], 1)

  #------------------------------------------------------------------------#
  # Updata book. (error)
  #------------------------------------------------------------------------#
  def test_update_book_for_400(self):
    res = self.client().patch('/books/123456', json={'rating': 5})
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 400)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'], 'Bad request')
  
  #------------------------------------------------------------------------#
  # Delete book.
  #------------------------------------------------------------------------#
  def test_for_delete_book(self):
    book=Book.query.all()[-1]
    res = self.client().delete('/books/' + str(book.id))
    data = json.loads(res.data)

    book = Book.query.filter(Book.id == book.id).one_or_none()

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(data['deleted'])
    self.assertTrue(data['books'])
    self.assertTrue(data['total_books'])

  #------------------------------------------------------------------------#
  # Delete book. (error)
  #------------------------------------------------------------------------#
  def test_delete_book_for_400(self):
    res = self.client().delete('/books/123456')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 400)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'], 'Bad request')

  #------------------------------------------------------------------------#
  # Create book.
  #------------------------------------------------------------------------#
  def test_for_create_book(self):
    res = self.client().post('/books', json=self.new_book)
    data = json.loads(res.data)
    pass

  #------------------------------------------------------------------------#
  # Create book. (error)
  #------------------------------------------------------------------------#
  def test_create_book_for_422(self):
    res = self.client().post('/books', json=self.new_book)
    data = json.loads(res.data)
    pass

if __name__ == '__main__':
  unittest.main()