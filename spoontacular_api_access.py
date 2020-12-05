from bs4 import BeautifulSoup
import json
import unittest
import re
import os
import requests
import sqlite3

# Spoontacular API_KEY = "8cf1b23a038a4372835238e67ffd74ab"

# Yelp
# client_ID = "rkuo0PKmfif1pdFsWx3U1Q"
API_KEY = "hKxIMdkKPpO81Uq7XqdeG7OB8Eq0TBDhVijsuWbkFguL8W-aR_c9gq3sWXZhZe1p5QEB-cLoRuimq-iW9yukU_KJsXtDC9NoSEkhALOgnTQibKi-3X2PJlRxABXLX3Yx"

def scrape_100_top_cities():
    url = "https://worldpopulationreview.com/us-cities"
    r = requests.get(url)
    
    soup = BeautifulSoup(r.content, 'html.parser')

    city_list = []

    # gets content of table which contains all over 100 most populace US cities
    table_body = soup.find('tbody', class_='jsx-2642336383')
    
    # gets only top 100 city names
    for element in table_body.find_all('tr'):
        if int(str(element.td.text)) <= 100:
            city_list.append(element.td.find_next_sibling('td').a.text)

    return city_list

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpCitiesTable(cur, conn):
    cities = scrape_100_top_cities()

    cur.execute("DROP TABLE IF EXISTS Cities")
    cur.execute("CREATE TABLE Cities (id INTEGER PRIMARY KEY, Name TEXT)")

    for i in range(len(cities)):
        cur.execute("INSERT INTO Cities (id, Name) VALUES (?, ?)", (i, cities[i]))
    conn.commit()

def main():
    cur, conn = setUpDatabase('cities.db')
    setUpCitiesTable(cur, conn)

    conn.close()

class TestAllMethods(unittest.TestCase):
    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.conn = sqlite3.connect(path+'/'+'cities.db')
        self.cur = self.conn.cursor()

    def test_cities_table(self):
        self.cur.execute('SELECT * FROM Cities')
        cities_list = self.cur.fetchall()
        self.assertEqual(len(cities_list), 100)
        self.assertEqual(len(cities_list[0]), 2)

if __name__ == '__main__':
    # print(scrape_100_top_cities())
    main()
    unittest.main(verbosity = 2)