# 📖 Manual de Uso – CupcakeApp

**Projeto Integrador Transdisciplinar em Engenharia de Software II**
**Aluno:** Guilherme França Demetino – RGM 33160236

O CupcakeApp é a loja online de uma confeitaria de cupcakes gourmet. Pelo celular ou pelo computador:

- o **cliente** escolhe os cupcakes, vê ingredientes e alergênicos, faz o pedido e acompanha a entrega;
- o **administrador** (funcionário da loja) cuida do cardápio e faz os pedidos andarem até a entrega.

## Sumário

1. [Instalação e primeiro acesso](#1-instalação-e-primeiro-acesso)
2. [Contas para teste](#2-contas-para-teste)
3. [Guia do cliente](#3-guia-do-cliente)
4. [Guia do administrador](#4-guia-do-administrador)
5. [Mensagens do sistema](#5-mensagens-do-sistema)
6. [Problemas comuns](#6-problemas-comuns)
7. [Para desenvolvedores: rodando os testes](#7-para-desenvolvedores-rodando-os-testes)

---

## 1. Instalação e primeiro acesso

### 1.1 O que é preciso ter instalado

| Programa | Versão | Onde baixar | Observação |
|---|---|---|---|
| **Python** | 3.11 ou superior | python.org/downloads | No Windows, marque **"Add python.exe to PATH"** na primeira tela do instalador |
| **PostgreSQL** | 14 ou superior | postgresql.org/download | Anote a **senha** do usuário `postgres` criada durante a instalação |
| **Git** *(opcional)* | qualquer | git-scm.com | Só é necessário para baixar com `git clone`. Também dá para baixar o .zip pelo GitHub |

### 1.2 Passo a passo (Windows)

**Passo 1 – Baixar o projeto.** No GitHub, clique em **Code → Download ZIP** e descompacte. Ou, pelo terminal:

```powershell
git clone https://github.com/Guilherme-demetino/cupcakes-app.git
cd cupcakes-app
```

**Passo 2 – Configurar a senha do banco.** Na pasta do projeto, copie o arquivo `.env.example` com o nome `.env`. Abra o `.env` no Bloco de Notas e troque a segunda palavra `postgres` (a senha) pela senha que você criou na instalação:

```ini
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/cupcakeapp
SECRET_KEY=qualquer-frase-longa-e-secreta
TEST_DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/cupcakeapp_test
```

**Passo 3 – Instalar as dependências.** Abra o terminal (PowerShell) na pasta do projeto:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> Quando o ambiente virtual está ativo, aparece `(.venv)` no começo da linha do terminal. Repita o `activate` sempre que abrir um terminal novo.

**Passo 4 – Criar o banco, as tabelas e os dados de exemplo** (só na primeira vez):

```powershell
flask --app run init-db
```

Na primeira vez, o comando **cria o banco `cupcakeapp` sozinho** (em UTF-8, para os acentos aparecerem certos). Não é preciso abrir o pgAdmin. A mensagem esperada é **"Banco criado e populado com os dados de exemplo."**

> ⚠️ Este comando **apaga e recria** todo o banco. Use-o de novo só quando quiser voltar aos dados de exemplo.

**Passo 5 – Abrir o sistema:**

```powershell
flask --app run run --debug
```

Abra o navegador em **http://127.0.0.1:5000**. Para parar o sistema, aperte `Ctrl + C` no terminal.

> **Linux / macOS:** os comandos são os mesmos, com duas diferenças: use `source .venv/bin/activate` no lugar de `.venv\Scripts\activate` e `cp .env.example .env` para copiar o arquivo.

---

## 2. Contas para teste

O comando `init-db` cria estas contas, além de 6 cupcakes e 2 pedidos de exemplo:

| Perfil | E-mail | Senha |
|---|---|---|
| Cliente | `mariana@email.com` | `Cupcake@123` |
| Administrador | `admin@cupcakeapp.com.br` | `Admin@2026` |

Também é possível criar novas contas de cliente pela tela **Criar conta**.

---

## 3. Guia do cliente

A **barra inferior** está sempre visível:

- 🏠 **Início:** cardápio;
- 🛒 **Carrinho:** com o número de itens;
- 📦 **Pedidos:** aparece depois de entrar na conta;
- 👤 **Entrar:** depois de entrar, mostra o seu primeiro nome.

### 3.1 Ver o cardápio, buscar e filtrar

| Cardápio | Busca por nome |
|:---:|:---:|
| <img src="manual/01-catalogo.png" width="260" alt="Cardápio"> | <img src="manual/02-busca.png" width="260" alt="Busca"> |

- A tela inicial mostra todos os cupcakes disponíveis, com foto, nome e preço.
- Toque em uma **categoria** (Clássicos, Recheados, Veganos, Zero açúcar) para ver só aquele tipo.
- Digite no campo **Buscar cupcake…** e aperte Enter. Maiúsculas e minúsculas não fazem diferença.
- Se nada for encontrado, o sistema avisa e mostra o botão **Ver todos os cupcakes**.

### 3.2 Ver os detalhes e os alergênicos

| Detalhes do cupcake | Depois de adicionar |
|:---:|:---:|
| <img src="manual/03-detalhes.png" width="260" alt="Detalhes"> | <img src="manual/04-adicionado.png" width="260" alt="Adicionado ao carrinho"> |

1. Toque em um cupcake para abrir os detalhes: foto, descrição, tamanho, peso, preço e **ingredientes**.
2. Os ingredientes **alergênicos** (glúten, leite, ovos, oleaginosas…) aparecem com **⚠ e borda laranja**. Logo abaixo há um aviso com a lista completa.
3. Escolha a quantidade com os botões **−** e **+**, de 1 a 20 unidades por sabor. O botão mostra o valor total.
4. Toque em **Adicionar ao carrinho**. Aparece a confirmação, com um atalho **Ver carrinho**.

### 3.3 Carrinho

<img src="manual/05-carrinho.png" width="260" alt="Carrinho" align="right">

- Use **−** e **+** para mudar a quantidade. O total é recalculado na hora.
- O ícone 🗑 remove o item. Se foi sem querer, toque em **↩ Desfazer remoção**.
- O total inclui a **taxa de entrega fixa de R$ 8,00**.
- Se a loja tirar um cupcake do cardápio enquanto ele está no seu carrinho, ele é retirado automaticamente e aparece um aviso.
- O carrinho continua guardado enquanto o navegador estiver aberto, mesmo trocando de página ou entrando na conta. Ao tocar em **Sair da conta**, ele é esvaziado.

Toque em **Finalizar pedido** para continuar.

<br clear="right">

### 3.4 Entrar ou criar conta

| Entrar | Criar conta (com erro de senha) |
|:---:|:---:|
| <img src="manual/06-login-para-finalizar.png" width="260" alt="Entrar"> | <img src="manual/07-cadastro-erro.png" width="260" alt="Criar conta"> |

- Para finalizar o pedido é preciso ter uma conta. Ao tocar em **Finalizar pedido** sem estar logado, o sistema leva para o login. **O carrinho não se perde.**
- **Já tem conta?** Digite e-mail e senha e toque em **Entrar**. O botão 👁 mostra a senha digitada.
- **Primeira vez?** Toque em **Criar conta** e preencha nome, e-mail, telefone com DDD e senha (mínimo de 8 caracteres). Se algo estiver errado, a mensagem aparece em vermelho embaixo do campo.
- Depois de entrar ou criar a conta, você volta direto para a finalização do pedido.

### 3.5 Finalizar o pedido

| Endereço | Pagamento | Confirmação |
|:---:|:---:|:---:|
| <img src="manual/08-checkout.png" width="230" alt="Endereço"> | <img src="manual/09-checkout-pagamento.png" width="230" alt="Pagamento"> | <img src="manual/10-confirmacao.png" width="230" alt="Confirmação"> |

1. Confira o **resumo** no topo.
2. Preencha o **endereço de entrega**. Ao digitar o **CEP**, rua, bairro e cidade são preenchidos sozinhos (é preciso estar conectado à internet). Nos próximos pedidos, o último endereço já vem preenchido.
3. Escolha como vai **pagar na entrega**: PIX, cartão (maquininha) ou dinheiro. Se precisar de troco, avise no campo **Observação**.
4. Toque em **Confirmar pedido**. Aparece o **número do pedido**, e o carrinho é esvaziado.

### 3.6 Acompanhar e cancelar pedidos

| Meus pedidos | Andamento do pedido | Cancelar |
|:---:|:---:|:---:|
| <img src="manual/11-meus-pedidos.png" width="230" alt="Meus pedidos"> | <img src="manual/12-acompanhar.png" width="230" alt="Acompanhar"> | <img src="manual/13-cancelar.png" width="230" alt="Cancelar"> |

- Em 📦 **Pedidos** aparecem todos os seus pedidos, do mais recente para o mais antigo, com uma etiqueta colorida de status.
- Toque em um pedido para ver a **linha do tempo**: Recebido → Em preparo → Saiu para entrega → Entregue, com data e hora de cada etapa. Também aparecem os itens, o endereço e a forma de pagamento.
- **Cancelar:** o botão **Cancelar pedido** só aparece enquanto o pedido está **Recebido**. O sistema pede confirmação antes de cancelar. Depois que a loja começa o preparo, não dá mais para cancelar pelo app. Nesse caso, fale com a loja.

### 3.7 Minha conta e sair

<img src="manual/14-conta.png" width="260" alt="Minha conta" align="right">

Em 👤 (seu nome) você vê seus dados, tem atalhos para os pedidos e o carrinho e encontra o botão **Sair da conta**.

> Usando um computador ou celular compartilhado? Sempre toque em **Sair da conta** ao terminar.

<br clear="right">

---

## 4. Guia do administrador

Entre com a conta de administrador (veja a [seção 2](#2-contas-para-teste)). Você vai direto para a lista de pedidos, e a barra inferior muda para o **menu da loja**:

- 📋 **Pedidos**;
- 🧁 **Cupcakes**;
- 🏪 **Ver loja:** mostra a loja como o cliente vê;
- 👤 **Conta.**

> Clientes não conseguem abrir nenhuma página de administrador. Se tentarem, veem a mensagem "Você não tem permissão para acessar esta página."

### 4.1 Pedidos: do recebimento à entrega

| Lista de pedidos | Detalhe do pedido | Depois de avançar |
|:---:|:---:|:---:|
| <img src="manual/20-admin-pedidos.png" width="230" alt="Lista de pedidos"> | <img src="manual/21-admin-pedido.png" width="230" alt="Detalhe"> | <img src="manual/22-admin-status.png" width="230" alt="Status avançado"> |

- **Lista:** os pedidos **em andamento aparecem primeiro**, do mais antigo para o mais novo, ou seja, quem pediu antes é atendido antes. Os entregues e cancelados ficam no final. Use os filtros no topo (Recebido, Em preparo…) para ver só um status. O número ao lado de cada filtro mostra quantos pedidos há nele.
- **Botão rápido:** em cada pedido da lista há um botão com o próximo passo, como **Iniciar preparo**, sem precisar abrir o pedido.
- **Detalhe:** mostra o cliente com o **telefone clicável** (no celular, já faz a ligação), o endereço, a forma de pagamento, a **observação em destaque** (troco, interfone…), os **itens a preparar**, o total a receber e o histórico.

**O caminho de um pedido:**

| Status | O que significa | Botão para avançar |
|---|---|---|
| 🔵 Recebido | O cliente acabou de pedir | **Iniciar preparo** |
| 🟠 Em preparo | A cozinha está fazendo | **Despachar** |
| 🟣 Saiu para entrega | O entregador está a caminho | **Confirmar entrega** |
| 🟢 Entregue | Concluído | — |
| 🔴 Cancelado | Cancelado pelo cliente ou pela loja | — |

- O sistema **não deixa pular etapas** nem voltar atrás.
- A loja pode **cancelar** um pedido Recebido ou Em preparo. Toque em **Cancelar pedido** e confirme em **Sim, cancelar pedido**. Depois que o pedido sai para entrega, não é mais possível cancelar.
- Se duas pessoas mexerem no mesmo pedido ao mesmo tempo, quem estava com a tela desatualizada recebe o aviso "Este pedido foi atualizado por outra pessoa…" e nada é sobrescrito.

### 4.2 Cupcakes: cardápio

| Lista de cupcakes | Novo cupcake com erros | Editar | Ingredientes e foto |
|:---:|:---:|:---:|:---:|
| <img src="manual/23-admin-cupcakes.png" width="190" alt="Lista"> | <img src="manual/24-admin-form-erro.png" width="190" alt="Erros"> | <img src="manual/25-admin-editar.png" width="190" alt="Editar"> | <img src="manual/26-admin-ingredientes.png" width="190" alt="Ingredientes"> |

**Ver a lista:** mostra todos os cupcakes, inclusive os que estão fora do cardápio (em cinza), e quantas vezes cada um foi vendido.

**Tirar ou colocar no cardápio:** use o **interruptor** ao lado do cupcake (verde = à venda). O cupcake fora do cardápio some da loja na hora, mas continua aparecendo nos pedidos antigos.

> Não existe "excluir" de propósito: assim o histórico de vendas nunca perde informação.

**Cadastrar um cupcake novo:** toque em **+ Novo cupcake** e preencha:

| Campo | Regra |
|---|---|
| Nome | Obrigatório. Não pode repetir o nome de outro cupcake |
| Categoria | Obrigatória |
| Descrição | **Obrigatória.** É o texto que o cliente lê nos detalhes |
| Preço | Maior que zero. Pode digitar com vírgula, como `16,90` |
| Peso | De 10 a 1000 gramas |
| Tamanho | Mini, Tradicional ou Gigante |
| Foto | **Obrigatória.** WebP, JPG ou PNG de **até 200 KB**. A foto aparece em pré-visualização antes de salvar |
| Ingredientes | Marque pelo menos um. Os marcados com ⚠ são alergênicos e aparecerão em destaque para o cliente |

Toque em **Salvar**. Se algo estiver faltando, os campos com problema ficam em vermelho, com a explicação embaixo, e nada do que você digitou se perde.

**Editar:** na lista, toque no **nome** do cupcake. Para manter a foto atual, é só não enviar arquivo nenhum. Mudar o preço **não altera** pedidos já feitos: eles guardam o preço do dia da compra.

> 💡 **Dica para as fotos:** para ficar abaixo de 200 KB, salve em **WebP** com cerca de 600 × 600 pixels. Sites gratuitos como o squoosh.app fazem essa conversão.

---

## 5. Mensagens do sistema

| Mensagem | Quando aparece | O que fazer |
|---|---|---|
| "Preencha este campo." | Campo obrigatório vazio | Preencha o campo indicado |
| "Digite um e-mail válido, como nome@exemplo.com." | E-mail em formato errado | Corrija o e-mail |
| "Este e-mail já tem cadastro. Quer entrar na sua conta?" | Criar conta com um e-mail já usado | Toque em **Entrar** |
| "A senha precisa ter pelo menos 8 caracteres." | Senha curta no cadastro | Use uma senha maior |
| "E-mail ou senha incorretos. Confira e tente de novo." | Login com dados errados | Confira o e-mail e a senha (maiúsculas fazem diferença na senha) |
| "Digite um telefone com DDD, como (11) 99999-9999." | Telefone sem DDD | Inclua o DDD |
| "CEP inválido. Digite os 8 números do seu CEP." | CEP incompleto | Digite os 8 números |
| "Informe rua, número, bairro e cidade para a entrega." | Endereço incompleto | Preencha os campos destacados |
| "O máximo é 20 unidades por sabor…" | Mais de 20 unidades de um cupcake | Para encomendas maiores, fale com a loja |
| "O cupcake … acabou de sair do cardápio e foi retirado do seu carrinho." | A loja desativou um item que estava no carrinho | Revise o carrinho e escolha outro sabor |
| "Este cupcake não está mais disponível." | Link de um cupcake fora do cardápio | Toque em **Ver cardápio** |
| "Para salvar, adicione uma foto e uma descrição do cupcake." | *(Admin)* Cadastro sem foto ou sem descrição | Envie a foto e escreva a descrição |
| "O preço deve ser maior que R$ 0,00." | *(Admin)* Preço zerado ou inválido | Corrija o preço |
| "A foto deve ter no máximo 200 KB…" | *(Admin)* Foto pesada | Converta para WebP (veja a dica na seção 4.2) |
| "Não é possível mudar de … para …" | *(Admin)* Tentativa de pular etapa | Siga a ordem do pedido |
| "Você não tem permissão para acessar esta página." | Cliente tentando abrir a área do administrador | — |
| "Algo deu errado do nosso lado…" | Erro inesperado do sistema | Tente de novo em instantes |

---

## 6. Problemas comuns

| Problema | Causa provável | Solução |
|---|---|---|
| `'python' não é reconhecido…` | O Python não foi adicionado ao PATH | Reinstale o Python marcando **"Add python.exe to PATH"** |
| `…não pode ser carregado porque a execução de scripts foi desabilitada` (ao ativar o `.venv`) | Bloqueio de segurança do PowerShell | Rode uma vez: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e responda **S** |
| `'flask' não é reconhecido…` | O ambiente virtual não está ativo | Rode `.venv\Scripts\activate` (aparece `(.venv)` na linha) |
| `Não foi possível conectar ao PostgreSQL…` ou `password authentication failed` | Senha errada no `.env` ou PostgreSQL desligado | Corrija a senha nas duas linhas do `.env`. Se a senha estiver certa, veja a linha abaixo |
| `connection refused` / `could not connect to server` | O PostgreSQL não está rodando | Windows: abra **Serviços**, procure **postgresql** e clique em **Iniciar** |
| `function gen_salt(...) does not exist` | A extensão pgcrypto não está disponível | Ela vem com o instalador oficial do PostgreSQL. No Linux, instale o pacote `postgresql-contrib` |
| O endereço não é preenchido pelo CEP | Sem internet ou o serviço ViaCEP está fora do ar | Digite o endereço manualmente. Todo o resto funciona normalmente |
| As fotos dos cupcakes não aparecem | O sistema foi aberto a partir de outra pasta | Rode os comandos **dentro** da pasta `cupcakes-app` |
| Quero apagar tudo e recomeçar | — | `flask --app run init-db` (apaga e recria os dados de exemplo) |
| A porta 5000 já está em uso | Outro programa está usando essa porta | `flask --app run run --debug --port 5001` e abra http://127.0.0.1:5001 |

---

## 7. Para desenvolvedores: rodando os testes

Com o ambiente virtual ativo (o banco de teste `cupcakeapp_test` é criado sozinho na primeira execução):

```powershell
pytest
```

O resultado esperado é **204 passed**. Os testes recriam o banco `cupcakeapp_test` a cada execução, então **nunca** use nele o mesmo banco do sistema.

Detalhes da arquitetura, das sprints e do que cada teste verifica estão no [README da Etapa 2](README.md).
