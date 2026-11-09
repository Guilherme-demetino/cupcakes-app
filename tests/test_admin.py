"""Testes da área administrativa: manter cupcakes (US10) e gerenciar pedidos (US11)."""
import io
import re
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest

from app.models import cupcake_model as cm

FOTO_WEBP = (Path(__file__).resolve().parent.parent / "app/static/img/cupcakes/red-velvet.webp").read_bytes()

NOVO = {"nome": "Pistache", "categoria_id": "1", "descricao": "Massa de pistache com ganache branca.",
        "preco": "16,90", "peso_gramas": "95", "tamanho": "TRADICIONAL", "ingredientes": ["1", "2"]}


def html(resposta):
    return resposta.get_data(as_text=True)


def entrar_admin(client):
    return client.post("/login", data={"email": "admin@cupcakeapp.com.br", "senha": "Admin@2026"})


def entrar_cliente(client):
    client.post("/login", data={"email": "mariana@email.com", "senha": "Cupcake@123"})


def enviar_cupcake(client, url="/admin/cupcakes/novo", foto=FOTO_WEBP, nome_arquivo="foto.webp", **mudancas):
    dados = {**NOVO, **mudancas}
    if foto is not None:
        dados["foto"] = (io.BytesIO(foto), nome_arquivo)
    return client.post(url, data=dados, content_type="multipart/form-data")


def consultar(banco, sql, params=None):
    with psycopg.connect(banco) as conexao:
        return conexao.execute(sql, params).fetchall()


# ================= Validação do cupcake (unitário) =================

def _dados(**mudancas):
    base = {"nome": "Pistache", "descricao": "Gostoso", "preco": "16,90", "tamanho": "TRADICIONAL",
            "peso_gramas": "95", "categoria_id": 1, "ingrediente_ids": [1, 2]}
    return {**base, **mudancas}


def validar(dados, tem_foto=True):
    return cm.validar_cupcake(dados, tem_foto, categorias_validas=[1, 2, 3, 4], ingredientes_validos=range(1, 19))


def test_cupcake_valido():
    dados = _dados()
    assert validar(dados) == {}
    assert dados["preco_decimal"] == Decimal("16.90")


def test_sem_foto_ou_sem_descricao_mostra_msg08():  # RN01
    assert validar(_dados(), tem_foto=False)["foto"] == "Para salvar, adicione uma foto e uma descrição do cupcake."
    assert validar(_dados(descricao=""))["descricao"].startswith("Para salvar")


@pytest.mark.parametrize("preco,valido", [("16,90", True), ("16.90", True), ("1.234,50", True), ("0,01", True),
                                          ("0", False), ("-5", False), ("abc", False), ("", False), ("NaN", False)])
def test_preco_maior_que_zero_msg09(preco, valido):  # RN02
    erros = validar(_dados(preco=preco))
    assert ("preco" not in erros) is valido
    if not valido:
        assert erros["preco"] == "O preço deve ser maior que R$ 0,00."


def test_preco_com_milhar_e_virgula():
    dados = _dados(preco="1.234,50")
    validar(dados)
    assert dados["preco_decimal"] == Decimal("1234.50")


@pytest.mark.parametrize("campo,valor", [("peso_gramas", "5"), ("peso_gramas", "abc"), ("tamanho", "ENORME"),
                                         ("categoria_id", 99), ("categoria_id", None), ("ingrediente_ids", []),
                                         ("ingrediente_ids", [1, 999]), ("nome", ""), ("nome", "x" * 81)])
def test_campos_invalidos(campo, valor):
    chave = "ingredientes" if campo == "ingrediente_ids" else campo
    assert chave in validar(_dados(**{campo: valor}))


# ================= Controle de acesso (RNF06) =================

ROTAS_ADMIN = ["/admin", "/admin/cupcakes", "/admin/cupcakes/novo", "/admin/cupcakes/1/editar",
               "/admin/pedidos", "/admin/pedidos/1"]


