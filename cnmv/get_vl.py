import os
import sqlite3
import zipfile

import requests
from bs4 import BeautifulSoup
from lxml import etree

MESES = list(('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
            'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'))

def download_file(year, month, url):
    print(f"{month = }, {url =}")

    r = requests.get(url, allow_redirects=True)
    open(f"{year}/{month}.zip", 'wb').write(r.content)


def get_files(year):

    year = str(year)

    url = f"https://www.cnmv.es/portal/Publicaciones/Descarga-Informacion-Individual.aspx?ejercicio={year}"

    # head obtiene el tamaño del fichero para poder comparar
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text)

    results = soup.select('td[data-th="Documento"]')

    if not os.path.exists(year):
        os.makedirs(year)

    for result in results:
        month_name = result.parent.td.text
        relative_url = result.a["href"]

        os.path.exists(f'{year}/{month_name}')

        r = requests.get(url, allow_redirects=True)

        file_name =f'{year}/{month_name}.zip'

        print (f"----- writing {file_name = } ------")
        with open(file_name, 'wb') as f:
            f.write(r.content)



def get_content(elm, tag):
    query = f".//{tag}"

    sub_elm = elm.find(query)
    if sub_elm is None:
        return 0

    print(sub_elm.text)

    return sub_elm.text


def read_vl(fn):

    root = etree.parse(fn)
    entidades = root.findall("Entidad")

    conn = sqlite3.connect("cnmv.db")
    c = conn.cursor()

    for ent in entidades:

        tipo = get_content(ent, "Tipo")
        registro = get_content(ent, "NumeroRegistro")
        compartimento = get_content(ent, "NumeroCompartimento")
        isin = get_content(ent, "ISIN")
        clase = get_content(ent, "NumeroClase")

        sql = f"INSERT INTO 'info_fondo' VALUES ('{isin}', '{tipo}', '{registro}', {compartimento}, {clase})"

        try:
            c.execute(sql)
        except Exception as e:
            print(f"Error creating table info_fondo {e = }\n{sql =}", )

        conn.commit()

        vl = get_content(ent, "VLDiario")
        participes = get_content(ent, "ParticipesDiario")
        patrimonio = get_content(ent, "PatrimonioDiario")

        for dia in range(1, 31):
            vl = get_content(ent, f"VL_Dia{dia}")
            participes = get_content(ent, f"Participes_Dia{dia}")
            patrimonio = get_content(ent, f"Patrimonio_Dia{dia}")
            fecha = f"2020-02-{dia}"

            sql = f"INSERT INTO 'fondo_diario' VALUES ('{isin}', {fecha}, {vl}, '{participes}', {patrimonio})"

            print(sql)

            try:
                c.execute(sql)
            except Exception as e:
                print(f"Error creating table info_fondo {e = }\n{sql =}", )

            conn.commit()

    conn.close()


def main():

    for year in range(2010, 2020):
        get_files (year)

        continue

        for month in range(0, 11):
            pass
            # extract(year, month)

def extract(year, month):

    month_name = MESES[month]

    zip_fn = month_name + ".zip"

    with zipfile.ZipFile(zip_fn, "r") as zip_ref:
        zip_ref.extractall("/tmp/" + month_name)

        month_name = f"/tmp/{month_name}/FONDMENS_{year}{month}.xml"

        read_vl(month_name)


if __name__ == "__main__":
    main()
