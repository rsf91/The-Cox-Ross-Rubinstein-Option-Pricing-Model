#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024 Sept 24 17:44:40

@author: roferreira23

based on work of @author: mattiacalzetta

"""

import numpy as np
import copy

def BinomialTreeCRR(option_type,S0, K, r, sigma, T, N=200 ,american="false", portfolio = False):
    """
    Params:
        type: C (call) or P (put)
        S0: stock price at t=0
        K: strike price
        r: constant riskless short rate
        sigma: constant volatility (i.e. standard deviation of returns) of S
        T: the horizion in year fractions (i.e. 1, 2, 3.5 etc)
        american: false (european) or true (american)
    Assumptions:
        1) the original Cox, Ross & Rubinstein (CRR) method as been used (paper below)
            http://static.stevereads.com/papers_to_read/option_pricing_a_simplified_approach.pdf
        2) no dividends
    Output:
        Value of the option today
    """

    #deltaT  
    dT = float(T)/N
 
    # up and down factor calculated using the underlying volatility sigma as per the original CRR
    u = np.exp(sigma * np.sqrt(dT)) #up factor
    d = np.exp(-sigma * np.sqrt(dT)) #down factor
 
    #We are using N+1 because the number of outcomes is always equal to N+1
    value=[]
    for i in range(N+1):
        value.append(float(0))
    value=np.asarray(value)

    
    #we need the stock tree for calculations of expiration values (all possible combinations of ups and downs)
    stock_price=[]
    for i in range(N+1):
        stock_price.append(S0 * u**i * d**(N - i))
    stock_price=np.asarray(stock_price)   
    
    
    #strikes as well to use arrays efficiently 
    strike=[]
    for i in range(N+1):
        strike.append(float(K))
    strike=np.asarray(strike)
    
    
    #the original paper uses "q" to indicate the probability but anyway
    p = (np.exp(r * dT) - d)/ (u - d)
    oneMinusP = 1 - p
    
    # Compute the leaves for every element [:] in the array
    if option_type =="C": #if it's a call 
        value[:] = np.maximum(stock_price-strike, 0)
        
    elif option_type == "P": #if it's a put
        value[:] = np.maximum(-stock_price+strike, 0)
    
    """
    Calculate backward the option prices for each node:
        1) in "value" we have the option prices
        2) in loop (one for each N), we calculate the price of the option (backwards) by pairing the outcomes 2 by 2
        3) we finally arrive to the price of the option today
    """
    value_backwards = []
    delta_backwards = []
    stock_backwards = []
    
    if portfolio == False:
        for i in range(N):
            #For each (except last one) = bla bla * (except first + except last one) - this is to couple all the leaves at each node
            #
            # O que vai acontecer aqui é o seguinte:
            # 
            # vamos assumir que a arvore abriu até uma lista de 5 valores = array([ 0.        ,  0.        ,  0.        , 22.14027582, 49.18246976])
            # O resultado do modelo que vc vai fazer é [ 0 + 0 , 0 + 0, 0 + 22, 22 + 49 ]. Isso é igual a somar duas listas. [0,0,0,22] + [0,0,22,49]

            # Isso é igual a pegar a lista toda menos o primeiro termo e chamar de UP, 
            # pegar a lista toda menos o ultimo termo e chamar de DOWN

            # ISSO QUE ACONTECE AQUI EMBAIXO - quebrei pra ficar mais evidente

            up_list = value[1:]
            down_list = value[:-1]
            value[:-1]=np.exp(-r * dT) * (p * up_list + oneMinusP * down_list)
            value_backwards.append((value[:-(i+1)]))
            #multiplying all stock prices as we are going backwards. we are using u and not p as we are walking backwards from bottom to top 
            stock_price[:]=stock_price[:]*u
            
            #only for american options as for american options we must check at each node if the option is worth more alive then dead
            if american=='true':
            #check if the option is worth more alive or dead (i.e. comparing the payoff against the value of the option)
                if option_type =="C":
                    value[:]=np.maximum(value[:],stock_price[:]-strike[:])
                elif option_type == "P":
                    value[:]=np.maximum(value[:],-stock_price[:]+strike[:])
            
        print(value)
    
    if portfolio == True:
        for i in range(N):
            up_list = value[1:]
            down_list = value[:-1]

            s_up_list = stock_price[1:]
            s_down_list = stock_price[:-1]

            delta = (up_list - down_list) / (s_up_list - s_down_list)

            value_backwards.append(value.copy())
            delta_backwards.append(delta.copy())
            stock_backwards.append(stock_price.copy())
            print(value_backwards)
            print(delta_backwards)
            print(stock_backwards)
            

            #Return VALUE

            value[:-1]=np.exp(-r * dT) * (p * up_list + oneMinusP * down_list)
            value = value[:-1]

            #Return STOCK
            stock_price[:]=stock_price[:]*u
            stock_price = stock_price[:-1]

            

            #multiplying all stock prices as we are going backwards. we are using u and not p as we are walking backwards from bottom to top 
            # stock_price[:]=stock_price[:]*u

            #if len(value_backwards[-1]) == 2:
            #    pass
                # Should be true EITHER WAY

            
            #only for american options as for american options we must check at each node if the option is worth more alive then dead
            if american=='true':
            #check if the option is worth more alive or dead (i.e. comparing the payoff against the value of the option)
                if option_type =="C":
                    value[:]=np.maximum(value[:],stock_price[:]-strike[:])
                elif option_type == "P":
                    value[:]=np.maximum(value[:],-stock_price[:]+strike[:])
        
        message = "A seguir vc vai ver os valores relevantes do calculo da arvore. \nO preço da opcao é {}, e o delta atual para fazer o hedge é {}".format(
            value[0],
            delta_backwards[-1][0]
        )
        message_2 = "Essa funcao tambem te retornará esses valores da seguinte forma: value[0], value_backwards, stock_backwards, delta_backwards"

        print(message)
        print(message_2)

        return {
                "value" : value[0], 
                "value_tree": value_backwards, 
                "stock_tree": stock_backwards, 
                "delta_tree" : delta_backwards
                }
            
        
                
    # print first value - i.e. first element of array 
    return value[0]


def main():
    """
    Params:
        option_type: C (call) or P (put)
        S0: stock price at t=0
        K: strike price
        r: constant riskless short rate
        sigma: constant volatility (i.e. standard deviation of returns) of S
        T: the horizion in year fractions (i.e. 1, 2, 3.5 etc)
        american: false (european) or true (american)
    Assumptions:
        1) the original Cox, Ross & Rubinstein (CRR) method as been used (paper below)
            http://static.stevereads.com/papers_to_read/option_pricing_a_simplified_approach.pdf
        2) no dividends
    Output:
        Value of the option today
    """   
    option_type = "C"
    S0 = 100
    K = 100
    r = 0.05
    sigma = 0.20
    T = 1
    american = 'false'
    result = BinomialTreeCRR(option_type,
                    S0 = S0,
                    K = K, 
                    r=r, 
                    sigma=sigma, 
                    T=T, 
                    N=3 ,
                    american=american,
                    portfolio = True)
    return result



x = main()
""" 
#x.keys() : dict_keys(['value', 'value_tree', 'stock_tree', 'delta_tree'])
# value : valor do PayOff ajustado ao preço atual
# value_tree : Árvore feita do ultimo nó pra trás para o valor da Opcao
# stock_tree : Árvore feita do ultimo nó pra trás para o valor da Açao
# delta_tree : Árvore feita do ultimo nó pra trás para o valor que o Delta deve ser para garantir Portfolio para próxima etapa
"""
print(x)

