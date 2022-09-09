import graphlib
import threading
import paho.mqtt.client as mqtt
import os

def on_connect(client, userdata, flags, rc):
    global topico
    global nome_usuario
    #os.system('cls' if os.name == 'nt' else 'clear')
    print("Seja bem-vindo "+nome_usuario+", você está conectado no grupo "+topico)
    client.subscribe(topico)

def on_message(client, userdata, msg):
    global nome_usuario
    global topico
    mensagem_entrada = msg.payload.decode()
    mensagem_separada = [x.strip() for x in mensagem_entrada.split(',',1)]
    remetente = mensagem_separada[0]

    if remetente != nome_usuario and remetente != "noticia":
        print(remetente + ": " + mensagem_separada[1])
    elif remetente == "noticia":
        print(mensagem_separada[1])

def publish():
    global nome_usuario
    global topico
    nova_mensagem = input()
    client.publish(topico, nome_usuario + "," + nova_mensagem);
    return publish()

def subscribe():
    global nome_usuario
    global topico
    client.publish(topico,"noticia" + "," + nome_usuario + " entrou neste tópico") 
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()


def config():
    global nome_usuario
    global topico
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        nome_usuario = input("Digite o seu nome: ")
        if nome_usuario.isalpha():
            break
        print("Por gentileza use apenas caracteres de A-Z")
    
    while True:
        topico = input("Digite o tópico no qual quer se conectar: ")
        if topico.isalpha():
            break
        print("Por gentileza use apenas caracteres de A-Z")
    
    return "Entrando no tópico ("+topico+")..."

print(config())
client = mqtt.Client()
client.connect("broker.hivemq.com",1883,60)
thr_pub = threading.Thread(target=publish)
thr_sub = threading.Thread(target=subscribe)
thr_pub.start()
thr_sub.start()