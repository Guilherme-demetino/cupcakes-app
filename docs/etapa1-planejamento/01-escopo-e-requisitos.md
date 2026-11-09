# 1. Escopo e Requisitos – CupcakeApp

**Projeto:** CupcakeApp – aplicação web responsiva (mobile-first) para uma loja de cupcakes gourmet
**Aluno:** Guilherme França Demetino – RGM 33160236
**Disciplina:** Projeto Integrador Transdisciplinar em Engenharia de Software II – Situação 1

---

## 1.1 Revisão do PI I (Kaizen – melhoria contínua)

No Projeto Integrador I, a situação-problema escolhida foi o **app mobile de uma loja de cupcakes gourmet**. O trabalho especificou uma única história de usuário, a **US05**: *"Como cliente, eu quero ver os detalhes de um cupcake, para que possa decidir com segurança antes de comprar"*. Junto com ela vieram critérios de aceitação, uma regra de negócio (todo produto tem foto e descrição) e um requisito não funcional (imagens otimizadas).

Ao revisar esse planejamento para executá-lo, identificamos os pontos abaixo:

| # | Ponto identificado na revisão | Melhoria adotada no PI II |
|---|---|---|
| 1 | O escopo cobria apenas a tela de detalhes. Sozinha, ela não forma um produto utilizável. | Escopo ampliado para o fluxo completo de compra: catálogo → detalhes → carrinho → pedido, além da área administrativa. |
| 2 | Não havia modelagem UML. | Criação dos diagramas de casos de uso, classes, sequência, atividades e estados (documento 02). |
| 3 | Não havia protótipo de telas nem catálogo de mensagens. | Mapa de navegação, especificação das telas, catálogo de mensagens e protótipo navegável (documento 03). |
| 4 | Não havia projeto de dados. | Modelos conceitual, lógico normalizado e físico (PostgreSQL), além do dicionário de dados (documentos 04 e 05). |
| 5 | A US05 citava "ingredientes" como um texto livre. | Ingredientes viraram uma entidade própria, com marcação de **alergênicos**. Isso permite exibir alertas ao cliente e respeita a 1ª Forma Normal. |
| 6 | O RNF "imagens otimizadas" não era mensurável. | O RNF passou a ter métrica: imagem ≤ 200 KB em formato WebP e carregamento da tela de detalhes em menos de 3 s em rede 4G. |
| 7 | "App mobile" exigiria uma tecnologia nativa, fora das linguagens pedidas no PI II. | Adotada uma **aplicação web responsiva mobile-first**, em HTML/CSS/JS no front-end e MVC no back-end. Ela roda no navegador do celular e atende ao enunciado do PI II. |

## 1.2 Visão do produto

> Para **clientes que querem comprar cupcakes gourmet pelo celular**, o **CupcakeApp** é uma loja online que mostra **todos os detalhes de cada produto** (foto, ingredientes, alergênicos, tamanho e preço) e permite **montar e acompanhar o pedido**. O objetivo é reduzir dúvidas e insatisfações com o produto recebido. Diferente de pedir por mensagem de WhatsApp, o cliente vê o cardápio sempre atualizado, sabe exatamente o que está comprando e acompanha o status do pedido.

## 1.3 Escopo

**Dentro do escopo**
- Cadastro e login de clientes.
- Catálogo de cupcakes com filtro por categoria e busca por nome.
- Tela de detalhes do produto (US05 original).
- Carrinho de compras.
- Finalização do pedido com endereço de entrega e forma de pagamento escolhida (o pagamento é feito na entrega).
- Histórico e acompanhamento do status dos pedidos.
- Área administrativa para cadastrar, editar e desativar cupcakes e para atualizar o status dos pedidos.

**Fora do escopo (versões futuras)**
- Pagamento online integrado (gateway de cartão ou PIX automático).
- Cálculo de frete por distância. Nesta versão a taxa de entrega é fixa.
- Notificações push e e-mail.
- Programa de fidelidade e cupons de desconto.
- Aplicativo nativo publicado nas lojas (Android/iOS).

