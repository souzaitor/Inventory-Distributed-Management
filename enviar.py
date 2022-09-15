import graphlib
import threading
import paho.mqtt.client as mqtt
import os

nome_usuario = "Centro Distribuição"
topico = "Reabastecimento(produto)"

def on_connect(client, userdata, flags, rc):

    os.system('cls' if os.name == 'nt' else 'clear')
    print(nome_usuario + " conectado ao tópico " + topico)
    client.subscribe(topico)

def on_message(client, userdata, msg):

    mensagem_entrada = msg.payload.decode()
    mensagem_separada = [x.strip() for x in mensagem_entrada.split(',',1)]
    remetente = mensagem_separada[0]

    if remetente != nome_usuario and remetente != "noticia":
        print(remetente + ": " + mensagem_separada[1])
    elif remetente == "noticia":
        print(mensagem_separada[1])

def publish():

    nova_mensagem = input()
    client.publish(topico, nome_usuario + "," + nova_mensagem)
    return publish()

def subscribe():

    client.publish(topico,"noticia"+ "," + nome_usuario + " conectado ao tópico " + topico) 
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()

client = mqtt.Client()
client.connect("broker.hivemq.com",1883,60)
thr_pub = threading.Thread(target=publish)
thr_sub = threading.Thread(target=subscribe)
thr_pub.start()
thr_sub.start()