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
nome_usuario = "Centro Distribuição"
topico = "repo"

# Lê estoque de arquivo .csv e salva em lista
estoque = pd.read_csv('estoque.csv', delimiter=',', index_col=0) 

def credito_estoque(index_produto, quantidade_produto):
    """Retira uma quantiadade de produtos do estoque

    Parâmetros:
        index_produto: Número do produto a ser retirado do estoque
        quantidade_produto: Quantidade de elementos do produto a ser retirado do estoque

    """
    global estoque

    quantidade_antiga = estoque["Quantidade"].values[index_produto]

    estoque.loc[index_produto,["Quantidade","Porcentagem"]] = [quantidade_antiga + quantidade_produto, (quantidade_antiga + quantidade_produto)/200 * 100]

######################################################################################
#                           Funções Pub/Sub                                          #
######################################################################################

def on_connect(client, userdata, flags, rc):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(nome_usuario + " conectada ao tópico " + topico)
    client.subscribe(topico)


def on_message(client, userdata, msg):

    mensagem_entrada = msg.payload.decode()
    mensagem_separada = [x.strip() for x in mensagem_entrada.split(',',1)]
    remetente = mensagem_separada[0]

    global produtos_credito
    produtos_credito = mensagem_separada[1].split(",")

    if remetente != nome_usuario and remetente != "noticia":
        print(remetente + " requisiou os produtos: " + mensagem_separada[1])

    elif remetente == "noticia":
        print(mensagem_separada[1])

def publish():
    nova_mensagem = input()

    if(len(produtos_credito)>0):
        # Realiza o crédito do estoque
        for produto in produtos_credito:
            client.publish(topico, nome_usuario + "," + "Enviou {} do produto {}".format(10, produto))


    
    return publish()


def subscribe():
    client.publish(topico,"noticia" + "," + nome_usuario + " entrou neste tópico") 
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