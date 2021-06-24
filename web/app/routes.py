from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username' : 'Marvin'}
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
    return render_template('index.html', title='Home', user=user, posts=posts)

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)