from dataclasses import dataclass
from pydoc import describe
from typing import Sequence, List
import random
import csv
import sys

from bs4 import BeautifulSoup
import discord
from discord import Message, Embed


@dataclass()
class Spell:
    name: str
    link: str
    traditions: Sequence[str]
    rarity: str
    traits: Sequence[str]
    cantrip: bool
    focus: bool
    level: int
    summary: str
    heightened: bool


def soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html.parser')


def random_spell(max_level: int) -> Spell:
    with open('spells.csv') as f:
        reader = csv.DictReader(f)
        spell = random.choice(list(filter(lambda x: int(x['Level']) <= max_level, reader)))

    def text(s: BeautifulSoup) -> str: return s.u.a.text
    def text_list(raw: str) -> List[str]:
        return [text(soup(x)) for x in raw.split(',')]

    name_soup = soup(spell['Name'])

    return Spell(
        text(name_soup),
        f'https://2e.aonprd.com/{name_soup.u.a.attrs["href"]}',
        text_list(spell['Traditions']),
        text(soup(spell['Rarity'])),
        text_list(spell['Traits']),
        spell['Cantrip'] == 'True',
        spell['Focus'] == 'True',
        int(spell['Level']),
        spell['Summary'],
        spell['Heightened?'] == 'True'
    )


class Client(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def chaos(self, msg: Message):
        spell = random_spell(int(msg.content.split(' ')[1]))
        embed = Embed(title=f'{spell.name} {spell.level}', url=spell.link, description=spell.summary)

        embed.add_field(name="Rarity", value=spell.rarity)
        embed.add_field(name="Traditions", value=', '.join(spell.traditions))
        embed.add_field(name="Traits", value=', '.join(spell.traits))
        embed.add_field(name="Cantrip", value='✅' if spell.cantrip else '❌')
        embed.add_field(name="Heightened", value='✅' if spell.heightened else '❌')
        embed.add_field(name="Level", value=spell.level)
        await msg.channel.send(embed=embed)

    async def on_message(self, msg: Message):
        if msg.content.startswith('chaos'):
            await self.chaos(msg)


if len(sys.argv) != 2: raise SystemExit('usage: python bot.py <token>')
Client().run(sys.argv[1])