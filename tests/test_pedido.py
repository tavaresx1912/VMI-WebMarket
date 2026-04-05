from app.models.estoque import Estoque
from app.models.user import User
from app.core.security import hash_password


class TestCriarPedidoManual:
    def test_criar_pedido_manual_sucesso(self, client, usuario_headers, contrato):
        resp = client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": contrato.id, "quantidade": 5}]
        }, headers=usuario_headers)

        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pendente"
        assert data["origem"] == "manual"
        assert len(data["itens"]) == 1
        assert data["itens"][0]["produto_fornecedor_id"] == contrato.id
        assert data["itens"][0]["quantidade"] == 5
        # preco_unitario deve ser o snapshot do contrato
        assert data["itens"][0]["preco_unitario"] == contrato.preco_contratado

    def test_pedido_com_contrato_inexistente_retorna_404(self, client, usuario_headers):
        resp = client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": 9999, "quantidade": 5}]
        }, headers=usuario_headers)
        assert resp.status_code == 404

    def test_pedido_sem_itens_retorna_422(self, client, usuario_headers):
        resp = client.post("/usuario/pedidos", json={"itens": []}, headers=usuario_headers)
        assert resp.status_code == 422

    def test_sem_autenticacao_retorna_401(self, client, contrato):
        resp = client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": contrato.id, "quantidade": 1}]
        })
        assert resp.status_code == 401

    def test_fornecedor_nao_pode_criar_pedido_retorna_403(self, client, fornecedor_headers, contrato):
        resp = client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": contrato.id, "quantidade": 1}]
        }, headers=fornecedor_headers)
        assert resp.status_code == 403


class TestCriarPedidoAutomatico:
    def test_pedido_automatico_em_vermelho(self, client, usuario_headers, db, produto, usuario_user, contrato):
        # quantidade <= ponto_reposicao → vermelho
        e = Estoque(produto_id=produto.id, usuario_id=usuario_user.id,
                    quantidade=5, ponto_reposicao=10, ponto_amarelo=20)
        db.add(e); db.commit()

        resp = client.post(f"/usuario/pedidos/automatico/{e.id}", headers=usuario_headers)

        assert resp.status_code == 201
        data = resp.json()
        assert data["origem"] == "automatico"
        assert data["status"] == "pendente"
        assert len(data["itens"]) == 1
        # Quantidade deve ser a qtd_minima_pedido do contrato
        assert data["itens"][0]["quantidade"] == contrato.qtd_minima_pedido

    def test_pedido_automatico_em_amarelo(self, client, usuario_headers, db, produto, usuario_user, contrato):
        # ponto_reposicao < quantidade < ponto_amarelo → amarelo
        e = Estoque(produto_id=produto.id, usuario_id=usuario_user.id,
                    quantidade=15, ponto_reposicao=10, ponto_amarelo=20)
        db.add(e); db.commit()

        resp = client.post(f"/usuario/pedidos/automatico/{e.id}", headers=usuario_headers)

        assert resp.status_code == 201
        assert resp.json()["origem"] == "automatico"

    def test_pedido_automatico_negado_em_verde_retorna_422(self, client, usuario_headers, estoque, contrato):
        # estoque fixture tem quantidade=50, ponto_amarelo=20 → verde
        resp = client.post(f"/usuario/pedidos/automatico/{estoque.id}", headers=usuario_headers)
        assert resp.status_code == 422

    def test_pedido_automatico_sem_fornecedor_preferencial_retorna_422(
        self, client, usuario_headers, db, produto, usuario_user
    ):
        # Cria estoque em vermelho mas sem contrato preferencial
        e = Estoque(produto_id=produto.id, usuario_id=usuario_user.id,
                    quantidade=3, ponto_reposicao=10, ponto_amarelo=20)
        db.add(e); db.commit()

        resp = client.post(f"/usuario/pedidos/automatico/{e.id}", headers=usuario_headers)
        assert resp.status_code == 422

    def test_pedido_automatico_de_outro_usuario_retorna_403(
        self, client, db, estoque, contrato
    ):
        outro = User(nome="Outro", email="outro2@test.com",
                     senha_hash=hash_password("outro123"), role="usuario", ativo=True)
        db.add(outro); db.commit()
        token = client.post("/auth/login", json={"email": "outro2@test.com", "senha": "outro123"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.post(f"/usuario/pedidos/automatico/{estoque.id}", headers=headers)
        assert resp.status_code == 403

    def test_estoque_inexistente_retorna_404(self, client, usuario_headers):
        resp = client.post("/usuario/pedidos/automatico/9999", headers=usuario_headers)
        assert resp.status_code == 404


class TestListarPedidosUsuario:
    def test_listar_pedidos_vazio(self, client, usuario_headers):
        resp = client.get("/usuario/pedidos", headers=usuario_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_listar_pedidos_retorna_criado(self, client, usuario_headers, contrato):
        client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": contrato.id, "quantidade": 2}]
        }, headers=usuario_headers)

        resp = client.get("/usuario/pedidos", headers=usuario_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["origem"] == "manual"

    def test_usuario_so_ve_seus_proprios_pedidos(self, client, db, contrato):
        # Usuário 1 cria pedido
        u1 = User(nome="U1", email="u1@test.com",
                  senha_hash=hash_password("u1pass"), role="usuario", ativo=True)
        db.add(u1); db.commit()
        t1 = client.post("/auth/login", json={"email": "u1@test.com", "senha": "u1pass"}).json()["access_token"]
        h1 = {"Authorization": f"Bearer {t1}"}
        client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": contrato.id, "quantidade": 1}]
        }, headers=h1)

        # Usuário 2 lista pedidos — não deve ver o pedido do U1
        u2 = User(nome="U2", email="u2@test.com",
                  senha_hash=hash_password("u2pass"), role="usuario", ativo=True)
        db.add(u2); db.commit()
        t2 = client.post("/auth/login", json={"email": "u2@test.com", "senha": "u2pass"}).json()["access_token"]
        h2 = {"Authorization": f"Bearer {t2}"}

        resp = client.get("/usuario/pedidos", headers=h2)
        assert resp.json() == []