@pytest.mark.parametrize("rota", ROTAS_ADMIN)
def test_visitante_vai_para_o_login(client, rota):
    assert client.get(rota).headers["Location"].startswith("/login?next=")


@pytest.mark.parametrize("rota", ROTAS_ADMIN)
def test_cliente_recebe_msg17(client, rota):
    entrar_cliente(client)
    resposta = client.get(rota)
    assert resposta.status_code == 403
    assert "Você não tem permissão para acessar esta página." in html(resposta)


def test_cliente_nao_consegue_mudar_status_nem_cadastrar(client, banco):
    entrar_cliente(client)
    assert client.post("/admin/pedidos/2/status", data={"atual": "RECEBIDO", "novo": "EM_PREPARO"}).status_code == 403
    assert enviar_cupcake(client).status_code == 403
    assert consultar(banco, "SELECT status FROM pedido WHERE id = 2")[0][0] == "RECEBIDO"


def test_admin_entra_direto_nos_pedidos(client):
    assert entrar_admin(client).headers["Location"] == "/admin/pedidos"
    pagina = html(client.get("/admin/pedidos"))
    assert ">Cupcakes</a>" in pagina and ">Ver loja</a>" in pagina  # menu do administrador


# ================= US10 – Manter cupcakes =================

def test_lista_mostra_ativos_e_inativos(client, sql):
    sql("UPDATE cupcake SET ativo = FALSE WHERE id = 3")
    entrar_admin(client)
    pagina = html(client.get("/admin/cupcakes"))
    assert "Limão Siciliano" in pagina and "Fora do cardápio" in pagina
    assert "vendido em 1 pedido" in pagina  # Red Velvet aparece em 1 pedido do seed


def test_cadastrar_cupcake_completo(client, app, banco):
    entrar_admin(client)
    resposta = enviar_cupcake(client)
    assert resposta.status_code == 302
    assert "Cupcake salvo com sucesso." in html(client.get(resposta.headers["Location"]))  # MSG22

    (cid, preco, foto), = consultar(banco, "SELECT id, preco, foto_url FROM cupcake WHERE nome = 'Pistache'")
    assert preco == Decimal("16.90")
    assert re.fullmatch(r"/static/img/cupcakes/[0-9a-f]{32}\.webp", foto)  # nome gerado pelo sistema
    assert (Path(app.config["UPLOAD_FOLDER"]) / foto.rsplit("/", 1)[1]).read_bytes() == FOTO_WEBP

    detalhe = html(client.get(f"/cupcakes/{cid}"))  # já aparece para os clientes
    assert "Pistache" in detalhe and "R$ 16,90" in detalhe and "Farinha de trigo" in detalhe


def test_cadastrar_sem_foto_mostra_msg08_e_nao_grava(client, banco):  # RN01
    entrar_admin(client)
    resposta = enviar_cupcake(client, foto=None)
    assert resposta.status_code == 422
    assert "Para salvar, adicione uma foto e uma descrição do cupcake." in html(resposta)
    assert 'value="Pistache"' in html(resposta)  # mantém o que foi digitado
    assert consultar(banco, "SELECT count(*) FROM cupcake WHERE nome = 'Pistache'")[0][0] == 0


def test_arquivo_que_nao_e_imagem_e_recusado(client, banco):
    entrar_admin(client)
    resposta = enviar_cupcake(client, foto=b"<?php echo 'invasao'; ?>", nome_arquivo="foto.webp")
    assert "Envie uma imagem WebP, JPG ou PNG." in html(resposta)
    assert consultar(banco, "SELECT count(*) FROM cupcake WHERE nome = 'Pistache'")[0][0] == 0


def test_foto_acima_de_200kb_e_recusada(client):  # RNF01
    entrar_admin(client)
    grande = FOTO_WEBP[:12] + b"0" * (201 * 1024)
    assert "no máximo 200 KB" in html(enviar_cupcake(client, foto=grande))


