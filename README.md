### Python-HTTP-Server

Copy code
# Books Management HTTP Server

## Overview
This project implements a simple HTTP server for managing a collection of books. The server provides endpoints for creating, reading, updating, and deleting books. It also includes logging for tracking requests and operations on the books collection.

## Features
- Create a new book
- Get details of a specific book
- Get a list of all books with optional filtering
- Update the price of a book
- Delete a book
- Health check endpoint
- Request and operation logging with custom log formatting

## Endpoints
- `GET /books/health` - Health check endpoint
- `POST /book` - Create a new book
- `GET /book` - Get details of a specific book by ID
- `GET /books` - Get a list of all books with optional filters (author, price, year, genres)
- `GET /books/total` - Get the total count of books with optional filters
- `PUT /book` - Update the price of a specific book by ID
- `DELETE /book` - Delete a specific book by ID
- `GET /logs/level` - Get the current logging level for a specific logger
- `PUT /logs/level` - Set the logging level for a specific logger

## Logging
The server uses two loggers:
- `request-logger` - Logs incoming requests and their duration.
- `books-logger` - Logs operations related to books.

Log files are stored in the `logs` directory:
- `logs/requests.log` - Stores logs for requests.
- `logs/books.log` - Stores logs for books operations.
