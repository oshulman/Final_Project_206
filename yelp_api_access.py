from bs4 import BeautifulSoup
import json
import unittest
import re
import os
import requests
import sqlite3
import math
from yelpapi import YelpAPI

# Yelp
# client_ID = "rkuo0PKmfif1pdFsWx3U1Q"
API_KEY = "hKxIMdkKPpO81Uq7XqdeG7OB8Eq0TBDhVijsuWbkFguL8W-aR_c9gq3sWXZhZe1p5QEB-cLoRuimq-iW9yukU_KJsXtDC9NoSEkhALOgnTQibKi-3X2PJlRxABXLX3Yx"

# WEBSCRAPING

# NEW POTENTIAL PLAN: Scrape from 100 top cities website with more info and then compare with that
# potential variables: city budget, party type of mayor, population density, population change, area
def top_cities_data():
    url = "https://worldpopulationreview.com/us-cities"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    table_body = soup.find('tbody', class_='jsx-2642336383')

    data_tup_list = []
    for element in table_body.find_all('tr'):
        if int(str(element.td.text)) <= 100:
            city = element.td.find_next_sibling('td').text
            state = element.td.find_next_sibling('td').find_next_sibling('td').a.text
            pop = element.td.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').text.replace(",","")
            pop_change = element.td.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').span.text.replace("%","")
            density = element.td.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').text.replace(",","")
            area = element.td.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').text
            data_tup_list.append((city, state, pop, pop_change, density, area))

    
    for tup in data_tup_list:
        for element in tup:
            element = element.strip(',%')

    return data_tup_list


# DATABASE
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

#Table for list of city and its id
def setUpCitiesTable(cur, conn):
    cities = top_cities_data()

    #cur.execute("DROP TABLE IF EXISTS Cities")
    cur.execute("CREATE TABLE IF NOT EXISTS Cities (cities_id INTEGER PRIMARY KEY, city TEXT)")

    count = 0

    for i in range(len(cities)):
        #check if the data already exists
        cur.execute("SELECT cities_id FROM Cities WHERE cities_id = " + str(i))
        list_test = cur.fetchall()
        #if not, add the data to database
        if list_test == [] and count < 25:
            cur.execute("INSERT INTO Cities (cities_id, city) VALUES (?, ?)", (i, cities[i][0]))
            count = count + 1
    
    conn.commit()

#Table for city data, using cities_id as shared key (same api as Cities)
def setUpCitiesDataTable(cur, conn):
    cities = top_cities_data()

    #cur.execute("DROP TABLE IF EXISTS Cities_Data")
    cur.execute("CREATE TABLE IF NOT EXISTS Cities_Data (cities_id INTEGER PRIMARY KEY, state TEXT, pop INTEGER, pop_change REAL, pop_density INTEGER, area INTEGER)")

    #keep track of how many data we have already at in database/execution
    count = 0

    for i in range(len(cities)):
        #check if the data already exists
        cur.execute("SELECT cities_id FROM Cities_Data WHERE cities_id = " + str(i))
        list_test = cur.fetchall()
        #if not, add the data to database
        if list_test == [] and count < 25:
            cur.execute("SELECT cities_id FROM Cities WHERE cities_id = " + str(i))
            list_id = cur.fetchall()
            cur.execute("INSERT INTO Cities_Data (cities_id, state, pop, pop_change, pop_density, area) VALUES (?, ?, ?, ?, ?, ?)", (list_id[0][0], cities[i][1], cities[i][2], cities[i][3], cities[i][4], cities[i][5]))
            count = count + 1

    conn.commit()


#set up food table
#WEBSCRAPPING YELP API + DATABASE
#cities id can be the shared key
#scrape and insert data into database, 25/ per execution
#stop scraping after the database has 100 data

def setUpRestaurantsTable(cur, conn):

    #cur.execute("DROP TABLE IF EXISTS Restaurants")
    cur.execute("CREATE TABLE IF NOT EXISTS Restaurants (cities_id INTEGER PRIMARY KEY, num_of_healthy_place INTEGER)")
    
    conn.commit()
    #get list of tuple of city data from existing data base
    cur.execute("SELECT * FROM Cities")
    cities_list = cur.fetchall()

    yelp_api = YelpAPI(API_KEY)

    #keep track of how many data we have already inserted
    count = 0

    #get restaurants with key word "healthy in each city
    for i in range(len(cities_list)):

        #determine if the data is already in the database
        cur.execute("SELECT cities_id FROM Restaurants WHERE cities_id = " + str(cities_list[i][0]))
        list_test = cur.fetchall()
        #if not, add the data to database
        if list_test == [] and count < 25:
            city = cities_list[i][1]

            #scrape number of restaurants that have key word "healthy" in that city 
            search_results = yelp_api.search_query(term = 'healthy', location = city)
            cur.execute("INSERT INTO Restaurants (cities_id, num_of_healthy_place) VALUES (?, ?)", (cities_list[i][0], search_results["total"]))
            count = count + 1
    
    conn.commit()

def avg_num_healthy_restaurants(cur, conn):
    num_tup_list = []
    for row in cur.execute("SELECT num_of_healthy_place FROM Restaurants"):
        num_tup_list.append(row)
    conn.commit()

    total = 0
    for tup in num_tup_list:
        total += tup[0]
    
    return total/50

