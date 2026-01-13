import flet as ft
from auth_view import auth_view
from home_view import home_view


def main(page: ft.Page):
    page.window.height = 800
    page.window.width = 450
    page.window.resizable = False 
    
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    print("test")
    def route_change(route):
        print("route_change called:", route)

        page.views.clear()

        if page.route == "/":
            view = auth_view(page)
            page.views.append(view)

        elif page.route == "/home":
            view = home_view(page)
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
