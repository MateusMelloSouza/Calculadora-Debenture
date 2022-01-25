import json
import datetime  
import pandas as pd
 

#leitor do contrato 
def read_contrac(letra_contrato): 
    
    f = open('contrato{}.json'.format(letra_contrato.upper()))    
    contrato = json.load(f)
    
    return contrato

def read_feriados():

    feriados = pd.read_csv('feriados.csv')
    
    return feriados

#Numero de eventos de pagamento do titulo
def n_eventos(letra_contrato):

    contrato = read_contrac(letra_contrato)
    pagamentos = contrato["schedules"]
    
    hoje = datetime.datetime.now()
    n = 0

    for i in range(len(pagamentos)):
        data_evento =  datetime.datetime.strptime(pagamentos[i]['due_date'],"%Y-%m-%d")
        if data_evento <= hoje:
            n+=1

    return n


