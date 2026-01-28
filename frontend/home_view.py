import asyncio
import flet as ft
import time
from fpdf import FPDF
import os
import json
import requests

API_GENERATE_URL = "http://localhost:3000/api/actividades/generate-ia"

def home_view(page: ft.Page, t, c):
    # bg_color = "#0F0F10"
    # card_surface = "#1C1C1E" 
    # text_secondary = "#8E8E93"

    is_dark = page.session.store.get("theme")

    accent_gradient = ft.LinearGradient(
        begin=ft.Alignment.TOP_LEFT,
        end=ft.Alignment.BOTTOM_RIGHT,
        colors=[c['accent'], c['accent_gradient']],
    )

    all_conversations = [
        {
            "id": "chatId_mongo",
            "title": "DAM 1 - Media",
        }
    ]
    
    current_chat_id = None
    
    async def load_chats_from_backend():
        try:
            token = page.session.store.get("token")
            if not token:
                raise Exception("No authentication token found")

            headers = {"Authorization": f"Bearer {token}"}

            res = await asyncio.to_thread(
                requests.get,
                "http://localhost:3000/api/historial/chats",
                headers=headers,
                timeout=5
            )

            if res.status_code != 200:
                raise Exception(f"Server error: {res.status_code}")

            # Ensure JSON response
            if "application/json" not in res.headers.get("Content-Type", ""):
                raise Exception("Invalid response format")

            data = res.json()

            all_conversations.clear()
            for chat in data:
                all_conversations.append({
                    "id": chat.get("id"),
                    "title": chat.get("title", "Untitled chat")
                })

            update_drawer()

        except requests.exceptions.RequestException as e:
            snack_bar = ft.SnackBar(
                ft.Text("Network error while loading chats"),
                bgcolor="#B00020",
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()

        except Exception as e:
            print("LOAD CHAT ERROR:", e)
            snack_bar = ft.SnackBar(
                ft.Text(str(e)),
                bgcolor="#B00020",
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()

        
    async def load_messages_from_backend(chat_id):
        token = page.session.store.get("token")
        headers = {"Authorization": f"Bearer {token}"}

        res = await asyncio.to_thread(
            requests.get,
            f"http://localhost:3000/api/historial/chats/{chat_id}/mensajes",
            headers=headers
        )

        if res.status_code != 200:
            return []

        messages = []
        for m in res.json():
            messages.append({
                "is_user": m["role"] == "user",
                "text": m["message"]
            })

        return messages
    
    async def open_chat(chat):
        nonlocal current_chat_id

        current_chat_id = chat["id"]
        results_list.controls.clear()

        messages = await load_messages_from_backend(current_chat_id)

        for msg in messages:
            bubble = (
                user_message(msg["text"])
                if msg["is_user"]
                else chat_message(msg["text"])
            )
            bubble.opacity = 1
            bubble.offset = ft.Offset(0, 0)
            results_list.controls.append(bubble)

        header_section.visible = False
        form_section.visible = False
        results_section.visible = True

        btn_text.text = t['home']['btn_edit']
        generate_btn.on_click = show_edit_sheet

        await page.close_drawer()
        page.update()

    drawer = ft.NavigationDrawer(
        bgcolor=c['card'],
    )    
    
    async def open_drawer(e):
        drawer.open = True
        await page.show_drawer()
        drawer.update()
        page.update()

    user_name = page.session.store.get("user_name") or "User"
    user_initial = user_name[0].upper()

    profile_button = ft.Container(
        content=ft.Text(
            user_initial, 
            size=12, 
            weight="bold", 
            color="white"
        ),
        alignment=ft.Alignment.CENTER,
        width=32,
        height=32,
        bgcolor=c['accent'],
        border_radius=16,
        on_click=lambda _: page.go("/profile"),
        ink=True,
        tooltip=t['home']['profile_tooltip'],
    )
    
    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.MENU_ROUNDED, 
                    icon_color=c['text'],
                    on_click=open_drawer,
                ),
                ft.Text(t['home']['title'], size=18, weight="bold", color=c['text']),
                profile_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
    )
    
    def user_message(content):
        container = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("You", size=12, weight="bold", color=c['text'], text_align=ft.TextAlign.RIGHT),
                            ft.Text(content, size=14, color=c['text'], selectable=True, text_align=ft.TextAlign.LEFT,width=290,),
                        ],
                        spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END, expand=True,
                    ),
                    ft.Container(content=ft.Text(user_initial, size=12, weight="bold", color="white"), width=30, height=30, bgcolor=c['accent'], border_radius=15, alignment=ft.Alignment.CENTER),
                ],
                vertical_alignment="start", alignment=ft.MainAxisAlignment.END,
            ),
            padding=ft.padding.symmetric(vertical=10),
            offset=ft.Offset(0.3, 0),
            opacity=0,
            animate_opacity=300,
            animate_offset=ft.Animation(600, ft.AnimationCurve.EASE_OUT_QUART),
        )
        return container

    def chat_message(content):
        def on_download_click(e):
            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=c['card'],
                title=ft.Text(t['home']['pdf_pop'], color= c['text']),
                content=ft.Text(t['home']['pdf_pop_text'], color= c['text']),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda _: close_dialog(dialog)),
                    ft.ElevatedButton(
                        "Download",
                        icon=ft.Icons.FILE_DOWNLOAD_ROUNDED,
                        on_click=lambda _: confirm_download(dialog),
                        style=ft.ButtonStyle(
                            color=c['accent']
                        ),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
            
        def close_dialog(dialog):
            dialog.open = False
            page.update()

        def confirm_download(dialog):
            dialog.open = False
            page.update()

            generate_pdf(content)
            
            snack_bar = ft.SnackBar(
                ft.Text(t['home']['snack_bar']),
                bgcolor="#2E7D32",
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()



            # generate_pdf(content)
            

        container = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=16, color="white"), 
                        width=30, height=30, bgcolor="#383838", border_radius=15, 
                        alignment=ft.Alignment.CENTER
                    ),
                    ft.Column([
                        ft.Row([
                            ft.Text(t['home']['chat_name'], size=12, weight="bold", color=c['text']),
                            ft.Container(
                                content=ft.IconButton(
                                    icon=ft.Icons.FILE_DOWNLOAD_ROUNDED,
                                    icon_size=16,
                                    icon_color="#AFAFBD",
                                    tooltip=t['home']['chat_tooltip'],
                                    on_click=on_download_click,
                                    visual_density=ft.VisualDensity.COMPACT,
                                ),
                                width=50,
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), 
                        ft.Text(content, size=14, color=c['text'], selectable=True)
                    ], spacing=2, expand=True),
                ],
                vertical_alignment="start",
            ),
            padding=ft.padding.symmetric(vertical=10),
            offset=ft.Offset(-0.3, 0),
            opacity=0,
            animate_opacity=300,
            animate_offset=ft.Animation(600, ft.AnimationCurve.EASE_OUT_QUART),
        )
        return container
    
    
    def generate_pdf(text_content):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=t['home']['title'], ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=text_content)
        
        filename = "Exam_Export.pdf"
        pdf.output(filename)
        
        # os.startfile(filename) if hasattr(os, 'startfile') else None
    
    def clear_chat_view():
        nonlocal current_chat_id
        current_chat_id = None
        results_list.controls.clear()
        header_section.visible = True
        form_section.visible = True
        results_section.visible = False
        btn_text.text = t['home']['btn_start']
        generate_btn.on_click = handle_generate
        page.update()
        
    async def start_new_conversation(e):
        if len(results_list.controls) > 0:
            title = f"{curso_dd.value} {ciclo_dd.value} - {dificultad_dd.value} {solucion_dd.value}"

            messages_data = []
            for control in results_list.controls:
                row = control.content
                if row.alignment == ft.MainAxisAlignment.END:
                    message_column = row.controls[0]
                    is_user = True
                else:
                    message_column = row.controls[1]
                    is_user = False
                msg_text = message_column.controls[1].value
                messages_data.append(
                    {"text": msg_text, "is_user": is_user}
                )

            all_conversations.insert(
                0,
                {
                    "title": title,
                    "messages": messages_data,
                },
            )

            update_drawer()

        clear_chat_view()
    
    async def update_chat_title(chat_id, new_title):
        token = page.session.store.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        await asyncio.to_thread(
            requests.put,
            f"http://localhost:3000/api/historial/chats/{chat_id}",
            json={"title": new_title},
            headers=headers,
        )
        
    def open_edit_chat_title(chat):
        title_input = ft.TextField(
            value=chat["title"],
            prefix_icon=ft.Icons.EDIT,
            border_radius=12,
            border_color=c['border'],
            focused_border_color=c['accent'],
            bgcolor=c["input"],
            color=c['text'],
            height=55,
        )

        async def save_title(e):
            await update_chat_title(chat["id"], title_input.value)
            await load_chats_from_backend()
            bs.open = False
            page.update()

        bs = ft.BottomSheet(
            ft.Container(
                padding=20,
                bgcolor=c['card'],
                border_radius=ft.BorderRadius(30, 30, 0, 0),
                content=ft.Column([
                        ft.Container(
                            width=40, height=4, 
                            bgcolor="#48484A", 
                            border_radius=2, 
                        ),
                        
                        ft.Text(t['home']['btn_edit_title'], size=20, weight="bold", color=c['text'], text_align="center"),
                        title_input,
                        ft.Container(height=5),
                        ft.ElevatedButton(
                            t['profile']['btn_save'],
                            bgcolor=c['accent'],
                            color="white",
                            height=50,
                            width=250,
                            on_click=save_title
                        ),
                    ],
                    tight=True,
                    horizontal_alignment="center",
                    spacing=15
                )
            ),
            open=True
        )

        page.overlay.append(bs)
        page.update()
        
    def confirm_delete_chat(chat):
        
            
        async def delete_chat(dialog):
            token = page.session.store.get("token")
            headers = {"Authorization": f"Bearer {token}"}

            await asyncio.to_thread(
                requests.delete,
                f"http://localhost:3000/api/historial/chats/{chat['id']}",
                headers=headers,
            )

            if current_chat_id == chat["id"]:
                clear_chat_view()

            await load_chats_from_backend()
            dialog.open=False
            page.update()

        def close_dialog(dialog):
            dialog.open=False
            page.update()
        

        dialog = ft.AlertDialog(
            title=ft.Text(t['home']['delete_conv']),
            content=ft.Text(t['home']['delete_conv_text']),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog(dialog)),
                ft.TextButton("Borrar", on_click=lambda _: page.run_task(delete_chat, dialog)),
            ],
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
        
    def chat_list_item(chat):
        return ft.ListTile(
            title=ft.Text(chat["title"], color=c['text']),
            leading=ft.Icon(ft.Icons.CHAT_OUTLINED,color=c['text']),
            trailing=ft.Row(
                width=80,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        icon_size=18,
                        icon_color=c['text'],
                        tooltip="Editar título",
                        on_click=lambda e, c=chat: open_edit_chat_title(c),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_size=18,
                        icon_color=c['text'],
                        tooltip="Borrar chat",
                        on_click=lambda e, c=chat: confirm_delete_chat(c),
                    ),
                ],
            ),
            on_click=lambda e, c=chat: page.run_task(open_chat, c),
        )
        
    
    async def handle_logout(e):
        await page.close_drawer()
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(t['home']['logout_pop'], color=c['text']),
            content=ft.Text(t['home']['logout_Pop_text'], color=c['text']),
            bgcolor=c['card'],
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda _: close_logout_dialog(dialog),
                    style=ft.ButtonStyle(
                        color=c['accent']
                    ),
                ),
                ft.ElevatedButton(
                    "Log out",
                    icon=ft.Icons.LOGOUT_ROUNDED,
                    style=ft.ButtonStyle(bgcolor="#FF453A", color="white"),
                    on_click=lambda _: page.run_task(confirm_logout, dialog),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def close_logout_dialog(dialog):
        dialog.open = False
        page.update()


    async def confirm_logout(dialog):
        dialog.open = False
        page.update()
        saved_lang = page.session.store.get("lang") or "Spanish"
        saved_theme = page.session.store.get("theme") or False
        page.session.store.clear()
        page.session.store.set("lang", saved_lang)
        page.session.store.set("theme", saved_theme)
        page.go("/")
      
    def update_drawer():
        def on_dropdown_change(e):
            page.session.store.set("lang", language_dropdown.value)
            current = page.route
            page.go("/refresh")
            page.go(current)
            
        def theme_switch(e):
            page.session.store.set("theme", e.control.value)
            theme_icon.name = (
                ft.Icons.LIGHT_MODE if is_dark else ft.Icons.DARK_MODE 
            )
            # print(e.control.value)
            current = page.route
            page.go("/refresh")
            page.go(current)
            
        history_items = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            controls=[
                ft.Container(height=20),
                ft.Container(
                    # padding=ft.padding.symmetric(horizontal=20),
                    padding=ft.padding.Padding(20, 0, 20, 0),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Button(
                        t['home']['new_item'],
                        icon=ft.Icons.ADD_ROUNDED,
                        color="white",
                        bgcolor=c['accent'],
                        height=45,
                        on_click=start_new_conversation,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                    )
                ),
                ft.Divider(height=40, color=c['border']),
                ft.Container(
                    # padding=ft.padding.only(left=20, bottom=10),
                    padding=ft.padding.Padding(20, 0, 0, 10), 
                    content=ft.Text(t['home']['history_text'], size=11, color=c['second_text'], weight="bold")
                ),
            ]
        )

        for chat in all_conversations:
            history_items.controls.append(chat_list_item(chat))
        
        language_dropdown = ft.Dropdown(
            width=180,
            height=50,
            hint_text="Lang",
            options=[ft.dropdown.Option("English"), ft.dropdown.Option("Spanish"), ft.dropdown.Option("Catalan")],
            on_text_change=on_dropdown_change,
            color=c['text'],
            bgcolor=c['dropdown'],
            border_color=c['border'],
            focused_border_color=c['accent'],
            hint_style=ft.TextStyle(color=c['text']),
        )
        theme_icon = ft.Icon(
            ft.Icons.LIGHT_MODE if is_dark else ft.Icons.DARK_MODE,
            color=c['text'],
            size=18,
        )
                
        theme_switch = ft.Switch( 
            value= is_dark,
            on_change=theme_switch,
        )

        logout_section = ft.Container(
            # padding=ft.padding.symmetric(vertical=20, horizontal=10),
            padding=ft.padding.Padding(10, 20, 10, 20),
            # border=ft.border.only(top=ft.BorderSide(1, c['border'])),
            border=ft.Border(top=ft.BorderSide(1, c['border'])),
            content=ft.Column(
                horizontal_alignment="center",
                spacing=20,
                controls=[
                    ft.Row(
                        alignment="spaceBetween",
                        controls=[
                            language_dropdown,
                            theme_icon,
                            theme_switch,
                        ]
                    ),
                    ft.TextButton(
                        width=280, 
                        height=40,
                        style=ft.ButtonStyle(
                            bgcolor={"": "rgba(255, 255, 255, 0.05)"}, 
                            shape=ft.RoundedRectangleBorder(radius=5),
                        ),
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.LOGOUT_ROUNDED, color="#FF453A", size=20),
                                ft.Text("Logout", color="#FF453A", weight="bold"),
                            ],
                            alignment="center",
                            spacing=10,
                        ),
                        on_click=handle_logout,
                    )
                ]
            )
        )

        drawer.controls = [
            ft.Container(
                height=page.height if page.height else 800, 
                content=ft.Column(
                    [
                        history_items,  
                        logout_section  
                    ],
                    tight=True,
                ),
            )
        ]
        
        try:
            drawer.update()
        except:
            pass
                           
    def show_edit_sheet(e):
        def close_bs(e):
            bs.open = False
            bs.update()
            page.run_task(handle_generate, None),
        bs = ft.BottomSheet(
            ft.Container(
                width=450,
                padding=25,
                bgcolor=c['card'],
                border_radius=ft.border_radius.only(top_left=30, top_right=30),
                content=ft.Column(
                    [
                        ft.Container(
                            width=40, height=4, 
                            bgcolor="#48484A", 
                            border_radius=2, 
                        ),
                        ft.Text(t['home']['edit_config'], size=16, weight="bold",color=c['text']),
                        dificultad_dd,
                        details_input,
                        ft.Divider(color="transparent", height=5),
                        ft.ElevatedButton(
                            t['home']['btn_update'],
                            color="white",
                            bgcolor=c['accent'],
                            height=45,
                            width=180,
                            on_click=close_bs,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                        ),
                    ],
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=30,
                ),
            ),
            open=True,
        )
        page.overlay.append(bs)
        page.update()
        
    header_section = ft.Column(
        [
            ft.Text(t['home']['second_title'], size=20, weight="bold", color=c['text']),
            ft.Text(t['home']['subtitle'], color=c['second_text'], size=13),
        ], 
        spacing=2,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=True
    )
    
    def create_mobile_dropdown(label, options):
        return ft.Dropdown(
            label=label,
            expand=True,
            width=300,
            label_style=ft.TextStyle(color=c['text'], size=11),
            border_radius=12,
            border_width=1,
            border_color=c['border'],
            bgcolor=c['dropdown'],
            color=c['text'],
            focused_border_color=c['accent'],
            options=[ft.dropdown.Option(opt) for opt in options],
            height=60,
            # content_padding=ft.padding.only(left=15, bottom=12),
            content_padding=ft.padding.Padding(15, 0, 0, 12),
            
        )

    ciclo_dd = create_mobile_dropdown(t['home']["ciclo"], ["DAM", "DAW", "ASIX"])
    curso_dd = create_mobile_dropdown(t['home']["curso"], ["1", "2"])
    dificultad_dd = create_mobile_dropdown(t['home']["dificultad"], ["Baja", "Media", "Alta"])
    solucion_dd = create_mobile_dropdown(t['home']["solución"], ["Si", "No"])
    
    details_input = ft.TextField(
        label=t['home']['context_lable'],
        label_style=ft.TextStyle(color=c['second_text'], size=11),
        hint_text=t['home']['details_input'],
        hint_style=ft.TextStyle(color="#48484A", size=13),
        multiline=True,
        min_lines=3,
        max_lines=4,
        border_radius=12,
        border_width=1,
        border_color=c['border'],
        bgcolor=c['input'],
        color=c['text'],
        focused_border_color=c['accent'],
        text_size=14,
    )

    form_section = ft.Column(
        [ciclo_dd, curso_dd, dificultad_dd, solucion_dd, details_input],
        spacing=5,
        visible=True
    )

    results_list = ft.Column(spacing=5)
    results_section = ft.Column(
        [
            ft.Divider(height=1, color="#2C2C2E"),
            results_list,
        ],
        visible=False,
    )
    
    async def handle_generate(e):
        nonlocal current_chat_id
        
        token = page.session.store.get("token")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        if form_section.visible:
            header_section.visible = False
            form_section.visible = False
            results_section.visible = True
            generate_btn.on_click = show_edit_sheet
            btn_text.text = "Edit"
            page.update() 

        if solucion_dd.value=="Si":
            prompt_text = f"Genera un examen para el {curso_dd.value or 'None'} de {ciclo_dd.value or 'None'} con una dificultad {dificultad_dd.value or 'Baja'}, y enseñame la solución. Otros detalles: {details_input.value}"
        else:
            prompt_text = f"Genera un examen para el {curso_dd.value or 'None'} de {ciclo_dd.value or 'None'} con una dificultad {dificultad_dd.value or 'Baja'}. Otros detalles: {details_input.value}"
        
        payload = {
            "ciclo": ciclo_dd.value if ciclo_dd.value else "DAM",
            "curso": curso_dd.value if curso_dd.value else 1,
            "nivel": dificultad_dd.value if dificultad_dd.value else "Baja",
            "solucion": solucion_dd.value if solucion_dd.value else "No",
            "userPrompt": prompt_text,
            "chatId": current_chat_id
        }
        
        u_msg = user_message(prompt_text)
        results_list.controls.append(u_msg)
        page.update()
        
        await asyncio.sleep(0.05)
        u_msg.opacity = 1
        u_msg.offset = ft.Offset(0, 0)
        u_msg.update()

        generate_btn.disabled = True
        progress_ring.visible = True
        page.update()

        try:
            response = await asyncio.to_thread(
                requests.post, 
                API_GENERATE_URL, 
                json=payload, 
                headers=headers, 
                timeout=10
            )

            if response.status_code in [200, 201]:
                data = response.json()
                if current_chat_id is None:
                    current_chat_id = data["chatId"]
                    await load_chats_from_backend()
                
                ai_content = (data.get("activity", {}).get("enunciado", "No content received from server."))
            else:
                ai_content = f"Error {response.status_code}: Could not generate exam. {response.text}"
        
        except Exception as err:
            ai_content = f"Connection Error: {str(err)}"

        ai_msg = chat_message(ai_content)
        results_list.controls.append(ai_msg)
        page.update()

        await asyncio.sleep(0.05)
        ai_msg.opacity = 1
        ai_msg.offset = ft.Offset(0, 0)
        ai_msg.update()
        
        progress_ring.visible = False
        generate_btn.disabled = False
        page.update()
        
    progress_ring = ft.ProgressRing(width=16, height=16, color="white", stroke_width=2, visible=False)
    btn_text = ft.Text(t['home']['btn_start'], weight="bold", size=15)

    generate_btn = ft.Container(
        content=ft.Row(
            [progress_ring, btn_text],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        gradient=accent_gradient,
        border_radius=12,
        width=330,
        height=54,
        on_click=handle_generate,
        animate_scale=ft.Animation(300, ft.AnimationCurve.DECELERATE),
    )

    main_card = ft.Container(
        width=450,
        height=600,
        margin=ft.Margin.only(top=40),
        bgcolor=c['card'],
        border_radius=24,
        border=ft.border.Border.all(1, c['border']), #"#2C2C2E"
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(controls=[
            ft.Container(
                height=520,
                padding=25,
                content=ft.Column(
                    controls=[
                        header_section,
                        ft.Divider(height=15, color="transparent"),
                        form_section,
                        results_section,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                    
                ),
            ),
            ft.Container(
                content=generate_btn,
                bottom=25,
                left=0,
                right=0,
                alignment=ft.Alignment.CENTER,
            ),
        ])
    )
    
    update_drawer()
    page.run_task(load_chats_from_backend)
    
    return ft.View(
        route="/home",
        bgcolor=c['bg'],
        drawer=drawer,
        # scroll=ft.ScrollMode.HIDDEN,
        controls=[
            ft.Column([        
                ft.Container(
                    expand=True,
                    content=ft.Column([
                        header,
                        main_card,
                        ft.Container(expand=True),
                        ft.Container(height=20),
                    ], horizontal_alignment="center")
                )
            ], expand=True)
        ],
    )