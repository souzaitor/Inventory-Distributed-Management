
# Solução Distribuida de Cadeia de Abastecimento

## Introdução

Projeto de implementação de solução distribuída para monitoramento de níveis de estoque de produtos em lojas de varejo e centro de distribuição.


## Enunciado do Problema

* Utilizar Docker/Python como plataforma de solução e HiveMQ como broker de comunicação entre Fábricas / CD / Lojas.

* 200 tipos de produtos; 20 lojas; 70 fabricantes, cada fabricante produz alguma quantidade de produto e 1 centro de distribuição


* Cada loja possui um estoque com 200 tipos de produtos, cada tipo de produto tem um PID. Se o produto for do **tipo A**, a loja começa com **100 unidades em estoque**. Se o produto for do **tipo B,** a loja começa com **60 unidades em estoque**. Se o produto for do **tipo C**, a loja começa com **20 unidades em estoque**.


* A quantidade de classicação dos produtos é feita de qualquer maneira.

* Para cada produto, se a quantidade em estoque estiver entre 100% e 50%, o produto recebe a cor **Verde**. Entre 50% e 25$ a cor **Amarela** e entre 25% e 0%, a cor **Vermelha**.

* Se a quantidade dos produtos em estoque for Verde ou Amarela, não se realiza nenhuma ação. Se a quantidade dos produtos em estoque for Vermelha, o centro de distribuição deve realizar reposição.


## Implementação da Solução

A solução para o problema proposta foi a implementação de 3 tipos de nós de sistema distribuído, um nó para as fábricas, um nó para as lojas e um nó para o centro de distribuição.

