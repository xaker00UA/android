import asyncio
from datetime import datetime
from typing import Callable
from flet import *
from app import All_General, PlayerInterface, User
from config import PLAYERS,SESSION,FORMAT_DATE
from app.utils import timer



class Event:
    def __init__(self) -> None:
        self._listener: dict[str, list[Callable]] = {}

    def on(self, event: str, listener: Callable):
        if event not in self._listener:
            self._listener[event] = []
        self._listener[event].append(listener)

    def emit(self, event: str, data=None):
        if event in self._listener:
            for listener in self._listener[event]:
                listener(data)
        

class Up(Row):
    def __init__(self, event: Event, page: Page):
        super(Up, self).__init__(height=150, alignment=MainAxisAlignment.SPACE_BETWEEN)
        self.handlers = event
        self.text = TextField(
            label="nickname", on_submit=self.on_click_search
        )
        self.page:Page = page
        self.theme = IconButton(icon="SUNNY", on_click=self.change_theme)
        self.search = ElevatedButton(
            icon="search", text="Найти", on_click=self.on_click_search
        )
        self.session = ElevatedButton(
            icon="update", text="Начать сессию", on_click=self.start_session
        )
        self.drop = Dropdown(on_change=self.drop_change)
        self.second_drop = Dropdown(on_change=self.drop_second_change)
        self.menu = PopupMenuButton()
        self.controls = [
            Column(
                [Row([self.theme, self.search, self.session]), self.menu,Row([self.drop, self.second_drop])]
            ),
            self.text,
        ]
        self.handler()
    @timer
    def start_session(self, e):
        if self.text.value:
            self.handlers.emit("pause")
            asyncio.run(PlayerInterface(name=self.text.value).reset())
            self.handlers.emit("start")
            self.add_menu(self.text.value)
        else:
            self.handlers.emit(event='start_session')
        self.text.value =""
        self.update()

    def on_click_search(self, e):
        if self.text.value:
            self.handlers.emit("text_button", data=self.text.value)
            self.drop_list(self.text.value)
            self.add_menu(self.text.value)
            self.text.value = ""
            self.update()
    def two_period(self, value_old, value_new):
        if value_new == "Сейчас":
            self.handlers.emit("period",data=value_old)
        else:
            self.handlers.emit("two_period",data=(value_old,value_new))

        
        
        

    def drop_second_change(self, e):
        value=e.control.value
        if self.drop.value:
            self.two_period(value_new=value,value_old=self.drop.value)

        


    def drop_change(self, e):
        value=e.control.value
        self.second_drop.options=[option for option in self.data.copy() if datetime.strptime(option.text,FORMAT_DATE)>datetime.strptime(value,FORMAT_DATE)]
        self.second_drop.options.append(dropdown.Option(text="Сейчас"))
        self.second_drop.update()
     
        
        

    def on_click_menu(self, e):
        self.handlers.emit(f"text_button", data=e.control.text)
        self.drop_list(e.control.text)

    def add_menu(self, n): 
        for item in self.menu.items:
            if item.text == n:
                return
        self.menu.items.append(PopupMenuItem(text=n, on_click=self.on_click_menu))

    def drop_list(self, n):
        self.data:list = [dropdown.Option(text=i.get("data")) for i in All_General().get(name=n)]
        self.drop.options = self.data.copy()
        self.second_drop.options=self.data.copy()
        self.second_drop.options.append(dropdown.Option(text="Сейчас"))
        self.update()

    def change_theme(self, e):
        self.page.theme_mode = "dark" if self.page.theme_mode == "light" else "light"
        self.page.update()

    def handler(self):
            for line in PLAYERS:
                self.add_menu(line)
            if SESSION:
                for line in PLAYERS:
                    asyncio.run(PlayerInterface(line).day_sessions())

