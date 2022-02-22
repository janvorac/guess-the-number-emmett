from emmett import App, now, redirect, url, abort
from emmett.orm import Model, Field, belongs_to, has_many, Database
from emmett.sessions import SessionManager
import random

import plotly.graph_objects as go

app = App(__name__)


class Game(Model):
    has_many('guesseds')

    last_played_date = Field.datetime()
    correct_number = Field.int()
    finished = Field.bool()

    default_values = {
        'finished': False
    }

    def __str__(self):
        return f"Game {self.id}"


class Guessed(Model):
    belongs_to('game')

    number = Field.int()

    fields_rw = {
        'game': False,
        'number': True
    }

    validation = {
        'number': {'in': {'range': (0, 100)}}
    }


db = Database(app)
db.define_models(Game, Guessed)

app.pipeline = [
    SessionManager.cookies('bflmpsvz'),
    db.pipe,
]


@app.route("/")
async def index():
    closed_games = db(db.games.finished == True).select()
    open_games = db(db.games.finished == False).select()
    return dict(closed_games=closed_games, open_games=open_games)


@app.route("/new")
async def new_game():
    game = Game.create(last_played_date=now(), correct_number=random.randint(0, 100))
    redirect(url('play', game.id))
    return dict(game=game)


@app.route("/detail/<int:game_id>")
async def play(game_id):
    def _validate_guess(form):
        form.params.game = game_id
    game = Game.get(game_id)
    if not game:
        abort(404)
    guesses = game.guesseds()
    form = await Guessed.form(onvalidation=_validate_guess)
    if form.accepted:
        guessed_num = int(form.params['number'])
        print(guessed_num, game.correct_number)
        if guessed_num == game.correct_number:
            game.finished = True
            game.save()
            redirect(url('inspect', game_id))
        redirect(url('play', game_id))
    guess_feedback = get_feedback(game)
    return dict(
        game=game,
        guesses=guesses,
        form=form,
        guess_feedback=guess_feedback
    )


def get_feedback(game):
    guesses = game.guesseds(orderby=~Guessed.id)
    if not guesses:
        return ''
    print(guesses)
    last_guess = int(guesses[0].number)
    if last_guess == game.correct_number:
        guess_feedback = 'Correct!'
    elif last_guess < game.correct_number:
        guess_feedback = 'Too low, shoot higher!'
    elif last_guess > game.correct_number:
        guess_feedback = 'Too high, shoot lower!'
    return guess_feedback


@app.route("/inspect/<int:game_id>")
async def inspect(game_id):
    game = Game.get(game_id)
    if not game:
        abort(404)
    guesses = [int(guess.number) for guess in game.guesseds()]
    plot = create_plot(guesses, game.correct_number)
    return dict(plot=plot.to_html())


def create_plot(ys, correct):
    trace = go.Scatter(y=ys, name='guesses')
    layout = go.Layout(
        title='Guess history', xaxis={'title': 'round'}, yaxis={'title': 'Guessed number'}
    )
    fig = go.Figure(data=[trace], layout=layout)
    fig.add_hline(y=correct)
    fig.add_annotation(x=0, y=correct, showarrow=False, text='Correct value', yshift=10)
    return fig
