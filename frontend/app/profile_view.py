import flet as ft

def profile_view(page: ft.Page, t, c):
    bg_color = "#0F0F10"
    card_surface = "#1C1C1E"
    accent_color = "#007AFF"
    
    avatar_options = [
        "https://api.dicebear.com/7.x/pixel-art/png?seed=Valentina",
        "https://api.dicebear.com/9.x/pixel-art/png?seed=Avery",
        "https://api.dicebear.com/9.x/pixel-art/png?seed=Wyatt",
        "https://api.dicebear.com/9.x/pixel-art/png?seed=Ryker",
    ]
    
    user_avatar = ft.Image(
        src="https://api.dicebear.com/7.x/pixel-art/png?seed=Valentina",
        fit="cover",
        width=100, height=100,
        border_radius=50,
    )

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
        dlg.open = True
        page.update()

    def profile_field(label, value):
        return ft.Column([
            ft.Text(f"{label}*", size=12, color=accent_color, weight="w500"),
            ft.TextField(
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
            content=ft.Icon(ft.Icons.EDIT_OUTLINED, size=14, color="white"),
            bgcolor=accent_color,
            width=30, height=30,
            border_radius=15,
            border=ft.border.all(2, card_surface),
            bottom=0, right=0,
            alignment=ft.Alignment.CENTER,
            on_click=open_dlg,
        )
    ])

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
            profile_field("First Name", page.session.store.get("user_name") or "User"),
            profile_field("Last Name", "test"),
            profile_field("Email", page.session.store.get("user_email") or "user@gmail.com"),
            ft.Container(height=30),
            ft.ElevatedButton("Save", bgcolor=accent_color, color="white", height=50, width=340),
            ft.OutlinedButton(
                "Change Password",
                height=50,
                width=340,
                style=ft.ButtonStyle(
                    color=accent_color,
                    side={"": ft.BorderSide(1, accent_color)},
                    shape=ft.RoundedRectangleBorder(radius=12)
                )
            ),
        ], horizontal_alignment="center", spacing=15)
    )

    return ft.View(
        route="/profile",
        bgcolor=bg_color,
        controls=[
            dlg,
            ft.Container(
                content=main_card,
                alignment=ft.Alignment.CENTER,
                expand=True
            )
        ],
    )