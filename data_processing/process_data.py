from pymongo import MongoClient
import pprint
import math

client = MongoClient('localhost', 27017)

db = client['bookmate']

def get_float(s):
    if type(s) is float:
        return s
    if s[0] == '+':
        return -1
    return float(s.replace(',', '.'))

def get_what_users_read():
    print("get_what_users_read start")
    sessions = db.bookmate_full_sessions
    users_preferences = {}

    cnt = 0

    for record in sessions.find():
        rec_to = get_float(record['_to'])
        if math.isnan(rec_to) or rec_to == -1:
            continue
        cnt += 1
        if cnt % 1000000 == 0:
            print("users", cnt, record)
        user = record['user_id']
        book = record['book_id']
        if (user, book) not in users_preferences:
            users_preferences[(user, book)] = (record['document_id'], record['item_id'], record['_to'])
        else:
            doc, item, to = users_preferences[(user, book)]
            if (int(item) < int(record['item_id']) or (int(item) == int(record['item_id']) and rec_to > get_float(to))):
                users_preferences[(user, book)] = (record['document_id'], record['item_id'], record['_to'])

    print("get users read done")
    return users_preferences

def leave_only_good_readers(n, users_read):
    print("leave only good readers start")
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
    print("len:", len(users))
    print("leave only good readers done")
    return result

def count_item_sizes(which_books_and_docs):
    print("count item sizes start")
    items = db.items
    result = {}
    
    cnt = 0
    for item in items.find():
        book = item['book_id']
        doc = item['document_id']
        cnt += 1
        if cnt % 100000 == 0:
            print("item size", cnt, item)
        if (book, doc) not in which_books_and_docs:
            continue
        if (book, doc) not in result:
            result[(book, doc)] = {'start_item': item['id'], 'list': [0]}
        if (result[(book, doc)]['start_item'] > item['id']):
            print("oops")
        result[(book, doc)]['list'].append(result[(book, doc)]['list'][-1] + item['media_file_size'])
    print("count item sizes done")
    return result

def count_read_percentage(users_read, item_sizes):
    print("percentage start")
    items = db.items
    result = {}

    cnt = 0
    for (user, book) in users_read:
        doc, item, to = users_read[(user, book)]
        if (book, doc) not in item_sizes:
            continue
        cnt += 1
        position = item - item_sizes[(book, doc)]['start_item'] + 1
        if position < 0 or position >= len(item_sizes[(book, doc)]['list']):
            continue
        sum_prev = item_sizes[(book, doc)]['list'][position - 1]
        cur_size = item_sizes[(book, doc)]['list'][position] - sum_prev
        result[(user, book)] = 100 * (sum_prev + get_float(to) / 100 * cur_size)
        result[(user, book)] /= item_sizes[(book, doc)]['list'][-1]
        if cnt % 100000 == 0:
            print("percentage", cnt, user, book, result[(user, book)])
    return result

users_read = leave_only_good_readers(10, get_what_users_read())
which_books_and_docs = set()

for (user, book) in users_read:
    doc, item, to = users_read[(user, book)]
    which_books_and_docs.add((book, doc))

print(len(which_books_and_docs))

item_sizes = count_item_sizes(which_books_and_docs)
read_percentage = count_read_percentage(users_read, item_sizes)
with open("data_users_and_books.txt", 'w') as f:
    for (user, book) in read_percentage:
        print(user, book, int(round(read_percentage[(user, book)])), file=f)
