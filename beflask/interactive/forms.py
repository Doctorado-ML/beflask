from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField
from benchmark.Arguments import ALL_METRICS


##### NOT USED #####
class RankingForm(FlaskForm):
    score = SelectField("Score", choices=ALL_METRICS)
    output = TextAreaField("Output")
    submit = SubmitField("Generate Ranking")
