import flet as ft
import requests
import httpx

BASE_URL = "http://localhost:3000/api/auth"

def profile_view(page: ft.Page, t, c):
    user_id = page.session.store.get("user_id")
    accent_color = c['accent']
    card_surface = c['card']
    text_color = c['text']
    border_color = c['border']

    name_input = ft.TextField(
        value=page.session.store.get("user_name") or "",
        text_size=14,
        color=c['text'],
        border="underline",
        border_color=c['border'],
        focused_border_color=accent_color,
        height=40,
        content_padding=ft.Padding(0, 0, 0, 10),
    )

    email_input = ft.TextField(
        value=page.session.store.get("user_email") or "",
        text_size=14,
        color=c['text'],
        border="underline",
        border_color=c['border'],
        focused_border_color=accent_color,
        height=40,
        content_padding=ft.Padding(0, 0, 0, 10),
    )

    old_pass = ft.TextField(
        label=t['profile']['current_password'],
        password=True,
        can_reveal_password=True,
        text_size=14,
        color=text_color,
        border="underline",
        border_color=border_color,
        focused_border_color=accent_color,
        height=45,
        content_padding=ft.Padding(0, 0, 0, 10),
    )

    new_pass = ft.TextField(
        label=t['profile']['new_password'],
        password=True,
        can_reveal_password=True,
        text_size=14,
        color=text_color,
        border="underline",
        border_color=border_color,
        focused_border_color=accent_color,
        height=45,
        content_padding=ft.Padding(0, 0, 0, 10),
    )

    confirm_new_pass = ft.TextField(
        label=t['profile']['confirm_new_password'],
        password=True,
        can_reveal_password=True,
        text_size=14,
        color=text_color,
        border="underline",
        border_color=border_color,
        focused_border_color=accent_color,
        height=45,
        content_padding=ft.Padding(0, 0, 0, 10),
    )

    def close_error_dialog(e):
        error_dialog.open = False
        page.update()

    error_dialog = ft.AlertDialog(
        title=ft.Text(t['profile']['error']),
        content=ft.Text(""),
        actions=[ft.TextButton("OK", on_click=close_error_dialog)],
    )

    def close_confirm_dialog(e):
        confirm_dialog.open = False
        page.update()

    async def confirm_password_change(e):
        if new_pass.value != confirm_new_pass.value:
            error_dialog.content.value = t['profile']['password_mismatch']
            error_dialog.open = True
            page.update()
            return

        confirm_dialog.open = False
        page.update()

        payload = {
            "id": user_id,
            "oldPassword": old_pass.value,
            "newPassword": new_pass.value
        }

        try:
            async with httpx.AsyncClient() as client:
                res = await client.put(
                    f"{BASE_URL}/change-password",
                    json=payload,
                    timeout=10
                )

            if res.status_code == 200:
                pass_sheet.open = False
                old_pass.value = ""
                new_pass.value = ""
                confirm_new_pass.value = ""

                snack_bar = ft.SnackBar(
                    ft.Text(t['profile']['password_updated']),
                    bgcolor="green"
                )
                page.overlay.append(snack_bar)
                snack_bar.open = True
            else:
                error_data = res.json()
                error_dialog.content.value = error_data.get("error", t['profile']['password_change_error'])
                error_dialog.open = True

            page.update()

        except httpx.RequestError:
            error_dialog.content.value = t['profile']['server_connection_error']
            error_dialog.open = True
            page.update()


    confirm_dialog = ft.AlertDialog(
        title=ft.Text(t['profile']['confirmation']),
        content=ft.Text(t['profile']['change_password_confirm']),
        actions=[
            ft.TextButton(t['profile']['btn_cancel'], on_click=close_confirm_dialog),
            ft.ElevatedButton(
                t['profile']['update'],
                bgcolor=accent_color,
                color="white",
                on_click=confirm_password_change,
            ),
        ],
    )

    page.overlay.extend([error_dialog, confirm_dialog])

    def open_confirm_dialog(e):
        if not old_pass.value or not new_pass.value:
            error_dialog.content.value = t['profile']['fill_all_fields']
            error_dialog.open = True
            page.update()
            return

        confirm_dialog.open = True
        page.update()

    pass_sheet = ft.BottomSheet(
        ft.Container(
            padding=ft.padding.only(left=25, right=25, top=10, bottom=30),
            bgcolor=card_surface,
            border_radius=ft.BorderRadius(30, 30, 0, 0),
            alignment=ft.Alignment.CENTER, 
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=40, height=4, 
                        bgcolor=ft.Colors.with_opacity(0.1, text_color), 
                        border_radius=10
                    )
                ], alignment="center"),
                
                ft.Container(height=5),
                
                ft.Text(t['profile']['profile_security'], size=20, weight="bold", color=text_color, text_align="center"),
                
                ft.Column([
                    ft.Column([
                        ft.Text(t['profile']['profile_verification'], size=11, weight="bold", color=accent_color),
                        old_pass,
                    ], spacing=2),

                    ft.Column([
                        ft.Text(t['profile']['profile_new_credential'], size=11, weight="bold", color=accent_color),
                        new_pass,
                        confirm_new_pass,
                    ], spacing=12),
                ], horizontal_alignment="center", spacing=20, width=320),

                ft.Container(height=10),

                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOCK_RESET_ROUNDED, size=20),
                        ft.Text(t['profile']['update'], weight="bold"),
                    ], alignment="center", spacing=10),
                    bgcolor=accent_color,
                    color="white",
                    height=48,
                    width=320, 
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                    on_click=open_confirm_dialog
                )
            ], 
            tight=True,
            horizontal_alignment="center",
            spacing=15
            )
        ),
    )
    page.overlay.append(pass_sheet)

    avatar_options = [
        "https://api.dicebear.com/7.x/pixel-art/png?seed=Valentina",
        "https://api.dicebear.com/9.x/pixel-art/png?seed=Avery",
        "https://api.dicebear.com/9.x/pixel-art/png?seed=Wyatt",
        "https://api.dicebear.com/9.x/pixel-art/png?seed=Ryker",
    ]

    user_avatar = ft.Image(
        src=avatar_options[0],
        fit="cover",
        width=100,
        height=100,
        border_radius=50,
    )

    def select_avatar(e):
        user_avatar.src = e.control.data
        user_avatar.update()
        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(
        title=ft.Text(t['profile']['title'], size=16),
        content=ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Image(src=url, width=60, height=60, border_radius=30),
                    on_click=select_avatar,
                    data=url,
                    border=ft.Border.all(1, c['border']),
                    border_radius=30,
                ) for url in avatar_options
            ], alignment="center", spacing=10),
            padding=10
        ),
    )

    async def save_profile(e):
        payload = {
            "id": user_id,
            "nombre": name_input.value,
            "email": email_input.value
        }

        try:
            response = requests.put(f"{BASE_URL}/update-profile", json=payload)

            if response.status_code == 200:
                data = response.json()
                page.session.store.set("user_name", data['user']['nombre'])
                page.session.store.set("user_email", data['user']['email'])

                snack_bar = ft.SnackBar(
                    ft.Text(t['profile']['profile_updated']),
                    bgcolor="green"
                )
            else:
                snack_bar = ft.SnackBar(
                    ft.Text(t['profile']['save_error']),
                    bgcolor="red"
                )
            
            page.overlay.append(snack_bar)
            snack_bar.open=True
            page.update()

        except Exception as err:
            print(f"Save Error: {err}")

    def profile_field(label, field):
        return ft.Column([
            ft.Text(f"{label}*", size=12, color=accent_color, weight="w500"),
            field
        ], spacing=5)

    avatar_section = ft.Stack([
        ft.Container(
            content=user_avatar,
            width=100,
            height=100,
            border_radius=50,
            border=ft.Border.all(2, c['border']),
            on_click=lambda _: (setattr(dlg, "open", True), page.update()),
        ),
        ft.Container(
            content=ft.Icon(ft.Icons.EDIT_OUTLINED, size=14, color="white"),
            bgcolor=accent_color,
            width=30,
            height=30,
            border_radius=15,
            border=ft.Border.all(2, card_surface),
            bottom=0,
            right=0,
            alignment=ft.Alignment.CENTER,
            on_click=lambda _: (setattr(dlg, "open", True), page.update()),
        )
    ])

    main_card = ft.Container(
        width=400,
        height=700,
        bgcolor=card_surface,
        border_radius=30,
        padding=30,
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                              icon_color=c['text'],
                              on_click=lambda _: page.go("/home")),
                ft.Text(t['profile']['title_edit'], size=18, weight="bold", color=c['text']),
                ft.Container(width=40)
            ], alignment="spaceBetween"),
            ft.Container(height=10),
            ft.Row([avatar_section], alignment="center"),
            ft.Container(height=20),
            profile_field(t['profile']['first_name'], name_input),
            profile_field(t['profile']['email'], email_input),
            ft.Container(height=30),
            ft.ElevatedButton(
                t['profile']['btn_save'],
                bgcolor=accent_color,
                color="white",
                height=50,
                width=340,
                on_click=save_profile
            ),
            ft.OutlinedButton(
                t['profile']['btn_change_pass'],
                height=50,
                width=340,
                style=ft.ButtonStyle(
                    color=c['text'],
                    side={"": ft.BorderSide(1, c['border'])},
                    shape=ft.RoundedRectangleBorder(radius=12)
                ),
                on_click=lambda _: (setattr(pass_sheet, "open", True), page.update())
            ),
        ], horizontal_alignment="center", spacing=15)
    )

    return ft.View(
        route="/profile",
        bgcolor=c['bg'],
        controls=[
            dlg,
            ft.Container(
                content=main_card,
                alignment=ft.Alignment.CENTER,
                expand=True
            )
        ],
    )
