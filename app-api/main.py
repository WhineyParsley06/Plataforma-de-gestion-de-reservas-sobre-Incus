from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import os
import time

app = FastAPI(title="app-api - Plataforma de Reservas")

APP_API_REQUESTS = {}

@app.middleware("http")
async def app_api_metrics_middleware(request: Request, call_next):
    response = await call_next(request)
    key = (request.method, request.url.path, str(response.status_code))
    APP_API_REQUESTS[key] = APP_API_REQUESTS.get(key, 0) + 1
    return response

@app.get("/metrics")
def metrics():
    lines = [
        "# HELP app_api_http_requests_total Total de peticiones HTTP recibidas por app-api",
        "# TYPE app_api_http_requests_total counter"
    ]

    for (method, endpoint, status), count in APP_API_REQUESTS.items():
        lines.append(
            f'app_api_http_requests_total{{method="{method}",endpoint="{endpoint}",status="{status}"}} {count}'
        )

    return Response("\n".join(lines) + "\n", media_type="text/plain")


CORE_URL = os.getenv("CORE_URL", "http://10.20.0.11:8001")


class ReservaRequest(BaseModel):
    nombre: str
    email: str
    recurso_id: int
    fecha_reserva: str


@app.get("/health")
def health():
    return {
        "service": "app-api",
        "status": "ok",
        "core_url": CORE_URL
    }


@app.get("/api/recursos")
def api_recursos():
    try:
        r = requests.get(f"{CORE_URL}/recursos", timeout=5)
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reservas")
def api_reservas():
    try:
        r = requests.get(f"{CORE_URL}/reservas", timeout=5)
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reservas")
def api_crear_reserva(data: ReservaRequest):
    try:
        r = requests.post(
            f"{CORE_URL}/reservas",
            json=data.dict(),
            timeout=5
        )

        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text)

        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/reservas/{reserva_id}")
