from bs4 import BeautifulSoup
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.lexers.python import Python3Lexer
from pygments.util import ClassNotFound
from typing import List, Dict, Any
import requests
import pathlib
import re


LANG_FILE: pathlib.Path = pathlib.Path(
    __file__).absolute().parent / 'langs.txt'


class PasteException(Exception):
    pass


class Sloth:
    URL = "https://paste.ubuntu.com"

    def get_link(self, payload: Dict[str, str]) -> str:
        req = requests.post(self.URL, data=payload)
        soup = BeautifulSoup(req.text, "html.parser")
        self.errors = [error.li.string for error in soup.find_all("ul", "errorlist")]
        if self.errors:
            raise PasteException(self.errors)
        return self.URL + soup.a.get('href').replace('plain/', '')

    def validate_link(self, link) -> bool:
        mather = re.match("https://paste.ubuntu.com/p/.+/", link)
        if not mather:
            self.errors.append("""
                İzin verilmeyen bir format kullandınız. Bu, benim suçum değil.
                paste.ubuntu.com bazen can sıkıcı olabiliyor."""
            )
            return False
        return True

    def run(self, text: str, poster: str) -> str:
        try:
            syntax_type: str = guess_lexer(text).aliases[0]
            langs = [line.rstrip('\n') for line in LANG_FILE.open(mode='r')]
            if not syntax_type in langs:
                syntax_type = "text"
            elif syntax_type in ('python2', 'python'):
                syntax_type = 'python3'
        except ClassNotFound:
            syntax_type = "text"
        paste_link = self.get_link(
            dict(
                poster=poster,
                syntax=syntax_type,
                content=text,
            )
        )
        if self.validate_link(paste_link):
            return paste_link
