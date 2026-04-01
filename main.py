import uvicorn

if __name__ == "__main__":
    # Ponto de entrada para rodar a aplicação em desenvolvimento
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
