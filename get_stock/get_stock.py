import investpy
import pandas as pd
import requests
from bs4 import BeautifulSoup

def display_options ():
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)


# Nombre del fondo a partir del isin
def get_name_by_isin (isin):
    try:
        df = investpy.funds.search_funds("isin", isin)
        name = df.loc[0,"name"]
        return name
    except:
        return None


def get_que_fondos (tipo, isin):
    url = "http://www.quefondos.com/es/" + tipo + "/ficha/index.html?isin=" + isin
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    selector = "span"

    l = soup.select(selector)
    for i, value in enumerate(l):
        if value.get_text () == "Valor liquidativo: ":
            valor = l[i+1].get_text()
        if value.get_text () == "Fecha: ":
            fecha = l[i+1].get_text()

    return valor,fecha


def main ():
    print (get_que_fondos ("fondos", "LU0244071956"))


    df = investpy.get_stock_recent_data(stock='tef',
                                        country='spain')
    print(df.head())



    df = investpy.get_fund_recent_data(fund='Esfera I Baelo Patrimonio Fi',
                                       country='spain')
    print(df)

#    get_fund_by_isin ("LU1670724373")
#    get_fund_by_isin ("ES0159202011")

    df = investpy.get_fund_historical_data(fund='bestinver futuro epsv', from_date='01/01/2009', to_date='19/12/2019',
                                       country='spain')
    print(df)

if __name__ == "__main__":
    main ()