from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    SelectField,
    TextAreaField,
    BooleanField,
    IntegerField,
)
from benchmark.Arguments import ALL_METRICS


class BenchmarkDatasetForm(FlaskForm):
    score = SelectField("Score", choices=ALL_METRICS)
    model = SelectField("Model")
    dataset = SelectField("Dataset")
    discretize = BooleanField("Discretize")
    stratified = BooleanField("Stratified")
    ignore_nan = BooleanField("Ignore NaN")
    fit_features = BooleanField("Fit Features")
    n_folds = IntegerField("# Folds")
    hyperparameters = TextAreaField("Hyperparameters")
    submit = SubmitField("Do Experiment!")


# ----- NOT USED ----- #
class RankingForm(FlaskForm):
    score = SelectField("Score", choices=ALL_METRICS)
    output = TextAreaField("Output")
    submit = SubmitField("Generate Ranking")
