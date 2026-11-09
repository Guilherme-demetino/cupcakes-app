"""Testes das rotas de pedido: checkout (US07), meus pedidos (US08) e cancelamento (US09).
Cada teste corresponde a um critério de aceitação da Etapa 1."""
import re

import psycopg

ENDERECO = {"cep": "01001-000", "logradouro": "Praça da Sé", "numero": "100", "complemento": "Sala 3",
            "bairro": "Sé", "cidade": "São Paulo", "uf": "SP", "forma_pagamento": "PIX", "observacao": ""}


def html(resposta):
    return resposta.get_data(as_text=True)


def entrar(client, email="mariana@email.com", senha="Cupcake@123"):
    client.post("/login", data={"email": email, "senha": senha})


def adicionar(client, cupcake_id, quantidade):
    client.post("/carrinho/adicionar", data={"cupcake_id": cupcake_id, "quantidade": quantidade})


def finalizar(client, **mudancas):
    return client.post("/checkout", data={**ENDERECO, **mudancas})


def contar_pedidos(banco):
    with psycopg.connect(banco) as conexao:
        return conexao.execute("SELECT count(*) FROM pedido").fetchone()[0]


# ---------------- US07 – Finalizar pedido ----------------

def test_carrinho_tem_botao_finalizar(client):
    adicionar(client, 1, 1)
    assert 'href="/checkout"' in html(client.get("/carrinho"))


def test_checkout_sem_login_vai_para_login_e_volta(client):
    adicionar(client, 1, 2)
    resposta = client.get("/checkout")
    assert resposta.headers["Location"] == "/login?next=/checkout"
    resposta = client.post("/login", data={"email": "mariana@email.com", "senha": "Cupcake@123", "next": "/checkout"})
    assert resposta.headers["Location"] == "/checkout"
    assert "R$ 33,80" in html(client.get("/checkout"))  # carrinho preservado


def test_checkout_com_carrinho_vazio_volta_ao_carrinho(client):
    entrar(client)
    resposta = client.get("/checkout", follow_redirects=True)
    assert "Seu carrinho está vazio" in html(resposta)


def test_checkout_preenche_o_ultimo_endereco(client):
    entrar(client)
    adicionar(client, 1, 1)
    pagina = html(client.get("/checkout"))
    assert 'value="Rua das Flores"' in pagina and 'value="01001000"' in pagina


def test_finalizar_pedido_com_sucesso(client, banco):
    entrar(client)
    adicionar(client, 1, 2)
    adicionar(client, 2, 1)
    resposta = finalizar(client)
    assert resposta.status_code == 302
    pedido_id = int(re.search(r"/pedidos/(\d+)/confirmacao", resposta.headers["Location"]).group(1))

    pagina = html(client.get(resposta.headers["Location"]))
    assert f"Pedido nº {pedido_id} recebido!" in pagina                         # MSG21
    assert "Você pode acompanhar em Meus pedidos." in pagina
    assert "R$ 48,30" in pagina                                                  # RN06

    with client.session_transaction() as sessao:
        assert not sessao.get("carrinho")                                        # carrinho esvaziado
    with psycopg.connect(banco) as conexao:
        status, total = conexao.execute("SELECT status, valor_total FROM pedido WHERE id = %s",
                                        (pedido_id,)).fetchone()
    assert status == "RECEBIDO" and str(total) == "48.30"


def test_cep_invalido_mostra_msg06_e_nao_grava(client, banco):
    entrar(client)
    adicionar(client, 1, 1)
    antes = contar_pedidos(banco)
    resposta = finalizar(client, cep="123")
    assert resposta.status_code == 422
    assert "CEP inválido. Digite os 8 números do seu CEP." in html(resposta)
    assert 'value="Praça da Sé"' in html(resposta)  # o que foi digitado continua na tela
    assert contar_pedidos(banco) == antes


def test_endereco_incompleto_mostra_msg07(client):
    entrar(client)
    adicionar(client, 1, 1)
    pagina = html(finalizar(client, logradouro="", numero=""))
    assert pagina.count("Informe rua, número, bairro e cidade para a entrega.") == 2


