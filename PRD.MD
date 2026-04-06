# PRD - Product Requirements Document
## ECommerce Platform - VMI (Vendor Managed Inventory)

**Versão:** 0.3
**Data:** 2026-04-06
**Status:** Rascunho

---

## 1. Visão Geral

Plataforma de e-commerce baseada no modelo **VMI (Vendor Managed Inventory)**, onde o fornecedor
é responsável por gerenciar o estoque dos produtos vinculados a ele. O sistema possui três perfis
de acesso: **Admin**, **Usuário** e **Fornecedor**.

Construído com Python/FastAPI no backend e uma interface web no frontend, o projeto serve como
base de estudo de algoritmos, arquitetura de software e integração cliente-servidor. Toda lógica
de busca e ordenação é implementada manualmente (conforme `RULES.md`).

---

## 2. Objetivos

- Implementar o modelo VMI: o fornecedor controla o estoque dos produtos que ele fornece.
- Construir uma API RESTful completa com três perfis de acesso distintos.
- Construir uma interface web para Admin, Usuário e Fornecedor consumirem a API.
- Implementar algoritmos de busca e ordenação do zero, sem usar funções nativas.
- Seguir boas práticas de arquitetura em camadas (Routes -> Services -> Repositories -> Models).
- Servir como base de estudo e evolução incremental do código.

---

## 3. Perfis de Usuário

| Perfil | Descrição |
|--------|-----------|
| Admin | Cadastra e gerencia usuários e fornecedores. Visão geral do sistema. |
| Usuário | Cria pedidos de compra e gerencia seu próprio estoque de produtos. |
| Fornecedor | Gerencia seu próprio estoque, seus clientes vinculados e os produtos associados a ele. |

---

## 4. Regras de Negócio

### RN-01 - Cadastro centralizado no Admin
Apenas o **Admin** pode cadastrar novos usuários e novos fornecedores. Usuários e fornecedores
não se auto-cadastram.

### RN-02 - Vínculo Produto <-> Fornecedor (N:N)
Ao cadastrar um produto, o **Usuário** deve vincular aquele produto a pelo menos um fornecedor.
Um mesmo produto pode ser fornecido por múltiplos fornecedores (ex.: "Caneta" pode ser fornecida
por Fornecedor X e Fornecedor Y). Cada vínculo produto-fornecedor possui um **contrato** próprio
com condições específicas (preço contratado, prazo de entrega, quantidade mínima de pedido).

### RN-03 - Gestão de estoque pelo Fornecedor (VMI)
O **Fornecedor** gerencia o estoque dos produtos vinculados a ele. O usuário visualiza o estoque,
mas quem atualiza a quantidade disponível é o fornecedor.

### RN-04 - Visibilidade restrita
- O Fornecedor vê apenas seus próprios produtos, clientes vinculados a ele e pedidos relacionados.
- O Usuário vê apenas seus próprios pedidos e os produtos disponíveis.
- O Admin tem visão completa do sistema.

### RN-05 - Pedido de compra
O Usuário cria um pedido de compra selecionando produtos. O pedido é direcionado automaticamente
ao fornecedor do produto. O fornecedor pode visualizar e atualizar o status do pedido.

### RN-06 - Semáforo de estoque (Kanban: Verde / Amarelo / Vermelho)
Cada item de estoque possui três faixas configuráveis pelo usuário:

| Cor | Condição | Significado |
|-----|----------|-------------|
| Verde | quantidade >= ponto_amarelo | Estoque saudável |
| Amarelo | ponto_reposicao < quantidade < ponto_amarelo | Atenção - estoque em queda |
| Vermelho | quantidade <= ponto_reposicao | Crítico - reposição necessária |

- `ponto_amarelo` e `ponto_reposicao` são definidos pelo usuário por produto.
- O semáforo é recalculado a cada atualização de estoque.

### RN-07 - Pedido automático por ponto de reposição
Quando um item atinge o status **Amarelo** (quantidade < ponto_amarelo) ou **Vermelho**
(quantidade <= ponto_reposicao), o sistema habilita o botão **"Enviar Pedido de Reposição"**.

- O botão fica visível para todos os itens com status Amarelo ou Vermelho.
- Ao acionar o botão, o sistema cria automaticamente um pedido de compra para o fornecedor
  definido no contrato ativo daquele produto (RN-02).
