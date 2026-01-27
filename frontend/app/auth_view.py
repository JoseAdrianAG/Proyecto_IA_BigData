import flet as ft
import requests

BASE_URL = "http://localhost:3000/api/auth"

def auth_view(page: ft.Page, t, c):
    page.theme_mode = ft.ThemeMode.DARK
    
    is_login = True

    
    icon_container = ft.Container(
        content=ft.Icon(ft.Icons.LOCK_PERSON_OUTLINED, size=80, color="#4D94FF"),
        margin=ft.margin.only(bottom=10)
    )

    title = ft.Text("Sign In", size=26, weight=ft.FontWeight.BOLD, color="white")
    subtitle = ft.Text("Enter valid credentials to continue", color="#B0B3B8", size=13)

    username_field = ft.TextField(
        label="Nombre",
        prefix_icon=ft.Icons.PERSON,
        border_radius=12,
        border_color="#3A3B3C",
        focused_border_color="#4D94FF",
        bgcolor="#242526",
        height=55,
    )
    
    email_field = ft.TextField(
        label="Email",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=12,
        border_color="#3A3B3C",
        focused_border_color="#4D94FF",
        bgcolor="#242526",
        height=55,
        keyboard_type=ft.KeyboardType.EMAIL,
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
        auth_button.content.disabled = True
        auth_button.content.content = ft.ProgressRing(width=20, height=20, color="white", stroke_width=2)
        page.update()

        current_mode_is_login = (title.value == "Sign In")
        
        endpoint = "login" if current_mode_is_login else "register"
        full_url = f"{BASE_URL}/{endpoint}"

        try:
            payload = {
                "nombre": username_field.value,
                "email": email_field.value, 
                "password": password_field.value
            }
            

            response = requests.post(full_url, json=payload, timeout=5)
            
            print("STATUS:", response.status_code)
            print("HEADERS:", response.headers)
            print("RAW RESPONSE:", response.text)

            
            if "application/json" in response.headers.get("Content-Type", ""):
                data = response.json()
            else:
                message_text.value = f"Server Error: {response.status_code}"
                message_text.color = ft.Colors.RED_400
                raise Exception("Non-JSON response received")

            if response.status_code == 200:
                user = data.get("user", {})

                page.session.store.set("token", data.get("token"))
                page.session.store.set("user_name", user.get("nombre", "User"))
                page.session.store.set("user_email", user.get("email"))
                page.session.store.set("user_id", user.get("id"))
                page.session.store.set("user_role", user.get("rol"))
                
                try:
                    page.go("/home")
                except Exception as err:
                    print("NAVIGATION ERROR:", err)

                return
 
            else:
                message_text.value = data.get('message') or data.get('error') or "Login failed"
                message_text.color = ft.Colors.RED_400
        
        except Exception as err:
            if "Expecting value" in str(err):
                message_text.value = "Backend returned HTML instead of JSON. Check URL."
            else:
                message_text.value = f"Connection Error: {str(err)}"
            message_text.color = ft.Colors.RED_400

        auth_button.content.disabled = False
        auth_button.content.content = ft.Text("Login" if current_mode_is_login else "Create Account", weight="bold")
        page.update()
        
    def toggle_mode(e):
        nonlocal is_login
        is_login = not is_login
        title.value = "Sign In" if is_login else "Sign Up" 
        auth_button.content.content.value = "Login" if is_login else "Create Account"
        toggle_button.text = "Sign Up" if is_login else "Sign In"
        subtitle.value = "Enter valid credentials to continue" if is_login else "Create a new account"
        message_text.value = ""
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

    toggle_button = ft.TextButton(
        "Sign Up", 
        on_click=toggle_mode, 
        style=ft.ButtonStyle(color="#4D94FF")
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
                                ft.Text("Need an account?", size=12, color="#B0B3B8"), 
                                toggle_button
                            ], 
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                bgcolor="#1C1C1E",
                padding=40,
                border_radius=30,
                width=420,
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