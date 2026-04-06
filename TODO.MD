# TODO - VMI WebMarket

Checklist consolidado com base no `PRD.MD` v0.3 e nas restrições definidas em `RULES.MD`.

Legenda:
- `[x]` concluído
- `[ ]` não iniciado ou pendente
- `[~]` parcial

---

## 1. Responsáveis

### Pessoa 1 - Guilherme Tavares
- Domínio: autenticação, usuários e administração
- Arquivos:
  - `app/core/security.py`
  - `app/database.py`
  - `app/dependencies.py`
  - `app/models/user.py`
  - `app/schemas/token.py`
  - `app/schemas/user.py`
  - `app/repositories/user_repository.py`
  - `app/services/auth_service.py`
  - `app/services/user_service.py`
  - `app/routes/auth.py`
  - `app/routes/admin.py`
  - `tests/test_auth.py`
  - `tests/test_admin.py`
- Responsabilidade: login, JWT, hash de senha, criação de usuários (`admin`, `fornecedor`, `usuario`) e desativação de contas

### Pessoa 2 - Ingrid Souza
- Domínio: produtos, fornecedores e contratos
- Arquivos:
  - `app/models/produto.py`
  - `app/models/produto_fornecedor.py`
  - `app/models/fornecedor.py`
  - `app/schemas/produto.py`
  - `app/schemas/produto_fornecedor.py`
  - `app/schemas/fornecedor.py`
  - `app/repositories/produto_repository.py`
  - `app/repositories/fornecedor_repository.py`
  - `app/services/produto_service.py`
  - `app/services/fornecedor_service.py`
  - `app/routes/fornecedor.py` (parcial - endpoints de produto/contrato)
  - `tests/test_fornecedor.py`
- Responsabilidade: CRUD de produtos, busca linear, ordenação por insertion sort, vínculo produto <-> fornecedor (N:N) e gerenciamento de fornecedores

### Pessoa 3 - Guilherme Tavares
- Domínio: estoque (VMI) e pedidos
- Arquivos:
  - `app/models/estoque.py`
  - `app/models/pedido_compra.py`
  - `app/models/item_pedido.py`
  - `app/schemas/estoque.py`
  - `app/schemas/pedido_compra.py`
  - `app/schemas/item_pedido.py`
  - `app/repositories/estoque_repository.py`
  - `app/repositories/pedido_compra_repository.py`
  - `app/repositories/item_pedido_repository.py`
  - `app/services/estoque_service.py`
  - `app/services/pedido_service.py`
  - `app/routes/usuario.py`
  - `app/routes/fornecedor.py` (parcial - endpoints de estoque/pedido)
  - `tests/test_estoque.py`
  - `tests/test_pedido.py`
- Responsabilidade: controle de estoque VMI, cálculo do status Kanban e criação de pedidos manuais e automáticos por threshold

### Frontend - Stephanie
- Domínio: interface web
- Responsabilidade: telas, navegação, sessão, integração com a API e responsividade

### Observações de coordenação
- [x] Separar `app/routes/fornecedor.py` em:
  - `app/routes/fornecedor_produto.py` -> Ingrid Souza
  - `app/routes/fornecedor_estoque.py` -> Guilherme Tavares
- [x] Implementar primeiro a base de autenticação e `current_user`, pois produtos, estoque e pedidos dependem disso nas rotas

---

## 2. Definições Iniciais

- [ ] Definir a stack do frontend SPA web
- [ ] Definir padrão de gerenciamento de sessão no frontend
- [ ] Definir convenção de organização das telas e componentes
- [~] Confirmar estratégia de integração entre frontend e backend
  - Backend já expõe API HTTP com autenticação JWT, mas o frontend ainda não existe

---

## 3. Backend - Autenticação e Autorização

Responsável: Guilherme Tavares

- [x] Implementar autenticação com JWT
- [x] Implementar endpoint de login consumível pelo frontend
- [x] Implementar controle de acesso por perfil (`admin`, `usuario`, `fornecedor`)
- [x] Proteger endpoints conforme o perfil permitido
- [x] Garantir retorno padronizado de erros de autenticação e autorização

---

## 4. Backend - Admin

Responsável: Guilherme Tavares

