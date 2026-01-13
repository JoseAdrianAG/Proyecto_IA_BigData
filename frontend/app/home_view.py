import asyncio
import flet as ft
import time
from fpdf import FPDF
import os

def home_view(page: ft.Page):
    bg_color = "#0F0F10"
    card_surface = "#1C1C1E" 
    accent_gradient = ft.LinearGradient(
        begin=ft.Alignment.TOP_LEFT,
        end=ft.Alignment.BOTTOM_RIGHT,
        colors=["#007AFF", "#0051AF"],
    )
    text_secondary = "#8E8E93"
    
    all_conversations = []
    
    MOCK_EXAM_DATA = {
        "title": "Python Programming Fundamentals",
        "questions": [
            "1. Explain the difference between 'is' and '==' in Python.",
            "2. Describe how memory management works with Python's Garbage Collector.",
            "3. Write a decorator that logs the execution time of a function.",
            "4. What are list comprehensions and why are they used?"
        ]
    }
    
    async def load_conversation(e):
        chat_index = drawer.selected_index - 1 
        
        if chat_index >= 0:
            selected_chat = all_conversations[chat_index]
            
            results_list.controls.clear()
            
            for msg in selected_chat["messages"]:
                if msg["is_user"]:
                    new_bubble = user_message(msg["text"])
                else:
                    new_bubble = chat_message(msg["text"])
                
                new_bubble.opacity = 1
                new_bubble.offset = ft.Offset(0, 0)
                results_list.controls.append(new_bubble)
            
            header_section.visible = False
            form_section.visible = False
            results_section.visible = True
            btn_text.text = "Edit"
            generate_btn.on_click = show_edit_sheet
            
            await page.close_drawer()
            page.update()

    drawer = ft.NavigationDrawer(
        bgcolor=card_surface, 
        on_change=load_conversation
    )    
    async def open_drawer(e):
        drawer.open = True
        await page.show_drawer()
        drawer.update()
        page.update()

    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.MENU_ROUNDED, 
                    icon_color="white", 
                    on_click=open_drawer,
                    visual_density=ft.VisualDensity.COMPACT
                ),
                ft.Text("Exam Generator", size=18, weight=ft.FontWeight.W_600, color="white"),
                ft.Container(
                    content=ft.Text("U", size=12, weight="bold"),
                    alignment=ft.Alignment.CENTER,
                    width=32,
                    height=32,
                    bgcolor="#007AFF",
                    border_radius=16,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        # padding=ft.padding.only(left=15, right=15, top=10),
    )
    
    def user_message(content):
        container = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("You", size=12, weight="bold", color="white", text_align=ft.TextAlign.RIGHT),
                            ft.Text(content, size=14, color="white", selectable=True, text_align=ft.TextAlign.RIGHT),
                        ],
                        spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END, expand=True,
                    ),
                    ft.Container(content=ft.Text("U", size=12, weight="bold", color="white"), width=30, height=30, bgcolor="#007AFF", border_radius=15, alignment=ft.Alignment.CENTER),
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
        def on_hover(e):
            e.control.scale = 1.1 if e.data == "true" else 1.0
            # Change background brightness on hover
            e.control.bgcolor = "#5286E0" if e.data == "true" else "#4472C4"
            e.control.update()
        def on_download_click(e):
            generate_pdf(content)

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
                            ft.Text("AI Assistant", size=12, weight="bold", color="white"),
                            ft.Container(
                                content=ft.IconButton(
                                    icon=ft.Icons.FILE_DOWNLOAD_ROUNDED,
                                    icon_size=16,
                                    icon_color="#AFAFBD",
                                    tooltip="Download Exam as PDF",
                                    on_click=on_download_click,
                                    visual_density=ft.VisualDensity.COMPACT,
                                ),
                                width=50,
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), 
                        ft.Text(content, size=14, color="white", selectable=True)
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
        pdf.cell(200, 10, txt="Generated Exam", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=text_content)
        
        filename = "Exam_Export.pdf"
        pdf.output(filename)
        
        os.startfile(filename) if hasattr(os, 'startfile') else None
    
    async def start_new_conversation(e):
        if len(results_list.controls) > 0:
            title = f"{curso_dd.value} {ciclo_dd.value} - {dificultad_dd.value}"

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


        results_list.controls.clear()
        header_section.visible = True
        form_section.visible = True
        results_section.visible = False
        btn_text.text = "Start Generating"
        generate_btn.on_click = handle_generate
        page.update()

    async def handle_logout(e):
        print("Logging out...")
        page.go("/")

    def update_drawer():
        history_items = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            controls=[
                ft.Container(height=20),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=20),
                    alignment=ft.Alignment.CENTER,
                    content=ft.ElevatedButton(
                        "New Conversation",
                        icon=ft.Icons.ADD_ROUNDED,
                        color="white",
                        bgcolor="#007AFF",
                        height=45,
                        on_click=start_new_conversation,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                    )
                ),
                ft.Divider(height=40, color="#2C2C2E"),
                ft.Container(
                    padding=ft.padding.only(left=20, bottom=10), 
                    content=ft.Text("RECENT HISTORY", size=11, color=text_secondary, weight="bold")
                ),
            ]
        )

        for chat in all_conversations:
            history_items.controls.append(
                ft.ListTile(
                    title=ft.Text(chat["title"], color="white", size=14),
                    leading=ft.Icon(ft.Icons.CHAT_OUTLINED, color=text_secondary),
                    on_click=load_conversation,
                )
            )

        logout_section = ft.Container(
            padding=ft.padding.symmetric(vertical=20),
            border=ft.border.only(top=ft.BorderSide(1, "#2C2C2E")),
            alignment=ft.Alignment.CENTER, 
            content=ft.TextButton(
                width=200, 
                height=35,
                style=ft.ButtonStyle(
                    bgcolor={"": ft.Colors.with_opacity(0.05, "white")}, 
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.LOGOUT_ROUNDED, color="#FF453A", size=20),
                        ft.Text("Logout", color="#FF453A", weight="bold"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                on_click=handle_logout,
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
                bgcolor=card_surface,
                border_radius=ft.border_radius.only(top_left=30, top_right=30),
                content=ft.Column(
                    [
                        ft.Container(
                            width=40, height=4, 
                            bgcolor="#48484A", 
                            border_radius=2, 
                        ),
                        ft.Text("Edit Config", size=16, weight="bold"),
                        dificultad_dd,
                        details_input,
                        ft.Divider(color="transparent", height=5),
                        ft.ElevatedButton(
                            "Update",
                            color="white",
                            bgcolor="#4472C4",
                            height=45,
                            width=180,
                            on_click=close_bs,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                        ),
                    ],
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
            ),
            open=True,
        )
        page.overlay.append(bs)
        page.update()
        
    header_section = ft.Column(
        [
            ft.Text("Exam Config", size=20, weight="bold", color="white"),
            ft.Text("change the difficulty and content", color=text_secondary, size=13),
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
            label_style=ft.TextStyle(color=text_secondary, size=11),
            border_radius=12,
            border_width=1,
            border_color="#2C2C2E",
            bgcolor="#242426",
            color="white",
            focused_border_color="#007AFF",
            options=[ft.dropdown.Option(opt) for opt in options],
            height=60,
            content_padding=ft.padding.only(left=15, bottom=12),
        )

    ciclo_dd = create_mobile_dropdown("Ciclo", ["DAM", "DAW", "ASIX"])
    curso_dd = create_mobile_dropdown("Curso", ["1", "2"])
    dificultad_dd = create_mobile_dropdown("Dificultad", ["Baja", "Media", "Alta"])
    
    details_input = ft.TextField(
        label="Context & Details",
        label_style=ft.TextStyle(color=text_secondary, size=11),
        hint_text="What should we focus on?",
        hint_style=ft.TextStyle(color="#48484A", size=13),
        multiline=True,
        min_lines=3,
        max_lines=4,
        border_radius=12,
        border_width=1,
        border_color="#2C2C2E",
        bgcolor="#242426",
        focused_border_color="#007AFF",
        text_size=14,
    )

    form_section = ft.Column(
        [ciclo_dd, curso_dd, dificultad_dd, details_input],
        spacing=15,
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
        prompt_text = (
            f"Generate an exam for {curso_dd.value or 'None'} {ciclo_dd.value or 'None'} Difficulty {dificultad_dd.value or 'Baja'} Additional details {details_input.value}"
        )
        
        if form_section.visible:
            header_section.visible = False
            form_section.visible = False
            results_section.visible = True
            generate_btn.on_click = show_edit_sheet
            btn_text.text = "Edit"
            page.update() 
            await asyncio.sleep(0.1) 

        u_msg = user_message(prompt_text)
        results_list.controls.append(u_msg)
        page.update()
        
        await asyncio.sleep(0.05)
        u_msg.opacity = 1
        u_msg.offset = ft.Offset(0, 0)
        u_msg.scale = 1
        u_msg.update()

        generate_btn.disabled = True
        progress_ring.visible = True
        page.update()
        
        await asyncio.sleep(1.5) 

        ai_content = "\n\n".join(MOCK_EXAM_DATA["questions"])
        ai_msg = chat_message(ai_content)
        results_list.controls.append(ai_msg)
        page.update()

        await asyncio.sleep(0.05)
        ai_msg.opacity = 1
        ai_msg.offset = ft.Offset(0, 0)
        ai_msg.scale = 1
        ai_msg.update()
        # results_list.scroll_to(key=str(len(results_list.controls)-1), duration=500)
        
        progress_ring.visible = False
        generate_btn.disabled = False
        page.update()
        
    progress_ring = ft.ProgressRing(width=16, height=16, color="white", stroke_width=2, visible=False)
    btn_text = ft.Text("Start Generating", weight="bold", size=15)

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
        bgcolor=card_surface,
        border_radius=24,
        border=ft.border.all(1, "#2C2C2E"),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack([
            ft.Container(
                padding=25,
                content=ft.Column([
                    header_section,
                    ft.Divider(height=15, color="transparent"),
                    form_section,
                    results_section,
                    ft.Container(height=10),
                    generate_btn,
                ], horizontal_alignment="center", scroll=ft.ScrollMode.AUTO)
            ),
        ])
    )
    
    update_drawer()
    
    return ft.View(
        route="/home",
        bgcolor=bg_color,
        drawer=drawer,
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