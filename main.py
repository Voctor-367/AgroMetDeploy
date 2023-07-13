import flet as ft

import config.routes

from componentes.NavigationBar import navigation_bar


def main(page: ft.Page):

    navigation_bar.page = page
    config.routes.RouteConfig(page)
   
    # firebase = config.firebase.FirebaseConfig(page)


ft.app(target=main, assets_dir="assets")
