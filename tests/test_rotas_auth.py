"""Testes das rotas de cadastro, login, logout e "Minha conta" (US01, US02).
Cada teste corresponde a um critério de aceitação da Etapa 1."""
from flask import Blueprint

from app.auth import admin_obrigatorio, destino_seguro

NOVO = {"nome": "Ana Lima", "email": "ana@email.com", "telefone": "11987654321", "senha": "segredo123"}


def html(resposta):
    return resposta.get_data(as_text=True)


def logado_como(client):
    with client.session_transaction() as sessao:
        return sessao.get("usuario_nome")


def entrar(client, email="mariana@email.com", senha="Cupcake@123", **extra):
    return client.post("/login", data={"email": email, "senha": senha, **extra})


# ---------------- US01 – Cadastro ----------------

def test_cadastro_valido_cria_conta_e_ja_entra_logado(client):
    resposta = client.post("/cadastro", data=NOVO)
    assert resposta.status_code == 302
    assert logado_como(client) == "Ana Lima"
    assert "Boas-vindas, Ana" in html(client.get("/"))


def test_cadastro_com_email_existente_mostra_msg03(client):
    resposta = client.post("/cadastro", data={**NOVO, "email": "mariana@email.com"})
    assert resposta.status_code == 422
    assert "Este e-mail já tem cadastro. Quer entrar na sua conta?" in html(resposta)
    assert logado_como(client) is None


def test_cadastro_mostra_email_repetido_e_senha_curta_ao_mesmo_tempo(client):
    pagina = html(client.post("/cadastro", data={**NOVO, "email": "mariana@email.com", "senha": "123"}))
    assert "Este e-mail já tem cadastro" in pagina
    assert "A senha precisa ter pelo menos 8 caracteres." in pagina


def test_cadastro_com_senha_curta_mostra_msg04(client):
    resposta = client.post("/cadastro", data={**NOVO, "senha": "123"})
    assert "A senha precisa ter pelo menos 8 caracteres." in html(resposta)


def test_cadastro_com_erro_mantem_dados_mas_nunca_a_senha(client):
    pagina = html(client.post("/cadastro", data={**NOVO, "email": "invalido", "senha": "segredo123"}))
    assert 'value="Ana Lima"' in pagina
    assert "segredo123" not in pagina
    assert 'aria-invalid="true"' in pagina  # acessibilidade do erro


def test_cadastro_vazio_mostra_msg01_em_todos_os_campos(client):
    pagina = html(client.post("/cadastro", data={}))
    assert pagina.count("Preencha este campo.") == 4


def test_nome_com_html_e_exibido_como_texto(client):  # proteção XSS
    client.post("/cadastro", data={**NOVO, "nome": "<b>Ana</b> Lima"})
    pagina = html(client.get("/conta"))
    assert "<b>Ana</b>" not in pagina
    assert "&lt;b&gt;Ana&lt;/b&gt; Lima" in pagina


# ---------------- US02 – Login / logout ----------------

def test_login_correto_entra_e_volta_ao_catalogo(client):
    resposta = entrar(client)
    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/"
    assert logado_como(client) == "Mariana Souza"


def test_login_com_senha_errada_mostra_msg05(client):
    resposta = entrar(client, senha="errada123")
    assert resposta.status_code == 401
    assert "E-mail ou senha incorretos. Confira e tente de novo." in html(resposta)
    assert logado_como(client) is None


def test_login_nao_revela_se_o_email_existe(client):
    """E-mail inexistente e senha errada devem dar exatamente a mesma resposta."""
    a = html(entrar(client, email="ninguem@email.com", senha="qualquer1"))
    b = html(entrar(client, email="mariana@email.com", senha="qualquer1"))
    assert a.replace("ninguem@email.com", "X") == b.replace("mariana@email.com", "X")


def test_login_volta_para_a_pagina_de_origem(client):
    resposta = entrar(client, next="/carrinho")
    assert resposta.headers["Location"] == "/carrinho"


def test_login_nao_redireciona_para_site_externo(client):  # proteção "open redirect"
    resposta = entrar(client, next="https://site-falso.com/login")
    assert resposta.headers["Location"] == "/"


def test_carrinho_e_mantido_depois_do_login(client):  # critério da US07
    client.post("/carrinho/adicionar", data={"cupcake_id": 1, "quantidade": 2})
    entrar(client)
    with client.session_transaction() as sessao:
        assert sessao["carrinho"] == {"1": 2}


def test_logout_encerra_a_sessao(client):
    entrar(client)
    resposta = client.post("/logout", follow_redirects=True)
    assert "Você saiu da sua conta." in html(resposta)
    assert logado_como(client) is None


def test_logout_nao_funciona_por_get(client):
    """Sair só por POST: impede que um link ou imagem de outro site deslogue o cliente."""
    entrar(client)
    assert client.get("/logout").status_code == 405
    assert logado_como(client) == "Mariana Souza"


def test_barra_inferior_mostra_entrar_ou_primeiro_nome(client):
    assert ">Entrar</a>" in html(client.get("/"))
    entrar(client)
    assert ">Mariana</a>" in html(client.get("/"))


# ---------------- Minha conta e controle de acesso ----------------

def test_minha_conta_exige_login(client):
    resposta = client.get("/conta")
    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/login?next=/conta"


def test_minha_conta_mostra_dados_do_cliente(client):
    entrar(client)
    pagina = html(client.get("/conta"))
    assert "Mariana Souza" in pagina
    assert "mariana@email.com" in pagina
    assert "(11) 98888-7777" in pagina


def test_usuario_logado_nao_ve_tela_de_login_de_novo(client):
    entrar(client)
    assert client.get("/login").status_code == 302
    assert client.get("/cadastro").status_code == 302


def test_area_admin_bloqueia_cliente_com_msg17(app):  # RNF06
    bp = Blueprint("teste_admin", __name__)

    @bp.get("/admin-teste")
    @admin_obrigatorio
    def pagina_admin():
        return "área do administrador"

    app.register_blueprint(bp)
    client = app.test_client()

    assert client.get("/admin-teste").status_code == 302          # visitante -> login
    entrar(client)
    resposta = client.get("/admin-teste")                           # cliente -> bloqueado
    assert resposta.status_code == 403
    assert "Você não tem permissão para acessar esta página." in html(resposta)
    client.post("/logout")
    entrar(client, email="admin@cupcakeapp.com.br", senha="Admin@2026")
    assert html(client.get("/admin-teste")) == "área do administrador"  # admin -> liberado


def test_destino_seguro():
    assert destino_seguro("/carrinho") == "/carrinho"
    for perigoso in ["https://site-falso.com", "//site-falso.com", "/\\site-falso.com", "javascript:alert(1)", ""]:
        assert destino_seguro(perigoso) == "/"
