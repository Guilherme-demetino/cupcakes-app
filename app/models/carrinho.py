"""Model do Carrinho (US06).

O carrinho NÃO é gravado no banco: ele vive na sessão do usuário (cookie assinado),
como definido no diagrama de classes da Etapa 1. Esta classe guarda apenas
{id_do_cupcake: quantidade} e concentra as regras de negócio:
  RN03 - quantidade de 1 a 20 por item
  RN04 - cupcakes inativos saem do carrinho
  RN06 - total = soma(quantidade × preço) + taxa de entrega
"""
from decimal import Decimal

QTD_MIN = 1
QTD_MAX = 20
TAXA_ENTREGA = Decimal("8.00")


class Carrinho:
    def __init__(self, dados=None):
        # A sessão guarda as chaves como texto; aqui convertemos para inteiro.
        self.itens = {int(k): int(v) for k, v in (dados or {}).items()}

    # ---------- Alterações ----------
    def adicionar(self, cupcake_id, quantidade):
        """Soma a quantidade ao item (sem duplicar linhas).
        Devolve True se precisou limitar a 20 unidades (para exibir MSG13)."""
        quantidade = self._validar(quantidade)
        nova = self.itens.get(cupcake_id, 0) + quantidade
        self.itens[cupcake_id] = min(nova, QTD_MAX)
        return nova > QTD_MAX

    def alterar(self, cupcake_id, quantidade):
        """Define a quantidade de um item. Zero ou menos remove o item.
        Devolve True se precisou limitar a 20 unidades."""
        if cupcake_id not in self.itens:
            return False
        if int(quantidade) < QTD_MIN:
            self.remover(cupcake_id)
            return False
        self.itens[cupcake_id] = min(int(quantidade), QTD_MAX)
        return int(quantidade) > QTD_MAX

    def remover(self, cupcake_id):
        """Remove o item e devolve a quantidade que ele tinha (para o 'Desfazer')."""
        return self.itens.pop(cupcake_id, 0)

    def esvaziar(self):
        self.itens.clear()

    # ---------- Consultas ----------
    @property
    def quantidade_total(self):
        return sum(self.itens.values())

    @property
    def vazio(self):
        return not self.itens

    def resumo(self, cupcakes_por_id):
        """Monta as linhas e os totais com os preços atuais.

        cupcakes_por_id: {id: {"nome":..., "preco": Decimal, ...}} só com cupcakes ATIVOS.
        Itens cujo cupcake não está no dicionário (inativo/excluído) são retirados
        do carrinho e devolvidos em "removidos" (RN04 / MSG15).
        """
        removidos = [cid for cid in self.itens if cid not in cupcakes_por_id]
        for cid in removidos:
            self.remover(cid)

        linhas = []
        for cid, qtd in self.itens.items():
            cupcake = cupcakes_por_id[cid]
            linhas.append({"cupcake": cupcake, "quantidade": qtd,
                           "subtotal": Decimal(cupcake["preco"]) * qtd})

        subtotal = sum((linha["subtotal"] for linha in linhas), Decimal("0.00"))
        taxa = TAXA_ENTREGA if linhas else Decimal("0.00")
        return {"linhas": linhas, "subtotal": subtotal, "taxa_entrega": taxa,
                "total": subtotal + taxa, "removidos": removidos}

    def para_sessao(self):
        return {str(k): v for k, v in self.itens.items()}

    # ---------- Interno ----------
    @staticmethod
    def _validar(quantidade):
        try:
            quantidade = int(quantidade)
        except (TypeError, ValueError):
            raise ValueError("A quantidade deve ser um número inteiro.") from None
        if quantidade < QTD_MIN:
            raise ValueError(f"A quantidade mínima é {QTD_MIN}.")
        return quantidade
