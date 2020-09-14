from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os


def download_file (year, month, url):
    print (f"{month = }, {url =}")

    r = requests.get(url, allow_redirects=True)
    open(f"{year}/{month}.zip", 'wb').write(r.content)


def get_files (year):
    url = f"https://www.cnmv.es/portal/Publicaciones/Descarga-Informacion-Individual.aspx?ejercicio={year}"


    # head obtiene el tamaño del fichero para poder comparar
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text)


    results = soup.select('td[data-th="Documento"]')

    if not os.path.exists(year):
        os.makedirs(year)

    for result in results:
        month = result.parent.td.text
        relative_url = result.a["href"]

        url_zip = urljoin (url, relative_url)
        download_file(year, month, url_zip)

get_files("2019")