from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import psycopg2
import operator

for i in range(494):
    my_url = 'http://tis.nhai.gov.in/TollInformation?TollPlazaID={}'.format(i)
    uClient = uReq(my_url)
    page1_html = uClient.read()
    uClient.close()
    # html parsing
    page1_soup = soup(page1_html, 'html.parser')

    # grabing data
    containers = page1_soup.findAll('div', {'class': 'PA15'})

    # Make the connection to PostgreSQL
    conn = psycopg2.connect(database='loads',user='prashant', password='12345', port=5432)
    cursor = conn.cursor()
    for container in containers:
        toll_name1 = container.p.b.text
        toll_name = toll_name1.split(" ")[1]

        search1 = container.findAll('b')
        highway_number = search1[1].text.split(" ")[0]

        text = search1[1].get_text()
        onset = text.index('in')
        offset = text.index('Stretch')
        state = str(text[onset +2:offset]).strip(' ')

        location = list(container.p.descendants)[10]
        mystr = my_url[my_url.find('?'):]
        TID = mystr.strip('?TollPlazaID=')

        query = "INSERT INTO tollmaster1 (TID, toll_name, location, highway_number, state) VALUES (%s, %s, %s, %s, %s);"
        data = (TID, toll_name, location, highway_number, state)

        cursor.execute(query, data)

    # Commit the transaction
    conn.commit()
