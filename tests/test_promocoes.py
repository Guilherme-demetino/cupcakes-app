"""Testes das promoções (US12 / RN12) – incluídas na Etapa 3 a partir da sugestão C01 do avaliador 1.
Seed: Limão Siciliano de R$ 11,90 por R$ 9,90 (-17%) e Cenoura Vegano de R$ 13,50 por R$ 11,50 (-15%)."""
from decimal import Decimal

import psycopg
import pytest

from app.db import executar_migracoes
from app.models import cupcake_model as cm

LIMAO, CENOURA, RED_VELVET = 3, 4, 1


def html(resposta):
    return resposta.get_data(as_text=True)


def consultar(banco, sql, params=None):
    with psycopg.connect(banco) as conexao:
        return conexao.execute(sql, params).fetchall()


# ================= Validação do preço promocional (unitário) =================

def _dados(**mudancas):
    base = {"nome": "Pistache", "descricao": "Gostoso", "preco": "11,90", "preco_promocional": "",
            "tamanho": "TRADICIONAL", "peso_gramas": "95", "categoria_id": 1, "ingrediente_ids": [1]}
    return {**base, **mudancas}


def validar(dados):
    return cm.validar_cupcake(dados, True, categorias_validas=[1, 2, 3, 4], ingredientes_validos=range(1, 19))


def test_sem_promocao_e_valido():
    dados = _dados()
    assert validar(dados) == {}
    assert dados["promocao_decimal"] is None


def test_promocao_menor_que_o_preco_e_aceita():
    dados = _dados(preco_promocional="9,90")
    assert validar(dados) == {}
    assert dados["promocao_decimal"] == Decimal("9.90")


@pytest.mark.parametrize("promocao", ["11,90", "12,00", "99"])
def test_promocao_igual_ou_maior_que_o_preco_mostra_msg24(promocao):  # RN12
    assert validar(_dados(preco_promocional=promocao))["preco_promocional"] == \
        "O preço promocional deve ser menor que o preço normal."


@pytest.mark.parametrize("promocao", ["0", "-1", "abc"])
def test_promocao_invalida(promocao):
    assert "preco_promocional" in validar(_dados(preco_promocional=promocao))


# ================= Banco e model (integração) =================

def test_banco_tambem_recusa_promocao_maior_que_o_preco(sql):  # segunda camada (CHECK)
    with pytest.raises(psycopg.Error):
        sql("UPDATE cupcake SET preco_promocional = 20.00 WHERE id = 3")


def test_preco_de_venda_e_o_promocional(app):
    with app.app_context():
        limao = cm.buscar_ativo_por_id(LIMAO)
        red = cm.buscar_ativo_por_id(RED_VELVET)
    assert (limao["preco"], limao["preco_cheio"]) == (Decimal("9.90"), Decimal("11.90"))
    assert (red["preco"], red["preco_cheio"], red["preco_promocional"]) == (Decimal("12.90"), Decimal("12.90"), None)


def test_filtro_so_promocoes(app):
    with app.app_context():
        nomes = [c["nome"] for c in cm.listar_ativos(so_promocoes=True)]
        assert nomes == ["Cenoura Vegano", "Limão Siciliano"]
        assert [c["nome"] for c in cm.listar_ativos(categoria_id=1, so_promocoes=True)] == ["Limão Siciliano"]


# ================= Telas do cliente =================

def test_catalogo_tem_filtro_e_selo_de_promocao(client):
    pagina = html(client.get("/"))
    assert "Promoções</a>" in pagina
    assert "-17%" in pagina and "-15%" in pagina          # selos
    assert "R$ 11,90</s>" in pagina and "R$ 9,90" in pagina  # preço riscado e preço de venda


def test_pagina_de_promocoes(client):
    pagina = html(client.get("/?promocoes=1"))
    assert "Limão Siciliano" in pagina and "Cenoura Vegano" in pagina
    assert "Red Velvet" not in pagina


def test_sem_promocoes_mostra_aviso(client, sql):
    sql("UPDATE cupcake SET preco_promocional = NULL")
    assert "Nenhuma promoção no momento" in html(client.get("/?promocoes=1"))


def test_detalhe_mostra_economia(client):
    pagina = html(client.get(f"/cupcakes/{LIMAO}"))
    assert "economize R$ 2,00 por unidade" in pagina
    assert 'data-preco="9.90"' in pagina  # o total do botão usa o preço promocional


def test_carrinho_usa_preco_promocional(client):  # RN06 + RN12
    client.post("/carrinho/adicionar", data={"cupcake_id": LIMAO, "quantidade": 2})
    pagina = html(client.get("/carrinho"))
    assert "R$ 19,80" in pagina   # 2 × 9,90
    assert "R$ 27,80" in pagina   # + 8,00 de entrega


