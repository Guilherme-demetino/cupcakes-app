"""Testes do model de pedido: regras puras (unitário) e gravação no banco (integração)."""
from decimal import Decimal

import psycopg
import pytest

from app.models import pedido_model as pm
from app.models.carrinho import Carrinho
from app.models import cupcake_model

ENDERECO = {"cep": "01001000", "logradouro": "Praça da Sé", "numero": "100", "complemento": "",
            "bairro": "Sé", "cidade": "São Paulo", "uf": "SP"}
MARIANA = 2  # id da cliente no seed.sql


# ---------------- RN07: quem pode mudar o status (unitário) ----------------

@pytest.mark.parametrize("atual,novo,admin,esperado", [
    ("RECEBIDO", "CANCELADO", False, True),            # cliente cancela pedido recebido
    ("EM_PREPARO", "CANCELADO", False, False),         # cliente NÃO cancela em preparo
    ("RECEBIDO", "EM_PREPARO", False, False),          # cliente não muda status de produção
    ("EM_PREPARO", "CANCELADO", True, True),           # admin cancela em preparo
    ("RECEBIDO", "EM_PREPARO", True, True),
    ("EM_PREPARO", "SAIU_PARA_ENTREGA", True, True),
    ("SAIU_PARA_ENTREGA", "ENTREGUE", True, True),
    ("RECEBIDO", "ENTREGUE", True, False),             # não pula etapas
    ("SAIU_PARA_ENTREGA", "CANCELADO", True, False),
    ("ENTREGUE", "RECEBIDO", True, False),             # não volta
    ("CANCELADO", "RECEBIDO", True, False),
])
def test_pode_mudar_status(atual, novo, admin, esperado):
    assert pm.pode_mudar_status(atual, novo, por_admin=admin) is esperado


# ---------------- Validação do checkout (unitário) ----------------

def test_checkout_valido():
    assert pm.validar_checkout(ENDERECO, "PIX", "") == {}


def test_limpar_endereco_formata_cep_e_uf():
    dados = pm.limpar_endereco({**ENDERECO, "cep": " 01001-000 ", "uf": "sp", "bairro": "  Sé "})
    assert dados["cep"] == "01001000" and dados["uf"] == "SP" and dados["bairro"] == "Sé"


@pytest.mark.parametrize("cep", ["", "123", "0100100", "010010000"])
def test_cep_invalido_mostra_msg06(cep):
    assert pm.validar_checkout({**ENDERECO, "cep": cep}, "PIX", "")["cep"].startswith("CEP inválido")


@pytest.mark.parametrize("campo", ["logradouro", "numero", "bairro", "cidade"])
def test_campo_obrigatorio_do_endereco_mostra_msg07(campo):
    erros = pm.validar_checkout({**ENDERECO, campo: ""}, "PIX", "")
    assert erros[campo] == "Informe rua, número, bairro e cidade para a entrega."


def test_uf_e_forma_de_pagamento_invalidas():
    erros = pm.validar_checkout({**ENDERECO, "uf": "XX"}, "BITCOIN", "")
    assert set(erros) == {"uf", "forma_pagamento"}


def test_observacao_muito_longa():
    assert "observacao" in pm.validar_checkout(ENDERECO, "PIX", "x" * 256)


# ---------------- Banco (integração) ----------------

def _resumo(itens):
    carrinho = Carrinho(itens)
    return carrinho.resumo(cupcake_model.buscar_ativos_por_ids(carrinho.itens.keys()))


