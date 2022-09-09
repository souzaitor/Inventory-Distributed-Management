import graphlib
import threading
import paho.mqtt.client as mqtt
import os
import random
from tabulate import tabulate
import pandas as pd
import uuid
import numpy as np

# Variáveis globais
contador_clientes = 0

# Lê estoque de arquivo .csv e salva em lista
estoque = pd.read_csv('estoque.csv', delimiter=',', index_col=0) 

# Create a list of our conditions
conditions = [
    (estoque['Porcentagem'] >= 50),
    (estoque['Porcentagem'] >= 25) & (estoque['Porcentagem'] < 50),
    (estoque['Porcentagem'] >= 0) & (estoque['Porcentagem'] < 25)
    ]

# Create a list of the values we want to assign for each condition
values = ['Verde', 'Amarelo', 'Vermelho']

# create a new column and use np.select to assign values to it using our lists as arguments
estoque['Cor'] = np.select(conditions, values)



def publish():
    # Envia uma mensagem para cada produto em estoque na cor vermelha
    # no tópico reposição
    client = mqtt.Client()
    client.connect("broker.hivemq.com",1883,60)
    client.subscribe("repo")

    for numero_produto in produtos_no_vermelho:
        client.publish("repo", "Loja" + "," + "{}".format(numero_produto));



def imprimir_estoque():
    """
    Imprime o DataFrame estoque como tabela
    """
    print(tabulate(estoque, headers = 'keys'))




def debito_estoque(index_produto, quantidade_produto):
    """Retira uma quantiadade de produtos do estoque

    Parâmetros:
        index_produto: Número do produto a ser retirado do estoque
        quantidade_produto: Quantidade de elementos do produto a ser retirado do estoque

    """
    global estoque

    quantidade_antiga = estoque["Quantidade"].values[index_produto]

    estoque.loc[index_produto,["Quantidade","Porcentagem"]] = [quantidade_antiga - quantidade_produto, (quantidade_antiga - quantidade_produto)/200 * 100]



def atualizar_cores():
    """
    Atualiza a classificação da cor dos produtos
    em estoque com base em suas porcentagens
    """
    global estoque

    # Cria uma lista com as condições
    conditions = [
        (estoque['Porcentagem'] >= 50),
        (estoque['Porcentagem'] >= 25) & (estoque['Porcentagem'] < 50),
        (estoque['Porcentagem'] >= 0)  & (estoque['Porcentagem'] < 25)]

    # Lista com o valor atribuído a cada condição
    values = ['Verde', 'Amarelo', 'Vermelho']

    # Atualiza a coluna cor os valores
    estoque['Cor'] = np.select(conditions, values)



def clientes():
    quantidade_produtos = random.randint(2, 5)
    
    # Aleatoriza quais foram os produtos comprados pelos clientes
    produtos_comprados = []
    for i in range(quantidade_produtos):
        produtos_comprados.append(random.randint(0, 199))
    
    # Aleatoriza quais foram as quantidades comprados pelos clientes
    quantidade_comprados = []
    for i in range(quantidade_produtos):
        quantidade_comprados.append(random.randint(3, 10))

    # Realiza o débito do estoque
    for i in range(quantidade_produtos):
        debito_estoque(produtos_comprados[i], quantidade_comprados[i])

    # Exibe os dados da compra do cliente
    global contador_clientes

    print("O cliente {} comprou {} produtos: ".format(contador_clientes, quantidade_produtos))
    contador_clientes += 1

    for i in range(quantidade_produtos):
        print("\t{} produtos do tipo {}".format(quantidade_comprados[i], produtos_comprados[i]))
    print("\n")

     
if __name__ == '__main__':
    client = mqtt.Client()
    client.connect("broker.hivemq.com",1883,60)
    client.subscribe("repo")

    #imprimir_estoque()

    for i in range(10):
        clientes()
    atualizar_cores()

    #imprimir_estoque()
    
    # Lista de produtos com estoque na cor vermelha
    global produtos_no_vermelho
    produtos_no_vermelho = list(estoque[estoque["Cor"] == "Vermelho"].index)

    if (len(produtos_no_vermelho)>0):
        publish()



