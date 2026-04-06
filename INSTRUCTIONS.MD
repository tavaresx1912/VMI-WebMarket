# INSTRUCTIONS - VMI WebMarket

Este arquivo serve como guia rápido para quem ainda não conhece profundamente o projeto.
O objetivo é explicar a estrutura de pastas, o papel de cada camada e onde cada pessoa deve atuar.

Público principal:
- Ingrid Souza
- Stephanie

---

## 1. Visão Geral

O projeto é uma API em `FastAPI` organizada em camadas.
Hoje o backend está dentro da pasta `app/`.

Fluxo principal da aplicação:

`Route -> Service -> Repository -> Model`

E os dados de entrada/saída passam por:

`Schema`

Resumo de responsabilidade:
- `routes`: recebe HTTP
- `services`: regra de negócio
- `repositories`: acesso ao banco
- `models`: tabelas do banco
- `schemas`: validação e resposta da API

---

## 2. Estrutura do Projeto

### Raiz do projeto

Arquivos principais fora da pasta `app/`:

- `main.py`
  - ponto de entrada para rodar a aplicação em desenvolvimento
- `PRD.MD`
  - documento de produto com regras e funcionalidades
- `RULES.MD`
  - regras obrigatórias do projeto, principalmente sobre algoritmos e arquitetura
- `TODO.MD`
  - checklist do projeto com status e responsáveis
- `requirements.txt`
  - dependências Python
- `webmarket.db`
  - banco SQLite local
- `test_main.http`
  - arquivo para testar endpoints manualmente

---

## 3. Pasta `app/`

Essa é a pasta principal do backend.

### `app/main.py`

Responsável por:
- criar a aplicação FastAPI
- registrar os routers
- criar tabelas no banco ao subir a aplicação

Se você cria uma nova rota, normalmente ela precisa ser importada aqui.

---

## 4. Pasta `app/models/`

Aqui ficam os modelos do SQLAlchemy.
Cada arquivo representa uma tabela do banco.

Arquivos atuais:

- `user.py`
  - tabela de usuários
  - suporta `admin`, `usuario` e `fornecedor`

- `fornecedor.py`
  - cadastro do fornecedor
  - fica vinculado a um `User`

- `produto.py`
  - cadastro básico do produto

- `produto_fornecedor.py`
  - tabela de vínculo N:N entre produto e fornecedor
  - também representa o contrato
  - contém `preferencial`, `preco_contratado`, `prazo_entrega_dias`, `qtd_minima_pedido`

- `estoque.py`
  - estoque por usuário/produto
  - usado no VMI

- `pedido_compra.py`
  - cabeçalho do pedido

- `item_pedido.py`
  - itens do pedido

Quando alterar estrutura de dados, normalmente você começa em `models/`.

---

## 5. Pasta `app/schemas/`

Aqui ficam os schemas do Pydantic.
Eles definem:
- o que a API recebe
- o que a API devolve

Exemplo:
- `UserCreate`: entrada para criar usuário
- `UserResponse`: saída segura para devolver usuário

Arquivos principais:

- `user.py`
  - schemas de usuário
- `token.py`
  - login e resposta de token
- `fornecedor.py`
  - schemas de fornecedor
- `produto.py`
  - schemas de produto
- `produto_fornecedor.py`
  - schemas de contrato produto-fornecedor
- `estoque.py`
  - schemas de estoque
- `pedido_compra.py`
  - schemas de pedido
- `item_pedido.py`
  - schemas de item de pedido

Regra importante:
- rota não deve retornar dicionário genérico
- rota deve usar `response_model`

---

## 6. Pasta `app/repositories/`

Aqui fica o acesso ao banco.
Repositório não deve decidir regra de negócio.
Ele apenas:
- lê
- cria
- atualiza
- consulta dados

Exemplos:

- `user_repository.py`
  - busca usuário por email, id, lista todos

- `fornecedor_repository.py`
  - busca fornecedor, lista, cria

- `pedido_compra_repository.py`
  - cria pedido e busca pedidos

