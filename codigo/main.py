import datetime
from calculos import analise_contrato

def analise_pu():
    letra = input('Escolha a letra do contrato: ')
    juros = input('Escolha o juros negociado: ')
    data = input('Insira a data na forma Y-m-d: ')

    b = analise_contrato(letra).pu_op(datetime.datetime.strptime(data,"%Y-%m-%d") ,juros)
    a = analise_contrato(letra).pupar(datetime.datetime.strptime(data,"%Y-%m-%d"))
    
    print('PU : {}\nPU op: {}'.format(a,b))


def analise_dados():
    letra = input('Escolha a letra do contrato: ')
    datai = input('Insira a data na forma Y-m-d: ')
    dataf = input('Insira a data na forma Y-m-d: ')
    juro = input('Escolha o juros negociado: ') 
    
    analise_contrato(letra).plots(datetime.datetime.strptime(datai,"%Y-%m-%d"),datetime.datetime.strptime(dataf,"%Y-%m-%d"),juro)

def analise_juros():
    letra = input('Escolha a letra do contrato: ')
    data = input('Insira a data na forma Y-m-d: ')
    pu_op = input('Insira o PU da operação')

    a = analise_contrato(letra).calc_taxa(datetime.datetime.strptime(data,"%Y-%m-%d"), pu_op)

    return print('O valor da taxa negociada é: {}',format(a))
valor = input('Analise PU/PU Operação:1\nPlotar valor contrato:2 \nAnalise Juros:3 \nInsira a operação: ')

if valor == '1':
    analise_pu()
if valor == '2':
    analise_dados()