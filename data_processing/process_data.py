from pymongo import MongoClient
import pprint
import math

client = MongoClient('localhost', 27017)

db = client['bookmate']

def get_float(s):
    if type(s) is float:
        return s
    return float(s.replace(',', '.'))

def get_what_users_read():
    sessions = db.bookmate_full_sessions
    users_preferences = {}

    for record in sessions.find():
        if math.isnan(get_float(record['_to'])):
            continue
        user = record['user_id']
        book = record['book_id']
        if (user, book) not in users_preferences:
            users_preferences[(user, book)] = (record['document_id'], record['item_id'], record['_to'])
        else:
            doc, item, to = users_preferences[(user, book)]
            if (int(item) < int(record['item_id']) or (int(item) == int(record['item_id']) and get_float(record['_to']) > get_float(to))):
                users_preferences[(user, book)] = (record['document_id'], record['item_id'], record['_to'])

    return users_preferences

def leave_only_good_readers(n, users_read):
    users = {}
    result = {}
    for (user, book) in users_read:
        if user not in users:
            users[user] = {book}
        else:
            users[user].add(book)
    for (user, book) in users_read:
        if len(users[user]) >= n:
            result[(user, book)] = users_read[(user, book)]
    return result

def count_item_sizes(which_books_and_docs):
    items = db.items
    result = {}
    
    for item in items.find():
        book = item['book_id']
        doc = item['document_id']
        if (book, doc) not in which_books_and_docs:
            continue
        if (book, doc) not in result:
            result[(book, doc)] = [0]
        result[(book, doc)].append(result[(book, doc)][-1] + item['media_file_size'])
    return result

def count_read_percentage(users_read, item_sizes):
    items = db.items
    result = {}
    for (user, book) in users_read:
        doc, item, to = users_read[(user, book)]
        line = items.find_one({'book_id': book, 'document_id': doc, 'id': item})
        if not line:
            continue
        position = line['position']
        result[(user, book)] = 100 * (item_sizes[(book, doc)][position - 1] + get_float(to) * (line['media_file_size']))
        result[(user, book)] /= item_sizes[(book, doc)][-1]
    return result

users_read = leave_only_good_readers(10, get_what_users_read())
which_books_and_docs = set()

for (user, book) in users_read:
    doc, item, to = users_read[(user, book)]
    which_books_and_docs.add((book, doc))

item_sizes = count_item_sizes(which_books_and_docs)
read_percentage = count_read_percentage(users_read, item_sizes)
with open("data_users_and_books.txt", 'w') as f:
    for (user, book) in read_percentage:
        print(user, book, int(round(read_percentage[(user, book)])), file=f)
