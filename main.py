import requests
from bs4 import BeautifulSoup
import re
import platform

mapf = {'thessaloniki':'Θεσσαλονίκη', 'athens':'Αθήνα', 'patras':'Πάτρα', 'heraklion':'Ηράκλειο', 'ioannina':'Ιωάννινα'}

def ftoc(f):
    return round((f - 32) / 1.8, 2)


def scrape_city(city):
    url = "https://www.wunderground.com/weather/gr/" + city
    html_content = requests.get(url).content

    soup = BeautifulSoup(html_content, "html.parser")
    data = {}
    temp = soup.find('span', {'class': "wu-value wu-value-to"})
    temp = ftoc(int(temp.text))
    data["temperature"] = temp

    divs = soup.find_all('div', {'class': 'small-12 medium-4 large-4 columns forecast-wrap ng-star-inserted'})
    divtoday = None
    for div in divs:
        dateT = div.find('span', {'class': 'day'}).text
        if ((dateT != 'Today' or dateT != 'Tonight') and divtoday is not None):
            continue
        else:
            divtoday = div

    innerdiv = divtoday.find('div', {'class': 'columns small-12'})
    precip = innerdiv.find('a', {'class': 'hook'}).text

    percprec = re.split('(Precip.)', precip)[0]
    data["prec"] = percprec

    return data

def sortcities(d):
    temps = []
    for city in d:
        temps.append(d[city]['temperature'])
    temps.sort(reverse=True)
    sortedCities = []
    for t in temps:
        for c in d:
            if(d[c]['temperature'] == t):
                if(c not in sortedCities):
                    sortedCities.append(c)
                    break
                else:
                    continue
    return sortedCities


if __name__ == '__main__':
    cities = ['athens','thessaloniki','patras','ioannina','heraklion']
    data = dict()

    choicestr = input("Για ποιες πόλεις δεν θέλεις ενημέρωση;\n1.Αθήνα\n2.Θεσσαλονίκη\n3.Πάτρα\n4.Ιωάννινα\n5.Ηράκλειο\n6.Θέλω για όλες\nΔώσε απάντηση: ")
    choices = choicestr.split(",")
    choices = [int(x) for x in choices]

    if(6 not in choices):
        cities = [city for (index, city) in enumerate(cities) if index+1 not in choices]

    for city in cities:
        data[city] = scrape_city(city)
    sortedCities = sortcities(data)

    for city in sortedCities:
        message = "Η θερμοκρασία στην πόλη " + mapf[city] + " είναι " + str(data[city]["temperature"]) + "°C!\nΠιθανότητα για βροχή: " + str(
        data[city]["prec"]) + "."
        os_name = platform.system()
        if (os_name == 'Linux'):
            import subprocess as s  
            s.call(['notify-send', mapf[city], message])
        elif (os_name == 'Windows'):
            from win10toast import ToastNotifier
            notifier = ToastNotifier()
            notifier.show_toast(mapf[city], message)