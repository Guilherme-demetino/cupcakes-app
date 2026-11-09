"""Model de Pedido: finalizar (US07), acompanhar (US08) e cancelar (US09).

Regras de negócio aplicadas aqui:
  RN05 - o preço de cada item fica congelado no pedido (item_pedido.preco_unitario)
  RN06 - total = soma dos itens + taxa de entrega
  RN07 - fluxo de status (também garantido por um gatilho no banco)
  RN10 - só finaliza com endereço de entrega válido
"""
import re

from ..db import consultar, consultar_um, get_db
from ..messages import msg

STATUS = {
    "RECEBIDO": "Recebido",
    "EM_PREPARO": "Em preparo",
    "SAIU_PARA_ENTREGA": "Saiu para entrega",
    "ENTREGUE": "Entregue",
    "CANCELADO": "Cancelado",
}
ETAPAS = ["RECEBIDO", "EM_PREPARO", "SAIU_PARA_ENTREGA", "ENTREGUE"]
FORMAS_PAGAMENTO = {"PIX": "PIX", "CARTAO": "Cartão (maquininha)", "DINHEIRO": "Dinheiro"}
UFS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR",
       "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
CAMPOS_ENDERECO = ("cep", "logradouro", "numero", "complemento", "bairro", "cidade", "uf")

# RN07: para quais status cada status pode ir
TRANSICOES = {
    "RECEBIDO": ["EM_PREPARO", "CANCELADO"],
    "EM_PREPARO": ["SAIU_PARA_ENTREGA", "CANCELADO"],
    "SAIU_PARA_ENTREGA": ["ENTREGUE"],
    "ENTREGUE": [],
    "CANCELADO": [],
}


class PedidoNaoPodeSerCancelado(Exception):
    pass


# ---------------- Regras puras (testadas sem banco) ----------------

def pode_mudar_status(atual, novo, por_admin):
    """RN07: o cliente só cancela pedidos RECEBIDOS; o administrador segue TRANSICOES."""
    if novo not in TRANSICOES.get(atual, []):
        return False
    if not por_admin:
        return atual == "RECEBIDO" and novo == "CANCELADO"
    return True


def limpar_endereco(form):
    """Pega os campos do formulário, tirando espaços extras e formatando CEP e UF."""
    dados = {campo: (form.get(campo) or "").strip() for campo in CAMPOS_ENDERECO}
    dados["cep"] = re.sub(r"\D", "", dados["cep"])
    dados["uf"] = dados["uf"].upper()
    return dados


def validar_checkout(endereco, forma_pagamento, observacao):
    """Devolve {campo: mensagem} com os problemas encontrados (vazio = tudo certo)."""
    erros = {}
    if len(endereco["cep"]) != 8:
        erros["cep"] = msg("MSG06")
    for campo, limite in (("logradouro", 150), ("numero", 10), ("bairro", 80), ("cidade", 80)):
        if not endereco[campo]:
            erros[campo] = msg("MSG07")
        elif len(endereco[campo]) > limite:
            erros[campo] = f"Use no máximo {limite} caracteres."
    if len(endereco["complemento"]) > 60:
        erros["complemento"] = "Use no máximo 60 caracteres."
    if endereco["uf"] not in UFS:
        erros["uf"] = "Escolha o estado."
    if forma_pagamento not in FORMAS_PAGAMENTO:
        erros["forma_pagamento"] = "Escolha como vai pagar na entrega."
    if len(observacao or "") > 255:
        erros["observacao"] = "A observação pode ter no máximo 255 caracteres."
    return erros


# ---------------- Banco ----------------

def ultimo_endereco(usuario_id):
    """Endereço do pedido mais recente (ou o último cadastrado), para preencher o checkout."""
    return consultar_um(
        """SELECT e.cep, e.logradouro, e.numero, coalesce(e.complemento, '') AS complemento,
                  e.bairro, e.cidade, e.uf
           FROM endereco e
           LEFT JOIN pedido p ON p.endereco_id = e.id
           WHERE e.usuario_id = %s
           ORDER BY p.criado_em DESC NULLS LAST, e.id DESC
           LIMIT 1""",
        (usuario_id,),
    )