def test_criar_pedido_grava_itens_total_e_historico(app, banco):  # RN05, RN06
    with app.app_context():
        pedido_id = pm.criar(MARIANA, ENDERECO, "CARTAO", "Sem cebola", _resumo({"1": 2, "2": 1}))
        pedido = pm.buscar_do_usuario(pedido_id, MARIANA)
    assert pedido["status"] == "RECEBIDO"
    assert pedido["valor_total"] == Decimal("48.30")         # 25,80 + 14,50 + 8,00
    assert pedido["taxa_entrega"] == Decimal("8.00")
    assert {(i["nome"], i["quantidade"], i["preco_unitario"]) for i in pedido["itens"]} == \
        {("Red Velvet", 2, Decimal("12.90")), ("Brigadeiro Belga", 1, Decimal("14.50"))}
    assert [h["status"] for h in pedido["historico"]] == ["RECEBIDO"]  # gravado pelo gatilho
    assert pedido["observacao"] == "Sem cebola"
    assert pedido["pode_cancelar"] is True


def test_preco_fica_congelado_no_pedido(app, sql):  # RN05
    with app.app_context():
        pedido_id = pm.criar(MARIANA, ENDERECO, "PIX", "", _resumo({"1": 1}))
    sql("UPDATE cupcake SET preco = 99.90 WHERE id = 1")
    with app.app_context():
        pedido = pm.buscar_do_usuario(pedido_id, MARIANA)
    assert pedido["itens"][0]["preco_unitario"] == Decimal("12.90")
    assert pedido["valor_total"] == Decimal("20.90")


def test_endereco_repetido_nao_e_duplicado(app, banco):
    with app.app_context():
        pm.criar(MARIANA, ENDERECO, "PIX", "", _resumo({"1": 1}))
        pm.criar(MARIANA, ENDERECO, "PIX", "", _resumo({"2": 1}))
    with psycopg.connect(banco) as conexao:
        qtd = conexao.execute("SELECT count(*) FROM endereco WHERE usuario_id = %s", (MARIANA,)).fetchone()[0]
    assert qtd == 2  # o do seed + o novo, usado pelos dois pedidos


def test_pedido_sem_itens_nao_e_criado(app):
    with app.app_context(), pytest.raises(ValueError):
        pm.criar(MARIANA, ENDERECO, "PIX", "", _resumo({}))


def test_ultimo_endereco_vem_do_pedido_mais_recente(app):
    with app.app_context():
        assert pm.ultimo_endereco(MARIANA)["logradouro"] == "Rua das Flores"   # do seed
        pm.criar(MARIANA, ENDERECO, "PIX", "", _resumo({"1": 1}))
        assert pm.ultimo_endereco(MARIANA)["logradouro"] == "Praça da Sé"
        assert pm.ultimo_endereco(1) is None  # admin não tem endereço


def test_listar_do_usuario_traz_mais_recente_primeiro(app):
    with app.app_context():
        novo = pm.criar(MARIANA, ENDERECO, "PIX", "", _resumo({"1": 3}))
        pedidos = pm.listar_do_usuario(MARIANA)
    assert [p["id"] for p in pedidos][0] == novo
    assert len(pedidos) == 3
    assert pedidos[0]["qtd_itens"] == 3


def test_cliente_nao_ve_pedido_de_outro(app):
    with app.app_context():
        assert pm.buscar_do_usuario(2, MARIANA) is not None
        assert pm.buscar_do_usuario(2, 1) is None


def test_cancelar_pedido_recebido(app):  # US09
    with app.app_context():
        pm.cancelar_pelo_cliente(2, MARIANA)
        pedido = pm.buscar_do_usuario(2, MARIANA)
    assert pedido["status"] == "CANCELADO"
    assert [h["status"] for h in pedido["historico"]] == ["RECEBIDO", "CANCELADO"]
    assert pedido["pode_cancelar"] is False


@pytest.mark.parametrize("pedido_id,usuario_id", [(1, MARIANA), (2, 1), (999, MARIANA)])
def test_nao_cancela_entregue_de_outro_ou_inexistente(app, pedido_id, usuario_id):
    with app.app_context(), pytest.raises(pm.PedidoNaoPodeSerCancelado):
        pm.cancelar_pelo_cliente(pedido_id, usuario_id)