## 1.4 Atores (personas)

| Ator | Descrição |
|---|---|
| **Visitante** | Pessoa não autenticada. Pode navegar no catálogo, ver detalhes e montar o carrinho. |
| **Cliente** | Usuário cadastrado e autenticado. Pode finalizar pedidos e acompanhá-los. |
| **Administrador** | Funcionário da loja. Mantém o catálogo e atualiza o status dos pedidos. |

**Persona principal – Mariana, 29 anos.** Analista administrativa que compra doces para aniversários do escritório pelo celular, no horário de almoço. Ela tem intolerância a lactose, por isso precisa ver os ingredientes antes de comprar. Já se frustrou ao receber um produto diferente do que imaginava.

## 1.5 Histórias de usuário

Prioridade pelo método **MoSCoW**: M = Must (obrigatória), S = Should (importante), C = Could (desejável). A estimativa está em *story points* (Fibonacci).

| ID | História | Prioridade | Pontos |
|---|---|---|---|
| US01 | Como **visitante**, quero me cadastrar, para poder fazer pedidos. | M | 3 |
| US02 | Como **cliente**, quero fazer login e logout, para acessar minha conta com segurança. | M | 3 |
| US03 | Como **visitante**, quero ver o catálogo de cupcakes, para conhecer as opções da loja. | M | 3 |
| US04 | Como **visitante**, quero filtrar por categoria e buscar por nome, para encontrar rápido o que desejo. | S | 2 |
| US05 | Como **cliente**, quero ver os detalhes de um cupcake, para que possa decidir com segurança antes de comprar. *(história original do PI I)* | M | 3 |
| US06 | Como **visitante**, quero adicionar, alterar e remover itens do carrinho, para montar meu pedido. | M | 5 |
| US07 | Como **cliente**, quero finalizar o pedido informando endereço e forma de pagamento, para receber os cupcakes em casa. | M | 5 |
| US08 | Como **cliente**, quero ver meus pedidos e o status de cada um, para acompanhar a entrega. | S | 3 |
| US09 | Como **cliente**, quero cancelar um pedido que ainda não entrou em preparo, para corrigir uma compra errada. | C | 2 |
| US10 | Como **administrador**, quero cadastrar, editar e desativar cupcakes, para manter o cardápio atualizado. | M | 5 |
| US11 | Como **administrador**, quero ver os pedidos e atualizar o status deles, para organizar a produção e a entrega. | M | 3 |

### 1.5.1 Critérios de aceitação (formato Dado / Quando / Então)

**US01 – Cadastro**
- *Dado* que estou na tela de cadastro, *quando* preencho nome, e-mail, telefone e senha válidos, *então* minha conta é criada e entro logado no sistema.
- *Dado* que informo um e-mail já cadastrado, *quando* envio o formulário, *então* vejo a mensagem **MSG03** e a conta não é criada.
- *Dado* que informo uma senha com menos de 8 caracteres, *quando* envio o formulário, *então* vejo a mensagem **MSG04**.

**US02 – Login**
- *Dado* que tenho conta, *quando* informo e-mail e senha corretos, *então* sou levado à tela de onde vim (catálogo ou carrinho).
- *Dado* que erro o e-mail ou a senha, *quando* tento entrar, *então* vejo **MSG05**, sem o sistema dizer qual dos dois está errado.
- *Dado* que estou logado, *quando* clico em "Sair", *então* minha sessão é encerrada.

**US03 – Catálogo**
- *Dado* que abro o app, *quando* a tela inicial carrega, *então* vejo os cupcakes **ativos**, cada um com foto, nome e preço.
- *Dado* que um cupcake foi desativado pelo administrador, *quando* abro o catálogo, *então* ele não aparece.
- *Dado* que não há cupcakes ativos, *quando* abro o catálogo, *então* vejo **MSG10**.

