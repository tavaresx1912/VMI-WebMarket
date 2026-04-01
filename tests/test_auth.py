import pytest
from jose import JWTError
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.models.user import User


class TestHashSenha:
    def test_hash_diferente_do_original(self):
        assert hash_password("minhasenha") != "minhasenha"

    def test_verificacao_senha_correta(self):
        h = hash_password("minhasenha")
        assert verify_password("minhasenha", h) is True

    def test_verificacao_senha_errada(self):
        h = hash_password("minhasenha")
        assert verify_password("outrasenha", h) is False

    def test_mesmo_input_gera_hashes_diferentes(self):
        # bcrypt usa salt aleatório a cada chamada
        assert hash_password("abc") != hash_password("abc")


class TestJWT:
    def test_token_criado_e_decodificado_corretamente(self):
        # sub deve ser string conforme RFC 7519
        token = create_access_token({"sub": "42", "role": "admin"})
        payload = decode_access_token(token)
        assert payload["sub"] == "42"
        assert payload["role"] == "admin"

    def test_token_invalido_levanta_excecao(self):
        with pytest.raises(JWTError):
            decode_access_token("token.completamente.invalido")

    def test_token_adulterado_levanta_excecao(self):
        token = create_access_token({"sub": 1})
        adulterado = token[:-5] + "XXXXX"
        with pytest.raises(JWTError):
            decode_access_token(adulterado)


class TestLoginEndpoint:
    def test_login_valido_retorna_token(self, client, db):
        db.add(User(nome="U", email="u@test.com", senha_hash=hash_password("senha123"), role="usuario", ativo=True))
        db.commit()

        resp = client.post("/auth/login", json={"email": "u@test.com", "senha": "senha123"})

        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_token_contem_role_e_sub_como_string(self, client, db):
        db.add(User(nome="A", email="a@test.com", senha_hash=hash_password("s"), role="admin", ativo=True))
        db.commit()

        token = client.post("/auth/login", json={"email": "a@test.com", "senha": "s"}).json()["access_token"]
        payload = decode_access_token(token)

        assert payload["role"] == "admin"
        assert isinstance(payload["sub"], str)

    def test_login_senha_errada_retorna_401(self, client, db):
        db.add(User(nome="U", email="u@test.com", senha_hash=hash_password("certa"), role="usuario", ativo=True))
        db.commit()

        resp = client.post("/auth/login", json={"email": "u@test.com", "senha": "errada"})
        assert resp.status_code == 401

    def test_login_email_inexistente_retorna_401(self, client):
        resp = client.post("/auth/login", json={"email": "nao@existe.com", "senha": "qualquer"})
        assert resp.status_code == 401

    def test_login_usuario_inativo_retorna_403(self, client, db):
        db.add(User(nome="U", email="u@test.com", senha_hash=hash_password("s"), role="usuario", ativo=False))
        db.commit()

        resp = client.post("/auth/login", json={"email": "u@test.com", "senha": "s"})
        assert resp.status_code == 403

    def test_login_email_formato_invalido_retorna_422(self, client):
        resp = client.post("/auth/login", json={"email": "nao-e-um-email", "senha": "123"})
        assert resp.status_code == 422


class TestRotasProtegidas:
    def test_sem_token_retorna_401(self, client):
        resp = client.get("/admin/usuarios")
        assert resp.status_code == 401

    def test_token_invalido_retorna_401(self, client):
        resp = client.get("/admin/usuarios", headers={"Authorization": "Bearer token.falso"})
        assert resp.status_code == 401

    def test_role_insuficiente_retorna_403(self, client, db):
        db.add(User(nome="U", email="u@test.com", senha_hash=hash_password("s"), role="usuario", ativo=True))
        db.commit()
        token = client.post("/auth/login", json={"email": "u@test.com", "senha": "s"}).json()["access_token"]

        resp = client.get("/admin/usuarios", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_usuario_desativado_com_token_valido_retorna_403(self, client, db):
        """Token emitido antes da desativação não deve dar acesso."""
        user = User(nome="A", email="a@test.com", senha_hash=hash_password("s"), role="admin", ativo=True)
        db.add(user)
        db.commit()

        token = client.post("/auth/login", json={"email": "a@test.com", "senha": "s"}).json()["access_token"]

        # desativa diretamente no banco após emissão do token
        user.ativo = False
        db.commit()

        resp = client.get("/admin/usuarios", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
