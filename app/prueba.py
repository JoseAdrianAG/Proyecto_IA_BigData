# Frontend Flet (Python)
# Aplicación: Generador de actividades DAM / DAW / ASIX
# Este frontend consume un backend Node.js vía API REST

import flet as ft
import requests

API_URL = "http://localhost:3000/api"

# ----------------------
# COMPONENTES REUTILIZABLES
# ----------------------

def input_text(label, password=False):
    return ft.TextField(
        label=label,
        password=password,
        can_reveal_password=password,
        width=350
    )

# ----------------------
# PANTALLA LOGIN
# ----------------------

def login_view(page: ft.Page):
    email = input_text("Email")
    password = input_text("Contraseña", password=True)
    error_text = ft.Text(color=ft.Colors.RED)

    def login(e):
        try:
            res = requests.post(f"{API_URL}/auth/login", json={
                "email": email.value,
                "password": password.value
            })
            if res.status_code == 200:
                page.session.set("token", res.json()["token"])
                page.go("/dashboard")
            else:
                error_text.value = "Credenciales incorrectas"
                page.update()
        except Exception:
            error_text.value = "No se puede conectar con el servidor"
            page.update()

    return ft.View(
        route="/",
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Generador de actividades FP", size=26, weight="bold"),
                    email,
                    password,
                    ft.ElevatedButton("Entrar", on_click=login),
                    error_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        ]
    )

# ----------------------
# DASHBOARD
# ----------------------

def dashboard_view(page: ft.Page):
    ciclo = ft.Dropdown(
        label="Ciclo",
        options=[
            ft.dropdown.Option("DAM"),
            ft.dropdown.Option("DAW"),
            ft.dropdown.Option("ASIX")
        ],
        width=300
    )

    modulo = input_text("Módulo")

    curso = ft.Dropdown(
        label="Curso",
        options=[
            ft.dropdown.Option("1"),
            ft.dropdown.Option("2")
        ],
        width=300
    )

    dificultad = ft.Dropdown(
        label="Dificultad",
        options=[
            ft.dropdown.Option("baja"),
            ft.dropdown.Option("media"),
            ft.dropdown.Option("alta")
        ],
        width=300
    )

    resultado = ft.TextField(
        label="Actividad generada",
        multiline=True,
        min_lines=10,
        max_lines=20,
        width=600
    )

    def generar(e):
        token = page.session.get("token")
        headers = {"Authorization": f"Bearer {token}"}

        res = requests.post(
            f"{API_URL}/activities/generate",
            headers=headers,
            json={
                "ciclo": ciclo.value,
                "modulo": modulo.value,
                "curso": curso.value,
                "dificultad": dificultad.value
            }
        )

        if res.status_code == 200:
            resultado.value = res.json()["contenido"]
        else:
            resultado.value = "Error al generar la actividad"
        page.update()

    return ft.View(
        route="/dashboard",
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Nueva actividad", size=22, weight="bold"),
                    ciclo,
                    modulo,
                    curso,
                    dificultad,
                    ft.ElevatedButton("Generar actividad", on_click=generar),
                    resultado
                ],
                scroll=ft.ScrollMode.AUTO
            )
        ]
    )

# ----------------------
# APP PRINCIPAL
# ----------------------

def main(page: ft.Page):
    page.title = "Generador FP con IA"
    page.window_width = 900
    page.window_height = 700

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(login_view(page))
        elif page.route == "/dashboard":
            page.views.append(dashboard_view(page))
        page.update()

    page.on_route_change = route_change
    page.go(page.route)

ft.app(target=main)
