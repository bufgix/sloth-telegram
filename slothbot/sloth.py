from bs4 import BeautifulSoup
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.lexers.python import Python3Lexer
from pygments.util import ClassNotFound
from typing import List, Dict, Any
import requests
import pathlib

LANG_FILE: pathlib.Path = pathlib.Path(__file__).absolute().parent / 'langs.txt'


class Sloth:
    URL = "https://paste.ubuntu.com"
    soup: BeautifulSoup = None

    def __init__(self, *args: List, **kwargs: Dict[str, str]):
        pass

    def get_link(self, payload: Dict[str, str]) -> str:
        req = requests.post(self.URL, data=payload)
        self.soup = BeautifulSoup(req.text, "html.parser")

        return f"{self.URL}{self.soup.a.get('href').replace('plain/', '')}"

    def run(self, text: str, poster: str) -> str:
        payload = dict()
        try:
            syntax_type: str = guess_lexer(text).aliases[0]

            langs = [line.rstrip('\n')
                     for line in LANG_FILE.open(mode='r')]
            if not syntax_type in langs:
                syntax_type = "text"

            if syntax_type in ('python2', 'python'):
                syntax_type = 'python3'

        except ClassNotFound:
            syntax_type = "text"

        payload: Dict[str, str] = {
            "poster": poster,
            "syntax": syntax_type,
            "content": text
        }
        paste_link: str = self.get_link(payload)
        return paste_link