**US04 – Filtro e busca**
- *Dado* que estou no catálogo, *quando* seleciono uma categoria, *então* vejo apenas os cupcakes dessa categoria.
- *Dado* que digito um termo na busca, *quando* confirmo, *então* vejo os cupcakes cujo nome contém o termo, sem diferenciar maiúsculas de minúsculas.
- *Dado* que a busca não encontra resultados, *então* vejo **MSG11**.

**US05 – Detalhes do produto** *(revisados a partir do PI I)*
- *Dado* que estou no catálogo, *quando* toco em um cupcake, *então* vejo foto, nome, descrição, ingredientes, tamanho, peso e preço.
- *Dado* que o cupcake contém ingredientes alergênicos, *quando* vejo os detalhes, *então* esses ingredientes aparecem destacados com o aviso "Contém alergênicos".
- *Dado* que estou nos detalhes, *quando* escolho a quantidade (1 a 20) e toco em "Adicionar ao carrinho", *então* o item vai para o carrinho e vejo a confirmação **MSG20**.
- *Dado* que acesso o endereço de um cupcake inexistente ou desativado, *então* vejo **MSG12** e um botão para voltar ao catálogo.

**US06 – Carrinho**
- *Dado* que adicionei itens, *quando* abro o carrinho, *então* vejo cada item com quantidade e subtotal, além da taxa de entrega e do total geral.
- *Dado* que altero a quantidade de um item, *então* o subtotal e o total são recalculados na hora.
- *Dado* que adiciono um cupcake que já está no carrinho, *então* a quantidade é somada à existente, sem criar uma linha duplicada.
- *Dado* que tento ultrapassar 20 unidades de um item, *então* vejo **MSG13** e a quantidade fica em 20.
- *Dado* que removo o último item, *então* vejo **MSG14**.

**US07 – Finalizar pedido**
- *Dado* que tenho itens no carrinho e não estou logado, *quando* toco em "Finalizar", *então* sou levado ao login e depois volto ao checkout com o carrinho preservado.
- *Dado* que estou logado, *quando* informo um endereço válido e a forma de pagamento, *então* o pedido é registrado com status **RECEBIDO**, o carrinho é esvaziado e vejo a tela de confirmação com o número do pedido.
- *Dado* que deixo um campo obrigatório do endereço vazio ou informo um CEP inválido, *então* vejo **MSG06** ou **MSG07** ao lado do campo.
- *Dado* que um cupcake do carrinho foi desativado enquanto eu comprava, *quando* finalizo, *então* vejo **MSG15** e o item é retirado do carrinho.

**US08 – Meus pedidos**
- *Dado* que estou logado, *quando* abro "Meus pedidos", *então* vejo meus pedidos do mais recente para o mais antigo, com data, total e status.
- *Dado* que toco em um pedido, *então* vejo os itens, o endereço e o histórico de status.

**US09 – Cancelar pedido**
- *Dado* que meu pedido está com status **RECEBIDO**, *quando* toco em "Cancelar" e confirmo, *então* o status muda para **CANCELADO**.
- *Dado* que meu pedido já está **EM_PREPARO** ou em uma etapa posterior, *então* o botão "Cancelar" não aparece.

**US10 – Manter catálogo (admin)**
- *Dado* que sou administrador, *quando* cadastro um cupcake com todos os campos obrigatórios, *então* ele aparece no catálogo.
- *Dado* que tento salvar um cupcake sem foto ou sem descrição, *então* vejo **MSG08** e ele não é salvo (regra RN01).
- *Dado* que desativo um cupcake, *então* ele some do catálogo, mas continua aparecendo nos pedidos antigos.

**US11 – Gerenciar pedidos (admin)**
- *Dado* que sou administrador, *quando* abro "Pedidos", *então* vejo todos os pedidos e posso filtrá-los por status.
- *Dado* que altero o status de um pedido, *então* a mudança só é aceita se seguir a ordem permitida (RN07). Caso contrário, vejo **MSG16**.

## 1.6 Regras de negócio