def pop_dens_pearson_corr(cur, conn):
    pop_dens_num_tup_list = []
    ex_str = """SELECT Cities_Data.pop_density, Restaurants.num_of_healthy_place 
        FROM Cities_Data JOIN Restaurants ON Cities_Data.cities_id = Restaurants.cities_id 
        """
    for row in cur.execute(ex_str):
        pop_dens_num_tup_list.append(row)
    conn.commit()

    # uses pearson summation formula from https://www.statisticshowto.com/probability-and-statistics/correlation-coefficient-formula/

    # summation of all pop_density values
    x_total = 0
    # summation of all num_of_healthy_place values
    y_total = 0
    # summation of all pop_density * num_of_healthy_place 
    xy_total = 0
    # summation of all squares of pop_density values
    x2_total = 0
    # summation of all squares of num_of_healthy_place values
    y2_total = 0
    # sample size
    n = 100

    for tup in pop_dens_num_tup_list:
        x_total += tup[0]
        y_total += tup[1]
        xy_total += (tup[0] * tup[1])
        x2_total += (tup[0] * tup[0])
        y2_total += (tup[1] * tup[1])
    
    r = ((n * xy_total) - (x_total * y_total))/(math.sqrt(((n * x2_total) - (x_total * x_total)) * ((n * y2_total) - (y_total * y_total))))

    return r

def pop_pearson_corr(cur, conn):
    pop_num_tup_list = []
    ex_str = """SELECT Cities_Data.pop, Restaurants.num_of_healthy_place 
        FROM Cities_Data JOIN Restaurants ON Cities_Data.cities_id = Restaurants.cities_id 
        """
    for row in cur.execute(ex_str):
        pop_num_tup_list.append(row)
    conn.commit()

        # uses pearson summation formula from https://www.statisticshowto.com/probability-and-statistics/correlation-coefficient-formula/

    # summation of all pop values
    x_total = 0
    # summation of all num_of_healthy_place values
    y_total = 0
    # summation of all pop * num_of_healthy_place 
    xy_total = 0
    # summation of all squares of pop values
    x2_total = 0
    # summation of all squares of num_of_healthy_place values
    y2_total = 0
    # sample size = 100 cities
    n = 100

    for tup in pop_num_tup_list:
        x_total += tup[0]
        y_total += tup[1]
        xy_total += (tup[0] * tup[1])
        x2_total += (tup[0] * tup[0])
        y2_total += (tup[1] * tup[1])
    
    r = ((n * xy_total) - (x_total * y_total)) / (math.sqrt(((n * x2_total) - (x_total * x_total)) * ((n * y2_total) - (y_total * y_total))))

    return r

def pop_change_pearson_corr(cur, conn):
    pop_change_tup_list = []
    ex_str = """SELECT Cities_Data.pop_change, Restaurants.num_of_healthy_place 
        FROM Cities_Data JOIN Restaurants ON Cities_Data.cities_id = Restaurants.cities_id 
        """
    for row in cur.execute(ex_str):
        pop_change_tup_list.append(row)
    conn.commit()

        # uses pearson summation formula from https://www.statisticshowto.com/probability-and-statistics/correlation-coefficient-formula/

    # summation of all pop_change values
    x_total = 0
    # summation of all num_of_healthy_place values
    y_total = 0
    # summation of all pop_change * num_of_healthy_place 
    xy_total = 0
    # summation of all squares of pop_change values
    x2_total = 0
    # summation of all squares of num_of_healthy_place values
    y2_total = 0
    # sample size = 100 cities
    n = 100

    for tup in pop_change_tup_list:
        x_total += tup[0]
        y_total += tup[1]
        xy_total += (tup[0] * tup[1])
        x2_total += (tup[0] * tup[0])
        y2_total += (tup[1] * tup[1])
    
    r = ((n * xy_total) - (x_total * y_total)) / (math.sqrt(((n * x2_total) - (x_total * x_total)) * ((n * y2_total) - (y_total * y_total))))

    return r

def area_pearson_corr(cur, conn):
    area_num_tup_list = []
    ex_str = """SELECT Cities_Data.area, Restaurants.num_of_healthy_place 
        FROM Cities_Data JOIN Restaurants ON Cities_Data.cities_id = Restaurants.cities_id 
        """
    for row in cur.execute(ex_str):
        area_num_tup_list.append(row)
    conn.commit()

        # uses pearson summation formula from https://www.statisticshowto.com/probability-and-statistics/correlation-coefficient-formula/

    # summation of all area values
    x_total = 0
    # summation of all num_of_healthy_place values
    y_total = 0
    # summation of all area * num_of_healthy_place 
    xy_total = 0
    # summation of all squares of area values
    x2_total = 0
    # summation of all squares of num_of_healthy_place values
    y2_total = 0
    # sample size = 100 cities
    n = 100

    for tup in pop_num_tup_list:
        x_total += tup[0]
        y_total += tup[1]
        xy_total += (tup[0] * tup[1])
        x2_total += (tup[0] * tup[0])
        y2_total += (tup[1] * tup[1])
    
    r = ((n * xy_total) - (x_total * y_total)) / (math.sqrt(((n * x2_total) - (x_total * x_total)) * ((n * y2_total) - (y_total * y_total))))

    return r

def main():
    cur, conn = setUpDatabase('cities.db')
    setUpCitiesTable(cur, conn)
    setUpCitiesDataTable(cur, conn)
    setUpRestaurantsTable(cur, conn)
    avg_num_healthy_restaurants(cur,conn)
    pop_pearson_corr(cur, conn)
    pop_change_pearson_corr(cur, conn)
    pop_dens_pearson_corr(cur, conn)
    area_pearson_corr(cur, conn)

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
    def test_restuarants_table(self):
        self.cur.execute('SELECT num_of_healthy_place FROM Restaurants')
        restaurants_list = self.cur.fetchall()
        self.assertEqual(len(restaurants_list), 100)

if __name__ == '__main__':
    # print(scrape_100_top_cities())
    # print(city_urls())
    #print(arcgis_info())
    #print(top_cities_data())
    main()
    #unittest.main(verbosity = 2)
