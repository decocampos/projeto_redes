import datetime as dt

#retorna os dados relativos à tempo
def get_time_data():
  return dt.datetime.now().strftime("%Hh%Mm%Ss %d/%m/%Y ") #ex: 13h58m57s 14/06/2024
