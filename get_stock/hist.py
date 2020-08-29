import requests
import json
import pandas as pd
from datetime import datetime
import re

class Hist:

    def get_data (self, id):
        url = self.url.format (id)

        page = requests.get(url)
        return (page.content)

    def get (self, id):
        data = self.get_data (id)


        l = self.extract (data)

        new_l = []
        for i, v in enumerate(l):
            new_v = self.convert (v)
            new_l.append (new_v)

        df = pd.DataFrame(new_l, columns=['fecha', 'valor'])
        print (df)
        return df


    def load_files (self, df):

        df = df.drop(df[df['tipo_cod'] == "bestinver"].index)

        for i, row in df.iterrows():
            name = row["name"]
            name = name.replace(" ", "_") + ".csv"

            print (pd.read_csv (name, sep='\t'))

    def store (self, df):

        df = df.loc[df["tipo_cod"] == self.tipo_cod ]
        l_id = df.id.unique()

        df_total = pd.DataFrame(columns=['fecha'])

        for id in l_id:
            df_prices = self.get (id)
            row = df[df.id == id].iloc[0]
            name = row["name"]
            name = name.replace(" ", "_")


            # rename columna valor
            df_prices = df_prices.rename (columns={"valor": name})
            df_prices.interpolate(method='time', limit_direction='forward', inplace=True)

            df_total = pd.merge(df_total, df_prices, how='outer', on=['fecha'])
            file = name + ".csv"
            df_prices.to_csv (file, sep='\t', index=False, float_format='%.3f', decimal=",")

        print (df_total)
        # df_total.to_csv(file + ".csv", sep='\t', index=False, float_format='%.3f', decimal=",")
        return df_total

# ----------------------------------------------------------------------------------------------------------------
class Hist_ms(Hist):
    def __init__(self):
        self.url = "https://tools.morningstar.es/api/rest.svc/timeseries_price/2nhcdckzon?id={}%5D2%5D1%5D&currencyId=EUR&idtype=Morningstar&frequency=daily&startDate=2006-01-01&endDate=2019-12-23&performanceType=&outputType=COMPACTJSON"
        self.tipo_cod = "isin"

    def extract (self, data):
        l = json.loads(data)
        return l

    def convert (self, v):
        ts = v[0] / 1000
        v[0] = datetime.fromtimestamp(ts).strftime("%d/%m/%Y")
        return v

# ----------------------------------------------------------------------------------------------------------------
class Hist_finect(Hist):
    def __init__(self):
        self.url = "https://api.finect.com/v4/products/funds/{}/timeseries?start=2008-01-01&adjusted=false&key=OgcqanUxQ4S6Y5VVvnwlJayUuxeg8Ah5"
        self.tipo_cod = "finect"

    def extract (self, data):
        var = json.loads(data)
        return var['data']

    def convert (self, v):
        str = v["datetime"]
        dt = datetime.strptime(str, '%Y-%m-%dT%H:%M:%S.%fZ')
        fecha = dt.strftime("%d/%m/%Y")
        valor = float(v["price"])

        return [fecha, valor]
# ----------------------------------------------------------------------------------------------------------------
class Hist_quefondos(Hist):
    def __init__(self):
        self.url = "https://www.quefondos.com/es/planes/ficha/index.html?isin={}"
        self.tipo_cod = "quefondos"

    def extract (self, data):
        src_code = data.decode('utf-8')
        match = re.search("var fondo = (.*);", src_code)
        str = match.group(1)

        var = json.loads(str)
        return var

    def convert (self, v):
        dt = datetime.strptime(v[0], '%m/%d/%Y')
        v[0] = dt.strftime("%d/%m/%Y")
        return v

        str = v["datetime"]
        dt = datetime.strptime(str, '%Y-%m-%dT%H:%M:%S.%fZ')
        fecha = dt.strftime("%d/%m/%Y")
        valor = float(v["price"])

        return [fecha, valor]


# ----------------------------------------------------------------------------------------------------------------
def get_fondos ():
    df = pd.read_csv("fondos.csv")

    col_filter = ["fecha", "name", "tipo_cod", "cod", "part", "gestora", "tipo", "titular", "i_compra", "id"]

    df = df[col_filter]
    df = df.dropna ()
    return df

def main ():
    #df = ms.get ("F0GBR04PSY")
    df_fondos = get_fondos ()

    hist = Hist ()
    hist.load_files(df_fondos)
    return

    ms = Hist_ms ()
    df_total = ms.store (df_fondos)

    finect = Hist_finect ()
    df = finect.store (df_fondos)

    df_total = pd.merge(df_total, df, how='outer', on=['fecha'])

    quefondos = Hist_quefondos ()
    df = quefondos.store (df_fondos)

    df_total = pd.merge(df_total, df, how='outer', on=['fecha'])

    df_total = df_total.set_index ("fecha")
    print (df_total)
    #df_total.interpolate(method='time', limit_direction='forward', inplace=True)

    import matplotlib.pyplot as plt

    # a scatter plot comparing num_children and num_pets
    #df.plot(kind='scatter',x='num_children',y='num_pets',color='red')
    ax = plt.gca()
    df_total.plot(kind="line",x="fecha", ax=ax)
    plt.show()
    #df_total.to_csv("todos_1.csv", sep='\t', index=False, float_format='%.3f', decimal=",")

if __name__ == "__main__":
    main()
