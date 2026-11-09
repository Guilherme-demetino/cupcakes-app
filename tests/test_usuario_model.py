"""Testes do model de usuário: validação (unitário) e cadastro/autenticação (integração)."""
import pytest

from app.models import usuario_model as um

VALIDO = {"nome": "Ana Lima", "email": "ana@email.com", "telefone": "(11) 98765-4321", "senha": "segredo123"}


# ---------------- Validação (unitário, sem banco) ----------------

def test_cadastro_valido_nao_tem_erros():
    assert um.validar_cadastro(**VALIDO) == {}


@pytest.mark.parametrize("campo", ["nome", "email", "telefone", "senha"])
def test_campo_vazio_mostra_msg01(campo):
    dados = {**VALIDO, campo: "   " if campo != "senha" else ""}
    assert um.validar_cadastro(**dados)[campo] == "Preencha este campo."


@pytest.mark.parametrize("email", ["ana", "ana@", "ana@email", "ana @email.com", "@email.com"])
def test_email_invalido_mostra_msg02(email):
    assert "e-mail válido" in um.validar_cadastro(**{**VALIDO, "email": email})["email"]


def test_senha_curta_mostra_msg04():  # US01
    erros = um.validar_cadastro(**{**VALIDO, "senha": "1234567"})
    assert erros["senha"] == "A senha precisa ter pelo menos 8 caracteres."


def test_senha_com_exatamente_8_caracteres_e_aceita():
    assert um.validar_cadastro(**{**VALIDO, "senha": "12345678"}) == {}


@pytest.mark.parametrize("telefone,valido", [
    ("11987654321", True), ("(11) 3333-4444", True), ("987654321", False), ("119876543210", False)])
def test_telefone_precisa_de_ddd(telefone, valido):
    erros = um.validar_cadastro(**{**VALIDO, "telefone": telefone})
    assert ("telefone" not in erros) is valido


def test_nome_com_uma_letra_e_recusado():
    assert "nome" in um.validar_cadastro(**{**VALIDO, "nome": "A"})


def test_formatar_telefone():
    assert um.formatar_telefone("11987654321") == "(11) 98765-4321"
    assert um.formatar_telefone("1133334444") == "(11) 3333-4444"


def test_normalizar_email():
    assert um.normalizar_email("  Ana@Email.COM ") == "ana@email.com"


# ---------------- Banco (integração) ----------------

def test_criar_usuario_grava_hash_bcrypt_e_nao_a_senha(app, banco):  # RN09
    import psycopg
    with app.app_context():
        usuario = um.criar(**VALIDO)
    assert usuario["perfil"] == "CLIENTE"
    assert usuario["telefone"] == "(11) 98765-4321"
    assert "senha_hash" not in usuario
    with psycopg.connect(banco) as conexao:
        hash_gravado = conexao.execute("SELECT senha_hash FROM usuario WHERE email = %s",
                                       ("ana@email.com",)).fetchone()[0]
    assert hash_gravado.startswith("$2a$10$")
    assert "segredo123" not in hash_gravado


def test_email_e_gravado_em_minusculas(app):
    with app.app_context():
        usuario = um.criar(**{**VALIDO, "email": "ANA@Email.com"})
    assert usuario["email"] == "ana@email.com"


def test_email_duplicado_gera_erro(app):  # RN08
    with app.app_context():
        with pytest.raises(um.EmailJaCadastrado):
            um.criar(**{**VALIDO, "email": "mariana@email.com"})


def test_email_existe(app):
    with app.app_context():
        assert um.email_existe("MARIANA@email.com")
        assert not um.email_existe("ninguem@email.com")


def test_autenticar_com_senha_correta(app):  # US02 (usuária do seed.sql)
    with app.app_context():
        usuario = um.autenticar("mariana@email.com", "Cupcake@123")
    assert usuario["nome"] == "Mariana Souza"
    assert usuario["perfil"] == "CLIENTE"


@pytest.mark.parametrize("email,senha", [
    ("mariana@email.com", "senhaerrada"), ("mariana@email.com", "cupcake@123"),
    ("ninguem@email.com", "Cupcake@123"), ("", ""), ("mariana@email.com", "")])
def test_autenticar_falha_com_dados_errados(app, email, senha):
    with app.app_context():
        assert um.autenticar(email, senha) is None


def test_autenticar_ignora_maiusculas_no_email(app):
    with app.app_context():
        assert um.autenticar("  Mariana@EMAIL.com ", "Cupcake@123") is not None