def test_cupcake_desativado_durante_a_compra_mostra_msg15(client, sql, banco):
    entrar(client)
    adicionar(client, 1, 1)
    adicionar(client, 2, 1)
    sql("UPDATE cupcake SET ativo = FALSE WHERE id = 1")
    antes = contar_pedidos(banco)
    resposta = finalizar(client, )
    assert resposta.headers["Location"] == "/carrinho"
    pagina = html(client.get("/carrinho"))
    assert "O cupcake Red Velvet acabou de sair do cardápio" in pagina
    assert contar_pedidos(banco) == antes  # o cliente revisa antes de confirmar


def test_enviar_o_pedido_duas_vezes_nao_duplica(client, banco):
    entrar(client)
    adicionar(client, 1, 1)
    antes = contar_pedidos(banco)
    finalizar(client)
    finalizar(client)  # segundo envio: o carrinho já está vazio
    assert contar_pedidos(banco) == antes + 1


# ---------------- US08 – Meus pedidos ----------------

def test_meus_pedidos_exige_login(client):
    assert client.get("/pedidos").headers["Location"] == "/login?next=/pedidos"


def test_meus_pedidos_lista_do_mais_recente_para_o_mais_antigo(client):
    entrar(client)
    adicionar(client, 3, 1)
    novo = int(re.search(r"/pedidos/(\d+)", finalizar(client).headers["Location"]).group(1))
    pagina = html(client.get("/pedidos"))
    posicoes = [pagina.index(f"Pedido nº {n}<") for n in (novo, 2, 1)]
    assert posicoes == sorted(posicoes)
    assert "Entregue" in pagina and "Recebido" in pagina


def test_detalhe_mostra_itens_endereco_e_linha_do_tempo(client):
    entrar(client)
    pagina = html(client.get("/pedidos/1"))  # pedido ENTREGUE do seed
    for esperado in ["2× Red Velvet", "R$ 12,90 cada", "R$ 33,80", "Rua das Flores, 120", "PIX",
                     "Em preparo", "Saiu para entrega", 'aria-current="step"']:
        assert esperado in pagina
    assert "Cancelar pedido" not in pagina  # já entregue


def test_cliente_nao_ve_pedido_de_outro_cliente(client):
    client.post("/cadastro", data={"nome": "Outro Cliente", "email": "outro@email.com",
                                   "telefone": "11911112222", "senha": "senha12345"})
    assert client.get("/pedidos/1").status_code == 404
    assert "Pedido nº 1<" not in html(client.get("/pedidos"))
    assert client.post("/pedidos/2/cancelar").status_code == 404


def test_pedidos_vazio(client):
    client.post("/cadastro", data={"nome": "Nova Cliente", "email": "nova@email.com",
                                   "telefone": "11911112222", "senha": "senha12345"})
    assert "Você ainda não fez nenhum pedido." in html(client.get("/pedidos"))


# ---------------- US09 – Cancelar pedido ----------------

def test_cancelar_pede_confirmacao_msg18(client):
    entrar(client)
    assert "/pedidos/2/cancelar" in html(client.get("/pedidos/2"))  # pedido RECEBIDO do seed
    pagina = html(client.get("/pedidos/2/cancelar"))
    assert "Cancelar o pedido nº 2? Esta ação não pode ser desfeita." in pagina
    assert "Manter pedido" in pagina


def test_cancelar_pedido_recebido(client):
    entrar(client)
    pagina = html(client.post("/pedidos/2/cancelar", follow_redirects=True))
    assert "Pedido nº 2 cancelado." in pagina
    assert "Pedido cancelado" in pagina          # linha do tempo
    assert "/pedidos/2/cancelar" not in pagina   # botão some


def test_nao_cancela_pedido_em_preparo(client, sql):
    sql("UPDATE pedido SET status = 'EM_PREPARO' WHERE id = 2")
    entrar(client)
    assert "/pedidos/2/cancelar" not in html(client.get("/pedidos/2"))
    pagina = html(client.post("/pedidos/2/cancelar", follow_redirects=True))
    assert "não pode mais ser cancelado" in pagina
    assert "Em preparo" in pagina


def test_cancelar_nao_funciona_por_get(client):
    """O GET só mostra a pergunta; quem cancela é o POST."""
    entrar(client)
    client.get("/pedidos/2/cancelar")
    assert "Recebido" in html(client.get("/pedidos/2"))
