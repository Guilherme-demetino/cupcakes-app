# 🧁 CupcakeApp

Loja online responsiva (mobile-first) de cupcakes gourmet: catálogo com detalhes completos e alergênicos, carrinho, pedidos com acompanhamento de status e área administrativa.

Projeto Integrador Transdisciplinar em Engenharia de Software II
**Aluno:** Guilherme França Demetino – RGM 33160236

## Documentação

| Etapa | Conteúdo | Status |
|---|---|---|
| [Etapa 1 – Planejamento](docs/etapa1-planejamento/) | Escopo, histórias de usuário, UML, IHC, protótipo, banco de dados e dicionário | ✅ Concluída |
| Etapa 2 – Desenvolvimento | Front-end, back-end MVC, testes unitários e manual de uso | ⏳ Em andamento |
| Etapa 3 – Validação | Testes de verificação e validação, avaliação de 5 usuários, correções e vídeo | ⏳ A fazer |

## Tecnologias

- **Banco de dados:** PostgreSQL 14+
- **Front-end:** HTML, CSS e JavaScript
- **Back-end:** padrão MVC *(linguagem a definir na Etapa 2)*

## Como criar o banco

```bash
createdb cupcakeapp
psql -d cupcakeapp -f database/schema.sql
psql -d cupcakeapp -f database/seed.sql
```

## Estrutura do repositório

```
cupcakes-app/
├── docs/
│   ├── etapa1-planejamento/
│   ├── etapa2-desenvolvimento/
│   └── etapa3-validacao/
├── database/        ← schema.sql e seed.sql
├── src/             ← código (Etapa 2)
└── tests/           ← testes (Etapa 2)
```