def api_eliminar_reserva(reserva_id: int):
    try:
        r = requests.delete(f"{CORE_URL}/reservas/{reserva_id}", timeout=5)

        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text)

        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reservas Académicas</title>
  <style>
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: #eef2f7;
      color: #1f2937;
    }

    header {
      background: linear-gradient(135deg, #2563eb, #1e40af);
      color: white;
      padding: 35px 20px;
      text-align: center;
    }

    header h1 {
      margin: 0;
      font-size: 32px;
    }

    header p {
      margin-top: 10px;
      font-size: 16px;
      opacity: 0.95;
    }

    main {
      max-width: 1100px;
      margin: 30px auto;
      padding: 0 20px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }

    .card {
      background: white;
      border-radius: 18px;
      padding: 24px;
      box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
    }

    .card h2 {
      margin-top: 0;
      color: #1d4ed8;
    }

    label {
      display: block;
      margin-top: 14px;
      font-weight: bold;
      font-size: 14px;
    }

    input, select {
      width: 100%;
      margin-top: 6px;
      padding: 11px;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      font-size: 15px;
      background: white;
    }

    button {
      margin-top: 18px;
      width: 100%;
      padding: 12px;
      border: none;
      border-radius: 10px;
      background: #2563eb;
      color: white;
      font-size: 16px;
      font-weight: bold;
      cursor: pointer;
    }

    button:hover {
      background: #1d4ed8;
    }

    .btn-delete {
      margin-top: 10px;
      width: auto;
      padding: 8px 12px;
      background: #dc2626;
      font-size: 13px;
    }

    .btn-delete:hover {
      background: #b91c1c;
    }

    .item {
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 14px;
      margin-bottom: 12px;
      background: #f8fafc;
    }

    .item strong {
      color: #111827;
    }

    .badge {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 999px;
      background: #dcfce7;
      color: #166534;
      font-size: 12px;
      margin-top: 6px;
    }

    .msg {
      margin-top: 14px;
      padding: 12px;
      border-radius: 10px;
      display: none;
    }

    .ok {
      background: #dcfce7;
      color: #166534;
    }

    .error {
      background: #fee2e2;
      color: #991b1b;
    }

    footer {
      text-align: center;
      padding: 20px;
      color: #64748b;
      font-size: 14px;
    }

    @media (max-width: 800px) {
      main {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <header>
    <h1>Plataforma de Gestión de Reservas</h1>
    <p>Laboratorios académicos sobre Incus · app-api · app-core · PostgreSQL</p>
  </header>

  <main>
    <section class="card">
      <h2>Recursos disponibles</h2>
      <div id="recursos">Cargando recursos...</div>
    </section>

    <section class="card">
      <h2>Crear reserva</h2>

      <label>Nombre</label>
      <input id="nombre" placeholder="Ej: David Valderrama">

      <label>Correo</label>
      <input id="email" placeholder="Ej: deivid870@hotmail.com">

      <label>Recurso</label>
      <select id="recurso_id">
        <option value="">Cargando recursos...</option>
      </select>

      <label>Fecha</label>
      <input id="fecha" type="date">

      <label>Hora</label>
      <select id="hora">
        <option value="">Selecciona una hora</option>
        <option value="07:00:00">07:00 a.m.</option>
        <option value="08:00:00">08:00 a.m.</option>
        <option value="09:00:00">09:00 a.m.</option>
        <option value="10:00:00">10:00 a.m.</option>
        <option value="11:00:00">11:00 a.m.</option>
        <option value="12:00:00">12:00 p.m.</option>
        <option value="13:00:00">01:00 p.m.</option>
        <option value="14:00:00">02:00 p.m.</option>
        <option value="15:00:00">03:00 p.m.</option>
        <option value="16:00:00">04:00 p.m.</option>
        <option value="17:00:00">05:00 p.m.</option>
        <option value="18:00:00">06:00 p.m.</option>
      </select>

      <button onclick="crearReserva()">Reservar</button>

      <div id="mensaje" class="msg"></div>
    </section>

    <section class="card" style="grid-column: 1 / -1;">
      <h2>Reservas registradas</h2>
      <div id="reservas">Cargando reservas...</div>
    </section>
  </main>

  <footer>
    Proyecto final de Sistemas Distribuidos · Infraestructura con Incus, Ansible y OpenTofu
  </footer>

  <script>
    async function cargarRecursos() {
      const contenedor = document.getElementById("recursos");
      const select = document.getElementById("recurso_id");

      try {
        const res = await fetch("/api/recursos");
        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.detail || "Error consultando recursos");
        }

        contenedor.innerHTML = "";
        select.innerHTML = '<option value="">Selecciona un recurso</option>';

        data.forEach(r => {
          contenedor.innerHTML += `
            <div class="item">
              <strong>${r.nombre}</strong><br>
              Tipo: ${r.tipo}<br>
              <span class="badge">${r.disponible ? "Disponible" : "No disponible"}</span>
            </div>
          `;

          if (r.disponible) {
            select.innerHTML += `<option value="${r.id}">${r.nombre}</option>`;
          }
        });
      } catch (e) {
        contenedor.innerHTML = "No se pudieron cargar los recursos: " + e.message;
        select.innerHTML = '<option value="">No hay recursos disponibles</option>';
      }
    }

    async function cargarReservas() {
      const contenedor = document.getElementById("reservas");

      try {
        const res = await fetch("/api/reservas");
        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.detail || "Error consultando reservas");
        }

        if (data.length === 0) {
          contenedor.innerHTML = "Todavía no hay reservas registradas.";
          return;
        }

        contenedor.innerHTML = "";

        data.forEach(r => {
          contenedor.innerHTML += `
            <div class="item">
              <strong>${r.recurso}</strong><br>
              Usuario: ${r.usuario}<br>
              Correo: ${r.email}<br>
              Fecha: ${r.fecha_reserva}<br>
              Estado: <span class="badge">${r.estado}</span><br>
              <button class="btn-delete" onclick="eliminarReserva(${r.id})">Eliminar reserva</button>
            </div>
          `;
        });
      } catch (e) {
        contenedor.innerHTML = "No se pudieron cargar las reservas: " + e.message;
      }
    }

    async function crearReserva() {
      const mensaje = document.getElementById("mensaje");

      const nombre = document.getElementById("nombre").value.trim();
      const email = document.getElementById("email").value.trim();
      const recurso_id = document.getElementById("recurso_id").value;
      const fecha = document.getElementById("fecha").value;
      const hora = document.getElementById("hora").value;

      if (!nombre || !email || !recurso_id || !fecha || !hora) {
        mensaje.style.display = "block";
        mensaje.className = "msg error";
        mensaje.innerText = "Completa nombre, correo, recurso, fecha y hora.";
        return;
      }

      const data = {
        nombre: nombre,
        email: email,
        recurso_id: parseInt(recurso_id),
        fecha_reserva: fecha + " " + hora
      };

      try {
        const res = await fetch("/api/reservas", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(data)
        });

        const result = await res.json();

        if (!res.ok || !result.reserva_id) {
          throw new Error(result.detail || "La reserva no fue creada correctamente.");
        }

        mensaje.style.display = "block";
        mensaje.className = "msg ok";
        mensaje.innerText = "Reserva creada correctamente. ID: " + result.reserva_id;

        await cargarReservas();
      } catch (e) {
        mensaje.style.display = "block";
        mensaje.className = "msg error";
        mensaje.innerText = "Error al crear la reserva: " + e.message;
      }
    }

    async function eliminarReserva(id) {
      const confirmar = confirm("¿Seguro que deseas eliminar esta reserva?");

      if (!confirmar) {
        return;
      }

      try {
        const res = await fetch("/api/reservas/" + id, {
          method: "DELETE"
        });

        const result = await res.json();

        if (!res.ok) {
          throw new Error(result.detail || "No se pudo eliminar la reserva.");
        }

        await cargarReservas();
        alert("Reserva eliminada correctamente.");
      } catch (e) {
        alert("Error al eliminar la reserva: " + e.message);
      }
    }

    cargarRecursos();
    cargarReservas();
  </script>
</body>
</html>
    """
