from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os

import zipfile 
from lxml import etree
import sqlite3

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

def get_content (elm, tag):
    query = f".//{tag}"

    sub_elm = elm.find(query)
    if sub_elm  is None:
        return 0

    print (sub_elm.text)

    return sub_elm.text


def read_vl(fn):

    root = etree.parse(fn)
    entidades = root.findall("Entidad")

    conn= sqlite3.connect("cnmv.db")
    c = conn.cursor()


    for ent in entidades:

        tipo = get_content (ent, "Tipo")
        registro = get_content (ent, "NumeroRegistro")
        compartimento = get_content (ent, "NumeroCompartimento")
        isin = get_content (ent, "ISIN")
        clase = get_content (ent, "NumeroClase")


        sql = f"INSERT INTO 'info_fondo' VALUES ('{isin}', '{tipo}', '{registro}', {compartimento}, {clase})"

        try:
            c.execute(sql)
        except Exception as e:
            print(f"Error creating table info_fondo {e = }\n{sql =}", )

        conn.commit()

        vl = get_content (ent, "VLDiario")
        participes = get_content (ent, "ParticipesDiario")
        patrimonio = get_content (ent, "PatrimonioDiario")

        for dia in range(1,31):
            vl = get_content (ent, f"VL_Dia{dia}")
            participes = get_content (ent, f"Participes_Dia{dia}")
            patrimonio = get_content (ent, f"Patrimonio_Dia{dia}")
            _date = f"2020-02-{dia}"

            sql = f"INSERT INTO 'fondo_diario' VALUES ('{isin}', {_date}, {vl}, '{participes}', {patrimonio})"

            print(sql)

            try:
                c.execute(sql)
            except Exception as e:
                print(f"Error creating table info_fondo {e = }\n{sql =}", )

            conn.commit()


    conn.close()

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