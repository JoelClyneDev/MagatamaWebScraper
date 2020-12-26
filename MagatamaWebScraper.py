from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json

magatama_url = "https://megamitensei.fandom.com/wiki/Magatama"

def get_url(url):
    try:
        with closing(get(url, stream=True)) as response:
            if is_good_response(response):
                return response.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(response):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = response.headers['Content-Type'].lower()
    return (response.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def get_magatama_list(raw_html):
    parsed_html = BeautifulSoup(raw_html, 'html.parser')
    magatama_table = parsed_html.select_one('table[class="customtable smt3"]')
    return magatama_table

def get_magatama_links(magatama_table):
    link_list = []

    for magatama in magatama_table.find_all('a'):
        #print(type(magatama))
        #print(magatama)
        link_list.append("https://megamitensei.fandom.com" + magatama.get('href'))

        """
        row_magatama_link = magatama.find_all('td')
        if row_magatama_link is not None:
            for individual_magatama_link in row_magatama_link:
                individual_magatama_link = individual_magatama_link.find_all('a').get('href')
                link_list.append(individual_magatama_link)
        """
    for link in link_list:
        print(link)
    return link_list

def get_magatama_stats( link, dict ):
    connection = get_url(link)
    parsed_html = BeautifulSoup( connection, 'html.parser')
    name = parsed_html.select_one('h1[id="firstHeading"]').text

    #gets the stats as the 3 tables according to the 3 rows on the website
    #stats = parsed_html.select_one('div[class="mw-parser-output"]').select_one('table[align="center"]').select('table[class="customtable"]')
    stats = parsed_html.select_one('table[style="min-width:650px;text-align:center; background: #222; border:2px solid #333158; border-radius:10px; font-size:75%; font-family:verdana;"]').select('table[class="customtable"]')

    if stats is None:
        print("wait")
        stats = parsed_html.select_one('div[class="mw-parser-output"]').select_one('table[align="center"]').select('table')

    reg_skills = stats[0]
    #print(reg_skills)

    effects = reg_skills.select('td[ style="background:#000;color:#fff"]')

    points = reg_skills.select('td[style="text-align:right;padding:0 3px"]')

    attributes = stats[1].select('td[style="background:#000;color:#fff"]')

    battle_skills = stats[2].select("tr")[2:]

    skill_list = []
    for skill in battle_skills:
        skill_name = skill.select_one("th").text.replace('\n', '')
        other_skill_attrs = skill.select("td")
        temp_skill = ({
            'skill_name': skill_name,
            'cost': other_skill_attrs[0].text.replace('\n', ''),
            'effect': other_skill_attrs[1].text.replace('\n', ''),
            'level': other_skill_attrs[2].text.replace('\n', '')
        })
        skill_list.append(temp_skill)

    dict['magatamas'].append({
        'name': name,
        'element': effects[0].text.replace('\n', ''),
        'wild_effects': effects[1].text.replace('\n', ''),
        'st': points[0].text.replace('\n', ''),
        'ma': points[1].text.replace('\n', ''),
        'vt': points[2].text.replace('\n', ''),
        'ag': points[3].text.replace('\n', ''),
        'lu': points[4].text.replace('\n', ''),
        'reflect': attributes[0].text.replace('\n', ''),
        'absorb': attributes[1].text.replace('\n', ''),
        'void': attributes[2].text.replace('\n', ''),
        'weak': attributes[3].text.replace('\n', ''),
        'resist': attributes[4].text.replace('\n', ''),
        'skills': skill_list
    })




def main():
    magatama_connection = get_url(magatama_url)
    magatama_table = get_magatama_list(magatama_connection)
    links = get_magatama_links(magatama_table)
    magatama_dict = {}
    magatama_dict['magatamas'] = []
    for link in links:
       get_magatama_stats( link, magatama_dict )
    with open('magatamaList.json', 'w') as outfile:
        json.dump(magatama_dict['magatamas'], outfile)

main()