# 2. Modelagem UML – CupcakeApp

Os diagramas estão escritos em **Mermaid**, e o GitHub os desenha automaticamente ao abrir este arquivo. As versões em imagem (PNG) e o código-fonte de cada diagrama (`.mmd`) estão na pasta [`diagramas/`](diagramas/), prontos para colar num documento ou slide.

---

## 2.1 Diagrama de Casos de Uso

![Diagrama de casos de uso](diagramas/casos-de-uso.svg)

*Imagem também em [PNG](diagramas/casos-de-uso.png). O diagrama de casos de uso foi desenhado em SVG porque o Mermaid não tem notação UML própria para atores e casos de uso.*

**Leitura do diagrama:** a seta com triângulo vazado indica **generalização**: o *Cliente* é um *Visitante* autenticado e herda todos os casos de uso dele. «include» indica que finalizar o pedido **sempre** exige login. «extend» indica comportamentos **opcionais**: filtrar o catálogo e cancelar um pedido a partir do acompanhamento. O *Administrador* também faz login (UC02).

### Especificação do caso de uso principal – UC07 Finalizar pedido

| Item | Descrição |
|---|---|
| **Ator** | Cliente |
| **Pré-condições** | O carrinho tem pelo menos 1 item. |
| **Pós-condições** | Pedido gravado com status RECEBIDO e carrinho esvaziado. |
| **Fluxo principal** | 1. O cliente toca em "Finalizar pedido" no carrinho. 2. O sistema verifica se o cliente está logado (include UC02). 3. O sistema exibe o resumo do pedido e o formulário de endereço, já preenchido com o último endereço usado, se houver. 4. O cliente confirma ou edita o endereço e escolhe a forma de pagamento (PIX, cartão ou dinheiro na entrega). 5. O cliente toca em "Confirmar pedido". 6. O sistema valida os dados e confere se todos os cupcakes continuam ativos. 7. O sistema grava o pedido com os preços atuais congelados (RN05) e calcula o total (RN06). 8. O sistema esvazia o carrinho e mostra a tela de confirmação com o número do pedido. |
| **Fluxo alternativo A1** – não logado | No passo 2, o sistema redireciona para o login e, depois de autenticar, volta ao passo 3 com o carrinho preservado. |
| **Fluxo de exceção E1** – dados inválidos | No passo 6, o sistema destaca os campos com erro (MSG06/MSG07) e volta ao passo 4. |
| **Fluxo de exceção E2** – cupcake desativado | No passo 6, o sistema remove o item, exibe MSG15 e volta ao carrinho. |
| **Regras** | RN03, RN04, RN05, RN06, RN10 |

---

## 2.2 Diagrama de Classes (domínio)

Este diagrama mostra as classes do sistema com atributos e principais métodos. A classe **Carrinho** existe apenas na sessão do usuário e **não é persistida** no banco.

<sub>🖼 Versão em imagem: [classes.png](diagramas/classes.png)</sub>

```mermaid
classDiagram
    direction LR

    class Usuario {
        -int id
        -String nome
        -String email
        -String senhaHash
        -String telefone
        -Perfil perfil
        -DateTime criadoEm
        +autenticar(senha) bool
        +isAdmin() bool
    }

    class Endereco {
        -int id
        -String cep
        -String logradouro
        -String numero
        -String complemento
        -String bairro
        -String cidade
        -String uf
        +validarCep() bool
    }

    class Categoria {
        -int id
        -String nome
    }

    class Cupcake {
        -int id
        -String nome
        -String descricao
        -Decimal preco
        -Tamanho tamanho
        -int pesoGramas
        -String fotoUrl
        -bool ativo
        +validar() List~String~
        +temAlergenicos() bool
        +desativar() void
    }

    class Ingrediente {
        -int id
        -String nome
        -bool alergenico
    }

    class Carrinho {
        -List~ItemCarrinho~ itens
        +adicionar(cupcake, qtd) void
        +alterarQuantidade(cupcakeId, qtd) void
        +remover(cupcakeId) void
        +subtotal() Decimal
        +total() Decimal
        +esvaziar() void
    }

    class ItemCarrinho {
        -Cupcake cupcake
        -int quantidade
        +subtotal() Decimal
    }

    class Pedido {
        -int id
        -StatusPedido status
        -FormaPagamento formaPagamento
        -Decimal taxaEntrega
        -Decimal valorTotal
        -String observacao
        -DateTime criadoEm
        +calcularTotal() Decimal
        +alterarStatus(novo, porAdmin) void
        +podeSerCancelado(porAdmin) bool
    }

    class ItemPedido {
        -int quantidade
        -Decimal precoUnitario
        +subtotal() Decimal
    }

    class HistoricoStatus {
        -int id
        -StatusPedido status
        -DateTime alteradoEm
    }

    class Perfil {
        <<enumeration>>
        CLIENTE
        ADMIN
    }
    class Tamanho {
        <<enumeration>>
        MINI
        TRADICIONAL
        GIGANTE
    }
    class StatusPedido {
        <<enumeration>>
        RECEBIDO
        EM_PREPARO
        SAIU_PARA_ENTREGA
        ENTREGUE
        CANCELADO
    }
    class FormaPagamento {
        <<enumeration>>
        PIX
        CARTAO
        DINHEIRO
    }

    Usuario "1" --> "0..*" Endereco : possui
    Usuario "1" --> "0..*" Pedido : realiza
    Categoria "1" --> "0..*" Cupcake : agrupa
    Cupcake "0..*" --> "1..*" Ingrediente : contém
    Carrinho "1" *-- "0..*" ItemCarrinho
    ItemCarrinho "0..*" --> "1" Cupcake
    Pedido "1" *-- "1..*" ItemPedido
    ItemPedido "0..*" --> "1" Cupcake
    Pedido "0..*" --> "1" Endereco : entregue em
    Pedido "1" *-- "1..*" HistoricoStatus
    Usuario ..> Perfil
    Cupcake ..> Tamanho
    Pedido ..> StatusPedido
    Pedido ..> FormaPagamento
```

