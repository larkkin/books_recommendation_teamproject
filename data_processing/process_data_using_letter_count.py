from pymongo import MongoClient
import pprint
import math
import csv

client = MongoClient('localhost', 27017)

last_sec = 1440277820000
month_sec = 2629743000
db = client['bookmate']

def get_float(s):
    if type(s) is float:
        return s
    if type(s) is not str:
        return -1
    if s[0] == '+':
        return -1
    return float(s.replace(',', '.'))

def get_what_users_read():
    print("get_what_users_read start")
    sessions = db.bookmate_full_sessions
    users_read_amount = {}

    cnt = 0
    min_time = {}

    for record in sessions.find():
        rec_to = get_float(record['_to'])
        rec_from = get_float(record['_from'])
        if math.isnan(rec_to) or rec_to == -1:
            continue
        if math.isnan(rec_from) or rec_from == -1:
            continue
        if record['_to'] < record['_from']:
            continue
        cnt += 1
        if cnt % 1000000 == 0:
            print("users", cnt, record)
        user = record['user_id']
        book = record['book_id']
        if (user, book) not in users_read_amount:
            users_read_amount[(user, book)] = int(record['size'])
            min_time[(user, book)] = int(record['read_at'])
        else:
            users_read_amount[(user, book)] += int(record['size'])
            min_time[(user, book)] = min(min_time[(user, book)], record['read_at'])

    print("get users read done")
    return (users_read_amount, min_time)

def leave_only_good_readers(n, users_read, min_time):
    print("leave only good readers start")
    users = {}
    result = {}
    for (user, book) in users_read:
        if min_time[(user, book)] > last_sec - month_sec:
            continue
        if user not in users:
            users[user] = {book}
        else:
            users[user].add(book)
    for (user, book) in users_read:
        if user in users and len(users[user]) >= n and min_time[(user, book)] <= last_sec - month_sec:
            result[(user, book)] = users_read[(user, book)]
    print("len:", len(users))
    print("leave only good readers done")
    return result

def read_book_sizes():
    print("read book sizes start")
    
    result = {}
    cnt = 0
    with open("CBBR/books.csv", 'r') as csv_file:
        f = csv.reader(csv_file, delimiter=',', quotechar='"')
        for line in f:
            if cnt == 0:
                cnt += 1
                continue
            book, _, _, size, _, _, _ = line
            cnt += 1
            if size == "NULL" or size == "0":
                continue
            if cnt % 100000 == 0:
                print("book size", book, size)
            result[int(book)] = int(size)
    print("count book sizes done")
    return result

def count_read_percentage(users_read, book_sizes):
    print("percentage start")
    result = {}

    cnt = 0
    for (user, book) in users_read:
        read = users_read[(user, book)]
        if book not in book_sizes:
            continue
        cnt += 1
        if book_sizes[book] < read:
            read = book_sizes[book]
        result[(user, book)] = (read / book_sizes[book]) * 100
        if cnt % 100000 == 0:
            print("percentage", cnt, user, book, result[(user, book)])
    return result

all_read, min_time = get_what_users_read()
users_read = leave_only_good_readers(10, all_read, min_time)

book_sizes = read_book_sizes()
read_percentage = count_read_percentage(users_read, book_sizes)
with open("data_users_and_books_more_books.txt", 'w') as f:
    for (user, book) in read_percentage:
        print(user, book, int(round(read_percentage[(user, book)])), file=f)