- [x] Implementar cadastro de usuário
- [x] Implementar listagem de usuários
- [x] Implementar busca manual de usuários
- [x] Implementar cadastro de fornecedor
- [x] Implementar listagem de fornecedores
- [x] Implementar busca manual de fornecedores
- [x] Implementar desativação de usuário
- [x] Implementar desativação de fornecedor
- [x] Implementar visualização de todos os pedidos do sistema

---

## 5. Backend - Usuário

Responsáveis:
- Ingrid Souza: catálogo, busca, ordenação e cadastro de produto com vínculo a fornecedor
- Guilherme Tavares: estoque, pedidos e regras de reposição

- [ ] Implementar visualização de catálogo de produtos
- [ ] Implementar busca manual de produtos por nome
- [ ] Implementar busca manual de produtos por categoria
- [ ] Implementar ordenação manual de produtos por preço
- [ ] Implementar ordenação manual de produtos por nome
- [ ] Implementar cadastro de produto com vínculo a fornecedor
- [x] Implementar configuração de pontos de reposição por produto
- [x] Implementar visualização do estoque do usuário
- [x] Implementar detalhamento de pedido
- [x] Implementar listagem dos pedidos do usuário
- [x] Implementar criação de pedido manual

---

## 6. Backend - Fornecedor

Responsáveis:
- Ingrid Souza: produtos, catálogo e fornecedores
- Guilherme Tavares: estoque e pedidos recebidos

- [ ] Implementar visualização de produtos vinculados ao fornecedor
- [x] Implementar atualização de estoque dos produtos vinculados
- [ ] Implementar adição de produto ao catálogo do fornecedor
- [ ] Implementar remoção de produto do catálogo do fornecedor
- [ ] Implementar visualização de clientes vinculados ao fornecedor
- [x] Implementar visualização de pedidos recebidos
- [x] Implementar atualização de status dos pedidos recebidos
- [ ] Implementar busca manual de produtos do fornecedor
- [ ] Implementar ordenação manual de produtos do fornecedor por nome
- [ ] Implementar ordenação manual de produtos do fornecedor por estoque

---

## 7. Backend - Domínio VMI

Responsáveis:
- Ingrid Souza: `ProdutoFornecedor` e contratos
- Guilherme Tavares: estoque, semáforo e pedidos automáticos

- [~] Implementar entidade `ProdutoFornecedor` para vínculo N:N
  - Modelo existe e é usado por estoque/pedidos, mas a gestão do domínio ainda não foi implementada
- [~] Implementar contrato com `preferencial`, preço, prazo e quantidade mínima
  - Estrutura existe no modelo, sem CRUD/serviços completos
- [x] Implementar regra de fornecedor preferencial
- [ ] Implementar seleção de fornecedor quando não houver preferencial
- [x] Implementar controle de estoque gerenciado pelo fornecedor
- [x] Implementar cálculo do semáforo de estoque
- [x] Implementar status `Verde`, `Amarelo` e `Vermelho`
- [~] Implementar regra de habilitação do botão de reposição
  - Regra de backend existe via validação do pedido automático; frontend ainda não existe
- [x] Implementar criação de pedido automático
- [x] Implementar origem do pedido (`manual` / `automatico`)
- [x] Implementar vínculo de item do pedido ao contrato específico do fornecedor

---

## 8. Frontend - Estrutura Base

Responsável: Stephanie

- [ ] Criar aplicação frontend
- [ ] Configurar roteamento
- [ ] Configurar cliente HTTP para consumo da API
- [ ] Configurar armazenamento da sessão autenticada
- [ ] Implementar logout
- [ ] Implementar rotas protegidas por perfil
- [ ] Implementar layout responsivo base
- [ ] Implementar feedback visual de carregamento
- [ ] Implementar feedback visual de sucesso
- [ ] Implementar feedback visual de erro

---

## 9. Frontend - Admin

Responsável: Stephanie

- [ ] Criar tela de login
- [ ] Criar dashboard do Admin
- [ ] Criar tela de cadastro de usuário
- [ ] Criar tela de listagem/busca de usuários
- [ ] Criar tela de cadastro de fornecedor
- [ ] Criar tela de listagem/busca de fornecedores
- [ ] Criar tela de listagem de todos os pedidos

---

## 10. Frontend - Usuário

Responsável: Stephanie

