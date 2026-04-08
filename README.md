# VMI WebMarket

API backend em FastAPI para um sistema de e-commerce com modelo VMI (Vendor Managed Inventory), onde o fornecedor acompanha o estoque do cliente e participa do processo de reposição.

## Visão geral

O projeto implementa três perfis principais:

- `admin`: cadastra usuários e fornecedores, consulta usuários, fornecedores e pedidos.
- `usuario`: gerencia seu estoque, define pontos de reposição e cria pedidos manuais ou automáticos.
- `fornecedor`: monitora o estoque vinculado aos seus produtos e atualiza o status dos pedidos.

O sistema usa semáforo Kanban para o estoque:

- `verde`: quantidade maior ou igual ao ponto amarelo.
- `amarelo`: quantidade entre o ponto de reposição e o ponto amarelo.
- `vermelho`: quantidade menor ou igual ao ponto de reposição.

Pedidos automáticos só podem ser gerados quando o item está em `amarelo` ou `vermelho`.

## Stack

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- JWT com `python-jose`
- `bcrypt` para hash de senha
- `pytest` para testes

## Estrutura

```text
app/
  algorithms/     Algoritmos auxiliares de busca e ordenação
  core/           Segurança e JWT
  models/         Modelos SQLAlchemy
  repositories/   Acesso a dados
  routes/         Endpoints da API
  schemas/        Schemas Pydantic
  services/       Regras de negócio
tests/            Testes automatizados
main.py           Entrada local para desenvolvimento
webmarket.db      Banco SQLite local
```

## Requisitos

- Python 3.11+ recomendado
- `pip`

## Instalação

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração

O projeto usa por padrão:

- banco SQLite em `./webmarket.db`
- chave JWT via variável `SECRET_KEY`

Se `SECRET_KEY` não for definida, a aplicação usa a chave de desenvolvimento embutida no código. Para ambiente real, defina uma chave própria antes de subir a API.

Exemplo no PowerShell:

```powershell
$env:SECRET_KEY="troque-esta-chave"
```

## Como executar

Opção 1, pelo arquivo principal:

```bash
python main.py
```

Opção 2, diretamente com Uvicorn:

```bash
uvicorn app.main:app --reload
```

Após iniciar, a API ficará disponível em:

- `http://127.0.0.1:8000`
- documentação Swagger: `http://127.0.0.1:8000/docs`
- documentação ReDoc: `http://127.0.0.1:8000/redoc`

As tabelas são criadas automaticamente na inicialização.

## Autenticação

A autenticação é feita com JWT via header:

```http
Authorization: Bearer <token>
```

Endpoint de login:

```http
POST /auth/login
Content-Type: application/json

{
  "email": "admin@test.com",
  "senha": "admin123"
}
```

Resposta esperada:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

## Endpoints principais

### Admin

- `POST /admin/usuarios`
- `GET /admin/usuarios`
- `PATCH /admin/usuarios/{user_id}/desativar`
- `POST /admin/fornecedores`
- `GET /admin/fornecedores`
- `PATCH /admin/fornecedores/{fornecedor_id}/desativar`
- `GET /admin/pedidos`

### Usuário

- `POST /usuario/estoque`
- `GET /usuario/estoque`
- `PATCH /usuario/estoque/{estoque_id}/pontos`
- `POST /usuario/pedidos`
- `POST /usuario/pedidos/automatico/{estoque_id}`
- `GET /usuario/pedidos`
- `GET /usuario/pedidos/{pedido_id}`

### Fornecedor

- `GET /fornecedor/estoque`
- `PATCH /fornecedor/estoque/{estoque_id}`
- `GET /fornecedor/pedidos`
- `PATCH /fornecedor/pedidos/{pedido_id}/status`

## Exemplos de payload

Criar usuário:

```json
{
  "nome": "Joao",
  "email": "joao@test.com",
  "senha": "s123",
  "role": "usuario"
}
```

Criar fornecedor:

```json
{
  "nome": "Fornecedor A",
  "email": "fornecedor-a@test.com",
  "senha": "senha123",
  "cnpj": "12.345.678/0001-90"
}
```

Criar item de estoque:

```json
{
  "produto_id": 1,
  "quantidade": 30,
  "ponto_reposicao": 5,
  "ponto_amarelo": 15
}
```

Criar pedido manual:

```json
{
  "itens": [
    {
      "produto_fornecedor_id": 1,
      "quantidade": 5
    }
  ]
}
```

Atualizar status do pedido:

```json
{
  "status": "confirmado"
}
```

Status aceitos no fluxo de pedidos:

- `pendente`
- `confirmado`
- `enviado`
- `entregue`

## Testes

Execute a suíte com:

```bash
pytest
```

Os testes usam banco SQLite em memória, isolado por execução.

## Observações

- O banco local `webmarket.db` já pode existir no repositório para desenvolvimento.
- Não há sistema de migrations; o esquema é criado com `Base.metadata.create_all(...)` na inicialização.
- O arquivo `.env.example` existe, mas ainda não está preenchido com variáveis de exemplo.