def _obter_ou_criar_endereco(usuario_id, end):
    """Reaproveita o endereço se o cliente já usou exatamente o mesmo (evita duplicar linhas)."""
    db = get_db()
    existente = db.execute(
        """SELECT id FROM endereco
           WHERE usuario_id = %s AND cep = %s AND logradouro = %s AND numero = %s
             AND coalesce(complemento, '') = %s AND bairro = %s AND cidade = %s AND uf = %s""",
        (usuario_id, end["cep"], end["logradouro"], end["numero"], end["complemento"],
         end["bairro"], end["cidade"], end["uf"]),
    ).fetchone()
    if existente:
        return existente["id"]
    return db.execute(
        """INSERT INTO endereco (usuario_id, cep, logradouro, numero, complemento, bairro, cidade, uf)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
        (usuario_id, end["cep"], end["logradouro"], end["numero"], end["complemento"] or None,
         end["bairro"], end["cidade"], end["uf"]),
    ).fetchone()["id"]


def criar(usuario_id, endereco, forma_pagamento, observacao, resumo):
    """Grava pedido + itens numa única transação e devolve o número do pedido.

    resumo: resultado de Carrinho.resumo() com os preços ATUAIS dos cupcakes,
    que ficam congelados em item_pedido.preco_unitario (RN05).
    O histórico de status 'RECEBIDO' é gravado pelo gatilho do banco.
    """
    if not resumo["linhas"]:
        raise ValueError("Não é possível criar um pedido sem itens.")
    db = get_db()
    try:
        endereco_id = _obter_ou_criar_endereco(usuario_id, endereco)
        pedido_id = db.execute(
            """INSERT INTO pedido (usuario_id, endereco_id, forma_pagamento, taxa_entrega, valor_total, observacao)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (usuario_id, endereco_id, forma_pagamento, resumo["taxa_entrega"], resumo["total"],
             (observacao or "").strip() or None),
        ).fetchone()["id"]
        for linha in resumo["linhas"]:
            db.execute(
                """INSERT INTO item_pedido (pedido_id, cupcake_id, quantidade, preco_unitario)
                   VALUES (%s, %s, %s, %s)""",
                (pedido_id, linha["cupcake"]["id"], linha["quantidade"], linha["cupcake"]["preco"]),
            )
        db.commit()  # tudo ou nada: se algo falhar acima, nada é gravado
        return pedido_id
    except Exception:
        db.rollback()
        raise


def listar_do_usuario(usuario_id):
    return consultar(
        """SELECT p.id, p.status, p.valor_total, p.criado_em,
                  (SELECT sum(quantidade) FROM item_pedido WHERE pedido_id = p.id) AS qtd_itens
           FROM pedido p
           WHERE p.usuario_id = %s
           ORDER BY p.criado_em DESC, p.id DESC""",
        (usuario_id,),
    )


def buscar_do_usuario(pedido_id, usuario_id):
    """Pedido completo, SOMENTE se pertencer ao usuário (um cliente não vê o pedido de outro)."""
    pedido = consultar_um(
        """SELECT p.id, p.status, p.forma_pagamento, p.taxa_entrega, p.valor_total, p.observacao, p.criado_em,
                  e.cep, e.logradouro, e.numero, e.complemento, e.bairro, e.cidade, e.uf
           FROM pedido p JOIN endereco e ON e.id = p.endereco_id
           WHERE p.id = %s AND p.usuario_id = %s""",
        (pedido_id, usuario_id),
    )
    if pedido is None:
        return None
    pedido["itens"] = consultar(
        """SELECT c.id AS cupcake_id, c.nome, c.foto_url, i.quantidade, i.preco_unitario,
                  i.quantidade * i.preco_unitario AS subtotal
           FROM item_pedido i JOIN cupcake c ON c.id = i.cupcake_id
           WHERE i.pedido_id = %s ORDER BY c.nome""",
        (pedido_id,),
    )
    pedido["subtotal"] = sum(item["subtotal"] for item in pedido["itens"])
    pedido["historico"] = consultar(
        "SELECT status, alterado_em FROM historico_status WHERE pedido_id = %s ORDER BY alterado_em, id",
        (pedido_id,),
    )
    pedido["pode_cancelar"] = pode_mudar_status(pedido["status"], "CANCELADO", por_admin=False)
    return pedido


def cancelar_pelo_cliente(pedido_id, usuario_id):
    """US09: cancela só se o pedido for do cliente E ainda estiver RECEBIDO.
    O UPDATE com essas condições é atômico: dois cliques não causam problema."""
    db = get_db()
    cancelado = db.execute(
        """UPDATE pedido SET status = 'CANCELADO'
           WHERE id = %s AND usuario_id = %s AND status = 'RECEBIDO'
           RETURNING id""",
        (pedido_id, usuario_id),
    ).fetchone()
    if cancelado is None:
        raise PedidoNaoPodeSerCancelado(pedido_id)
    db.commit()
