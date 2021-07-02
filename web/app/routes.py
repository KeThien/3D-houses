import os
from app import app
from flask import render_template, request, redirect, url_for
from .weather import RequestWeather
from .scripts.predict import ML

predict = 0

@app.route('/', methods=['POST','GET'])
@app.route('/index', methods=['POST','GET'])
def index():
    global predict
    if request.method == 'POST':
        try:
            dict = request.form.to_dict(flat=False)
            dict3d = [dict.pop(key) for key in ['3d_street', '3d_num', '3d_city']]
            dict = {k: [int(v[0])] if v[0].isdigit() else v for k, v in dict.items()}
            predict = ML.to_predict.to_predict(dict)
            return redirect('/')
        except:
            return 'Oops'
    else:
        response = RequestWeather().request()
        return render_template('index.html', title='3D Houses', weather=response, predict=predict)

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