- Se o produto tiver múltiplos fornecedores, o sistema usa o fornecedor marcado como
  **preferencial** no contrato; se não houver preferencial, o usuário escolhe antes de confirmar.
- O pedido é criado com a **quantidade mínima** definida no contrato (RN-02).
- O pedido gerado automaticamente recebe a flag `origem: "automatico"` para rastreamento.

---

## 5. Funcionalidades por Perfil

### 5.1 Admin
- [ ] Cadastrar usuário (nome, e-mail, senha, role)
- [ ] Listar e buscar usuários (algoritmo manual - R-ALG-01)
- [ ] Cadastrar fornecedor (nome, e-mail, senha, CNPJ)
- [ ] Listar e buscar fornecedores (algoritmo manual - R-ALG-01)
- [ ] Desativar usuário ou fornecedor
- [ ] Visualizar todos os pedidos do sistema

### 5.2 Usuário
- [ ] Visualizar catálogo de produtos disponíveis
- [ ] Buscar produto por nome ou categoria (algoritmo manual - R-ALG-01)
- [ ] Ordenar produtos por preço ou nome (algoritmo manual - R-ALG-02)
- [ ] Cadastrar produto vinculando-o a um fornecedor (RN-02)
- [ ] Visualizar seu próprio estoque com semáforo Kanban (Verde / Amarelo / Vermelho)
- [ ] Configurar pontos de reposição por produto (ponto_reposicao, ponto_amarelo)
- [ ] Acionar botão "Enviar Pedido de Reposição" para itens em Amarelo ou Vermelho (RN-07)
- [ ] Criar pedido de compra manualmente
- [ ] Listar seus pedidos (com indicação de origem: manual ou automático)
- [ ] Detalhar pedido

### 5.3 Fornecedor
- [ ] Visualizar produtos vinculados a ele
- [ ] Atualizar estoque dos seus produtos (VMI - RN-03)
- [ ] Adicionar / remover produto do seu catálogo
- [ ] Visualizar clientes (usuários) vinculados a ele
- [ ] Visualizar e atualizar status dos pedidos recebidos
- [ ] Buscar produto por nome (algoritmo manual - R-ALG-01)
- [ ] Ordenar produtos por nome ou estoque (algoritmo manual - R-ALG-02)

### 5.4 Frontend Web
- [ ] Tela de login com autenticação por e-mail e senha
- [ ] Persistir sessão do usuário autenticado com controle de acesso por perfil
- [ ] Dashboard do Admin com atalhos para usuários, fornecedores e pedidos
- [ ] Dashboard do Usuário com visão do catálogo, estoque, semáforo e pedidos
- [ ] Dashboard do Fornecedor com visão do catálogo vinculado, clientes e pedidos recebidos
- [ ] Tela de listagem de usuários com busca manual e estado de ativação
- [ ] Tela de listagem de fornecedores com busca manual e estado de ativação
- [ ] Tela de catálogo de produtos com busca e ordenação manual
- [ ] Tela de cadastro de produto com vínculo a um ou mais fornecedores
- [ ] Tela de estoque do usuário com indicadores Verde / Amarelo / Vermelho
- [ ] Exibir botão "Enviar Pedido de Reposição" apenas para itens em Amarelo ou Vermelho
- [ ] Tela de pedidos do usuário com filtro por origem (manual / automático) e detalhamento
- [ ] Tela de pedidos do fornecedor com atualização de status
- [ ] Feedback visual para carregamento, sucesso e erro nas operações principais
- [ ] Navegação protegida conforme o papel do usuário autenticado
- [ ] Layout responsivo para desktop e mobile

---

## 6. Requisitos de Frontend

### 6.1 Objetivo da interface
A interface web deve permitir que os três perfis do sistema executem suas tarefas sem depender
diretamente do Swagger. O frontend deve consumir a API REST e refletir com clareza as regras de
negócio do domínio VMI.

### 6.2 Telas mínimas

#### Admin
- Login
- Dashboard
- Cadastro de usuário
- Listagem/busca de usuários
- Cadastro de fornecedor
- Listagem/busca de fornecedores
- Listagem de todos os pedidos

