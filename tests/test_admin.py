from app.core.security import hash_password
from app.models.user import User

class TestCriarUsuario:
    def test_criar_usuario_comum(self, client, auth_headers):
        resp = client.post("/admin/usuarios", json={
            "nome": "João", "email": "joao@test.com", "senha": "s123", "role": "usuario"
        }, headers=auth_headers)

        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "joao@test.com"
        assert data["role"] == "usuario"
        assert data["ativo"] is True

    def test_criar_fornecedor(self, client, auth_headers):
        resp = client.post("/admin/usuarios", json={
            "nome": "Forn", "email": "forn@test.com", "senha": "s123", "role": "fornecedor"
        }, headers=auth_headers)

        assert resp.status_code == 200
        assert resp.json()["role"] == "fornecedor"

    def test_criar_admin(self, client, auth_headers):
        resp = client.post("/admin/usuarios", json={
            "nome": "Admin2", "email": "admin2@test.com", "senha": "s123", "role": "admin"
        }, headers=auth_headers)

        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"

    def test_senha_nao_retornada_na_resposta(self, client, auth_headers):
        resp = client.post("/admin/usuarios", json={
            "nome": "U", "email": "u@test.com", "senha": "supersecreta", "role": "usuario"
        }, headers=auth_headers)

        assert "senha" not in resp.json()
        assert "senha_hash" not in resp.json()

    def test_email_duplicado_retorna_400(self, client, auth_headers):
        payload = {"nome": "A", "email": "dup@test.com", "senha": "s123", "role": "usuario"}
        client.post("/admin/usuarios", json=payload, headers=auth_headers)

        resp = client.post("/admin/usuarios", json=payload, headers=auth_headers)
        assert resp.status_code == 400

    def test_role_invalida_retorna_422(self, client, auth_headers):
        resp = client.post("/admin/usuarios", json={
            "nome": "X", "email": "x@test.com", "senha": "s123", "role": "superadmin"
        }, headers=auth_headers)
        assert resp.status_code == 422

    def test_sem_autenticacao_retorna_401(self, client):
        resp = client.post("/admin/usuarios", json={
            "nome": "X", "email": "x@test.com", "senha": "s123", "role": "usuario"
        })
        assert resp.status_code == 401

    def test_role_usuario_nao_acessa_admin_retorna_403(self, client, db):
        db.add(User(nome="U", email="u@test.com", senha_hash=hash_password("s"), role="usuario", ativo=True))
        db.commit()
        token = client.post("/auth/login", json={"email": "u@test.com", "senha": "s"}).json()["access_token"]

        resp = client.post("/admin/usuarios", json={
            "nome": "X", "email": "x@test.com", "senha": "s123", "role": "usuario"
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_role_fornecedor_nao_acessa_admin_retorna_403(self, client, db):
        db.add(User(nome="F", email="f@test.com", senha_hash=hash_password("s"), role="fornecedor", ativo=True))
        db.commit()
        token = client.post("/auth/login", json={"email": "f@test.com", "senha": "s"}).json()["access_token"]

        resp = client.post("/admin/usuarios", json={
            "nome": "X", "email": "x@test.com", "senha": "s123", "role": "usuario"
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403


class TestListarUsuarios:
    def test_listar_retorna_lista(self, client, auth_headers, admin_user):
        resp = client.get("/admin/usuarios", headers=auth_headers)

        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    def test_usuario_criado_aparece_na_listagem(self, client, auth_headers):
        client.post("/admin/usuarios", json={
            "nome": "Listado", "email": "listado@test.com", "senha": "s123", "role": "usuario"
        }, headers=auth_headers)

        emails = [u["email"] for u in client.get("/admin/usuarios", headers=auth_headers).json()]
        assert "listado@test.com" in emails


class TestDesativarUsuario:
    def test_desativar_muda_ativo_para_false(self, client, auth_headers):
        criado = client.post("/admin/usuarios", json={
            "nome": "Desativar", "email": "des@test.com", "senha": "s123", "role": "usuario"
        }, headers=auth_headers).json()

        resp = client.patch(f"/admin/usuarios/{criado['id']}/desativar", headers=auth_headers)

        assert resp.status_code == 200
        assert resp.json()["ativo"] is False

    def test_usuario_desativado_nao_consegue_logar(self, client, auth_headers):
        criado = client.post("/admin/usuarios", json={
            "nome": "Bloqueado", "email": "bloq@test.com", "senha": "senha123", "role": "usuario"
        }, headers=auth_headers).json()

        client.patch(f"/admin/usuarios/{criado['id']}/desativar", headers=auth_headers)

        resp = client.post("/auth/login", json={"email": "bloq@test.com", "senha": "senha123"})
        assert resp.status_code == 403

    def test_desativar_usuario_inexistente_retorna_404(self, client, auth_headers):
        resp = client.patch("/admin/usuarios/9999/desativar", headers=auth_headers)
        assert resp.status_code == 404

    def test_desativar_sem_autenticacao_retorna_401(self, client):
        resp = client.patch("/admin/usuarios/1/desativar")
        assert resp.status_code == 401