Se a pergunta for “como eu salvo no banco?”,
normalmente a resposta está em `repositories/`.

---

## 7. Pasta `app/services/`

Essa é a pasta mais importante da regra de negócio.

Service decide:
- o que é permitido
- quais validações precisam ser feitas
- como diferentes repositórios se combinam

Exemplos:

- `auth_service.py`
  - valida login
  - gera JWT

- `user_service.py`
  - cria usuário
  - lista usuário
  - desativa usuário

- `fornecedor_service.py`
  - cria fornecedor
  - lista fornecedor
  - desativa fornecedor

- `estoque_service.py`
  - calcula semáforo
  - cria estoque
  - atualiza quantidade

- `pedido_service.py`
  - cria pedido manual
  - cria pedido automático
  - lista pedidos
  - atualiza status

- `produto_service.py`
  - hoje ainda está pendente/incompleto

Se a dúvida for “onde fica a lógica do sistema?”,
é em `services/`.

---

## 8. Pasta `app/routes/`

Aqui ficam os endpoints HTTP.

A rota deve:
- receber request
- validar usuário/perfil
- chamar service
- devolver response

Ela não deve concentrar regra de negócio.

Arquivos atuais:

- `auth.py`
  - login

- `admin.py`
  - gestão de usuários
  - gestão de fornecedores
  - visualização geral de pedidos

- `usuario.py`
  - estoque do usuário
  - pedidos do usuário

- `fornecedor_estoque.py`
  - estoque do fornecedor
  - pedidos recebidos pelo fornecedor

- `fornecedor.py`
  - hoje está reservado/parcial para o domínio de produto/contrato
  - a ideia é Ingrid usar essa área para endpoints de catálogo/contrato do fornecedor

Se você quer adicionar uma URL nova da API, é aqui.

---

## 9. Pasta `app/core/`

Aqui ficam utilidades centrais da aplicação.

- `security.py`
  - hash de senha
  - verificação de senha
  - criação e leitura do JWT

Essa pasta é para código transversal, não para regra de negócio específica.

---

## 10. Arquivos utilitários em `app/`

### `app/database.py`

Responsável por:
- engine do SQLAlchemy
- sessão do banco
- `Base`
- dependência `get_db`

### `app/dependencies.py`

Responsável por:
- pegar usuário atual via token
- validar role com `require_role(...)`

Exemplo:
- `require_role("admin")`
- `require_role("fornecedor")`

---

## 11. Pasta `app/algorithms/`

Aqui ficam os algoritmos manuais exigidos pelo projeto.

Arquivos:

- `search.py`
  - buscas manuais

- `sort.py`
  - ordenações manuais

Importante:
- o projeto proíbe usar atalhos nativos para busca e ordenação em cenários cobertos pelo `RULES.MD`
- sempre que Ingrid implementar busca/ordenação de produto, ela deve olhar essa pasta

---

## 12. Pasta `tests/`

Aqui ficam os testes automatizados com `pytest`.

Arquivos principais:

- `conftest.py`
  - fixtures compartilhadas
  - banco em memória
  - usuários de teste
  - contrato, estoque e autenticação de teste

- `test_auth.py`
  - login, JWT, segurança

- `test_admin.py`
  - endpoints do admin

- `test_estoque.py`
  - estoque e semáforo

- `test_pedido.py`
  - pedidos manuais e automáticos

- `test_fornecedor.py`
  - ainda praticamente vazio para o domínio da Ingrid

- `test_usuario.py`
  - ainda praticamente vazio para catálogo/produto

- `tests/test_algorithms/`
  - reservado para testes específicos de algoritmos

Regra prática:
- se você criou endpoint ou regra nova, deveria criar ou atualizar teste aqui

---

## 13. Guia Para Ingrid

Seu foco principal é:
- produtos
- fornecedores no domínio de catálogo
- contratos `produto <-> fornecedor`

