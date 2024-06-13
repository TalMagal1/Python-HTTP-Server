import time
from flask import Flask, request, jsonify
from loogger_config import request_logger, books_logger
import logging
import werkzeug

app = Flask(__name__)
books = []  # List to store books
books_id_counter = 1  # Counter to generate book IDs
VALID_GENRES = ["SCI_FI", "NOVEL", "HISTORY", "MANGA", "ROMANCE", "PROFESSIONAL"]
request_counter = 1


# Suppress Werkzeug WSGI server logs
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.WARNING)


def book_exists(title):
    title_lower = title.lower()
    for book in books:
        if book['title'].lower() == title_lower:
            return True
    return False


def filter_books(params):
    filtered_books = books
    if 'author' in params:
        filtered_books = [book for book in filtered_books if book['author'].lower() == params['author'].lower()]
    if 'price-bigger-than' in params:
        filtered_books = [book for book in filtered_books if book['price'] >= int(params['price-bigger-than'])]
    if 'price-less-than' in params:
        filtered_books = [book for book in filtered_books if book['price'] <= int(params['price-less-than'])]
    if 'year-bigger-than' in params:
        filtered_books = [book for book in filtered_books if book['year'] >= int(params['year-bigger-than'])]
    if 'year-less-than' in params:
        filtered_books = [book for book in filtered_books if book['year'] <= int(params['year-less-than'])]
    if 'genres' in params:
        genres = params['genres'].split(',')
        filtered_books = [book for book in filtered_books if any(genre in book['genres'] for genre in genres)]
    return filtered_books


def validate_genres(genres):
    return all(genre in VALID_GENRES for genre in genres)


def log_request_info(endpoint, verb, request_id):
    request_logger.info(f"Incoming request | #{request_id} | resource: {endpoint} | HTTP Verb {verb}",
                        extra={'request_number': request_id})


def log_request_duration(start_time, request_id):
    duration = int((time.time()-start_time)*1000)
    request_logger.debug(f"request #{request_id} duration: {duration}ms",
                         extra={'request_number': request_id})


@app.before_request
def before_request_logging():
    global request_counter
    request.start_time = time.time()
    request.request_id = request_counter
    log_request_info(request.path, request.method, request_counter)


@app.after_request
def after_request_logging(response):
    global request_counter
    # request.start_time = time.time()
    log_request_duration(request.start_time, request_counter)
    request_counter += 1
    return response


@app.route('/books/health', methods=['GET'])
def health():
    return 'OK', 200


@app.route('/book', methods=['POST'])
def create_book():
    global request_counter
    global books_id_counter
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    price = data.get('price')
    year = data.get('year')
    genres = data.get('genres')
    if book_exists(title):
        error_message = f"Error: Book with the title [{title}] already exists in the system"
        books_logger.error(error_message, extra={'request_number': request_counter})
        return jsonify(errorMessage=f"Error: Book with the title [{title}]"
                                    f" already exists in the system"), 409
    if not 1940 <= year <= 2100:
        error_message = (f"Error: Can't create new Book that its year [{year}]"
                         f" is not in the accepted range [1940 -> 2100]")
        books_logger.error(error_message, extra={'request_number': request_counter})
        return jsonify(errorMessage=f"Error: Can't create new Book that its year [{year}] "
                                    f"is not in the accepted range [1940 -> 2100]"), 409
    if price < 0:
        error_message = f"Error: Can't create new Book with negative price"
        books_logger.error(error_message, extra={'request_number': request_counter})
        return jsonify(errorMessage=f"Error: Can't create new Book with negative price"), 409

    books_logger.info(f"Creating new Book with Title [{title}]",  extra={'request_number': request_counter})
    books_logger.debug(f"Currently there are {len(books)} Books in the system. New Book will be assigned with id "
                       f"{books_id_counter}", extra={'request_number': request_counter})
    book = {
        'id': books_id_counter,
        'title': title,
        'author': author,
        'price': price,
        'year': year,
        'genres': genres
    }
    books.append(book)
    books_id_counter += 1
    return jsonify(result=book['id']), 200


