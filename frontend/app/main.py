import json
import flet as ft
from auth_view import auth_view
from home_view import home_view
from profile_view import profile_view


async def main(page: ft.Page):
    page.window.width = 420
    page.window.height = 720

    page.window.min_width = 420
    page.window.max_width = 420
    page.window.min_height = 720
    page.window.max_height = 720

    page.window.resizable = False
    page.window.minimizable = False
    page.window.maximizable = False

    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    await page.window.center()

    def get_current_t():
        with open("frontend/app/languages.json", "r", encoding="utf-8") as f:
            translations = json.load(f)
        lang = page.session.store.get("lang") or "English"
        return translations[lang]
    
    def get_palette():
        is_dark = page.theme_mode == ft.ThemeMode.DARK
        return {
            "bg": "#0F0F10" if is_dark else "#E3EDEA",
            "card": "#1C1C1E" if is_dark else "#FFFFFF",
            "text": "#FFFFFF" if is_dark else "#1C1C1E",
            "border": "#2C2C2E" if is_dark else "#E0E0E0",
            "input": "#242426" if is_dark else "#F9F9F9",
            "accent": "#007AFF" if is_dark else "#D1E5E0",
            "accent_text": "#FFFFFF" if is_dark else "#4F796F",
        }
    
    def route_change(route):
        print("route_change called:", route)

        page.views.clear()
        t = get_current_t()
        c = get_palette()

        if page.route == "/":
            view = auth_view(page, t, c)
            page.views.append(view)

        elif page.route == "/home":
            view = home_view(page, t, c)
            page.views.append(view)
            
        elif page.route == "/profile":
            view = profile_view(page, t, c)
            page.views.append(view)

        page.update()


    def view_pop(view):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go("/")
    route_change(page.route)
    
ft.run(main)