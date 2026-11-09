"""Testes de INTEGRAÇÃO do model de cupcake com o PostgreSQL (US03, US04, US05)."""
from decimal import Decimal

from app.models import cupcake_model


def test_listar_ativos_traz_os_seis_do_seed(app):
    with app.app_context():
        nomes = [c["nome"] for c in cupcake_model.listar_ativos()]
    assert len(nomes) == 6
    assert nomes == sorted(nomes)  # ordem alfabética


def test_cupcake_inativo_nao_aparece_no_catalogo(app, sql):  # RN04
    sql("UPDATE cupcake SET ativo = FALSE WHERE nome = 'Red Velvet'")
    with app.app_context():
        nomes = [c["nome"] for c in cupcake_model.listar_ativos()]
    assert "Red Velvet" not in nomes
    assert len(nomes) == 5


def test_filtrar_por_categoria(app):  # US04
    with app.app_context():
        recheados = cupcake_model.listar_ativos(categoria_id=2)
    assert {c["nome"] for c in recheados} == {"Brigadeiro Belga", "Ninho com Morango"}
    assert all(c["categoria"] == "Recheados" for c in recheados)


def test_busca_ignora_maiusculas_e_minusculas(app):  # US04
    with app.app_context():
        resultado = cupcake_model.listar_ativos(termo="VELVET")
    assert [c["nome"] for c in resultado] == ["Red Velvet"]


def test_busca_com_caractere_especial_nao_traz_tudo(app):
    """Um % digitado deve ser tratado como texto, e não como 'qualquer coisa' do SQL."""
    with app.app_context():
        assert cupcake_model.listar_ativos(termo="%") == []
        assert cupcake_model.listar_ativos(termo="_") == []


def test_busca_e_categoria_juntas(app):
    with app.app_context():
        assert cupcake_model.listar_ativos(categoria_id=1, termo="limão")[0]["nome"] == "Limão Siciliano"
        assert cupcake_model.listar_ativos(categoria_id=2, termo="limão") == []


def test_detalhe_traz_ingredientes_e_alergenicos(app):  # US05
    with app.app_context():
        c = cupcake_model.buscar_ativo_por_id(1)
    assert c["nome"] == "Red Velvet"
    assert c["preco"] == Decimal("12.90")
    assert c["foto_url"] and c["descricao"]  # RN01
    assert c["tamanho_rotulo"] == "Tradicional"
    assert {"Leite", "Ovos", "Farinha de trigo", "Cream cheese"} == set(c["alergenicos"])
    assert len(c["ingredientes"]) == 6
    # Os alergênicos vêm primeiro na lista, para chamar a atenção
    assert c["ingredientes"][0]["alergenico"] is True


def test_detalhe_de_cupcake_inexistente_ou_inativo_devolve_none(app, sql):
    sql("UPDATE cupcake SET ativo = FALSE WHERE id = 2")
    with app.app_context():
        assert cupcake_model.buscar_ativo_por_id(999) is None
        assert cupcake_model.buscar_ativo_por_id(2) is None


def test_buscar_ativos_por_ids(app, sql):
    sql("UPDATE cupcake SET ativo = FALSE WHERE id = 3")
    with app.app_context():
        encontrados = cupcake_model.buscar_ativos_por_ids([1, 3, 999])
        assert set(encontrados) == {1}
        assert cupcake_model.buscar_ativos_por_ids([]) == {}