@app.route('/books/total', methods=['GET'])
def get_total_books():
    global request_counter
    filtered_books = filter_books(request.args)
    global request_counter
    books_logger.info(f"Total Books found for requested filters is {len(filtered_books)}",
                      extra={'request_number': request_counter})
    return jsonify(result=len(filtered_books)), 200


@app.route('/books', methods=['GET'])
def get_books():
    global request_counter
    genres = request.args.get('genres')
    if genres and not validate_genres(genres.split(',')):
        books_logger.error(f"Error: Invalid genres specified", extra={'request_number': request_counter})
        return jsonify({"errorMessage": "Error: Invalid genres specified"}), 400
    filtered_books = filter_books(request.args)
    books_logger.info(f"Total Books found for requested filters is {len(filtered_books)}",
                      extra={'request_number': request_counter})
    return jsonify(result=sorted(filtered_books, key=lambda x: x['title'].lower())), 200


@app.route('/book', methods=['GET'])
def get_book():
    global request_counter
    genres = request.args.get('genres')
    if genres and not validate_genres(genres.split(',')):
        books_logger.error(f"Error: Invalid genres specified", extra={'request_number': request_counter})
        return jsonify(errorMessage=f"Error: Invalid genres specified"), 400

    book_id = int(request.args.get('id'))
    for book in books:
        if book['id'] == book_id:
            books_logger.debug(f"Fetching book id {book_id} details", extra={'request_number': request_counter})
            return jsonify(result=book), 200

    books_logger.error(f"Error: no such Book with id {book_id}", extra={'request_number': request_counter})
    return jsonify(errorMessage=f"Error: no such Book with id {book_id}"), 404


@app.route('/book', methods=['PUT'])
def update_book_price():
    global request_counter
    book_id = int(request.args.get('id'))
    new_price = int(request.args.get('price'))
    for book in books:
        if book['id'] == book_id:
            if book['price'] <= 0:
                books_logger.error(f"Error: price update for book [{book_id}] must be a positive integer",
                                   extra={'request_number': request_counter})
                return jsonify(errorMessage=f"Error: price update for book [{book_id}] must be a positive integer"), 409
            old_price = book['price']
            book['price'] = new_price
            books_logger.info(f"Update Book id [{book_id}] price to {new_price}",
                              extra={'request_number': request_counter})
            books_logger.debug(f"Book [{book['title']}] price change: {old_price} --> {new_price}",
                               extra={'request_number': request_counter})
            return jsonify(result=old_price), 200
    books_logger.error(f"Error: no such Book with id {book_id}", extra={'request_number': request_counter})
    return jsonify(errorMessage=f"Error: no such Book with id {book_id}"), 404


@app.route('/book', methods=['DELETE'])
def delete_book():
    global request_counter
    book_id = int(request.args.get('id'))
    for book in books:
        if book['id'] == book_id:
            books_logger.info(f"Removing book [{book['title']}]", extra={'request_number': request_counter})
            books.remove(book)
            books_logger.debug(f"After removing book [{book['title']}] id: [{book_id}] there are {len(books)} "
                               f"books in the system", extra={'request_number': request_counter})
            return jsonify(result=len(books)), 200
    books_logger.error(f"Error: no such Book with id {book_id}", extra={'request_number': request_counter})
    return jsonify(errorMessage=f"Error: no such Book with id {book_id}"), 404


@app.route('/logs/level', methods=['GET'])
def get_logger_level():
    logger_name = request.args.get('logger-name')
    if logger_name == 'request-logger':
        level = request_logger.level
    elif logger_name == 'books-logger':
        level = books_logger.level
    else:
        return "Invalid logger name", 400
    return f"{logging.getLevelName(level)}", 200


@app.route('/logs/level', methods=['PUT'])
def set_logger_level():
    logger_name = request.args.get('logger-name')
    new_level = request.args.get('logger-level')

    if new_level not in ['ERROR', 'DEBUG', 'INFO']:
        return "Invalid logger level", 400
    if logger_name == 'request-logger':
        request_logger.setLevel(getattr(logging, new_level.upper()))
    elif logger_name == 'books-logger':
        books_logger.setLevel(getattr(logging, new_level.upper()))
    else:
        return f"Invalid logger name", 400
    return f"{new_level}", 200


if __name__ == '__main__':
    app.run(port=8574)
