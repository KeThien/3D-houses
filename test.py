from predict_ML.ML import to_predict as pred_price


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    # Maison blanche
    to_predict = {"Number of rooms": [5], "Fully equipped kitchen": [1], "Terrace": [1], "Terrace Area": [8],
                  "Garden": [1], "Locality": [1341], "Area": [200], "State of the building": ["good"],
                  "Surface of the land": [1500], "Type of property": ["house"], "Number of facades": [4]}
    pred_price.to_predict(to_predict)
