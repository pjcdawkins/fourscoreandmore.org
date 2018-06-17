from flask import render_template, redirect, request, send_from_directory
from app import app
from app.forms import ChoralesForm, LiederForm
from app import scores, TheoryExercises, exercises
import os

@app.route('/apps/')
def index():
    return redirect('/cut-outs/', code=302)


@app.route(app.config["SCORE_DOWNLOAD_URI_PREFIX"] + '<path:filename>')
def custom_static(filename):
    mimetype = None
    if filename.endswith(".xml") or filename.endswith(".musicxml"):
        mimetype = "application/vnd.recordare.musicxml+xml"

    return send_from_directory(
        app.config["SCORE_DOWNLOAD_PATH"],
        filename,
        as_attachment=("download" in request.args),
        mimetype=mimetype
        )


@app.route('/apps/chorales/', methods=['GET', 'POST'])
def chorales():
    form=ChoralesForm(request.form)
    form.originalScore.choices = scores.list_scores(subDir="chorales");
    download = []

    if form.validate_on_submit():
        exercise = exercises.ChoraleExercise(
            scores.normalizeScorePath(form.originalScore.data, subDir="chorales"),
            beatsToCut=form.beatsToCut.data,
            partsToCut=form.partsToCut.data,
            shortScore=form.shortScore.data == 'short'
        )
        files = exercise.write(directory=os.path.join(app.config["SCORE_DOWNLOAD_PATH"], "chorales"))
        download = []
        for title, path in files:
            download.append(
                (title, path.replace(app.config["SCORE_DOWNLOAD_PATH"] + "/", app.config["SCORE_DOWNLOAD_URI_PREFIX"]))
            )
    else:
        # TODO: Find a way to set this as the default
        form.partsToCut.data = ['alto', 'tenor', 'bass']

    return render_template('chorales-form.html', form=form, download=download)


@app.route('/apps/lieder/', methods=['GET', 'POST'])
def lieder():
    form=LiederForm(request.form)
    form.originalScore.choices = scores.list_scores(subDir="lieder");
    download = []

    if form.validate_on_submit():
        exercise = exercises.LiedExercise(
            scores.normalizeScorePath(form.originalScore.data, subDir="lieder"),
            leaveRestBars=form.preserveRestBars.data,
            leaveBassLine=form.preserveBass.data,
            quarterLengthOfRest=form.restLength.data,
            addition=(None if form.addition.data == "none" else form.addition.data),
            quarterLength=form.harmonicRhythm.data
        )
        files = exercise.write(directory=os.path.join(app.config["SCORE_DOWNLOAD_PATH"], "lieder"))
        download = []
        for title, path in files:
            download.append(
                (title, path.replace(app.config["SCORE_DOWNLOAD_PATH"] + "/", app.config["SCORE_DOWNLOAD_URI_PREFIX"]))
            )

    return render_template('lieder-form.html', form=form, download=download)