![](https://i.imgur.com/sWUhSGc.png)


### Fábrica

* O nó fabrica é implementado no arquivo `fabrica.py`. 


```shell
python3 fabrica.py -h
usage: fabrica.py [-h] -n NUM -p PROD [PROD ...]

Simula fábrica da cadeia de produção

optional arguments:
  -h, --help            show this help message and exit
  -n NUM, --num NUM     Número da fábrica
  -p PROD [PROD ...], --prod PROD [PROD ...]
                        Lista de produtos produzidos pela fábrica
                        
```

* * O arquivo ao ser executado pelo terminal recebe dois parâmetros, uma flag -n acompanhada do número da fábrica e outra flag -p seguida da lista de produtos que a fabrica produz. Por exemplo, o comando abaixo inícia um nó da fábrica 1, que produz os produtos com ID 1, 2 e 3.


```shell
python3 fabrica.py -n 1 -p 1 2 3
```

* O programa `fabrica.py` instancia um cliente MQTT e o conecta no broker da HiveMQ. Depois, cria uma thread do método `subscribe()` e o executa em loop.

* O método `subscribe()` inscreve o cliente no tópico **Reabastecimento(produto)** e fica chamando os métodos     de conexão e de mensagens.

* O método de conexão `on_conect()` é chamado quando o broker responde a solicitação de conexão e realiza a inscrição de fato da fábrica no tópico, por meio do método da biblioteca paho.mqtt.

* O método de mensagem `on_message()` é chamado sempre que uma mensagem é recebida no tópico **Reabastecimento(produto)**. A mensagem é decodificada, se  o remente da mensagem for o Centro de Distribuição requisitando uma certa quantidade de reabastecimento para o ID de um produto, então a fábrica publica no tópico **Reabastecimento(produto)**, reabastecendo a quantidade do produto requisitado.


### Centro de Distribuição

* O nó Centro de distribuição é implementado no arquivo `centro_distribuicao.py`.

* O arquivo ao ser executado pelo terminal não recebe parâmetros. A execução é feita usando o comando:

```shell
python3 centro_distribuicao.py
```

* O programa `centro_distribuicao.py` instancia um cliente MQTT e o conecta no broker da HiveMQ. Depois, cria duas threads, uma do método `subscribe()` e uma do método `publish()`, e as executa em loop.

* O método `subscribe()` inscreve o cliente no tópico **Reabastecimento(produto)** e fica chamando os métodos     de conexão e de mensagens.

* O método de conexão `on_conect()` é chamado quando o broker responde a solicitação de conexão e realiza a inscrição de fato do centro de distribuição no tópico, por meio do método da biblioteca paho.mqtt.

* O método de mensagem `on_message()` é chamado sempre que uma mensagem é recebida no tópico **Reabastecimento(produto)** ou **Repo**. A mensagem é decodificada:
    * Se  o remente da mensagem for uma **fábrica**, no tópico  **Reabastecimento(produto)**, repondo uma certa quantidade de um produto, então o centro de distribuição realiza a operação de crédito, aumentando a quantidade de produtos recebidos no estoque. 
    * Se  o remente da mensagem for uma **loja**, no tópico **Repo**, requisitando uma certa quantidade de um produto, então o centro de distribuição realiza a operação de débito, diminuidndo a quantidade de produtos no estoque e publica mensagens no tópico **Repo**, simulando a reposição das lojas.

* O método `publish()` atualiza as cores do estoque no DataFrame com base na porcentagem atual de produto em estoque, e em seguida lista todos os produtos em estoque que estão no vermelho. Para cada um deles (produtos no vermelho) publica no tópico **Reabastecimento(produto)**, requisitando uma certa de quantidade de produtos para as fábricas que fabricam tais produtos, para reabastecer o estoque do centro de distribuição.

### Loja

* O nó loja é implementado no arquivo `loja.py`.

```shell
python3 loja.py -h
usage: loja.py [-h] -n NUM

Simula loja da cadeia de produção

optional arguments:
  -h, --help         show this help message and exit
  -n NUM, --num NUM  Número da loja
                        
```

* * O arquivo ao ser executado pelo terminal recebe  uma flag -n acompanhada do número da loja. Por exemplo, o comando abaixo inícia um nó da loja 1.


```shell
python3 loja.py -n 1 
```

* O programa `loja.py` instancia um cliente MQTT e o conecta no broker da HiveMQ. Depois, cria duas threads, uma do método `subscribe()` e uma do método `publish()`, e as executa em loop.

* O método `subscribe()` inscreve o cliente no tópico **Repo** e fica chamando os métodos de conexão e de mensagens.

* O método de conexão `on_conect()` é chamado quando o broker responde a solicitação de conexão e realiza a inscrição de fato da loja no tópico, por meio do método da biblioteca paho.mqtt.

* O método de mensagem `on_message()` é chamado sempre que uma mensagem é recebida no tópico **Repo**. A mensagem é decodificada.

*  Se  o remente da mensagem for o **centro de distribuição**, no tópico  **Repo**, repondo uma certa quantidade de um produto, então a loja realiza a operação de crédito, aumentando a quantidade de produtos recebidos no estoque. 


* O método `publish()` atualiza as cores do estoque no DataFrame com base na porcentagem atual de produto em estoque, e em seguida lista todos os produtos em estoque que estão no vermelho. Para cada um deles (produtos no vermelho) publica no tópico **Repo**, requisitando uma certa de quantidade de produtos para o centro de distribuição para reabastecer o estoque da loja.

* O estoque das lojas foi implementado como um DataFrame que lê um arquivo .csv. Assumindo que o estoque tem capacidade máxima de 100 produtos. A configuração inicial do estoque é a seguinte:

```
     Tipo      Quantidade    Porcentagem  Cor
---  ------  ------------  -------------  --------
  0  A                100           50    Verde
  1  A                100           50    Verde
  2  A                100           50    Verde
  3  A                100           50    Verde
  4  A                100           50    Verde
  5  A                100           50    Verde
  6  A                100           50    Verde
  7  A                100           50    Verde
  8  A                100           50    Verde
  9  A                100           50    Verde
 10  A                100           50    Verde
 11  A                100           50    Verde
 12  A                100           50    Verde
 13  A                100           50    Verde
 14  A                100           50    Verde
 15  A                100           50    Verde
 16  A                100           50    Verde
 17  A                100           50    Verde
 18  A                100           50    Verde
 19  A                100           50    Verde
 20  A                100           50    Verde
 21  A                100           50    Verde
 22  A                100           50    Verde
 23  A                100           50    Verde
 24  A                100           50    Verde
 25  A                100           50    Verde
 26  A                100           50    Verde
 27  A                100           50    Verde
 28  A                100           50    Verde
 29  A                100           50    Verde
 30  A                100           50    Verde
 31  A                100           50    Verde
 32  A                100           50    Verde
 33  A                100           50    Verde
 34  A                100           50    Verde
 35  A                100           50    Verde
 36  A                100           50    Verde
 37  A                100           50    Verde
 38  A                100           50    Verde
 39  A                100           50    Verde
 40  A                100           50    Verde
 41  A                100           50    Verde
 42  A                100           50    Verde
 43  A                100           50    Verde
 44  A                100           50    Verde
 45  A                100           50    Verde
 46  A                100           50    Verde
 47  A                100           50    Verde
 48  A                100           50    Verde
 49  A                100           50    Verde
 50  A                100           50    Verde
 51  A                100           50    Verde
 52  A                100           50    Verde
 53  A                100           50    Verde
 54  A                100           50    Verde
 55  A                100           50    Verde
 56  A                100           50    Verde
 57  A                100           50    Verde
 58  A                100           50    Verde
 59  A                100           50    Verde
 60  A                100           50    Verde
 61  A                100           50    Verde
 62  A                100           50    Verde
 63  A                100           50    Verde
 64  A                100           50    Verde
 65  A                100           50    Verde
 66  A                100           50    Verde
 67  A                100           50    Verde
 68  A                100           50    Verde
 69  A                100           50    Verde
 70  B                 60           30    Amarelo
 71  B                 60           30    Amarelo
 72  B                 60           30    Amarelo
 73  B                 60           30    Amarelo
 74  B                 60           30    Amarelo
 75  B                 60           30    Amarelo
 76  B                 60           30    Amarelo
 77  B                 60           30    Amarelo
 78  B                 60           30    Amarelo
 79  B                 60           30    Amarelo
 80  B                 60           30    Amarelo
 81  B                 60           30    Amarelo
 82  B                 60           30    Amarelo
 83  B                 60           30    Amarelo
 84  B                 60           30    Amarelo
 85  B                 60           30    Amarelo
 86  B                 60           30    Amarelo
 87  B                 60           30    Amarelo
 88  B                 60           30    Amarelo
 89  B                 60           30    Amarelo
 90  B                 60           30    Amarelo
 91  B                 60           30    Amarelo
 92  B                 60           30    Amarelo
 93  B                 60           30    Amarelo
 94  B                 60           30    Amarelo
 95  B                 60           30    Amarelo
 96  B                 60           30    Amarelo
 97  B                 60           30    Amarelo
 98  B                 60           30    Amarelo
 99  B                 60           30    Amarelo
100  B                 60           30    Amarelo
101  B                 60           30    Amarelo
102  B                 60           30    Amarelo
103  B                 60           30    Amarelo
104  B                 60           30    Amarelo
105  B                 60           30    Amarelo
106  B                 60           30    Amarelo
107  B                 60           30    Amarelo
108  B                 60           30    Amarelo
109  B                 60           30    Amarelo
110  B                 60           30    Amarelo
111  B                 60           30    Amarelo
112  B                 60           30    Amarelo
113  B                 60           30    Amarelo
114  B                 60           30    Amarelo
115  B                 60           30    Amarelo
116  B                 60           30    Amarelo
117  B                 60           30    Amarelo
118  B                 60           30    Amarelo
119  B                 60           30    Amarelo
120  B                 60           30    Amarelo
121  B                 60           30    Amarelo
122  B                 60           30    Amarelo
123  B                 60           30    Amarelo
124  B                 60           30    Amarelo
125  B                 60           30    Amarelo
126  B                 60           30    Amarelo
127  B                 60           30    Amarelo
128  B                 60           30    Amarelo
129  B                 60           30    Amarelo
130  B                 60           30    Amarelo
131  B                 60           30    Amarelo
132  B                 60           30    Amarelo
133  B                 60           30    Amarelo
134  B                 60           30    Amarelo
135  B                 60           30    Amarelo
136  B                 60           30    Amarelo
137  B                 60           30    Amarelo
138  B                 60           30    Amarelo
139  B                 60           30    Amarelo
140  C                 20           10    Vermelho
141  C                 20           10    Vermelho
142  C                 20           10    Vermelho
143  C                 20           10    Vermelho
144  C                 20           10    Vermelho
145  C                 20           10    Vermelho
146  C                 20           10    Vermelho
147  C                 20           10    Vermelho
148  C                 20           10    Vermelho
149  C                 20           10    Vermelho
150  C                 20           10    Vermelho
151  C                 20           10    Vermelho
152  C                 20           10    Vermelho
153  C                 20           10    Vermelho
154  C                 20           10    Vermelho
155  C                 20           10    Vermelho
156  C                 20           10    Vermelho
157  C                 20           10    Vermelho
158  C                 20           10    Vermelho
159  C                 20           10    Vermelho
160  C                 20           10    Vermelho
161  C                 20           10    Vermelho
162  C                 20           10    Vermelho
163  C                 20           10    Vermelho
164  C                 20           10    Vermelho
165  C                 20           10    Vermelho
166  C                 20           10    Vermelho
167  C                 20           10    Vermelho
168  C                 20           10    Vermelho
169  C                 20           10    Vermelho
170  C                 20           10    Vermelho
171  C                 20           10    Vermelho
172  C                 20           10    Vermelho
173  C                 20           10    Vermelho
174  C                 20           10    Vermelho
175  C                 20           10    Vermelho
176  C                 20           10    Vermelho
177  C                 20           10    Vermelho
178  C                 20           10    Vermelho
179  C                 20           10    Vermelho
180  C                 20           10    Vermelho
181  C                 20           10    Vermelho
182  C                 20           10    Vermelho
183  C                 20           10    Vermelho
184  C                 20           10    Vermelho
185  C                 20           10    Vermelho
186  C                 20           10    Vermelho
187  C                 20           10    Vermelho
188  C                 20           10    Vermelho
189  C                 20           10    Vermelho
190  C                 20           10    Vermelho
191  C                 20           10    Vermelho
192  C                 20           10    Vermelho
193  C                 20           10    Vermelho
194  C                 20           10    Vermelho
195  C                 20           10    Vermelho
196  C                 20           10    Vermelho
197  C                 20           10    Vermelho
198  C                 20           10    Vermelho
199  C                 20           10    Vermelho
```

### Escalonando a solução

![](https://i.imgur.com/AHyK766.png)

* Com a implementação dos nós pronta, para montar a solução distribúida utilizamos o Docker para rodar as diversas instâncias das Fábricas e Lojas.