class TestDetalharPedido:
    def test_detalhar_pedido_sucesso(self, client, usuario_headers, contrato):
        criado = client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": contrato.id, "quantidade": 3}]
        }, headers=usuario_headers).json()

        resp = client.get(f"/usuario/pedidos/{criado['id']}", headers=usuario_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == criado["id"]
        assert len(resp.json()["itens"]) == 1

    def test_detalhar_pedido_inexistente_retorna_404(self, client, usuario_headers):
        resp = client.get("/usuario/pedidos/9999", headers=usuario_headers)
        assert resp.status_code == 404

    def test_detalhar_pedido_de_outro_usuario_retorna_403(self, client, db, contrato, usuario_headers):
        criado = client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": contrato.id, "quantidade": 1}]
        }, headers=usuario_headers).json()

        outro = User(nome="Intruso", email="intruso@test.com",
                     senha_hash=hash_password("pass"), role="usuario", ativo=True)
        db.add(outro); db.commit()
        token = client.post("/auth/login", json={"email": "intruso@test.com", "senha": "pass"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get(f"/usuario/pedidos/{criado['id']}", headers=headers)
        assert resp.status_code == 403


class TestAtualizarStatusPedido:
    def test_fornecedor_atualiza_status_confirmado(
        self, client, usuario_headers, fornecedor_headers, contrato
    ):
        # Usuário cria pedido
        pedido = client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": contrato.id, "quantidade": 5}]
        }, headers=usuario_headers).json()

        # Fornecedor confirma
        resp = client.patch(f"/fornecedor/pedidos/{pedido['id']}/status", json={
            "status": "confirmado"
        }, headers=fornecedor_headers)

        assert resp.status_code == 200
        assert resp.json()["status"] == "confirmado"

    def test_fornecedor_avanca_status_ate_entregue(
        self, client, usuario_headers, fornecedor_headers, contrato
    ):
        pedido = client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": contrato.id, "quantidade": 5}]
        }, headers=usuario_headers).json()

        for novo_status in ("confirmado", "enviado", "entregue"):
            resp = client.patch(f"/fornecedor/pedidos/{pedido['id']}/status", json={
                "status": novo_status
            }, headers=fornecedor_headers)
            assert resp.status_code == 200
            assert resp.json()["status"] == novo_status

    def test_status_invalido_retorna_422(
        self, client, usuario_headers, fornecedor_headers, contrato
    ):
        pedido = client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": contrato.id, "quantidade": 1}]
        }, headers=usuario_headers).json()

        resp = client.patch(f"/fornecedor/pedidos/{pedido['id']}/status", json={
            "status": "inexistente"
        }, headers=fornecedor_headers)
        assert resp.status_code == 422

    def test_fornecedor_sem_vinculo_nao_pode_atualizar_retorna_403(
        self, client, db, usuario_headers, contrato
    ):
        pedido = client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": contrato.id, "quantidade": 1}]
        }, headers=usuario_headers).json()

        # Segundo fornecedor sem vínculo com este pedido
        u2 = User(nome="F2", email="f2b@test.com",
                  senha_hash=hash_password("f2pass"), role="fornecedor", ativo=True)
        db.add(u2); db.commit()
        from app.models.fornecedor import Fornecedor
        f2 = Fornecedor(user_id=u2.id, nome="Outro Forn", cnpj="99.999.999/0001-99")
        db.add(f2); db.commit()
        t2 = client.post("/auth/login", json={"email": "f2b@test.com", "senha": "f2pass"}).json()["access_token"]
        h2 = {"Authorization": f"Bearer {t2}"}

        resp = client.patch(f"/fornecedor/pedidos/{pedido['id']}/status", json={
            "status": "confirmado"
        }, headers=h2)
        assert resp.status_code == 403

    def test_pedido_inexistente_retorna_404(self, client, fornecedor_headers, fornecedor_entity):
        resp = client.patch("/fornecedor/pedidos/9999/status", json={
            "status": "confirmado"
        }, headers=fornecedor_headers)
        assert resp.status_code == 404

    def test_sem_autenticacao_retorna_401(self, client):
        resp = client.patch("/fornecedor/pedidos/1/status", json={"status": "confirmado"})
        assert resp.status_code == 401


class TestListarPedidosFornecedor:
    def test_fornecedor_lista_pedidos_recebidos(
        self, client, usuario_headers, fornecedor_headers, contrato
    ):
        client.post("/usuario/pedidos", json={
            "itens": [{"produto_fornecedor_id": contrato.id, "quantidade": 2}]
        }, headers=usuario_headers)

        resp = client.get("/fornecedor/pedidos", headers=fornecedor_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_fornecedor_sem_pedidos_retorna_lista_vazia(self, client, fornecedor_headers, fornecedor_entity):
        resp = client.get("/fornecedor/pedidos", headers=fornecedor_headers)
        assert resp.status_code == 200
        assert resp.json() == []