def test_pedido_congela_o_preco_promocional(client, sql, banco):  # RN05 + RN12
    client.post("/login", data={"email": "mariana@email.com", "senha": "Cupcake@123"})
    client.post("/carrinho/adicionar", data={"cupcake_id": LIMAO, "quantidade": 1})
    client.post("/checkout", data={"cep": "01001000", "logradouro": "Rua A", "numero": "1", "complemento": "",
                                   "bairro": "Centro", "cidade": "São Paulo", "uf": "SP",
                                   "forma_pagamento": "PIX", "observacao": ""})
    sql("UPDATE cupcake SET preco_promocional = NULL WHERE id = 3")  # a promoção acabou
    (preco, total), = consultar(banco, """SELECT i.preco_unitario, p.valor_total FROM pedido p
                                          JOIN item_pedido i ON i.pedido_id = p.id WHERE p.id = 3""")
    assert preco == Decimal("9.90") and total == Decimal("17.90")


# ================= Administrador =================

NOVO = {"nome": "Red Velvet", "categoria_id": "1", "descricao": "Massa aveludada.", "preco": "12,90",
        "peso_gramas": "90", "tamanho": "TRADICIONAL", "ingredientes": ["1", "3"]}


def entrar_admin(client):
    client.post("/login", data={"email": "admin@cupcakeapp.com.br", "senha": "Admin@2026"})


def test_admin_coloca_e_tira_promocao(client, banco):
    entrar_admin(client)
    client.post(f"/admin/cupcakes/{RED_VELVET}/editar", data={**NOVO, "preco_promocional": "10,90"},
                content_type="multipart/form-data")
    assert consultar(banco, "SELECT preco_promocional FROM cupcake WHERE id = 1")[0][0] == Decimal("10.90")
    assert "Red Velvet" in html(client.get("/?promocoes=1"))
    assert "🏷️ R$ 10,90 <s>R$ 12,90</s>" in html(client.get("/admin/cupcakes"))

    client.post(f"/admin/cupcakes/{RED_VELVET}/editar", data={**NOVO, "preco_promocional": ""},
                content_type="multipart/form-data")
    assert consultar(banco, "SELECT preco_promocional FROM cupcake WHERE id = 1")[0][0] is None
    assert "Red Velvet" not in html(client.get("/?promocoes=1"))


def test_admin_promocao_maior_mostra_msg24_e_nao_grava(client, banco):
    entrar_admin(client)
    resposta = client.post(f"/admin/cupcakes/{RED_VELVET}/editar", data={**NOVO, "preco_promocional": "15,00"},
                           content_type="multipart/form-data")
    assert resposta.status_code == 422
    assert "O preço promocional deve ser menor que o preço normal." in html(resposta)
    assert consultar(banco, "SELECT preco_promocional FROM cupcake WHERE id = 1")[0][0] is None


def test_formulario_de_edicao_mostra_a_promocao_atual(client):
    entrar_admin(client)
    assert 'name="preco_promocional" type="text" value="9.90"' in html(client.get(f"/admin/cupcakes/{LIMAO}/editar"))


# ================= Migração (banco que já existia antes das promoções) =================

def _voltar_ao_banco_antigo(sql):
    """Deixa o banco como estava antes da Etapa 3 (igual ao que está publicado no Render)."""
    sql("ALTER TABLE cupcake DROP CONSTRAINT ck_cupcake_promocao")
    sql("ALTER TABLE cupcake DROP COLUMN preco_promocional")
    sql("DROP TABLE migracao")


def test_migracao_acrescenta_promocoes_sem_apagar_dados(sql, banco):
    _voltar_ao_banco_antigo(sql)
    pedidos_antes = consultar(banco, "SELECT count(*) FROM pedido")[0][0]

    assert executar_migracoes(banco) == ["001_promocoes.sql"]
    assert consultar(banco, "SELECT preco_promocional FROM cupcake WHERE id = 3")[0][0] == Decimal("9.90")
    assert consultar(banco, "SELECT count(*) FROM pedido")[0][0] == pedidos_antes  # nada foi apagado
    with pytest.raises(psycopg.Error):  # a regra RN12 também passa a valer no banco antigo
        sql("UPDATE cupcake SET preco_promocional = 50 WHERE id = 1")


def test_migracao_roda_uma_vez_so(sql, banco):
    _voltar_ao_banco_antigo(sql)
    executar_migracoes(banco)
    sql("UPDATE cupcake SET preco_promocional = NULL WHERE id = 3")  # admin tirou a promoção
    assert executar_migracoes(banco) == []                             # 2ª vez: nada a fazer
    assert consultar(banco, "SELECT preco_promocional FROM cupcake WHERE id = 3")[0][0] is None


def test_init_db_se_vazio_aplica_a_migracao(app, sql):
    """É o comando que o Render roda a cada publicação."""
    _voltar_ao_banco_antigo(sql)
    resultado = app.test_cli_runner().invoke(args=["init-db", "--se-vazio"])
    assert "nada foi apagado" in resultado.output
    assert "Migrações aplicadas: 001_promocoes.sql" in resultado.output
