from app import app
from flask import render_template, request
from .weather import RequestWeather

votes = 0


@app.route('/')
@app.route('/index')
def index():
    test_btn = False
    response = RequestWeather().request()
    user = {'username': 'Rien'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!!!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'H2G2 movie was so cool!'
        }
    ]
    # if request.form.get('test-switch'):
    #     test_btn = not(test_btn)
    #     print("Switch clicked")

    return render_template('index.html', title='3D Houses', user=user, weather=response, votes=votes)

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


@app.route("/predict", methods=["POST"])
def submit():
    if request.method == 'POST':
        keyword = request.form['keyword']
        return keyword


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
