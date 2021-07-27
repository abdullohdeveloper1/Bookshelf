#------------------------------------------------------------------------#
# Imports.
#------------------------------------------------------------------------#
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Book

#------------------------------------------------------------------------#
# Pagineted books.
#------------------------------------------------------------------------#
BOOKS_PER_SHELF = 8

def paginate_books(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * BOOKS_PER_SHELF
  end = start + BOOKS_PER_SHELF
  books = [book.format() for book in selection]
  current_books = books[start:end]
  return current_books

#------------------------------------------------------------------------#
# Start the project.
#------------------------------------------------------------------------#
def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  #------------------------------------------------------------------------#
  # After request.
  #------------------------------------------------------------------------#
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  #------------------------------------------------------------------------#
  # Get all books.
  #------------------------------------------------------------------------#
  @app.route('/books')
  def retrieve_books():
    selection = Book.query.order_by(Book.id).all()
    current_books = paginate_books(request, selection)
    if len(current_books) == 0:
      abort(404)
    return jsonify({
      'success': True,
      'books': current_books,
      'total_books': len(Book.query.all())
    })

  #------------------------------------------------------------------------#
  # Update book.
  #------------------------------------------------------------------------#
  @app.route('/books/<int:book_id>', methods=['PATCH'])
  def update_books(book_id):
    body = request.get_json()
    try:
      book = Book.query.filter(Book.id == book_id).one_or_none()
      if book is None:
        abort(404)
      if 'rating' in body:
        book.rating = int(body.get('rating'))
      book.update()
      return jsonify({
        'success': True
      })
    except:
      abort(400)

  #------------------------------------------------------------------------#
  # Delete book.
  #------------------------------------------------------------------------#
  @app.route('/books/<int:book_id>', methods=['DELETE'])
  def delete_book(book_id):
    try:
      book = Book.query.filter(Book.id == book_id).one_or_none()
      if book == 0:
        abort(404)
      book.delete()
      selection = Book.query.order_by(Book.id).all()
      current_books = paginate_books(request, selection)
      return jsonify({
        'success': True,
        'deleted': book_id,
        'books': current_books,
        'total_books': len(Book.query.all())
      })
    except:
      abort(400)

  #------------------------------------------------------------------------#
  # Create book and search.
  #------------------------------------------------------------------------#
  @app.route('/books', methods=['POST'])
  def create_book():
    body = request.get_json()
    search = body.get('search', None)
    try:
      if search:
        selection = Book.query.order_by(Book.id).filter(Book.title.ilike('%{}%'.format(search)))
        current_books = paginate_books(request, selection)

        return jsonify({
          'success': True,
          'books': current_books,
          'total_books': len(selection.all())
        })
      else:
        book = Book(
          title = body.get('title', None),
          author = body.get('author', None),
          rating = body.get('rating', None)
        )
        book.insert()
        selection = Book.query.order_by(Book.id).all()
        current_books = paginate_books(request, selection)
        
        return jsonify({
          'success': False,
          'created': book.id,
          'books': current_books,
          'total_books': len(Book.query.all())
        })
    except:
      abort(422)

  #------------------------------------------------------------------------#
  # Error handlers.
  #------------------------------------------------------------------------#
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource not found'
    }), 404

  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'Not found'
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable'
    }), 422

  return app