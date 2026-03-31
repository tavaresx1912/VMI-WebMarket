# RULES — ECommerce Project

> Este arquivo define as regras que devem ser seguidas em todos os prompts e na geração de código deste projeto.
> Este projeto é de **nível universitário**: toda linguagem usada nos comentários e toda escolha de algoritmo deve ser acessível e condizente com o conteúdo ensinado em disciplinas de graduação (Algoritmos e Estruturas de Dados, Programação Orientada a Objetos, Banco de Dados).
> À medida que o projeto evolui, novas regras podem ser adicionadas aqui.

---

## Regras de Algoritmos

> **Princípio geral:** use apenas algoritmos estudados nas disciplinas básicas de graduação.
> Algoritmos avançados (ex.: árvores balanceadas, grafos, programação dinâmica) **não devem** ser usados sem justificativa explícita de que são conteúdo da disciplina.

### R-ALG-01 — Busca implementada manualmente
Todos os mecanismos de **busca** em listas, arrays ou coleções devem ser implementados
com algoritmos próprios no código. **Proibido** usar funções nativas da linguagem ou de bibliotecas
para localizar elementos (ex.: `in`, `list.index()`, `filter()`, `any()`, `find()` etc.).

- **Busca Linear** — percorre a lista do início ao fim, elemento por elemento. Usar quando a lista **não** estiver ordenada ou for pequena.
- **Busca Binária** — divide a lista ao meio a cada passo. Usar **somente** quando a lista já estiver ordenada.
- O algoritmo escolhido deve ser justificado por um comentário no código explicando o motivo da escolha.

### R-ALG-02 — Ordenação implementada manualmente
Todos os mecanismos de **ordenação** em listas, arrays ou coleções devem ser implementados
com algoritmos próprios no código. **Proibido** usar funções nativas ou de bibliotecas
(ex.: `sorted()`, `list.sort()`, `.order_by()` do ORM etc.).

- **Bubble Sort** — compara pares adjacentes repetidamente. Simples de entender; usar para listas pequenas (até ~20 itens) ou fins didáticos.
- **Selection Sort** — encontra o menor elemento e o coloca na posição correta a cada passo. Simples; usar para listas pequenas.
- **Insertion Sort** — insere cada elemento na posição correta em uma sublista já ordenada. Eficiente para listas quase ordenadas.
- **Merge Sort** — divide a lista ao meio, ordena cada metade e as une. Usar para listas médias ou grandes (> 100 itens).
- O algoritmo escolhido deve ser justificado por um comentário no código explicando o critério de escolha (tamanho da lista, ordenação parcial etc.).

---

## Regras de Arquitetura

> As camadas abaixo refletem o padrão ensinado em disciplinas de Engenharia de Software e Desenvolvimento Web de graduação. Mantenha a separação simples e clara.

### R-ARQ-01 — Separação de camadas
O projeto deve seguir separação clara de camadas:
- **Routes** — recebe a requisição HTTP e chama o Service. Sem lógica de negócio aqui.
- **Services** — contém as regras de negócio (o "o quê" o sistema faz).
- **Repositories** — responsável por ler e gravar dados no banco. Sem regras de negócio aqui.
- **Models** — representa as tabelas do banco de dados.
- **Schemas** — define o formato dos dados que entram e saem da API (validação com Pydantic).

Nenhuma camada deve assumir responsabilidades de outra.

### R-ARQ-02 — Sem lógica de negócio nas rotas
As funções de rota não devem conter lógica de negócio. Devem delegar para a camada de Service.

---

## Regras de Código

### R-COD-01 — Tipagem obrigatória
Todo código Python deve ter type hints em funções e variáveis onde o tipo não seja óbvio.
Isso facilita a leitura e o aprendizado — fica claro o que cada função recebe e retorna.

### R-COD-02 — Sem retornos genéricos nas rotas
Rotas da API devem sempre declarar `response_model` com um schema Pydantic explícito.

### R-COD-03 — Idioma do código
- **Código** (variáveis, funções, classes, rotas): inglês.
- **Comentários e docstrings**: português — explique o raciocínio de forma clara, como se estivesse descrevendo para um colega de turma.

### R-COD-04 — Complexidade de código
Evite padrões avançados desnecessários (decorators complexos, metaclasses, generators aninhados etc.).
Prefira código simples, legível e direto — condizente com o nível de uma disciplina de graduação.

---

## Como adicionar novas regras

1. Defina um identificador no formato `R-<CATEGORIA>-<NÚMERO>` (ex.: `R-ALG-03`, `R-SEC-01`).
2. Escreva uma descrição clara do que é obrigatório e do que é proibido.
3. Adicione exemplos quando necessário.
4. Verifique se o algoritmo ou padrão proposto é compatível com o nível universitário.
5. Registre a data de adição como comentário inline: `<!-- adicionado em YYYY-MM-DD -->`.

---

## Categorias existentes

| Prefixo | Categoria           |
|---------|---------------------|
| ALG     | Algoritmos          |
| ARQ     | Arquitetura         |
| COD     | Estilo de código    |
| SEC     | Segurança           |
| TST     | Testes              |
| DB      | Banco de dados      |
