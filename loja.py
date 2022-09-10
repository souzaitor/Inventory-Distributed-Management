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
nome_loja = "Loja 1"
topico = "repo"

# Lê estoque de arquivo .csv e salva em lista
estoque = pd.read_csv('estoque.csv', delimiter=',', index_col=0) 


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

def credito_estoque(index_produto, quantidade_produto):
    """Adiciona uma quantiadade de produtos do estoque

    Parâmetros:
        index_produto: Número do produto a ser retirado do estoque
        quantidade_produto: Quantidade de elementos do produto a ser retirado do estoque

    """
    global estoque

    quantidade_antiga = estoque["Quantidade"].values[index_produto]

    estoque.loc[index_produto,["Quantidade","Porcentagem"]] = [quantidade_antiga + quantidade_produto, (quantidade_antiga + quantidade_produto)/200 * 100]


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

######################################################################################
#                           Funções Pub/Sub                                          #
######################################################################################

def on_connect(client, userdata, flags, rc):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(nome_loja + " conectada ao tópico " + topico)
    client.subscribe(topico)


def on_message(client, userdata, msg):
    global estoque
    mensagem_entrada = msg.payload.decode()
    mensagem_separada = [x.strip() for x in mensagem_entrada.split(',',1)]
    remetente = mensagem_separada[0]

    # Se recebeu uma mensagem de abastecimento 
    # do centro de distribuição, realiza o crédito
    if remetente == "Centro Distribuição":
        print(remetente + ": " + mensagem_separada[1])
        
        mensagem_cortada = mensagem_separada[1].split()
        quantidade_credito = int(mensagem_cortada[1])
        index_produto = int(mensagem_cortada[4])
        credito_estoque(index_produto, quantidade_credito)

        atualizar_cores()
        estoque.to_csv('estoque.csv', index=True)

    elif remetente == "noticia":
        print(mensagem_separada[1])


def publish():
    """
    
    """
    nova_mensagem = input()
    
    # Simula a compra aleatória de produtos por clientes
    clientes()

    # Atualiza as cores do DataFrame
    atualizar_cores()

    # Atualiza o arquivo .csv
    estoque.to_csv('estoque.csv', index=True)

    # Lista de produtos com estoque na cor vermelha
    produtos_no_vermelho = list(estoque[estoque["Cor"] == "Vermelho"].index)

    # Se existem produtos no vermelho, envia mensagem no tópico 
    # reposição para que o centro de distribuição envie produtos 
    # para o estoque, completando o estoque
    if (len(produtos_no_vermelho)>0):
        nova_mensagem = ','.join(str(x) for x in produtos_no_vermelho)
        client.publish(topico, nome_loja + "," + nova_mensagem);

    return publish()


def subscribe():

    client.publish(topico, "noticia" + "," + nome_loja + " entrou neste tópico") 
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()


if __name__ == '__main__':
    client = mqtt.Client()
    client.connect("broker.hivemq.com",1883,60)
    thr_pub = threading.Thread(target=publish)
    thr_sub = threading.Thread(target=subscribe)
    thr_pub.start()
    thr_sub.start()
