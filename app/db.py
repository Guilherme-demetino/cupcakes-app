"""Conexão com o PostgreSQL (psycopg 3).

Cada requisição HTTP abre UMA conexão na primeira consulta e a fecha ao final
(confirmando a transação se tudo deu certo, ou desfazendo se houve erro).
"""
from pathlib import Path

import click
import psycopg
from flask import current_app, g
from psycopg.rows import dict_row

PASTA_SQL = Path(__file__).resolve().parent.parent / "database"


def get_db():
    """Devolve a conexão da requisição atual (cria se ainda não existir)."""
    if "db" not in g:
        g.db = psycopg.connect(current_app.config["DATABASE_URL"], row_factory=dict_row)
    return g.db


def close_db(erro=None):
    conexao = g.pop("db", None)
    if conexao is not None:
        if erro is None:
            conexao.commit()
        else:
            conexao.rollback()
        conexao.close()


def consultar(sql, params=None):
    """Executa um SELECT e devolve uma lista de dicionários.
    Sempre use %s nos parâmetros: o psycopg escapa os valores e evita SQL Injection (RNF05)."""
    return get_db().execute(sql, params).fetchall()


def consultar_um(sql, params=None):
    linhas = consultar(sql, params)
    return linhas[0] if linhas else None


def executar_scripts(url, *arquivos):
    """Roda arquivos .sql inteiros (usado pelo comando init-db e pelos testes)."""
    with psycopg.connect(url, autocommit=True) as conexao:
        for arquivo in arquivos:
            conexao.execute((PASTA_SQL / arquivo).read_text(encoding="utf-8"))


@click.command("init-db")
def init_db_command():
    """Cria as tabelas e carrega os dados de exemplo (APAGA o que existir)."""
    executar_scripts(current_app.config["DATABASE_URL"], "schema.sql", "seed.sql")
    click.echo("Banco criado e populado com os dados de exemplo.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
