import flet as ft
import requests

def profile_view(page: ft.Page, t, c):
    def load_profile():
        token = page.session.store.get("token")
        if not token:
            return

        res = requests.get(
            "http://localhost:3000/api/usuario/perfil",
            headers={"Authorization": f"Bearer {token}"}
        )

        if res.status_code == 200:
            user = res.json()["user"]
            page.session.store.set("user_name", user["nombre"])
            page.session.store.set("user_email", user["email"])
            page.session.store.set("user_avatar", user.get("avatar"))


    load_profile()
    
    snackbar = ft.SnackBar(
    content=ft.Text("", color="white"),
    bgcolor="#4CAF50",)
    
    page.snack_bar = snackbar

    bg_color = "#0F0F10"
    card_surface = "#1C1C1E"
    accent_color = "#007AFF"
    
    avatar_options = [
        "https://api.dicebear.com/7.x/pixel-art/png?seed=Valentina",
        "https://api.dicebear.com/9.x/pixel-art/png?seed=Avery",
        "https://api.dicebear.com/9.x/pixel-art/png?seed=Wyatt",
        "https://api.dicebear.com/9.x/pixel-art/png?seed=Ryker",
    ]
    
    # Cargar avatar desde la sesión o usar el default
    current_avatar = page.session.store.get("user_avatar") or avatar_options[0]
    
    user_avatar = ft.Image(
        src=current_avatar,
        fit="cover",
        width=100, height=100,
        border_radius=50,
    )

    # Referencias a los campos para acceder a sus valores
    first_name_ref = ft.Ref[ft.TextField]()
    email_ref = ft.Ref[ft.TextField]()

    def select_avatar(e):
        user_avatar.src = e.control.data
        user_avatar.update()
        dlg.open = False
        page.update()

    options_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Image(src=url, width=60, height=60, border_radius=30),
                on_click=select_avatar,
                data=url,
                border=ft.border.all(1, "#2C2C2E"),
                border_radius=30,
            ) for url in avatar_options
        ],
        alignment="center",
        spacing=10,
    )

    dlg = ft.AlertDialog(
        title=ft.Text("Choose an Avatar", size=16),
        content=ft.Container(content=options_row, padding=10),
        actions=[
            ft.TextButton("Cancel", on_click=lambda _: (setattr(dlg, "open", False), page.update())),
        ],
    )

    def open_dlg(e):
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def show_snackbar(message, is_error=False):
        snackbar.content.value = message
        snackbar.bgcolor = "#D32F2F" if is_error else "#4CAF50"
        snackbar.open = True
        page.update()


    def save_profile(e):
        try:
            token = page.session.store.get("token")

            if not token:
                show_snackbar("Error: sesión no válida", is_error=True)
                return

            nombre = first_name_ref.current.value
            email = email_ref.current.value

            if not nombre or not email:
                show_snackbar("Completa todos los campos", is_error=True)
                return

            payload = {
                "nombre": nombre,
                "email": email,
                "avatar": user_avatar.src
            }

            response = requests.put(
                "http://localhost:3000/api/usuario/update",
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )

            if response.status_code == 200:
                data = response.json()

                # Actualizar sesión
                page.session.store.set("user_name", data["user"]["nombre"])
                page.session.store.set("user_email", data["user"]["email"])
                page.session.store.set("user_avatar", data["user"].get("avatar"))
                
                first_name_ref.current.value = data["user"]["nombre"]
                email_ref.current.value = data["user"]["email"]

                show_snackbar("✅ Perfil actualizado correctamente")
                page.update()
            else:
                error = response.json().get("error", "Error desconocido")
                show_snackbar(error, is_error=True)

        except Exception as ex:
            show_snackbar(str(ex), is_error=True)

    def cambiar_password():
        pass
        
    def profile_field(label, value, ref):
        return ft.Column([
            ft.Text(f"{label}*", size=12, color=accent_color, weight="w500"),
            ft.TextField(
                ref=ref,
                value=value,
                text_size=14,
                color="white",
                border="underline",
                border_color="#2C2C2E",
                focused_border_color=accent_color,
                height=40,
                content_padding=ft.padding.only(bottom=10),
            )
        ], spacing=5)

    avatar_section = ft.Stack([
        ft.Container(
            content=user_avatar,
            width=100, height=100,
            border_radius=50,
            border=ft.border.all(2, "#2C2C2E"),
            on_click=open_dlg,
        ),
        ft.Container(
            content=ft.Icon(ft.Icons.EDIT, size=14, color="white"),
            bgcolor=accent_color,
            width=30, height=30,
            border_radius=15,
            border=ft.border.all(2, card_surface),
            bottom=0, right=0,
            alignment=ft.Alignment.CENTER,
            on_click=open_dlg,
        )
    ])

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar cambios"),
        content=ft.Text("¿Seguro que quieres guardar los cambios en tu perfil?"),
        actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def close_confirm_dialog():
        confirm_dialog.open = False
        page.update()

    def confirm_save():
        confirm_dialog.open = False
        page.update()
        save_profile(None)

    
    def open_confirm_dialog(e):
        confirm_dialog.actions = [
            ft.TextButton(
                "Cancelar",
                on_click=lambda _: close_confirm_dialog()
            ),
            ft.TextButton(
                "Guardar",
                on_click=lambda _: confirm_save()
            ),
        ]

        page.overlay.append(confirm_dialog)
        confirm_dialog.open = True
        page.update()


    main_card = ft.Container(
        width=400, height=700,
        bgcolor=card_surface,
        border_radius=30,
        padding=30,
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color="white", on_click=lambda _: page.go("/home")),
                ft.Text("Edit Profile", size=18, weight="bold", color="white"),
                ft.Container(width=40)
            ], alignment="spaceBetween"),
            ft.Container(height=10),
            ft.Row([avatar_section], alignment="center"),
            ft.Container(height=20),
            profile_field("First Name", page.session.store.get("user_name") or "User", first_name_ref),
            profile_field("Email", page.session.store.get("user_email") or "user@gmail.com", email_ref),
            ft.Container(height=30),
            ft.ElevatedButton(
                "Save",
                bgcolor=accent_color,
                color="white",
                height=50,
                width=340,
                on_click=open_confirm_dialog
            ),
            ft.OutlinedButton(
                "Change Password",
                height=50,
                width=340,
                style=ft.ButtonStyle(
                    color=accent_color,
                    side={"": ft.BorderSide(1, accent_color)},
                    shape=ft.RoundedRectangleBorder(radius=12)
                ),
                on_click=cambiar_password
            ),
        ], horizontal_alignment="center", spacing=15)
    )

    return ft.View(
        route="/profile",
        bgcolor=bg_color,
        controls=[
            ft.Container(
                content=main_card,
                alignment=ft.Alignment.CENTER,
                expand=True
            )
        ],
    )