- [ ] Criar dashboard do Usuário
- [ ] Criar tela de catálogo de produtos
- [ ] Criar interface de busca de produtos
- [ ] Criar interface de ordenação de produtos
- [ ] Criar tela de cadastro de produto
- [ ] Criar tela de estoque com semáforo visual
- [ ] Criar tela de configuração dos pontos de reposição
- [ ] Exibir botão "Enviar Pedido de Reposição" quando aplicável
- [ ] Criar tela de criação de pedido manual
- [ ] Criar tela de listagem de pedidos
- [ ] Criar filtro por origem do pedido
- [ ] Criar tela de detalhe do pedido

---

## 11. Frontend - Fornecedor

Responsável: Stephanie

- [ ] Criar dashboard do Fornecedor
- [ ] Criar tela de produtos vinculados
- [ ] Criar tela de gestão de estoque
- [ ] Criar tela de clientes vinculados
- [ ] Criar tela de pedidos recebidos
- [ ] Criar interface de atualização de status do pedido

---

## 12. Arquitetura e Qualidade

- [~] Garantir separação em camadas (`Routes`, `Services`, `Repositories`, `Models`, `Schemas`)
  - Estrutura existe, mas produto/fornecedor ainda têm partes pendentes do domínio da Ingrid
- [x] Garantir ausência de lógica de negócio nas rotas
- [x] Garantir `response_model` explícito em todas as rotas atuais
- [~] Garantir uso de type hints no código Python
  - Predominante, mas precisa validação completa nas áreas ainda vazias
- [x] Garantir código em inglês
- [x] Garantir comentários e docstrings em português
- [x] Evitar padrões avançados desnecessários

---

## 13. Regras de Algoritmos

- [~] Implementar buscas com algoritmo manual
- [~] Implementar ordenações com algoritmo manual
- [ ] Não usar `in`, `list.index()`, `filter()`, `any()`, `find()` para busca
- [ ] Não usar `sorted()`, `list.sort()` ou `.order_by()` para ordenação
- [ ] Adicionar comentário justificando o algoritmo de busca escolhido
- [ ] Adicionar comentário justificando o algoritmo de ordenação escolhido

Observação:
- Busca manual já cobre usuários/fornecedores e checagens internas de pedidos/estoque
- Ordenação manual já cobre listagens de pedidos com insertion sort
- Ainda faltam os algoritmos do domínio de produtos/fornecedores da Ingrid

---

## 14. Banco de Dados

- [x] Validar modelo de dados `User`
- [~] Validar modelo de dados `Fornecedor`
- [~] Validar modelo de dados `Produto`
- [~] Validar modelo de dados `ProdutoFornecedor`
- [x] Validar modelo de dados `Estoque`
- [x] Validar modelo de dados `PedidoCompra`
- [x] Validar modelo de dados `ItemPedido`
- [ ] Criar ou revisar migrations do banco

Observação:
- `Fornecedor`, `Produto` e `ProdutoFornecedor` existem, mas hoje funcionam como base parcial para estoque/pedidos

---

## 15. Testes

- [x] Criar testes unitários para autenticação
- [x] Criar testes unitários para regras de acesso por perfil
- [~] Criar testes unitários para busca manual
- [~] Criar testes unitários para ordenação manual
- [x] Criar testes unitários para semáforo de estoque
- [x] Criar testes unitários para pedido automático
- [x] Criar testes unitários para pedido manual
- [ ] Criar testes unitários para contratos `ProdutoFornecedor`
- [ ] Garantir cobertura mínima de 80%

Observação:
- `tests/test_admin.py` já cobre busca manual de usuários/fornecedores e ordenação de pedidos
- `tests/test_fornecedor.py`, `tests/test_usuario.py`, `tests/test_algorithms/test_search.py` e `tests/test_algorithms/test_sort.py` seguem vazios

---

## 16. Validação Final

- [~] Validar coerência entre `PRD.MD`, `RULES.MD` e implementação
  - Backend de auth/estoque/pedido está coerente em boa parte, mas produto/frontend ainda não
- [~] Validar fluxo completo de login até operação por perfil
  - Admin, usuário e fornecedor já têm fluxo de backend testado em partes
- [ ] Validar integração frontend-backend
- [ ] Validar responsividade em desktop e mobile
- [ ] Validar mensagens de erro e estados de carregamento
