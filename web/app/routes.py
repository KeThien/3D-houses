from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username' : 'Ke Thien'}
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
    return render_template('index.html', title='Home', user=user, posts=posts)

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)