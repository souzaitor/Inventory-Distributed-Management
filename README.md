# sist-dist-t2

Projeto de implementação de solução distribuída para monitoramento de níveis de estoque de produtos em lojas de varejo e centro de distribuição.

Premissas: Utilizar Docker/Python como plataforma de solução e HiveMQ como broker de comunicação entre Fábricas / CD / Lojas

### Cenário
* 200 tipos de produtos
* 20 lojas
* 70 fabricantes, cada fabricante produz alguma quantidade de produto
* 1 centro de distribuição


### Estoque da loja

* Cada loja possui um estoque com 200 tipos de produtos, cada tipo de produto tem um PID
* Se o produto for do tipo A, a loja começa com 100 unidades em estoque
* Se o produto for do tipo B, a loja começa com 60 unidades em estoque
* Se o produto for do tipo C, a loja começa com 20 unidades em estoque
* A quantidade de classicação dos produtos é do jeito que escolhermos, Sugestão: 1/3 produto A, 1/3 produto B, 1/3 produto C
* Tamanho máximo do estoque: Escolher

### Cores do estoque (para cada produto)
* [100%, 50%] Verde
* [50%, 25%] Amarelo
* [25%, 0%] Vermelho

### Ações do estoque (para cada produto)
* Se a quantidade do produto for:
* Verde: OK
* Amarelo: OK
* Vermelho: Enviar mensagem no tópico reposição para que o centro de distribuição envie produtos para o estoque, completando o estoque
