class UI:
    def __init__(self,menus,default_menu = "login"):
        self.menu = menus[default_menu]
        self.menus = menus

    def change_menu(self,menu_name):
        self.menu = self.menus[menu_name]

    def show(self):
        self.menu()

    def show_menu(self,menu_name):
        self.change_menu(menu_name)
        self.show
