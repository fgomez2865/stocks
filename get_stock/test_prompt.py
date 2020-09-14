import prompt_toolkit
import investpy 

from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.completion import WordCompleter


session = PromptSession()

def sel_list(l):
    completer = WordCompleter(l)
    return session.prompt(u"> ", completer=completer)

l_countries = investpy.funds.fund_countries_as_list()
country = sel_list (l_countries)

country = sel_list (l_countries)

funds = [_dict["name"] for _dict in investpy.funds.funds_as_dict(country)]

print (investpy.funds.funds_as_dict(country))

fund = sel_list (funds)

print( f"{country = }, {fund =}")
