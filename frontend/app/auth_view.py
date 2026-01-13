import flet as ft
import requests

BASE_URL = "http://127.0.0.1:8000"

def auth_view(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    
    is_login = True

    icon_container = ft.Container(
        content=ft.Icon(ft.Icons.LOCK_PERSON_OUTLINED, size=80, color="#4D94FF"),
        margin=ft.margin.only(bottom=10)
    )

    title = ft.Text("Sign In", size=26, weight=ft.FontWeight.BOLD, color="white")
    subtitle = ft.Text("Enter valid credentials to continue", color="#B0B3B8", size=13)

    username_field = ft.TextField(
        label="User name",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_radius=12,
        border_color="#3A3B3C",
        focused_border_color="#4D94FF",
        bgcolor="#242526",
        height=55,
    )

    password_field = ft.TextField(
        label="Password",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        border_radius=12,
        border_color="#3A3B3C",
        focused_border_color="#4D94FF",
        bgcolor="#242526",
        height=55,
    )

    message_text = ft.Text("", size=12, text_align=ft.TextAlign.CENTER)

    def handle_auth(e):
        btn = auth_button.content 
        btn.disabled = True
        btn.content = ft.ProgressRing(width=20, height=20, color="white", stroke_width=2)
        page.update()

        current_mode_is_login = (title.value == "Sign In")
        
        endpoint = "/login" if current_mode_is_login else "/register"
        payload = {"username": username_field.value, "password": password_field.value}

        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=5)
            if response.status_code in (200, 201):
                page.go("/home")
                return 
            else:
                data = response.json()
                message_text.value = f"Error: {data.get('detail', 'Invalid credentials')}"
                message_text.color = ft.Colors.RED_400
        except Exception:
            message_text.value = "Server error. Try again."
            message_text.color = ft.Colors.RED_400

        btn.disabled = False
        btn.content = ft.Text("Login" if current_mode_is_login else "Create Account", weight="bold")
        page.update()

    def toggle_mode(e):
        nonlocal is_login
        is_login = not is_login
        title.value = "Sign In" if is_login else "Sign Up" 
        auth_button.content.content.value = "Login" if is_login else "Create Account"
        toggle_button.text = "Sign Up" if is_login else "Sign In"
        page.update()

    auth_button = ft.Container(
        content=ft.ElevatedButton(
            content=ft.Text("Login", weight="bold"),
            style=ft.ButtonStyle(
                color="white", 
                bgcolor="#0066FF", 
                shape=ft.RoundedRectangleBorder(radius=12)
            ),
            width=320,
            height=50,
            on_click=handle_auth,
        )
    )

    toggle_button = ft.TextButton("Sign Up", on_click=toggle_mode, style=ft.ButtonStyle(color="#4D94FF"))


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
                        password_field,
                        message_text,
                        auth_button,
                        ft.Row(
                            [ft.Text("Need an account?", size=12, color="#B0B3B8"), toggle_button], 
                            alignment="center"
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                bgcolor="#1C1C1E",
                padding=40,
                border_radius=30,
                width=450,
                height=600,
                shadow=ft.BoxShadow(
                    blur_radius=30, 
                    color=ft.Colors.with_opacity(0.4, "black")
                ),
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        bgcolor="#121212"
    )