def test_nome_repetido(client):
    entrar_admin(client)
    assert "Já existe um cupcake com esse nome." in html(enviar_cupcake(client, nome="Red Velvet"))


def test_editar_sem_enviar_foto_mantem_a_atual(client, banco):
    entrar_admin(client)
    pagina = html(client.get("/admin/cupcakes/1/editar"))
    assert 'value="Red Velvet"' in pagina and "Envie um arquivo só se quiser trocar a foto." in pagina
    resposta = enviar_cupcake(client, url="/admin/cupcakes/1/editar", foto=None,
                              nome="Red Velvet", preco="13,50", ingredientes=["3", "10"])
    assert resposta.status_code == 302
    (preco, foto), = consultar(banco, "SELECT preco, foto_url FROM cupcake WHERE id = 1")
    assert preco == Decimal("13.50") and foto == "/static/img/cupcakes/red-velvet.webp"
    ingredientes = consultar(banco, "SELECT ingrediente_id FROM cupcake_ingrediente WHERE cupcake_id = 1 ORDER BY 1")
    assert [linha[0] for linha in ingredientes] == [3, 10]
    # RN05: o pedido antigo continua com o preço pago
    assert consultar(banco, "SELECT preco_unitario FROM item_pedido WHERE pedido_id = 1")[0][0] == Decimal("12.90")


def test_editar_cupcake_inexistente(client):
    entrar_admin(client)
    assert client.get("/admin/cupcakes/999/editar").status_code == 404


def test_tirar_e_voltar_ao_cardapio(client):  # RN04 / RN11
    entrar_admin(client)
    pagina = html(client.post("/admin/cupcakes/1/ativo", follow_redirects=True))
    assert "Red Velvet saiu do cardápio." in pagina
    assert "Red Velvet" not in html(client.get("/"))
    assert client.get("/cupcakes/1").status_code == 404
    assert "Red Velvet voltou ao cardápio." in html(client.post("/admin/cupcakes/1/ativo", follow_redirects=True))
    assert "Red Velvet" in html(client.get("/"))


# ================= US11 – Gerenciar pedidos =================

def mudar(client, pedido_id, atual, novo, **extra):
    return client.post(f"/admin/pedidos/{pedido_id}/status", data={"atual": atual, "novo": novo, **extra},
                       follow_redirects=True)


def test_lista_de_pedidos_com_filtro(client):
    entrar_admin(client)
    pagina = html(client.get("/admin/pedidos"))
    assert "Nº 1 • Mariana Souza" in pagina and "Nº 2 • Mariana Souza" in pagina
    assert pagina.index("Nº 2 •") < pagina.index("Nº 1 •")  # em andamento antes de entregue
    filtrada = html(client.get("/admin/pedidos?status=ENTREGUE"))
    assert "Nº 1 •" in filtrada and "Nº 2 •" not in filtrada
    assert "Nenhum pedido" in html(client.get("/admin/pedidos?status=CANCELADO"))


def test_detalhe_do_pedido_mostra_cliente_e_acoes(client):
    entrar_admin(client)
    pagina = html(client.get("/admin/pedidos/2"))
    for esperado in ["Mariana Souza", "(11) 98888-7777", "Troco para R$ 50,00", "Dinheiro",
                     "Iniciar preparo → Em preparo", "Cancelar pedido"]:
        assert esperado in pagina


def test_ciclo_completo_ate_a_entrega(client):
    entrar_admin(client)
    assert "Pedido nº 2: Em preparo." in html(mudar(client, 2, "RECEBIDO", "EM_PREPARO"))
    mudar(client, 2, "EM_PREPARO", "SAIU_PARA_ENTREGA")
    pagina = html(mudar(client, 2, "SAIU_PARA_ENTREGA", "ENTREGUE"))
    assert "Pedido nº 2: Entregue." in pagina
    assert "Cancelar pedido" not in pagina  # pedido entregue não tem mais ações
    # O cliente vê a linha do tempo completa
    client.post("/logout")
    entrar_cliente(client)
    cliente = html(client.get("/pedidos/2"))
    assert cliente.count('class="feito') == 4        # as 4 etapas concluídas
    assert 'status-ENTREGUE">Entregue' in cliente


