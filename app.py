from emmett import App, now, redirect, url, abort
from emmett.orm import Model, Field, belongs_to, has_many, Database
import random


app = App(__name__)


class Game(Model):
    has_many('guesseds')

    last_played_date = Field.datetime()
    correct_number = Field.int()
    finished = Field.bool()

    default_values = {
        'finished': False
    }


class Guessed(Model):
    belongs_to('game')

    number = Field.int()

    fields_rw = {
        'game': False
    }


db = Database(app)
db.define_models(Game, Guessed)

app.pipeline = [
    db.pipe
]


@app.route("/")
async def index():
    games = Game.all().select()
    return dict(games=games)


@app.route("/new")
async def new_game():
    game = Game.create(last_played_date=now(), correct_number=random.randint(0, 100))
    print(game)
    redirect(url('play', game.id))
    return dict(game=game)


@app.route("/<int:game_id>/detail")
async def play(game_id):
    def _validate_guess(form):
        form.params.game = game_id
    game = Game.get(game_id)
    if not game:
        abort(404)
    guesses = game.guesseds()
    form = Guessed.form(onvalidation=_validate_guess)
    if form.accepted:
        redirect(url('play', game_id))
    guess_feedback = ''
    return dict(
        game=game,
        guesses=guesses,
        form=form,
        guess_feedback=guess_feedback
    )
