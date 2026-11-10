"""Model de Cupcake: consultas do catálogo (US03, US04, US05) e manutenção pelo administrador (US10)."""
from decimal import Decimal, InvalidOperation

import psycopg

from ..db import consultar, consultar_um, get_db
from ..messages import msg

# Campos vistos pelo CLIENTE: "preco" já é o preço de venda (o promocional, se houver – RN12).
# "preco_cheio" é o preço normal, mostrado riscado quando há promoção.
_CAMPOS = """
    c.id, c.nome, c.descricao, coalesce(c.preco_promocional, c.preco) AS preco,
    c.preco AS preco_cheio, c.preco_promocional, c.tamanho, c.peso_gramas, c.foto_url,
    c.categoria_id, cat.nome AS categoria
"""

# Campos vistos pelo ADMINISTRADOR: os dois preços separados, como estão no banco.
_CAMPOS_ADMIN = """
    c.id, c.nome, c.descricao, c.preco, c.preco_promocional, c.tamanho, c.peso_gramas, c.foto_url,
    c.categoria_id, cat.nome AS categoria
"""

TAMANHOS = {"MINI": "Mini", "TRADICIONAL": "Tradicional", "GIGANTE": "Gigante"}


def _escapar_like(termo):
    """Faz % e _ digitados pelo usuário serem tratados como texto comum na busca."""
    return termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def listar_categorias():
    return consultar("SELECT id, nome FROM categoria ORDER BY id")


def listar_ativos(categoria_id=None, termo=None, so_promocoes=False):
    """Cupcakes ativos (RN04), com filtro opcional por categoria, por promoção (US12)
    e busca por nome (US04). A busca não diferencia maiúsculas de minúsculas."""
    sql = f"""SELECT {_CAMPOS}
              FROM cupcake c JOIN categoria cat ON cat.id = c.categoria_id
              WHERE c.ativo"""
    params = []
    if categoria_id:
        sql += " AND c.categoria_id = %s"
        params.append(categoria_id)
    if so_promocoes:
        sql += " AND c.preco_promocional IS NOT NULL"
    if termo:
        sql += " AND lower(c.nome) LIKE lower(%s) ESCAPE '\\'"
        params.append(f"%{_escapar_like(termo)}%")
    sql += " ORDER BY c.nome"
    return consultar(sql, params)


def buscar_ativo_por_id(cupcake_id):
    """Detalhes completos de um cupcake ativo, com ingredientes e alergênicos (US05).
    Devolve None se não existir ou estiver inativo."""
    cupcake = consultar_um(
        f"""SELECT {_CAMPOS}
            FROM cupcake c JOIN categoria cat ON cat.id = c.categoria_id
            WHERE c.id = %s AND c.ativo""",
        (cupcake_id,),
    )
    if cupcake is None:
        return None
    cupcake["ingredientes"] = consultar(
        """SELECT i.nome, i.alergenico
           FROM ingrediente i JOIN cupcake_ingrediente ci ON ci.ingrediente_id = i.id
           WHERE ci.cupcake_id = %s
           ORDER BY i.alergenico DESC, i.nome""",
        (cupcake_id,),
    )
    cupcake["alergenicos"] = [i["nome"] for i in cupcake["ingredientes"] if i["alergenico"]]
    cupcake["tamanho_rotulo"] = TAMANHOS.get(cupcake["tamanho"], cupcake["tamanho"])
    return cupcake


def buscar_ativos_por_ids(ids):
    """Devolve {id: cupcake} só com os cupcakes ativos da lista (usado pelo carrinho)."""
    ids = [int(i) for i in ids]
    if not ids:
        return {}
    marcadores = ", ".join(["%s"] * len(ids))
    linhas = consultar(
        f"""SELECT {_CAMPOS}
            FROM cupcake c JOIN categoria cat ON cat.id = c.categoria_id
            WHERE c.ativo AND c.id IN ({marcadores})""",
        ids,
    )
    return {linha["id"]: linha for linha in linhas}


def buscar_nome(cupcake_id):
    """Nome de um cupcake mesmo que esteja inativo (para avisar o cliente, MSG15)."""
    linha = consultar_um("SELECT nome FROM cupcake WHERE id = %s", (cupcake_id,))
    return linha["nome"] if linha else "selecionado"


# =====================================================================
# Área administrativa (US10) – Sprint 4
# =====================================================================
class NomeRepetido(Exception):
    """Já existe um cupcake com esse nome (UNIQUE no banco)."""


def listar_todos():
    """Todos os cupcakes, ativos e inativos, com quantas vezes foram vendidos."""
    return consultar(
        f"""SELECT {_CAMPOS_ADMIN}, c.ativo,
                   (SELECT count(*) FROM item_pedido i WHERE i.cupcake_id = c.id) AS vendas
            FROM cupcake c JOIN categoria cat ON cat.id = c.categoria_id
            ORDER BY c.ativo DESC, c.nome"""
    )


def listar_ingredientes():
    return consultar("SELECT id, nome, alergenico FROM ingrediente ORDER BY nome")