def test_nao_pula_etapas_msg16(client, banco):  # RN07
    entrar_admin(client)
    pagina = html(mudar(client, 2, "RECEBIDO", "ENTREGUE"))
    assert "Não é possível mudar de Recebido para Entregue." in pagina
    assert consultar(banco, "SELECT status FROM pedido WHERE id = 2")[0][0] == "RECEBIDO"


def test_dois_funcionarios_ao_mesmo_tempo(client, sql, banco):
    """Se outra pessoa já mudou o status, a tela desatualizada não sobrescreve."""
    sql("UPDATE pedido SET status = 'EM_PREPARO' WHERE id = 2")
    entrar_admin(client)
    pagina = html(mudar(client, 2, "RECEBIDO", "EM_PREPARO"))  # botão de uma tela antiga
    assert "Este pedido foi atualizado por outra pessoa e agora está &#34;Em preparo&#34;" in pagina
    assert consultar(banco, "SELECT count(*) FROM historico_status WHERE pedido_id = 2")[0][0] == 2


def test_admin_cancela_em_preparo_mas_nao_depois_de_despachar(client, sql, banco):
    sql("UPDATE pedido SET status = 'EM_PREPARO' WHERE id = 2")
    entrar_admin(client)
    assert "Pedido nº 2: Cancelado." in html(mudar(client, 2, "EM_PREPARO", "CANCELADO"))
    assert consultar(banco, "SELECT status FROM pedido WHERE id = 2")[0][0] == "CANCELADO"


def test_gatilho_do_banco_tambem_protege(sql):
    """Segunda camada: mesmo um UPDATE direto no banco não pula etapas (RN07)."""
    with pytest.raises(psycopg.Error):
        sql("UPDATE pedido SET status = 'ENTREGUE' WHERE id = 2")


def test_nao_cancela_pedido_que_saiu_para_entrega(client, sql, banco):
    sql("UPDATE pedido SET status = 'EM_PREPARO' WHERE id = 2")
    sql("UPDATE pedido SET status = 'SAIU_PARA_ENTREGA' WHERE id = 2")
    entrar_admin(client)
    assert "Cancelar pedido" not in html(client.get("/admin/pedidos/2"))
    assert "Não é possível mudar" in html(mudar(client, 2, "SAIU_PARA_ENTREGA", "CANCELADO"))


def test_botao_rapido_da_lista_volta_para_a_lista(client):
    entrar_admin(client)
    resposta = client.post("/admin/pedidos/2/status", data={"atual": "RECEBIDO", "novo": "EM_PREPARO",
                                                            "voltar": "lista", "filtro": "RECEBIDO"})
    assert resposta.headers["Location"] == "/admin/pedidos?status=RECEBIDO"


def test_pedido_inexistente(client):
    entrar_admin(client)
    assert client.get("/admin/pedidos/999").status_code == 404
    assert client.post("/admin/pedidos/999/status", data={"atual": "RECEBIDO", "novo": "EM_PREPARO"}).status_code == 404


def test_pedido_do_cliente_aparece_para_o_admin(client):
    """Integração das sprints: cliente compra -> loja recebe."""
    entrar_cliente(client)
    client.post("/carrinho/adicionar", data={"cupcake_id": 6, "quantidade": 4})
    client.post("/checkout", data={"cep": "01001000", "logradouro": "Rua A", "numero": "1", "complemento": "",
                                   "bairro": "Centro", "cidade": "São Paulo", "uf": "SP",
                                   "forma_pagamento": "CARTAO", "observacao": "Sem pressa"})
    client.post("/logout")
    entrar_admin(client)
    pagina = html(client.get("/admin/pedidos/3"))
    assert "4×</strong> Cacau Zero" in pagina and "Sem pressa" in pagina and "R$ 63,60" in pagina
