"""Catálogo de mensagens do sistema.

Os códigos e textos são os mesmos do documento
docs/etapa1-planejamento/03-ihc-interface.md (seção 3.4), para manter
a rastreabilidade entre o planejamento e o código.
"""

MENSAGENS = {
    "MSG01": "Preencha este campo.",
    "MSG02": "Digite um e-mail válido, como nome@exemplo.com.",
    "MSG03": "Este e-mail já tem cadastro. Quer entrar na sua conta?",
    "MSG04": "A senha precisa ter pelo menos 8 caracteres.",
    "MSG05": "E-mail ou senha incorretos. Confira e tente de novo.",
    "MSG06": "CEP inválido. Digite os 8 números do seu CEP.",
    "MSG07": "Informe rua, número, bairro e cidade para a entrega.",
    "MSG08": "Para salvar, adicione uma foto e uma descrição do cupcake.",
    "MSG09": "O preço deve ser maior que R$ 0,00.",
    "MSG10": "Nossos cupcakes estão saindo do forno! Volte daqui a pouco.",
    "MSG11": 'Não encontramos cupcakes com "{termo}". Tente outro nome ou veja todas as categorias.',
    "MSG12": "Este cupcake não está mais disponível.",
    "MSG13": "O máximo é 20 unidades por sabor. Para encomendas maiores, fale com a loja.",
    "MSG14": "Seu carrinho está vazio. Que tal escolher um cupcake?",
    "MSG15": "O cupcake {nome} acabou de sair do cardápio e foi retirado do seu carrinho.",
    "MSG16": "Não é possível mudar de {atual} para {novo}.",
    "MSG17": "Você não tem permissão para acessar esta página.",
    "MSG18": "Cancelar o pedido nº {id}? Esta ação não pode ser desfeita.",
    "MSG19": "{nome} removido do carrinho.",
    "MSG20": "{qtd}× {nome} adicionado ao carrinho.",
    "MSG21": "Pedido nº {id} recebido! Você pode acompanhar em Meus pedidos.",
    "MSG22": "Cupcake salvo com sucesso.",
    "MSG23": "Digite um telefone com DDD, como (11) 99999-9999.",
    "MSG24": "O preço promocional deve ser menor que o preço normal.",
    "MSG99": "Algo deu errado do nosso lado. Tente novamente em instantes.",
}


def msg(codigo, **valores):
    """Devolve o texto da mensagem já preenchido. Ex.: msg("MSG20", qtd=2, nome="Red Velvet")"""
    return MENSAGENS[codigo].format(**valores)