class Middle(Row):
    def __init__(self, event: Event, page: Page):
        super().__init__(
            alignment="center",
            expand=True,
        )
        self.controls = [
            Column(
                [
                    
                ],
                scroll="hidden",
                alignment="center",
                expand=True,
                horizontal_alignment="center",
            )
        ]
        self.event = event
        self.page = page
        self.handler()

    def crate_player(self, name):
        self.player:PlayerInterface = PlayerInterface(name=name)

    @timer
    def build_content(self, trigger: str = None, two_trigger:str = None):
        self.pause()
        self.controls[0].clean()
        try:
            if trigger:
                if two_trigger:
                    data:list[dict] = asyncio.run(self.player.result_of_the_two_period(period=trigger,period_now=two_trigger))
                else:
                    data:list[dict] = asyncio.run(self.player.result_of_the_period(period=trigger))
            else:
                data:list[dict]= asyncio.run(self.player.results())
            val=data.pop(-1)
            self.text=Text(value=f'Сессия игрока {val.get('name')} длиться {val.get('time')}',size=24,
                           color='red')
            keys = list(data[0].keys())[:-1]
            colum=[
                DataColumn(
                    Text(key),
                    on_sort=self.sorting,
                )
                for key in keys
            ]
            self.table = DataTable(columns=colum,border=border.all(3, "red"))
            self.table.rows = [
                DataRow(
                    cells=[
                        DataCell(
                            Text(value.get(key, ""), color=value["color"].get(key))
                        )
                        for key in keys
                    ]
                )
                for value in data
            ]
            self.state = {x: True for x in range(len(keys))}
            self.controls[0].controls = [Row([self.table],alignment="center",
                        vertical_alignment="center",
                        scroll=True,)]#ERROR
        except Exception as e:
            data = data if "data" in locals() else None
            self.text = Text(value=(data or e),color='red',size=32)
        finally:
            self.controls[0].controls.insert(0,self.text)
            self.controls[0].controls.insert(0,Divider(height=5,color="transparent"))
            self.page_start()

    def sorting(self, e: DataColumnSortEvent):
        index = e.column_index
        ascending = self.state[index]
        row = self.table.rows[:-1]
        row = sorted(row, reverse=ascending, key=lambda x: x.cells[index].content.value)
        self.table.rows[:-1] = row
        self.state[index] = not ascending
        self.table.update()

    def pause(self,*args):
        self.page.controls[0].disabled = True
        self.page.navigation_bar.disabled = True
        self.update()
        self.page.update()
    def page_start(self,*args):
        self.page.controls[0].disabled = False
        self.page.navigation_bar.disabled = False
        self.page.update()
    def period(self, period):
        self.build_content(trigger=period)
    def two_period(self, period:tuple):
        self.build_content(trigger=period[0],two_trigger=period[1])
    def __build_content(self, name):
        self.crate_player(name=name)
        self.build_content()
    def change_update(self, e):
        if hasattr(self, "player"):
            self.build_content()
    def start(self,e):
        if hasattr(self, "player"):
            self.pause()
            asyncio.run(self.player.reset())
            self.page_start()

    def handler(self):
        self.event.on("update", self.change_update)
        self.event.on("text_button", self.__build_content)
        self.event.on("period", self.period)
        self.event.on("start_session", self.start)
        self.event.on("pause", self.pause)
        self.event.on("start", self.page_start)
        self.event.on("two_period", self.two_period)



class Down(Row):
    """Будет одна кнопка обновить которая запускает верхнюю секции
    та в свою очередь генерирует таблицу"""

    def __init__(self, event: Event):
        super().__init__(height=100, alignment="center")
        self.controls = [ElevatedButton(icon=icons.TIPS_AND_UPDATES_ROUNDED,text="Update", on_click=self.get_update)]
        self.handler = event

    def get_update(self, e: ControlEvent):
        self.handler.emit(event="update")


def main(page: Page):
    event = Event()
    up = Up(event, page=page)
    middle = Middle(event, page=page)
    down = Down(event)
    content = Container(Column([up, middle, down]), expand=True)
    return content
