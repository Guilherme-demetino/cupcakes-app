"""Testes UNITÁRIOS da classe Carrinho (não precisam de banco).
Regras verificadas: RN03 (1 a 20 unidades), RN04 (inativos saem), RN06 (cálculo do total)."""
from decimal import Decimal

import pytest

from app.models.carrinho import QTD_MAX, TAXA_ENTREGA, Carrinho

RED_VELVET = {"id": 1, "nome": "Red Velvet", "preco": Decimal("12.90")}
BRIGADEIRO = {"id": 2, "nome": "Brigadeiro Belga", "preco": Decimal("14.50")}
CATALOGO = {1: RED_VELVET, 2: BRIGADEIRO}


def test_carrinho_novo_esta_vazio():
    carrinho = Carrinho()
    assert carrinho.vazio
    assert carrinho.quantidade_total == 0


def test_adicionar_item_novo():
    carrinho = Carrinho()
    limitado = carrinho.adicionar(1, 2)
    assert carrinho.itens == {1: 2}
    assert limitado is False


def test_adicionar_mesmo_cupcake_soma_quantidade_sem_duplicar_linha():
    carrinho = Carrinho()
    carrinho.adicionar(1, 2)
    carrinho.adicionar(1, 3)
    assert carrinho.itens == {1: 5}
    assert len(carrinho.itens) == 1


def test_adicionar_acima_de_20_limita_e_avisa():  # RN03 / MSG13
    carrinho = Carrinho()
    carrinho.adicionar(1, 15)
    limitado = carrinho.adicionar(1, 10)
    assert carrinho.itens[1] == QTD_MAX
    assert limitado is True


@pytest.mark.parametrize("quantidade_invalida", [0, -3, "abc", None])
def test_adicionar_quantidade_invalida_gera_erro(quantidade_invalida):  # RN03
    with pytest.raises(ValueError):
        Carrinho().adicionar(1, quantidade_invalida)


def test_alterar_quantidade():
    carrinho = Carrinho({"1": 2})
    carrinho.alterar(1, 7)
    assert carrinho.itens[1] == 7


def test_alterar_para_zero_remove_o_item():
    carrinho = Carrinho({"1": 2, "2": 1})
    carrinho.alterar(1, 0)
    assert 1 not in carrinho.itens


def test_alterar_acima_de_20_limita():
    carrinho = Carrinho({"1": 20})
    assert carrinho.alterar(1, 21) is True
    assert carrinho.itens[1] == 20


def test_alterar_item_que_nao_esta_no_carrinho_nao_faz_nada():
    carrinho = Carrinho({"1": 2})
    carrinho.alterar(99, 5)
    assert carrinho.itens == {1: 2}


def test_remover_devolve_quantidade_para_o_desfazer():
    carrinho = Carrinho({"1": 4})
    assert carrinho.remover(1) == 4
    assert carrinho.vazio
    assert carrinho.remover(1) == 0  # remover de novo não dá erro


def test_resumo_calcula_subtotais_taxa_e_total():  # RN06
    carrinho = Carrinho({"1": 2, "2": 1})
    resumo = carrinho.resumo(CATALOGO)
    # 2 × 12,90 = 25,80 ; 1 × 14,50 = 14,50 ; subtotal 40,30 ; + 8,00 de entrega = 48,30
    assert [linha["subtotal"] for linha in resumo["linhas"]] == [Decimal("25.80"), Decimal("14.50")]
    assert resumo["subtotal"] == Decimal("40.30")
    assert resumo["taxa_entrega"] == TAXA_ENTREGA == Decimal("8.00")
    assert resumo["total"] == Decimal("48.30")


def test_resumo_de_carrinho_vazio_nao_cobra_entrega():
    resumo = Carrinho().resumo(CATALOGO)
    assert resumo["total"] == Decimal("0.00")
    assert resumo["taxa_entrega"] == Decimal("0.00")


def test_resumo_retira_cupcake_inativo_do_carrinho():  # RN04 / MSG15
    carrinho = Carrinho({"1": 2, "3": 1})  # o cupcake 3 não está entre os ativos
    resumo = carrinho.resumo(CATALOGO)
    assert resumo["removidos"] == [3]
    assert 3 not in carrinho.itens
    assert resumo["total"] == Decimal("33.80")


def test_conversao_para_sessao_e_de_volta():
    carrinho = Carrinho()
    carrinho.adicionar(2, 3)
    dados = carrinho.para_sessao()
    assert dados == {"2": 3}
    assert Carrinho(dados).itens == {2: 3}
