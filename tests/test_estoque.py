from app.models.estoque import Estoque
from app.models.produto import Produto
from app.models.user import User
from app.core.security import hash_password


class TestCriarEstoque:
    def test_criar_estoque_sucesso(self, client, usuario_headers, produto):
        resp = client.post("/usuario/estoque", json={
            "produto_id": produto.id,
            "quantidade": 30,
            "ponto_reposicao": 5,
            "ponto_amarelo": 15,
        }, headers=usuario_headers)

        assert resp.status_code == 201
        data = resp.json()
        assert data["produto_id"] == produto.id
        assert data["quantidade"] == 30
        assert data["ponto_reposicao"] == 5
        assert data["ponto_amarelo"] == 15
        assert data["status_kanban"] == "verde"

    def test_criar_estoque_duplicado_retorna_409(self, client, usuario_headers, estoque, produto):
        resp = client.post("/usuario/estoque", json={
            "produto_id": produto.id,
            "quantidade": 10,
            "ponto_reposicao": 2,
            "ponto_amarelo": 8,
        }, headers=usuario_headers)

        assert resp.status_code == 409

    def test_criar_estoque_sem_autenticacao_retorna_401(self, client, produto):
        resp = client.post("/usuario/estoque", json={
            "produto_id": produto.id,
            "quantidade": 10,
            "ponto_reposicao": 2,
            "ponto_amarelo": 8,
        })
        assert resp.status_code == 401

    def test_fornecedor_nao_pode_criar_estoque_retorna_403(self, client, fornecedor_headers, produto):
        resp = client.post("/usuario/estoque", json={
            "produto_id": produto.id,
            "quantidade": 10,
            "ponto_reposicao": 2,
            "ponto_amarelo": 8,
        }, headers=fornecedor_headers)
        assert resp.status_code == 403


