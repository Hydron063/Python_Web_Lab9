from itertools import groupby
from bs4 import BeautifulSoup
import sqlite3
import requests

from django.http import HttpResponse
from django.template import loader


def add_to_table(array, cursor):
    cursor.execute(
        'INSERT INTO lab9 (year, country, name, subject, specific) values ("' + array[0] + '", "' + array[1] + '","' +
        array[2] + '","' + array[3] + '","' + array[4] + '")')


r = requests.get('https://ru.wikipedia.org/wiki/Университет_ИТМО')
htmlC = r.text
soup = BeautifulSoup(htmlC, "html.parser")

i = 0
trs = soup.find_all('tr')

rowN = 6
results = []
for tr in trs:
    i += 1
    if str(tr).find("Направления научных исследований") > 0:
        break

for j in range(rowN):
    print(j)
    innerArr = []
    for td in BeautifulSoup(str(trs[j + i]), 'html.parser').find_all(['th', 'td']):
        innerArr.append(td.text.rstrip().replace(u'\xa0', u' '))
        print(td.text)

    results.append(innerArr)

print("--------132123-----------")
print(results)

# ---lab-specific code

conn = sqlite3.connect('lab9.sqlite')
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS lab9')
cur.execute('CREATE TABLE lab9 (year, country, name, subject, specific)')


def get_filled_str(i):
    return "В году {} в стране {} человек по имени {} преуспел в области {} по спецификации {}".format(*i)


for i in results:
    add_to_table(i, cur)
conn.commit()
conn.close()


def get_by_year(year):
    string = ""
    for arr in results:
        if arr[0] == year:
            string = string + get_filled_str(arr) + '\n\n'
    if len(string) == 0:
        if not year.isdigit():
            string = 'Введённый адрес неверен: после "/" в адресной строке должно следовать число - год!'
        else:
            string = 'В {} году успехов отмечено не было.'.format(year)
    return string


def post_list(request, year):
    return HttpResponse(get_by_year(year))


def index(request):
    result_years = [el for el, _ in groupby([result[0] for result in results])]
    template = loader.get_template('../templates/index.html')
    context = {
        'result': result_years,
    }
    return HttpResponse(template.render(context, request))
