import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text

load_dotenv()


def create_app(init_db=True):
    app = Flask(__name__)
    CORS(app)

    app.config["JWT_SEED"] = os.getenv("JWT_SEED", "cambia-esto-en-produccion")
    database_url = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost:3306/db-store",
    )

    # pool_pre_ping y pool_recycle evitan errores por conexiones inactivas (guia 4.7)
    engine = create_engine(database_url, pool_pre_ping=True, pool_recycle=280)
    app.extensions["engine"] = engine

    if init_db:
        # La guia (5.4) usa el caso "la aplicacion crea las tablas sola al arrancar".
        # Si MySQL aun no esta listo, la app arranca igual y /health sigue funcionando.
        try:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "CREATE TABLE IF NOT EXISTS notes ("
                        "id INT AUTO_INCREMENT PRIMARY KEY, "
                        "body VARCHAR(255) NOT NULL, "
                        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                        ") CHARACTER SET utf8mb4"
                    )
                )
            print("Connected to MySQL")
        except Exception as exc:  # noqa: BLE001
            print(f"Connect Failed! {exc}")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/db-check")
    def db_check():
        """Ruta que SI consulta la base de datos (prueba definitiva del Paso 6)."""
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT DATABASE(), CURRENT_USER(), VERSION()")
            ).fetchone()
        return {"database": row[0], "user": row[1], "version": row[2]}

    @app.get("/notes")
    def list_notes():
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT id, body, created_at FROM notes ORDER BY id DESC")
            ).fetchall()
        return jsonify(
            [{"id": r[0], "body": r[1], "created_at": str(r[2])} for r in rows]
        )

    @app.post("/notes")
    def create_note():
        data = request.get_json(silent=True) or {}
        body = (data.get("body") or "").strip()
        if not body:
            return {"error": "El campo 'body' es obligatorio"}, 400
        with engine.begin() as conn:
            result = conn.execute(
                text("INSERT INTO notes (body) VALUES (:body)"), {"body": body}
            )
        return {"id": result.lastrowid, "body": body}, 201

    return app
