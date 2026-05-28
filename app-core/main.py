from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI(title="app-core - Reservas")

DB_HOST = os.getenv("DB_HOST", "10.10.0.12")
DB_NAME = os.getenv("DB_NAME", "reservas_db")
DB_USER = os.getenv("DB_USER", "reservas_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "reservas123")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

class ReservaRequest(BaseModel):
    nombre: str
    email: str
    recurso_id: int
    fecha_reserva: str

@app.get("/health")
def health():
    return {"service": "app-core", "status": "ok"}

@app.get("/recursos")
def listar_recursos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, tipo, disponible FROM recursos ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "nombre": r[1],
            "tipo": r[2],
            "disponible": r[3]
        }
        for r in rows
    ]

@app.post("/reservas")
def crear_reserva(data: ReservaRequest):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id FROM recursos WHERE id=%s AND disponible=true;", (data.recurso_id,))
    recurso = cur.fetchone()

    if not recurso:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Recurso no disponible o no existe")

    cur.execute("SELECT id FROM usuarios WHERE email=%s;", (data.email,))
    usuario = cur.fetchone()

    if usuario:
        usuario_id = usuario[0]
    else:
        cur.execute(
            "INSERT INTO usuarios (nombre, email) VALUES (%s, %s) RETURNING id;",
            (data.nombre, data.email)
        )
        usuario_id = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO reservas (usuario_id, recurso_id, fecha_reserva) VALUES (%s, %s, %s) RETURNING id;",
        (usuario_id, data.recurso_id, data.fecha_reserva)
    )

    reserva_id = cur.fetchone()[0]
    conn.commit()

    cur.close()
    conn.close()

    return {
        "message": "Reserva creada correctamente",
        "reserva_id": reserva_id,
        "usuario_id": usuario_id,
        "recurso_id": data.recurso_id
    }

@app.get("/reservas")
def listar_reservas():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.id, u.nombre, u.email, re.nombre, r.fecha_reserva, r.estado
        FROM reservas r
        JOIN usuarios u ON r.usuario_id = u.id
        JOIN recursos re ON r.recurso_id = re.id
        ORDER BY r.id;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "usuario": r[1],
            "email": r[2],
            "recurso": r[3],
            "fecha_reserva": str(r[4]),
            "estado": r[5]
        }
        for r in rows
    ]
