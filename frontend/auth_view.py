import flet as ft
import requests
import re

BASE_URL = "http://localhost:3000/api/auth"

def auth_view(page: ft.Page, t, c):
    
    is_login = True

    icon_container = ft.Container(
        content=ft.Icon(ft.Icons.LOCK_PERSON_OUTLINED, size=80, color=c['accent']),
        margin=ft.Margin(0, 0, 0, 10)
    )

    title = ft.Text(t['login']['title_signin'], size=26, weight=ft.FontWeight.BOLD, color=c['text'])
    subtitle = ft.Text(t['login']['subtitle_signin'], color=c['second_text'], size=13)

    username_field = ft.TextField(
        label="Nombre Completo",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_radius=12,
        border_color=c['border'],
        focused_border_color=c['accent'],
        bgcolor=c["input"],
        color=c['text'],
        height=55,
        visible=False 
    )

    email_field = ft.TextField(
        label=t['login']['email_label'],
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=12,
        border_color=c['border'],
        focused_border_color=c['accent'],
        bgcolor=c["input"],
        color=c['text'],
        height=55,
        keyboard_type=ft.KeyboardType.EMAIL,
    )

    password_field = ft.TextField(
        label=t['login']['password_label'],
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        border_radius=12,
        border_color=c['border'],
        focused_border_color=c['accent'],
        bgcolor=c["input"],
        color=c['text'],
        height=55,
    )

    message_text = ft.Text("", size=12, text_align=ft.TextAlign.CENTER)

    async def handle_auth(e):
        email = email_field.value.strip()
        password = password_field.value.strip()
        username = username_field.value.strip()
        
        error_msg = None
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        
        if not re.match(email_pattern, email):
            error_msg = "Introduce un correo electrónico válido"
        elif len(password) < 4:
            error_msg = "La contraseña debe tener al menos 4 caracteres"
        elif not is_login and len(username) < 3:
            error_msg = "El nombre debe tener al menos 3 caracteres"

        if error_msg:
            message_text.value = error_msg
            message_text.color = ft.Colors.RED_400
            page.update()
            return

        auth_button.disabled = True
        btn_text.value = "Cargando..."
        page.update()
        
        endpoint = "login" if is_login else "register"
        full_url = f"{BASE_URL}/{endpoint}"

        try:
            payload = {
                "email": email, 
                "password": password
            }
            if not is_login:
                payload["nombre"] = username
            
            response = requests.post(full_url, json=payload, timeout=5)
            data = response.json()

            if response.status_code in [200, 201]:
                user = data.get("user", data)
                
                page.session.store.set("token", data.get("token"))
                page.session.store.set("user_name", user.get("nombre"))
                page.session.store.set("user_email", user.get("email"))
                page.session.store.set("user_id", user.get("id") or user.get("_id"))
                
                await page.push_route("/home")
                return
            else:
                message_text.value = data.get('error') or "Error de credenciales"
                message_text.color = ft.Colors.RED_400
        
        except Exception:
            message_text.value = "No se pudo conectar con el servidor"
            message_text.color = ft.Colors.RED_400

        auth_button.disabled = False
        btn_text.value = t['login']['btn_login'] if is_login else t['login']['btn_create_account']
        page.update()
        
    def toggle_mode(e):
        nonlocal is_login
        is_login = not is_login
        
        username_field.visible = not is_login
        
        title.value = t['login']['title_signin'] if is_login else t['login']['title_signup']
        subtitle.value = t['login']['subtitle_signin'] if is_login else t['login']['subtitle_signup']
        btn_text.value = t['login']['btn_login'] if is_login else t['login']['btn_create_account']
        toggle_text_control.value = t['login']['toggle_signup'] if is_login else t['login']['toggle_signin']
        
        message_text.value = ""
        page.update()

    btn_text = ft.Text(t['login']['btn_login'], weight="bold")
    
    auth_button = ft.ElevatedButton(
        content=btn_text,
        style=ft.ButtonStyle(
            color="white", 
            bgcolor=c['accent'], 
            shape=ft.RoundedRectangleBorder(radius=12)
        ),
        width=320,
        height=50,
        on_click=handle_auth,
    )

    toggle_text_control = ft.Text(t['login']['toggle_signup'])
    toggle_button = ft.TextButton(
        content=toggle_text_control, 
        on_click=toggle_mode, 
        style=ft.ButtonStyle(color=c['accent'])
    )

    return ft.View(
        route="/",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        icon_container,
                        title,
                        subtitle,
                        username_field,
                        email_field,
                        password_field,
                        message_text,
                        auth_button,
                        ft.Row(
                            [
                                ft.Text(t['login']['need_account'], size=12, color="#B0B3B8"), 
                                toggle_button
                            ], 
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                bgcolor=c['card'],
                padding=40,
                border_radius=30,
                width=420,
                shadow=ft.BoxShadow(blur_radius=30, color=ft.Colors.with_opacity(0.4, "black")),
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        bgcolor=c['bg']
    )