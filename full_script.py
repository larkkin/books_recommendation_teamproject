from bs4 import BeautifulSoup
import operator
import requests
import pickle
import pprint

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
			b = author.replace(' ', '').replace('"','').replace('ё','е') #унифицируем формат авторов
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

#sorted_books = sorted(top_books.items(), key=operator.itemgetter(1))
#sorted_readers = sorted(top_readers.items(), key=operator.itemgetter(1))



common_with_readers = reader_related_titles & common_titles

common_users_same_authors = set()

for i in common_with_readers:
	a = titles_authors_bookmate[i].find(titles_authors_flibusta[i]) 
	if a != -1:
		common_users_same_authors.add(i)

#получили проверенный по авторам сет книг, который есть в файле данных о пользователях. Теперь нам нужно найти соответствие для айди и скачать
inverted_id_to_name_flibusta = inv_d = {v:k for k, v in id_to_name_flibusta.items()}
ids_to_download = {}
for key in inverted_id_to_name_flibusta:
	if key in common_users_same_authors:
		ids_to_download[inverted_id_to_name_flibusta[key]] =  key
print(len(ids_to_download),'-- какое количество книг нужно скачать')

for key in ids_to_download:
	proxy={'http': 'socks5://localhost:9050'}
	link = 'http://flibusta.is/b/' + key + '/read'
	print(link)
	l = requests.get(link, proxies=proxy).text
	l = l.replace('\n', ' ').replace('\r', '').replace('\xa0', '')
	filename = ids_to_download[key]
	f = open(filename, 'w+')
	pprint.pprint(l, f) #поместили скачанный файл в созданный, текст
	with open(filename) as fl:
		soup = BeautifulSoup(fl, 'html.parser') #теперь наша задача - избавиться от тегов
		plain_text = filename + 'plain'
		with open(plain_text, "w+") as file:
			file.write(soup.get_text())
