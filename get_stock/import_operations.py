from get_stock import *
import json
import re
from datetime import datetime

from get_stock import *
import webbrowser


# opciones de display
display_options ()

# cod : isin /pp , tipo: epsv/pp/fondo,


def get_price (tipo_cod, df):

    d_tipos = {"pp": "planes", "isin":"fondos"}
    df  = df.loc[df.tipo_cod == tipo_cod]

    for index, row in df.iterrows():
        valor, fecha = get_que_fondos(d_tipos[tipo_cod], row["cod"])
        print (row['fecha'], row['cod'], row['name'], valor, fecha)

def main ():
    df = pd.read_csv("fondos.csv")

    col_filter = ["fecha", "name", "tipo_cod", "cod", "part", "gestora", "tipo", "titular", "i_compra", "id"]

    df = df[col_filter]
    df = df.dropna ()
    df_total = store_ms(df)

    df_finect = store_finect (df)

    df_total = pd.merge(df_total, df_finect, how='outer', on=['fecha'])

    df_quefondos = store_quefondos(df)

    df_total = pd.merge(df_total, df_quefondos, how='outer', on=['fecha'])

    df_bestinver = store_bestinver(df)

    df_total = pd.merge(df_total, df_bestinver, how='outer', on=['fecha'])

    return

    df.to_csv("fondos_resumen.csv")
    return


    get_price ("pp", df)
    get_price ("isin", df)

def store_ms (df):
    df = df.loc[df["tipo_cod"] == "isin"]
    l_id = df.id.unique ()

    df_total = pd.DataFrame(columns=['fecha', 'valor'])

    for id in l_id:
        df_prices = get_histo_ms(id)
        row = df[df.id == id].iloc[0]
        name = row["name"]
        name = name.replace(" ", "_")
        file = name + ".csv"

        # rename columna valor
        df_prices = df_prices.rename (columns={"valor": name})

        df_total = pd.merge(df_total, df_prices, how='outer', on=['fecha'])
        #df_prices.to_csv (file, sep='\t', index=False, float_format='%.3f', decimal=",")

    print (df_total)
#    df_total.to_csv("merge.csv", sep='\t', index=False, float_format='%.3f', decimal=",")
    return df_total

def store_finect (df):
    df = df.loc[df["tipo_cod"] == "finect"]
    ids = df.id.unique ()

    for id in ids:
        df_prices = get_histo_finect(id)
        # get the code with the corresponding id , there are several with equal values take first [0]
        name = df[df.id == id].iloc[0].name
        cod = name.replace(" ", "_")
        file = cod + ".csv"
        df_prices.to_csv (file)

def store_quefondos (df):
    df = df.loc[df["tipo_cod"] == "quefondos"]
    ids = df.id.unique ()

    for id in ids:
        df_prices = get_histo_quefondos(id)
        # get the code with the corresponding id , there are several with equal values take first [0]
        name = df[df.id == id].iloc[0].name
        cod = name.replace(" ", "_")
        file = cod + ".csv"
        df_prices.to_csv (file)

def store_bestinver (df):
    df = df.loc[df["tipo_cod"] == "bestinver"]
    ids = df.id.unique ()

    for id in ids:
        url = "https://www.bestinver.es/WS/Api/Profitability/DownloadExcelLiquidity?productId=" + id
        # NO FUNCIONA por problema con INCAPSULA

        # Linux
        chrome_path = '/usr/bin/google-chrome %s'

        page = webbrowser.get(chrome_path).open(url)

    return

    page = requests.get(url)
    print (page.content)
    return

    df_prices = get_histo_quefondos(id)
    # get the code with the corresponding id , there are several with equal values take first [0]
    cod = df[df.id == id].iloc[0].cod
    file = cod + ".csv"
    df_prices.to_csv (file)

def get_histo_ms (id):
    url = "https://tools.morningstar.es/api/rest.svc/timeseries_price/2nhcdckzon?id=" + id + "%5D2%5D1%5D&currencyId=EUR&idtype=Morningstar&frequency=daily&startDate=2006-01-01&endDate=2019-12-23&performanceType=&outputType=COMPACTJSON"
    page = requests.get(url)
    l = json.loads(page.content)

    # https://timestamp-converter.com/

    for i, v in enumerate(l):
        ts = v[0] /1000
        l[i][0] = datetime.fromtimestamp(ts).strftime("%d/%m/%Y")

    df = pd.DataFrame(l, columns=['fecha', 'valor'])
    return df

def get_histo_finect (id):
    url = "https://api.finect.com/v4/products/funds/" + id + "/timeseries?start=2008-01-01&adjusted=false&key=OgcqanUxQ4S6Y5VVvnwlJayUuxeg8Ah5"
    page = requests.get(url)

    d = json.loads(page.content)
    l = d["data"]

    new_l = []

    for i, v in enumerate(l):
        str = v["datetime"]
        dt = datetime.strptime(str, '%Y-%m-%dT%H:%M:%S.%fZ')
        fecha = dt.strftime("%d/%m/%Y")
        valor = float(v["price"])
        new_l.append ([ fecha, valor])

    df = pd.DataFrame(new_l, columns=['fecha', 'valor'])
    return df

def get_histo_quefondos (id):
    url = "https://www.quefondos.com/es/planes/ficha/index.html?isin=" + id
    page = requests.get(url)

    src_code = page.content.decode('utf-8')
    match = re.search("var fondo = (.*);", src_code)
    str = match.group(1)

    l = json.loads(str)

    for i, v in enumerate(l):
        dt = datetime.strptime(v[0], '%m/%d/%Y')
        l[i][0] = dt.strftime("%d/%m/%Y")

    df = pd.DataFrame(l, columns=['fecha', 'valor'])
    return df


if __name__ == "__main__":
    main()

#https://api.finect.com/v4/products/funds/cd39daad/timeseries?start=2008-01-01&adjusted=false&key=OgcqanUxQ4S6Y5VVvnwlJayUuxeg8Ah5
# INITIAL STATE -> id

# CABK tendencias
#https://www.quefondos.com/es/planes/ficha/index.html?isin=N4468
# var fondo

# excel bestinver futuro epsv
# https://www.bestinver.es/WS/Api/Profitability/DownloadExcelLiquidity?productId=14

# excel bestinver-crecimiento
# https://www.bestinver.es/WS/Api/Profitability/DownloadExcelLiquidity?productId=15

