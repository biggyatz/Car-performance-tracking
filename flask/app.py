from flask import Flask,render_template,request
import pandas as pd
app=Flask(__name__)

import pickle
model = pickle.load(open(r'/Users/biggyatpandey/Desktop/data science/projects/applied_datascience_final-20BCE2763--main/flask/model.pkl','rb'))

@app.route('/')
def home():
    return render_template("finalweb.html")

@app.route('/Result', methods=["POST"])
def result():
    cylinders = request.form.get("cylinders")
    displacement = request.form.get("displacement")
    horsepower = request.form.get("horsepower")
    weight = request.form.get("weight")
    acceleration = request.form.get("acceleration")
    modelYear = request.form.get("modelYear")
    origin = request.form.get("origin")
    
    X = pd.DataFrame([[cylinders,displacement,horsepower,weight,acceleration,modelYear,origin]], columns = ["cylinders", "displacement", "horsepower", "weight", "acceleration", "model year", "origin"])
    output = model.predict(X)[0]
    s = "The mpg prediction is: " + str(output)
    return render_template("finalweb.html", resultText = s)
    
        
    
if __name__=='__main__':
    app.run(debug=True)