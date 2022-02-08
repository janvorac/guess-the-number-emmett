from emmett import App, now
from emmett.orm import Model, Field, belongs_to, has_many


app = App(__name__)


class Game(Model):
    has_many('guessed')

    last_played_date = Field.datetime()
    correct_number = Field.int()
    finished = Field.bool()


class Guessed(Model):
    belongs_to('game')

    number = Field.int()
