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
    soup: BeautifulSoup = None
    errors: List[str] = None
    syntax: str = None

    def __init__(self, *args: List, **kwargs: Dict[str, str]):
        pass

    def get_link(self, payload: Dict[str, str]) -> str:
        req = requests.post(self.URL, data=payload)
        self.soup = BeautifulSoup(req.text, "html.parser")
        errors = self.get_errors()
        if errors:
            self.errors = errors
            raise PasteException("Paste error.")
        return f"{self.URL}{self.soup.a.get('href').replace('plain/', '')}"

    def validate_link(self, link) -> bool:
        mather = re.match("https://paste.ubuntu.com/p/.+/", link)
        if not mather:
            self.errors.append("İzin verilmeyen bir format kullandınız. Bu, benim suçum değil. paste.ubuntu.com bazen can sıkıcı olabiliyor.")
            return False
        return True

    def get_errors(self) -> List[str]:
        error_list = list()
        for error in self.soup.find_all("ul", "errorlist"):
            error_list.append(error.li.string)

        return error_list

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
        self.get_errors()
        if self.validate_link(paste_link):
            self.syntax = syntax_type
            return paste_link
        else:
            return None
