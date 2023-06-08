from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from benchmark.Arguments import ALL_METRICS


class RankingForm(FlaskForm):
    score = SelectField("Score", choices=ALL_METRICS)
    submit = SubmitField("Generate Ranking")
