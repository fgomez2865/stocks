from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os

import zipfile 
from lxml import etree

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

def read_vl(fn):

    tags_text = ["Tipo", "NumerodeRegistro", "NumeroCompartimento", "ISIN"] 
    tags = ["VLDiario", "ParticipesDiario", "PatrimonioDiario"]

    tags_text = ["Tipo", "NumeroRegistro", "NumeroCompartimento", "ISIN"] 
    tags_diario = [("VLDiario","VL_Dia"), 
                  ("ParticipesDiario", "Participes_Dia"),
                  ("PatrimonioDiario", "Patrimonio_Dia")]

    root = etree.parse(fn)
    entidades = root.findall("Entidad")
    for ent in entidades:
        print (ent)

        for tag in tags_text:
          texto = ent.find(".//" + tag).text
          print (texto)

        for tag_root, tag in tags_diario:
          elm = ent.find(".//" + tag_root)

          elm_diarios = elm.xpath(f".//*[starts-with(name(), '{tag}')]")
          for elm_diario in elm_diarios:
                
            print (f"{elm_diario.tag = }, {elm_diario.text = }")

def main():
    # get_files("2019")

    fn = "Febrero"
    zip_fn = fn + ".zip"

    with zipfile.ZipFile(zip_fn,"r") as zip_ref:
        zip_ref.extractall("/tmp/" + fn)

    fn ="/tmp/Febrero/FONDMENS_202002.xml"

    read_vl (fn)

    return


if __name__ == "__main__":
    main()