#### Usuário
- Login
- Dashboard
- Catálogo de produtos
- Cadastro de produto
- Estoque com semáforo
- Configuração de pontos de reposição
- Criação de pedido manual
- Listagem de pedidos
- Detalhe do pedido

#### Fornecedor
- Login
- Dashboard
- Produtos vinculados
- Gestão de estoque
- Clientes vinculados
- Pedidos recebidos

### 6.3 Comportamentos esperados da interface
- O menu e as rotas visíveis devem mudar conforme o perfil autenticado.
- A interface deve bloquear acesso a páginas incompatíveis com o perfil do usuário.
- O semáforo de estoque deve ser exibido de forma visual e textual.
- A ação de reposição deve estar disponível apenas quando a regra RN-07 for satisfeita.
- As listagens com busca e ordenação devem refletir os algoritmos implementados no backend.
- Mensagens de erro da API devem ser apresentadas ao usuário de forma clara.
- Formulários devem validar campos obrigatórios antes do envio.
- A interface deve permitir logout e limpeza da sessão autenticada.

---

## 7. Requisitos Não-Funcionais

| ID | Requisito |
|----|-----------|
| RNF-01 | API RESTful com FastAPI |
| RNF-02 | Banco de dados relacional (SQLite para dev, PostgreSQL para prod) |
| RNF-03 | Autenticação via JWT com controle de role (admin/usuario/fornecedor) |
| RNF-04 | Busca e ordenação sem funções nativas (ver `RULES.md`) |
| RNF-05 | Cobertura de testes unitários mínima de 80% |
| RNF-06 | Documentação automática via Swagger (FastAPI nativo) |
| RNF-07 | Endpoints protegidos por role - cada perfil acessa apenas o que lhe compete |
| RNF-08 | Frontend web responsivo para desktop e mobile |
| RNF-09 | Controle de rotas e sessão no frontend compatível com autenticação JWT |
| RNF-10 | Integração frontend-backend com tratamento explícito de loading e erro |
| RNF-11 | Interface com linguagem simples e adequada ao contexto acadêmico |

---

## 8. Modelo de Dados (visão simplificada)

```text
User (id, nome, email, senha_hash, role, ativo)
  role: "admin" | "usuario" | "fornecedor"

Fornecedor (id, user_id -> User, nome, cnpj)

Produto (id, nome, descricao, categoria)
  - sem fornecedor_id direto; o vínculo é feito via ProdutoFornecedor

ProdutoFornecedor (
  id,
  produto_id -> Produto,
  fornecedor_id -> Fornecedor,
  preferencial,
  preco_contratado,
  prazo_entrega_dias,
  qtd_minima_pedido
)
  - tabela de contrato N:N entre Produto e Fornecedor
  - preferencial: bool - indica o fornecedor padrão para reposição automática

Estoque (id, produto_id -> Produto, usuario_id -> User, quantidade, ponto_reposicao, ponto_amarelo)
  - gerenciado pelo Fornecedor (VMI)
  - semáforo calculado a partir de quantidade vs. ponto_reposicao e ponto_amarelo

PedidoCompra (id, usuario_id -> User, status, origem, criado_em)
  status: "pendente" | "confirmado" | "enviado" | "entregue" | "cancelado"
  origem: "manual" | "automatico"

ItemPedido (id, pedido_id -> PedidoCompra, produto_fornecedor_id -> ProdutoFornecedor, quantidade, preco_unitario)
  - referencia o contrato específico (produto + fornecedor) para rastrear qual fornecedor atendeu
```

---

## 9. Fora do Escopo (v0.3)

- Gateway de pagamento
- Sistema de avaliações/reviews
- Notificações por e-mail
- Reposição automática de estoque sem ação do usuário
- Aplicativo mobile nativo
- Dashboard analítico avançado com gráficos

---

## 10. Stack Tecnológica

| Componente | Tecnologia |
|------------|------------|
| Linguagem Backend | Python 3.12+ |
| Framework Backend | FastAPI |
| ORM | SQLAlchemy |
| Banco (dev) | SQLite |
| Banco (prod) | PostgreSQL |
| Autenticação | JWT (`python-jose`) |
| Validação | Pydantic v2 |
| Testes Backend | pytest |
| Frontend | A definir (SPA web) |
