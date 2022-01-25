import datetime
import numpy as np
import sympy as sp
from leitor import read_contrac
import pandas as pd
from networkdays import networkdays
import matplotlib.pyplot as plt



class analise_contrato:
    
    def __init__(self, letra):
        
        self.letra =  letra
        
        
    def contr(self):

        contrato = read_contrac(self.letra)
        return contrato

    def feriado(self):
        
        feriados = pd.read_csv("feriados.csv")
        return feriados

    


    #dias uteis do dia do começo do contato até dia atual 
    def dias_uteis(self,start_date,end_date):
        
        feriados = analise_contrato.feriado(self)

        holidays = [datetime.datetime.strptime(feriado,"%Y-%m-%d") for feriado in feriados["Data"]]

        dias = networkdays.Networkdays(start_date,end_date,holidays)
        dias = len(dias.networkdays())
        
        return  dias

    #Amortização 
    def ati(self,data):
        
        contrato = analise_contrato.contr(self)

        pagamentos = contrato["schedules"]
        
        amt = 0
        for i in range(len(pagamentos)):
            
            
            data_evento =  datetime.datetime.strptime(pagamentos[i]['due_date'],"%Y-%m-%d")
            
            if data_evento < data:
                amt += contrato['emission_price']*pagamentos[i]['amount'] 

        return amt

    #Juros a serem pagos
    def juros(self,data):

        contrato = analise_contrato.contr(self)

        pagamentos = contrato["schedules"]      

        juros_total = 0
        
        for j in range(len(pagamentos)):
            
            if datetime.datetime.strptime(pagamentos[j]['due_date'],"%Y-%m-%d") >= data:
                
                dias = analise_contrato.dias_uteis(self,datetime.datetime.strptime(pagamentos[j-1]['due_date'],"%Y-%m-%d"), datetime.datetime.strptime(pagamentos[j]['due_date'],"%Y-%m-%d"))
                
                v = analise_contrato.vna(self,data)
                multi = (1+contrato['spread'])**(dias/252)-1 

                juro = v*multi
                
                j = (1+contrato['spread'])**(dias/252)

                juros_total += juro/j

        return juros_total

    #Amortização a ser paga
    def atj(self,data):
        
        contrato = analise_contrato.contr(self)

        pagamentos = contrato["schedules"]
        
        amt_total = 0
        for i in range(len(pagamentos)):
            
            dias = analise_contrato.dias_uteis(self,datetime.datetime.strptime(pagamentos[i-1]['due_date'],"%Y-%m-%d"), datetime.datetime.strptime(pagamentos[i]['due_date'],"%Y-%m-%d"))
            
            data_evento =  datetime.datetime.strptime(pagamentos[i]['due_date'],"%Y-%m-%d")
            
            if data_evento > data:
                
                amt = contrato['emission_price']*pagamentos[i]['amount'] 
                
                amt_total += amt/(1+contrato['spread'])**(dias/252)

        return amt_total

    #Valor nominal atualizado 
    def vna(self,data):
        
        contrato = analise_contrato.contr(self)
        
        vna = contrato['emission_price'] - analise_contrato.ati(self,data)
        return vna

    #PuPar
    def pupar(self,data):
        
        contrato = analise_contrato.contr(self)
        pagamentos = contrato["schedules"]
        
        for i in range(len(pagamentos)):
 
            if data <= datetime.datetime.strptime(pagamentos[1]['due_date'],"%Y-%m-%d") :   
                
                pagamento_ant = datetime.datetime.strptime(contrato['start_date'],"%Y-%m-%d")
            
            elif data > datetime.datetime.strptime(pagamentos[i]['due_date'],"%Y-%m-%d") :
                pagamento_ant = datetime.datetime.strptime(pagamentos[i]['due_date'],"%Y-%m-%d")
                
            elif data == datetime.datetime.strptime(pagamentos[i]['due_date'],"%Y-%m-%d"):
                pagamento_ant = datetime.datetime.strptime(pagamentos[i-1]['due_date'],"%Y-%m-%d")
                break
        
   
        mult = (1 + contrato["spread"])**(analise_contrato.dias_uteis(self,pagamento_ant,data)/252)
        pupar = analise_contrato.vna(self,data) * mult

        return pupar

    #Pu Operação 
    def pu_op(self,data,juros_neg):

        contrato = analise_contrato.contr(self)

        pagamentos = contrato["schedules"]
        
        juros_neg = float(juros_neg) 

        pu_op = 0

        for i in range(len(pagamentos)):

            data_pag = datetime.datetime.strptime(pagamentos[i]['due_date'],"%Y-%m-%d") 
            
            if i == 0:

                ant = datetime.datetime.strptime(contrato['start_date'],"%Y-%m-%d") 
            else:
                ant = datetime.datetime.strptime(pagamentos[i-1]['due_date'],"%Y-%m-%d")

            if data_pag >= data:   

                amort = pagamentos[i]['amount']*contrato['emission_price']
                
                vna = analise_contrato.vna(self,data_pag)

                juro = vna*((1+contrato['spread'])**((analise_contrato.dias_uteis(self,ant,data_pag)/252))-1)
                
                pu_op += (amort + juro)/(1+juros_neg)**(analise_contrato.dias_uteis(self,data,data_pag)/252)          

                
        return pu_op

    def calc_taxa(self,data,pu_op):

        pu_op = float(pu_op)

        contrato = analise_contrato.contr(self)
        pagamentos = contrato["schedules"]
        
        pu = []
        juros = []

        for i in range(len(pagamentos)):

            data_pag = datetime.datetime.strptime(pagamentos[i]['due_date'],"%Y-%m-%d") 
            
            if i == 0:

                ant = datetime.datetime.strptime(contrato['start_date'],"%Y-%m-%d") 
            else:
                ant = datetime.datetime.strptime(pagamentos[i-1]['due_date'],"%Y-%m-%d")

            if data_pag >= data:   

                amort = pagamentos[i]['amount']*contrato['emission_price']
                
                vna = analise_contrato.vna(self,data_pag)

                juro = vna*((1+contrato['spread'])**((analise_contrato.dias_uteis(self,ant,data_pag)/252))-1)
                
                pu.append(round((amort + juro),4))          

                juros.append(round((analise_contrato.dias_uteis(self,data,data_pag)/252),4))
                
            eq_set = []

            j = sp.symbols('j')

            eq_total = 0 
            
            for i in range(len(pu)):
               eq_set.append(pu[i]/(1 + j)**juros[i])

            for i in range(len(eq_set)):
                
                eq_total += eq_set[i] 
            
            eq_total = sp.Eq(eq_total,pu_op)

            solved = sp.nsolve(eq_total,(0,1),solver='bisect', verify=False)    

        return solved

    def plots(self,data_init,data_final,juros):

        q_dias = abs((data_init-data_final).days)        

        pu = []

        pu_op = []
       
        dia = []

        data = data_init

        for i in range(q_dias):
            
            dia.append(data.strftime('%m/%d/%Y'))
            
            pu.append(analise_contrato.pupar(self,data))

            pu_op.append(analise_contrato.pu_op(self,data,juros))

            data = data + datetime.timedelta(days = 1)

        dado = {'pu':pu,'pu_op':pu_op,'data':dia}
    
        df = pd.DataFrame(dado)
        
        fig, ax = plt.subplots() 

        df.plot(x = 'data', y = 'pu', ax = ax) 
        
        df.plot(x = 'data', y = 'pu_op', ax = ax, secondary_y = True) 

        plt.show()
        
        return 





   