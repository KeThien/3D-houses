import os
from app import app
from flask import render_template, request, redirect, url_for
from .weather import RequestWeather
from .scripts.predict import ML


@app.route('/')
@app.route('/index')
def index():
    to_predict = {"Number of rooms": [5], "Fully equipped kitchen": [1], "Terrace": [1], "Terrace Area": [8],
                  "Garden": [1], "Locality": [1341], "Area": [200], "State of the building": ["good"],
                  "Surface of the land": [1500], "Type of property": ["house"], "Number of facades": [4]}
    response = RequestWeather().request()
    user = {'username': 'Rien'}
    predict = ML.to_predict.to_predict(to_predict)

    return render_template('index.html', title='3D Houses', user=user, weather=response, predict=predict)

# POST request to this endpoint(route) results in the number of votes after upvoting


@app.route("/up", methods=["POST"])
def upvote():
    global votes
    votes = votes + 1
    return str(votes)

# POST request to this endpoint(route) results in the number of votes after downvoting


@app.route("/down", methods=["POST"])
def downvote():
    global votes
    if votes >= 1:
        votes = votes - 1
    return str(votes)


@app.route("/predict", methods=["POST", "GET"])
def submit():
    if request.method == 'POST':
        dict = request.form.to_dict(flat=False)
        return dict


# @app.route('/predict', methods=['POST', 'GET'])
# def predict():
#     if request.method == 'POST':
#         number = request.form['nm']
#         return redirect(url_for('success', name=number))

#     else:
#         number = request.args.get('nm')
#         return redirect(url_for('success', name=number))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
