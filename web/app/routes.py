import os
from app import app
import scripts
from flask import render_template, request, redirect, url_for
from .weather import RequestWeather


@app.route('/')
@app.route('/index')
def index():
    response = RequestWeather().request()
    user = {'username' : 'Rien'}
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
    return render_template('index.html', title='3D Houses', user=user, weather=response)


@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        number = request.form['nm']
        return redirect(url_for('success', name=number))


    else:
        number = request.args.get('nm')
        return redirect(url_for('success', name=number))

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)


