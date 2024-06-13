import logging


class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.asctime = self.formatTime(record, self.datefmt)
        log_message = super().format(record)
        request_number = getattr(record, 'request_number', 'N/A')
        return f"{record.asctime} {record.levelname}: {log_message} | request #{request_number}"


logging.basicConfig(level=logging.INFO)

request_logger = logging.getLogger('request-logger')
books_logger = logging.getLogger('books-logger')

request_handler = logging.FileHandler('logs/requests.log')
request_handler.setFormatter(CustomFormatter('%(message)s'))
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(CustomFormatter('%(message)s'))
request_logger.addHandler(request_handler)
#request_logger.addHandler(logging.StreamHandler())
request_logger.addHandler(console_handler)

books_handler = logging.FileHandler('logs/books.log')
books_handler.setLevel(logging.DEBUG)
books_handler.setFormatter(CustomFormatter('%(message)s'))
books_logger.addHandler(books_handler)
#books_logger.addHandler(logging.StreamHandler())

books_logger.addHandler(books_handler)
#books_logger.addHandler(logging.StreamHandler())