| ID | Regra |
|---|---|
| **RN01** | Todo cupcake deve ter **foto e descrição** cadastradas para ser salvo. *(regra original do PI I)* |
| RN02 | O preço de um cupcake deve ser maior que zero. |
| RN03 | A quantidade por item no carrinho ou no pedido vai de **1 a 20** unidades. |
| RN04 | Cupcakes inativos não aparecem no catálogo e não podem ser adicionados ao carrinho. |
| RN05 | O preço de cada item fica **congelado** no momento do pedido. Mudar o preço do cupcake depois não altera pedidos já feitos. |
| RN06 | O total do pedido é a soma de (quantidade × preço unitário) de todos os itens, mais a taxa de entrega fixa de **R$ 8,00**. |
| RN07 | Fluxo de status permitido: RECEBIDO → EM_PREPARO → SAIU_PARA_ENTREGA → ENTREGUE. O cancelamento só é possível a partir de RECEBIDO (pelo cliente) ou de RECEBIDO/EM_PREPARO (pelo administrador). |
| RN08 | O e-mail é único por usuário. |
| RN09 | A senha tem no mínimo 8 caracteres e é armazenada apenas como **hash** (bcrypt), nunca em texto puro. |
| RN10 | Só é possível finalizar um pedido estando logado e com um endereço de entrega válido. |
| RN11 | Um cupcake que já aparece em algum pedido não pode ser excluído, apenas desativado. Isso preserva o histórico. |

## 1.7 Requisitos não funcionais

| ID | Categoria | Requisito | Como medir |
|---|---|---|---|
| **RNF01** | Desempenho | Imagens dos produtos otimizadas *(evolução do RNF do PI I)*. | Cada imagem ≤ 200 KB, em WebP; a tela de detalhes carrega em < 3 s em 4G (Lighthouse, perfil "Slow 4G"). |
| RNF02 | Usabilidade | Interface mobile-first, utilizável a partir de 360 px de largura. | Testar nos tamanhos 360, 768 e 1280 px sem rolagem horizontal. |
| RNF03 | Usabilidade | Áreas de toque com no mínimo 44 × 44 px. | Inspeção do CSS. |
| RNF04 | Acessibilidade | Contraste de texto WCAG AA e texto alternativo (`alt`) em todas as fotos. | Lighthouse Accessibility ≥ 90. |
| RNF05 | Segurança | Senhas com hash bcrypt; consultas SQL parametrizadas (proteção contra SQL Injection); áreas restritas exigem login. | Revisão de código e testes. |
| RNF06 | Segurança | A área administrativa só é acessível pelo perfil ADMIN. | Teste: um cliente que tenta acessar `/admin` recebe a mensagem MSG17. |
| RNF07 | Manutenibilidade | Arquitetura em camadas no padrão **MVC**. | Estrutura de pastas models/ views/ controllers/. |
| RNF08 | Confiabilidade | Erros inesperados exibem uma mensagem amigável (MSG99) e são registrados em log, sem mostrar detalhes técnicos ao usuário. | Teste forçando uma falha. |
| RNF09 | Portabilidade | Funciona nas duas últimas versões do Chrome, Safari, Firefox e Edge. | Teste manual. |
| RNF10 | Dados | O SGBD é o **PostgreSQL** 14 ou superior. | Script `database/schema.sql`. |

## 1.8 Planejamento das sprints

Sprints de 1 semana. A estimativa considera a disponibilidade de um estudante.

| Sprint | Histórias | Entrega |
|---|---|---|
| 0 | – | Etapa 1 (este documento), repositório Git e ambiente configurado. |
| 1 | US03, US04, US05 | Catálogo e detalhes funcionando com o banco. |
| 2 | US06, US01, US02 | Carrinho, cadastro e login. |
| 3 | US07, US08, US09 | Checkout e acompanhamento de pedidos. |
| 4 | US10, US11 | Área administrativa e testes unitários. |
| 5 | – | Testes com 5 usuários, correções, vídeo e documentação final (Etapa 3). |