**Notas de modelagem**
- **Composição** (losango cheio): um `ItemPedido` não existe sem o seu `Pedido`. O mesmo vale para `ItemCarrinho` em relação ao `Carrinho` e para `HistoricoStatus` em relação ao `Pedido`.
- `ItemPedido.precoUnitario` guarda uma cópia do preço no momento da compra (RN05). Por isso ele não é redundante com `Cupcake.preco`.
- O relacionamento Cupcake ↔ Ingrediente é **muitos-para-muitos**: um cupcake tem vários ingredientes e um ingrediente (ex.: leite) aparece em vários cupcakes.

### 2.2.1 Diagrama de Classes de Persistência

Estas são as classes que viram tabelas, com as chaves e os tipos que serão usados no banco. Daqui saem os modelos lógico e físico do documento 04.

<sub>🖼 Versão em imagem: [classes-persistencia.png](diagramas/classes-persistencia.png)</sub>

```mermaid
classDiagram
    direction LR
    class usuario { <<tabela>>
        PK id : serial
        nome : varchar(100)
        email : varchar(150) UK
        senha_hash : varchar(255)
        telefone : varchar(20)
        perfil : varchar(10)
        criado_em : timestamp
    }
    class endereco { <<tabela>>
        PK id : serial
        FK usuario_id : int
        cep : char(8)
        logradouro : varchar(150)
        numero : varchar(10)
        complemento : varchar(60)
        bairro : varchar(80)
        cidade : varchar(80)
        uf : char(2)
    }
    class categoria { <<tabela>>
        PK id : serial
        nome : varchar(50) UK
    }
    class cupcake { <<tabela>>
        PK id : serial
        FK categoria_id : int
        nome : varchar(80) UK
        descricao : text
        preco : numeric(8,2)
        tamanho : varchar(12)
        peso_gramas : smallint
        foto_url : varchar(255)
        ativo : boolean
        criado_em : timestamp
        atualizado_em : timestamp
    }
    class ingrediente { <<tabela>>
        PK id : serial
        nome : varchar(60) UK
        alergenico : boolean
    }
    class cupcake_ingrediente { <<tabela>>
        PK,FK cupcake_id : int
        PK,FK ingrediente_id : int
    }
    class pedido { <<tabela>>
        PK id : serial
        FK usuario_id : int
        FK endereco_id : int
        status : varchar(20)
        forma_pagamento : varchar(10)
        taxa_entrega : numeric(8,2)
        valor_total : numeric(10,2)
        observacao : varchar(255)
        criado_em : timestamp
    }
    class item_pedido { <<tabela>>
        PK,FK pedido_id : int
        PK,FK cupcake_id : int
        quantidade : smallint
        preco_unitario : numeric(8,2)
    }
    class historico_status { <<tabela>>
        PK id : serial
        FK pedido_id : int
        status : varchar(20)
        alterado_em : timestamp
    }
    usuario "1" -- "0..*" endereco
    usuario "1" -- "0..*" pedido
    endereco "1" -- "0..*" pedido
    categoria "1" -- "0..*" cupcake
    cupcake "1" -- "0..*" cupcake_ingrediente
    ingrediente "1" -- "0..*" cupcake_ingrediente
    pedido "1" -- "1..*" item_pedido
    cupcake "1" -- "0..*" item_pedido
    pedido "1" -- "1..*" historico_status
```

