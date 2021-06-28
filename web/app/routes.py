from app import app
from flask import render_template
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
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='3D Houses', user=user, weather=response)

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)