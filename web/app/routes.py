import os, glob
from app import app
from flask import render_template, request, redirect, url_for
from .weather import RequestWeather
from .scripts.predict import ML
from .scripts import draw_house

dir_path = os.path.dirname(os.path.realpath(__file__))
predict = 0
form = {
    '3d_street': ['Sijslostraat'], 
    '3d_num': ['104'],
    'Locality': ['8020'],
    '3d_city': ['OOSTKAMP'],
    'Type of property': ['house'],
    'Number of facades': ['4'],
    'Number of rooms': ['4'],
    'Surface of the land': ['457']
    }

@app.route('/', methods=['POST','GET'])
@app.route('/index', methods=['POST','GET'])
def index():
    global predict, form
    files = glob.glob(f'{dir_path}/static/3d-models/*')
    nmesh = len(files)
    
    if request.method == 'POST':
        try:
            form = request.form.to_dict(flat=False)
            dict = request.form.to_dict(flat=False)
            dict3d = {key: dict[key] for key in dict.keys() & {'3d_street', '3d_num', '3d_city'}}
            dict_reject = [dict.pop(key) for key in ['3d_street', '3d_num', '3d_city']]
            dict = {k: [int(v[0])] if v[0].isdigit() else v for k, v in dict.items()}
            predict = ML.to_predict.to_predict(dict)
            
            files = glob.glob(f'{dir_path}/static/3d-models/*')
            nmesh = len(files)
            for f in files:
                os.remove(f)
            draw_house.draw_houses(dict3d['3d_street'][0] + ' ' + dict3d['3d_num'][0] + ' ' + str(dict['Locality'][0]), dict3d['3d_city'][0].upper())
            return redirect('/')
        except ValueError:
            raise
            # return redirect('/')
    else:
        response = RequestWeather().request()
        return render_template('index.html', title='3D Houses', weather=response, predict=predict, nmesh=nmesh, form=form)

# POST request to this endpoint(route) results in the number of votes after upvoting

# @app.route("/load3d", methods=["POST"])
# def load3d():
#     if request.method == 'POST':
#         dict = form
#         dict3d = {key: dict[key] for key in dict.keys() & {'3d_street', '3d_num', '3d_city'}}
#         dict3d = list(dict3d.values())
#         files = glob.glob(f'{dir_path}/static/3d-models/*')
#         for f in files:
#             os.remove(f)
#         draw_house.draw_houses(dict3d[0][0] + ' ' + dict3d[1][0], dict3d[2][0].upper())
#     # return redirect('/')
#     return str(dict3d)

# POST request to this endpoint(route) results in the number of votes after downvoting

# @app.route("/down", methods=["POST"])
# def downvote():
#     global votes
#     if votes >= 1:
#         votes = votes - 1
#     return str(votes)

# @app.route("/predict", methods=["POST", "GET"])
# def submit():
#     if request.method == 'POST':
#         dict = request.form.to_dict(flat=False)
#         return dict

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