---

## 2.3 Diagrama de Sequência – Finalizar pedido (UC07)

Mostra como as camadas **MVC** conversam no fluxo mais importante do sistema.

<sub>🖼 Versão em imagem: [sequencia-finalizar-pedido.png](diagramas/sequencia-finalizar-pedido.png)</sub>

```mermaid
sequenceDiagram
    autonumber
    actor Cliente
    participant View as View<br/>(checkout.html)
    participant Ctrl as PedidoController
    participant Car as Carrinho<br/>(sessão)
    participant Cup as CupcakeModel
    participant Ped as PedidoModel
    participant DB as PostgreSQL

    Cliente->>View: Preenche endereço e pagamento
    View->>Ctrl: POST /pedidos
    Ctrl->>Ctrl: verifica sessão (logado?)
    alt não logado
        Ctrl-->>View: redireciona /login?next=/checkout
    else logado
        Ctrl->>Ctrl: valida endereço e forma de pagamento
        alt dados inválidos
            Ctrl-->>View: 422 + mensagens MSG06/MSG07
        else dados válidos
            Ctrl->>Car: obter itens
            Car-->>Ctrl: itens [cupcakeId, qtd]
            Ctrl->>Cup: buscarAtivos(ids)
            Cup->>DB: SELECT ... WHERE id IN (...) AND ativo
            DB-->>Cup: cupcakes
            Cup-->>Ctrl: cupcakes ativos
            alt algum cupcake inativo
                Ctrl->>Car: remover(itens inativos)
                Ctrl-->>View: redireciona /carrinho + MSG15
            else todos ativos
                Ctrl->>Ped: criar(usuario, endereco, itens, preços)
                Ped->>DB: BEGIN
                Ped->>DB: INSERT pedido / item_pedido / historico_status
                Ped->>DB: COMMIT
                DB-->>Ped: id do pedido
                Ped-->>Ctrl: pedido criado
                Ctrl->>Car: esvaziar()
                Ctrl-->>View: redireciona /pedidos/{id}/confirmacao
                View-->>Cliente: "Pedido nº {id} recebido!" (MSG21)
            end
        end
    end
```

---

## 2.4 Diagrama de Atividades – Jornada de compra

<sub>🖼 Versão em imagem: [atividades-compra.png](diagramas/atividades-compra.png)</sub>

```mermaid
flowchart TD
    I((Início)) --> A[Abrir catálogo]
    A --> B{Deseja filtrar<br/>ou buscar?}
    B -- Sim --> B1[Escolher categoria / digitar termo] --> C
    B -- Não --> C[Tocar em um cupcake]
    C --> D[Ver detalhes:<br/>foto, ingredientes, alergênicos, preço]
    D --> E{Quer comprar?}
    E -- Não --> A
    E -- Sim --> F[Escolher quantidade 1–20]
    F --> G[Adicionar ao carrinho]
    G --> H{Continuar<br/>comprando?}
    H -- Sim --> A
    H -- Não --> J[Abrir carrinho e revisar]
    J --> K[Tocar em Finalizar]
    K --> L{Está logado?}
    L -- Não --> L1[Login ou cadastro] --> M
    L -- Sim --> M[Informar endereço e pagamento]
    M --> N{Dados válidos?}
    N -- Não --> N1[Exibir erros nos campos] --> M
    N -- Sim --> O{Itens ainda<br/>ativos?}
    O -- Não --> O1[Remover itens inativos<br/>e avisar MSG15] --> J
    O -- Sim --> P[Gravar pedido com status RECEBIDO]
    P --> Q[Esvaziar carrinho]
    Q --> R[Exibir confirmação com nº do pedido]
    R --> F2((Fim))
```

---

## 2.5 Diagrama de Estados – Pedido

Este diagrama formaliza a regra **RN07**, que define quais mudanças de status são permitidas.

<sub>🖼 Versão em imagem: [estados-pedido.png](diagramas/estados-pedido.png)</sub>

```mermaid
stateDiagram-v2
    [*] --> RECEBIDO : cliente confirma pedido
    RECEBIDO --> EM_PREPARO : admin inicia produção
    RECEBIDO --> CANCELADO : cliente ou admin cancela
    EM_PREPARO --> SAIU_PARA_ENTREGA : admin despacha
    EM_PREPARO --> CANCELADO : admin cancela
    SAIU_PARA_ENTREGA --> ENTREGUE : admin confirma entrega
    ENTREGUE --> [*]
    CANCELADO --> [*]
```