class TestListarEstoqueUsuario:
    def test_listar_estoque_vazio(self, client, usuario_headers):
        resp = client.get("/usuario/estoque", headers=usuario_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_listar_retorna_entrada_criada(self, client, usuario_headers, estoque):
        resp = client.get("/usuario/estoque", headers=usuario_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["id"] == estoque.id

    def test_sem_autenticacao_retorna_401(self, client):
        assert client.get("/usuario/estoque").status_code == 401


class TestSemaforoKanban:
    """Testa o cálculo correto do semáforo para os três status."""

    def test_status_verde(self, client, usuario_headers, produto, db, usuario_user):
        # quantidade >= ponto_amarelo → verde
        e = Estoque(produto_id=produto.id, usuario_id=usuario_user.id,
                    quantidade=50, ponto_reposicao=10, ponto_amarelo=20)
        db.add(e); db.commit()

        resp = client.get("/usuario/estoque", headers=usuario_headers)
        item = next(i for i in resp.json() if i["id"] == e.id)
        assert item["status_kanban"] == "verde"

    def test_status_amarelo(self, client, usuario_headers, produto, db, usuario_user):
        # ponto_reposicao < quantidade < ponto_amarelo → amarelo
        e = Estoque(produto_id=produto.id, usuario_id=usuario_user.id,
                    quantidade=15, ponto_reposicao=10, ponto_amarelo=20)
        db.add(e); db.commit()

        resp = client.get("/usuario/estoque", headers=usuario_headers)
        item = next(i for i in resp.json() if i["id"] == e.id)
        assert item["status_kanban"] == "amarelo"

    def test_status_vermelho_por_igualdade(self, client, usuario_headers, produto, db, usuario_user):
        # quantidade == ponto_reposicao → vermelho
        e = Estoque(produto_id=produto.id, usuario_id=usuario_user.id,
                    quantidade=10, ponto_reposicao=10, ponto_amarelo=20)
        db.add(e); db.commit()

        resp = client.get("/usuario/estoque", headers=usuario_headers)
        item = next(i for i in resp.json() if i["id"] == e.id)
        assert item["status_kanban"] == "vermelho"

    def test_status_vermelho_abaixo(self, client, usuario_headers, produto, db, usuario_user):
        # quantidade < ponto_reposicao → vermelho
        e = Estoque(produto_id=produto.id, usuario_id=usuario_user.id,
                    quantidade=3, ponto_reposicao=10, ponto_amarelo=20)
        db.add(e); db.commit()

        resp = client.get("/usuario/estoque", headers=usuario_headers)
        item = next(i for i in resp.json() if i["id"] == e.id)
        assert item["status_kanban"] == "vermelho"

    def test_status_verde_em_ponto_amarelo(self, client, usuario_headers, produto, db, usuario_user):
        # quantidade == ponto_amarelo → verde (limiar verde é inclusivo)
        e = Estoque(produto_id=produto.id, usuario_id=usuario_user.id,
                    quantidade=20, ponto_reposicao=10, ponto_amarelo=20)
        db.add(e); db.commit()

        resp = client.get("/usuario/estoque", headers=usuario_headers)
        item = next(i for i in resp.json() if i["id"] == e.id)
        assert item["status_kanban"] == "verde"


class TestConfigurarPontos:
    def test_atualizar_pontos_sucesso(self, client, usuario_headers, estoque):
        resp = client.patch(f"/usuario/estoque/{estoque.id}/pontos", json={
            "ponto_reposicao": 15,
            "ponto_amarelo": 30,
        }, headers=usuario_headers)

        assert resp.status_code == 200
        data = resp.json()
        assert data["ponto_reposicao"] == 15
        assert data["ponto_amarelo"] == 30

    def test_configurar_pontos_recalcula_kanban(self, client, usuario_headers, estoque, db):
        # estoque.quantidade=50, ponto_amarelo original=20 → verde
        # Após ajuste para ponto_amarelo=60, deve ficar amarelo (50 < 60, 50 > 10)
        resp = client.patch(f"/usuario/estoque/{estoque.id}/pontos", json={
            "ponto_reposicao": 10,
            "ponto_amarelo": 60,
        }, headers=usuario_headers)

        assert resp.status_code == 200
        assert resp.json()["status_kanban"] == "amarelo"

    def test_estoque_inexistente_retorna_404(self, client, usuario_headers):
        resp = client.patch("/usuario/estoque/9999/pontos", json={
            "ponto_reposicao": 5,
            "ponto_amarelo": 10,
        }, headers=usuario_headers)
        assert resp.status_code == 404

    def test_outro_usuario_nao_pode_configurar_retorna_403(self, client, db, estoque):
        # Cria outro usuário e tenta configurar o estoque do primeiro
        outro = User(nome="Outro", email="outro@test.com",
                     senha_hash=hash_password("outro123"), role="usuario", ativo=True)
        db.add(outro); db.commit()
        token = client.post("/auth/login", json={"email": "outro@test.com", "senha": "outro123"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.patch(f"/usuario/estoque/{estoque.id}/pontos", json={
            "ponto_reposicao": 5, "ponto_amarelo": 10,
        }, headers=headers)
        assert resp.status_code == 403


class TestAtualizarQuantidadeFornecedor:
    def test_fornecedor_atualiza_quantidade_sucesso(
        self, client, fornecedor_headers, estoque, contrato
    ):
        resp = client.patch(f"/fornecedor/estoque/{estoque.id}", json={
            "quantidade": 100
        }, headers=fornecedor_headers)

        assert resp.status_code == 200
        assert resp.json()["quantidade"] == 100

    def test_kanban_recalculado_apos_atualizacao(
        self, client, fornecedor_headers, estoque, contrato
    ):
        # Reduz a quantidade para zona vermelha
        resp = client.patch(f"/fornecedor/estoque/{estoque.id}", json={
            "quantidade": 5
        }, headers=fornecedor_headers)

        assert resp.status_code == 200
        assert resp.json()["status_kanban"] == "vermelho"

    def test_fornecedor_sem_vinculo_retorna_403(self, client, db, estoque):
        # Fornecedor sem produtos vinculados não pode atualizar
        user2 = User(nome="F2", email="f2@test.com",
                     senha_hash=hash_password("f2pass"), role="fornecedor", ativo=True)
        db.add(user2); db.commit()
        from app.models.fornecedor import Fornecedor
        f2 = Fornecedor(user_id=user2.id, nome="Outro Forn", cnpj="00.000.000/0001-00")
        db.add(f2); db.commit()
        token = client.post("/auth/login", json={"email": "f2@test.com", "senha": "f2pass"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.patch(f"/fornecedor/estoque/{estoque.id}", json={"quantidade": 10}, headers=headers)
        assert resp.status_code == 403

    def test_usuario_nao_pode_atualizar_quantidade_retorna_403(
        self, client, usuario_headers, estoque
    ):
        resp = client.patch(f"/fornecedor/estoque/{estoque.id}", json={"quantidade": 10},
                            headers=usuario_headers)
        assert resp.status_code == 403

    def test_sem_autenticacao_retorna_401(self, client, estoque):
        resp = client.patch(f"/fornecedor/estoque/{estoque.id}", json={"quantidade": 10})
        assert resp.status_code == 401


class TestListarEstoqueFornecedor:
    def test_listar_estoque_fornecedor(self, client, fornecedor_headers, estoque, contrato):
        resp = client.get("/fornecedor/estoque", headers=fornecedor_headers)
        assert resp.status_code == 200
        ids = [i["id"] for i in resp.json()]
        assert estoque.id in ids

    def test_fornecedor_sem_produtos_retorna_lista_vazia(self, client, db):
        user = User(nome="Vazio", email="vazio@test.com",
                    senha_hash=hash_password("vazio123"), role="fornecedor", ativo=True)
        db.add(user); db.commit()
        from app.models.fornecedor import Fornecedor
        f = Fornecedor(user_id=user.id, nome="Vazio Ltda", cnpj="11.111.111/0001-11")
        db.add(f); db.commit()
        token = client.post("/auth/login", json={"email": "vazio@test.com", "senha": "vazio123"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/fornecedor/estoque", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []
