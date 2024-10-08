import json
from flet import *
from app.utils import timer
from app.database import All_General
from .page1 import Up, Middle, Down, Event
from app import ClanInterface, Clan
import asyncio
from config import CLANS, SESSION


class Up_clan(Up):
    def __init__(self, page, event):
        super().__init__(page=page, event=event)
        self.text.label = "tag"
        self.session.on_click = self.start_session

    @timer
    def start_session(self, e):
        if self.text.value:
            asyncio.run(ClanInterface(name=self.text.value).reset())
            self.add_menu(self.text.value)
        else:
            self.handlers.emit("start_session")
        self.text.value = ""
        self.text.update()

    def drop_list(self, n):
        self.drop.options.clear()
        self.second_drop.options.clear()
        self.data: list = [
            dropdown.Option(text=i.get("data"))
            for i in All_General().get_clan(clan_id=n)
        ]
        self.drop.options = self.data.copy()
        self.second_drop.options = self.data.copy()
        self.second_drop.options.append(dropdown.Option(text="Сейчас"))
        self.update()

    def handler(self):
        for line in CLANS:
            self.add_menu(line)
        if SESSION:
            for line in CLANS:
                asyncio.run(ClanInterface(name=line).day_sessions())


class Middle_clan(Middle):
    def __init__(self, page, event):
        super().__init__(page=page, event=event)

    def crate_player(self, name):
        self.player: ClanInterface = ClanInterface(clan_tag=name)

    def build_content(self, trigger: str = None, two_trigger: str = None):
        super().build_content(trigger, two_trigger)
        if hasattr(self, "table"):
            self.text.value = self.text.value.replace("игрока", "клана")
            self.text.update()

    # def change_update(self, e):
    #     if hasattr(self, "player"):
    #         self.build_content(name=self.player.clan_tag)

    # def period(self, period):
    #     self.build_content(trigger=period)

    # def two_period(self, period: tuple):
    #     self.build_content(
    #         name=self.player.clan_tag, trigger=period[0], two_trigger=period[1]
    #     )


class Down_clan(Down):
    def __init__(self, page, event):
        super().__init__(event)


def main(page: Page):
    event = Event()
    up = Up_clan(page, event)
    middle = Middle_clan(page, event)
    down = Down_clan(page, event)
    return Container(content=Column([up, middle, down]), expand=True)
