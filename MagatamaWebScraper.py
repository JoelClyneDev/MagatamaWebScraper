from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

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


magatama_connection = get_url(magatama_url)
magatama_table = get_magatama_list(magatama_connection)
get_magatama_links(magatama_table)