Onde você mais vai trabalhar:
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
- `app/routes/fornecedor.py`
- `tests/test_fornecedor.py`
- `tests/test_usuario.py`
- `tests/test_algorithms/test_search.py`
- `tests/test_algorithms/test_sort.py`

O que já existe e você deve respeitar:
- autenticação pronta
- `require_role(...)` pronto
- estoque e pedido já usam `Produto`, `Fornecedor` e `ProdutoFornecedor`

Cuidado:
- não quebrar o que estoque e pedido já usam
- manter código em inglês
- comentários em português
- implementar busca e ordenação manualmente

Fluxo recomendado para adicionar funcionalidade:
1. ajustar model se necessário
2. criar/ajustar schema
3. criar repository
4. implementar service
5. expor route
6. escrever teste

---

## 14. Guia Para Stephanie

Seu foco principal é o frontend.
Hoje o frontend ainda não existe no repositório.

Isso significa que você provavelmente vai:
- criar uma pasta nova para o frontend
- definir stack
- consumir a API já existente

O backend que você vai consumir já oferece:
- `/auth/login`
- `/admin/...`
- `/usuario/...`
- `/fornecedor/...`

O que você precisa entender do backend:
- login devolve token JWT
- token deve ser enviado no header:
  - `Authorization: Bearer <token>`
- o menu e as telas devem mudar pelo papel do usuário:
  - `admin`
  - `usuario`
  - `fornecedor`

Telas esperadas no PRD:
- login
- dashboard admin
- dashboard usuário
- dashboard fornecedor
- telas de estoque
- telas de pedidos
- telas de usuários/fornecedores
- catálogo de produtos

Antes de começar, você precisa definir:
- framework do frontend
- pasta onde o frontend vai morar
- estratégia de sessão
- estratégia de rotas protegidas

Sugestão prática de trabalho:
1. criar frontend
2. fazer login
3. persistir token
4. criar layout base
5. criar rotas protegidas
6. integrar telas por perfil

O que observar:
- backend ainda não tem o domínio de produto totalmente pronto
- então algumas telas de catálogo podem depender da entrega da Ingrid

---

## 15. Regras Importantes do Projeto

Essas regras valem para todo mundo:

- código em inglês
- comentários e docstrings em português
- rotas sem lógica de negócio
- `response_model` explícito
- type hints
- busca manual quando o caso exigir
- ordenação manual quando o caso exigir

Antes de mexer em qualquer parte importante, ler:
- `PRD.MD`
- `RULES.MD`
- `TODO.MD`

---

## 16. Como Pensar a Arquitetura

Use esta pergunta para decidir onde colocar código:

- “É endpoint HTTP?”
  - vai para `routes`

- “É regra de negócio?”
  - vai para `services`

- “É acesso ao banco?”
  - vai para `repositories`

- “É tabela?”
  - vai para `models`

- “É contrato de entrada/saída da API?”
  - vai para `schemas`

- “É algoritmo manual reutilizável?”
  - vai para `app/algorithms`

---

## 17. Dúvidas Comuns

### Onde descubro como autenticar?
- `app/routes/auth.py`
- `app/services/auth_service.py`
- `app/core/security.py`

### Onde vejo como proteger uma rota por perfil?
- `app/dependencies.py`

### Onde vejo exemplo de fluxo completo bem montado?
- `usuario.py` + `estoque_service.py` + `estoque_repository.py` + `schemas/estoque.py`

### Onde vejo como os testes criam dados?
- `tests/conftest.py`

### Onde estão as funcionalidades ainda faltantes?
- `TODO.MD`

---

## 18. Resumo Final

Para Ingrid:
- seu trabalho é completar domínio de produto, fornecedor e contrato
- sua referência de arquitetura deve ser o que já foi feito em auth, estoque e pedido

Para Stephanie:
- seu trabalho é criar a interface web consumindo a API existente
- você não precisa mexer no backend para começar login, sessão e estrutura base

Se houver dúvida de onde colocar código, sigam a separação:
- rota recebe
- service decide
- repository consulta
- model representa
- schema valida
