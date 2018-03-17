matrix_users_books = {}

import operator

bookmate_titles = set()
flibusta_titles = set()
id_to_name = {}
id_to_name_flibusta = {}
titles_authors_bookmate = {}
titles_authors_flibusta = {}

with open("books_corrected.csv") as bookmate_data:
	bookmate_data.readline()
	for line in bookmate_data:
		sth = line.split(',')
		name = sth[1].lower()
		book_id = sth[0]
		bookmate_titles.add(name)
		id_to_name[book_id] = name
		if len(sth) >= 3:
			author = sth[2].lower()
			b = author.replace(' ', '').replace('"','').replace('ё','е')
			titles_authors_bookmate[name] = b
		else:
			titles_authors_bookmate[name] = ''


with open("catalog.txt") as flibusta_data:
	flibusta_data.readline()
	for line in flibusta_data:
		sth = line.split(';')
		book_id = sth[8].replace('\n', '')
		name = sth[3].lower()
		id_to_name_flibusta[book_id]= name
		flibusta_titles.add(name)
		author= sth[0]
		b = author.replace(' ', '').replace('"','').replace('ё','е')
		titles_authors_flibusta[sth[3].lower()] = b.lower()



common_titles = bookmate_titles & flibusta_titles


reader_related_titles = set()
top_readers = {}
top_books = {}
with open("bookmate_readers_books.txt") as readers_data:
	readers_data.readline()
	for line in readers_data:
		sth=line.strip().split(' ')
		book_id = sth[1]
		if book_id in id_to_name:
			name = (id_to_name[book_id])
			reader_related_titles.add(name)

common_with_readers = reader_related_titles & common_titles

common_users_same_authors = set()

for i in common_with_readers:
	a = titles_authors_bookmate[i].find(titles_authors_flibusta[i]) 
	if a != -1:
		common_users_same_authors.add(i)



inverted_id_to_name_bookmate = {v:k for k, v in id_to_name.items()}
map_of_common_users_same_authors = {}
for i in common_users_same_authors:
	map_of_common_users_same_authors[inverted_id_to_name_bookmate[i]] = 0

with open("bookmate_readers_books.txt") as readers_data:
	readers_data.readline()
	for line in readers_data:
		sth=line.strip().split(' ')
		user_id = sth[0]
		matrix_users_books[user_id] = map_of_common_users_same_authors #теперь каждому пользователю соответствует мапа книг

# надо сделать каждому пользователю список книг, которые он читал 
read_books_per_user = {}
with open("bookmate_readers_books.txt") as readers_data:
	readers_data.readline()
	for line in readers_data:
		sth=line.strip().split(' ')
		user_id = sth[0]
		book_id = sth[1]
		if user_id not in read_books_per_user:
			read_books_per_user[user_id] = [book_id]	
		else:
			read_books_per_user[user_id].append(book_id)

#теперь итерируемся по пользователям из matrix_users_books, внутри них итерируемся по книгам. если книга есть в read_books_per_user[user], то matrix_users_books[user][book]=1
for user in matrix_users_books:
	for book in user:
		if book in read_books_per_user[user]:
			matrix_users_books[user][book] = 1
