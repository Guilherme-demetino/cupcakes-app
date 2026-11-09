"""Configuração compartilhada dos testes (fixtures do Pytest).

Os testes de banco usam um banco SEPARADO, informado em TEST_DATABASE_URL
(veja .env.example). Antes de cada teste ele é apagado e recriado com
schema.sql + seed.sql, então cada teste começa sempre do mesmo estado.
"""
import os

import pytest
from dotenv import load_dotenv

from app import create_app
from app.db import criar_banco_se_nao_existir, executar_scripts

load_dotenv()
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest.fixture
def banco():
    if not TEST_DATABASE_URL:
        pytest.skip("Defina TEST_DATABASE_URL no .env para rodar os testes de banco.")
    criar_banco_se_nao_existir(TEST_DATABASE_URL)  # na 1ª vez, cria o banco de teste sozinho
    executar_scripts(TEST_DATABASE_URL, "schema.sql", "seed.sql")
    return TEST_DATABASE_URL


@pytest.fixture
def app(banco, tmp_path):
    # As fotos enviadas nos testes vão para uma pasta temporária, e não para o projeto.
    return create_app({"TESTING": True, "DATABASE_URL": banco, "SECRET_KEY": "chave-de-teste",
                       "UPLOAD_FOLDER": str(tmp_path / "uploads")})


@pytest.fixture
def client(app):
    """Simula um navegador fazendo requisições à aplicação."""
    return app.test_client()


@pytest.fixture
def sql(banco):
    """Executa SQL direto no banco de teste (para preparar cenários)."""
    import psycopg

    def executar(comando, params=None):
        with psycopg.connect(banco, autocommit=True) as conexao:
            conexao.execute(comando, params)
    return executar