def buscar_para_edicao(cupcake_id):
    """Cupcake (mesmo inativo) com a lista de ids dos ingredientes, para o formulário."""
    cupcake = consultar_um(f"""SELECT {_CAMPOS_ADMIN}, c.ativo
                               FROM cupcake c JOIN categoria cat ON cat.id = c.categoria_id
                               WHERE c.id = %s""", (cupcake_id,))
    if cupcake:
        cupcake["ingrediente_ids"] = [linha["ingrediente_id"] for linha in consultar(
            "SELECT ingrediente_id FROM cupcake_ingrediente WHERE cupcake_id = %s", (cupcake_id,))]
    return cupcake


def validar_cupcake(dados, tem_foto, categorias_validas, ingredientes_validos):
    """Valida o formulário do administrador. Devolve {campo: mensagem}.
    RN01: foto e descrição obrigatórias (MSG08). RN02: preço > 0 (MSG09)."""
    erros = {}
    if not dados["nome"]:
        erros["nome"] = msg("MSG01")
    elif len(dados["nome"]) > 80:
        erros["nome"] = "Use no máximo 80 caracteres."

    if not dados["descricao"]:
        erros["descricao"] = msg("MSG08")
    if not tem_foto:
        erros["foto"] = msg("MSG08")

    dados["preco_decimal"] = _ler_preco(dados["preco"])
    if dados["preco_decimal"] is None:
        erros["preco"] = msg("MSG09")

    # RN12: preço promocional é opcional; se informado, deve ser menor que o preço normal.
    dados["promocao_decimal"] = None
    if (dados.get("preco_promocional") or "").strip():
        promocao = _ler_preco(dados["preco_promocional"])
        if promocao is None:
            erros["preco_promocional"] = "Informe um preço promocional válido ou deixe em branco."
        elif dados["preco_decimal"] is not None and promocao >= dados["preco_decimal"]:
            erros["preco_promocional"] = msg("MSG24")
        else:
            dados["promocao_decimal"] = promocao

    if dados["tamanho"] not in TAMANHOS:
        erros["tamanho"] = "Escolha o tamanho."
    try:
        peso = int(dados["peso_gramas"])
        if not 10 <= peso <= 1000:
            raise ValueError
    except (TypeError, ValueError):
        erros["peso_gramas"] = "Informe o peso em gramas (de 10 a 1000)."

    if dados["categoria_id"] not in categorias_validas:
        erros["categoria_id"] = "Escolha a categoria."
    if not dados["ingrediente_ids"]:
        erros["ingredientes"] = "Marque pelo menos um ingrediente."
    elif not set(dados["ingrediente_ids"]) <= set(ingredientes_validos):
        erros["ingredientes"] = "Ingrediente inválido."
    return erros


def _ler_preco(texto):
    """'16,90', '16.90' ou '1.234,50' -> Decimal com 2 casas. Inválido ou <= 0 -> None."""
    texto = (texto or "").strip()
    try:
        preco = Decimal(texto.replace(".", "").replace(",", ".")) if "," in texto else Decimal(texto)
        if not Decimal("0") < preco < Decimal("1000000"):
            return None
        return preco.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None


def _gravar_ingredientes(db, cupcake_id, ingrediente_ids):
    db.execute("DELETE FROM cupcake_ingrediente WHERE cupcake_id = %s", (cupcake_id,))
    for ingrediente_id in sorted(set(ingrediente_ids)):
        db.execute("INSERT INTO cupcake_ingrediente (cupcake_id, ingrediente_id) VALUES (%s, %s)",
                   (cupcake_id, ingrediente_id))


def salvar(dados, foto_url, cupcake_id=None):
    """Cria (cupcake_id=None) ou atualiza um cupcake e seus ingredientes numa transação.
    Na edição, foto_url=None mantém a foto atual. Devolve o id."""
    db = get_db()
    valores = (dados["categoria_id"], dados["nome"], dados["descricao"], dados["preco_decimal"],
               dados.get("promocao_decimal"), dados["tamanho"], int(dados["peso_gramas"]))
    try:
        if cupcake_id is None:
            cupcake_id = db.execute(
                """INSERT INTO cupcake (categoria_id, nome, descricao, preco, preco_promocional,
                                       tamanho, peso_gramas, foto_url)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""", valores + (foto_url,)).fetchone()["id"]
        else:
            db.execute(
                """UPDATE cupcake SET categoria_id = %s, nome = %s, descricao = %s, preco = %s,
                          preco_promocional = %s, tamanho = %s, peso_gramas = %s, foto_url = coalesce(%s, foto_url)
                   WHERE id = %s""", valores + (foto_url, cupcake_id))
        _gravar_ingredientes(db, cupcake_id, dados["ingrediente_ids"])
        db.commit()
        return cupcake_id
    except psycopg.IntegrityError as erro:
        db.rollback()
        if getattr(erro, "sqlstate", None) == "23505":  # violação de UNIQUE: nome repetido
            raise NomeRepetido(dados["nome"]) from erro
        raise
    except Exception:
        db.rollback()
        raise


def alternar_ativo(cupcake_id):
    """Ativa/desativa (RN04). Não existe excluir: cupcakes vendidos ficam no histórico (RN11).
    Devolve o novo estado, ou None se o cupcake não existir."""
    db = get_db()
    linha = db.execute("UPDATE cupcake SET ativo = NOT ativo WHERE id = %s RETURNING nome, ativo",
                       (cupcake_id,)).fetchone()
    db.commit()
    return linha
