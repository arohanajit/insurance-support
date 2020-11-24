from flask import Flask, jsonify, request, render_template, url_for, session, redirect
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)
app.secret_key = 'abc'

@app.route('/',methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/data',methods=['GET','POST'])
def data():
    if request.method == 'GET':
        return render_template('location.html')
    if request.method == 'POST':
        loc = request.form.get('county').title() + ' County'
        df1 = pd.read_csv('files/al.csv')
        allergy = list(df1.loc[df1.COUNTY==loc].iloc[:3]['DESCRIPTION'])
        df2 = pd.read_csv('files/care.csv')
        careplan = list(df2.loc[df2.COUNTY==loc].iloc[:3]['DESCRIPTION'])
        df3 = pd.read_csv('files/enc.csv')
        encounter = list(df3.loc[df3.COUNTY==loc].iloc[:3]['DESCRIPTION'])
        df4 = pd.read_csv('files/im.csv')
        immune = list(df4.loc[df4.COUNTY==loc].iloc[:3]['DESCRIPTION'])
        df5 = pd.read_csv('files/obs.csv')
        observe = list(df5.loc[df5.COUNTY==loc].iloc[:3]['DESCRIPTION'])
        df6 = pd.read_csv('files/proc.csv')
        df6_1 = pd.read_csv('files/proc_support.csv')
        procedure = list(df6.loc[df6.COUNTY==loc].iloc[:3]['DESCRIPTION'])
        cost = []
        for i in procedure:
            cost.append(df6_1.loc[(df6_1.DESCRIPTION==i) & (df6_1.COUNTY==loc)].sort_values('BASE_COST',ascending=False)['BASE_COST'].iloc[0])
        df7 = pd.read_csv('files/prov.csv')
        provider = list(df7.loc[df7.COUNTY == loc]['SPECIALITY'].iloc[:3])
        return render_template('result.html',loc = loc, al = allergy, ob = observe, enc=encounter,
        cp=careplan, im=immune, proc=procedure, cost=cost, prov=provider)


@app.route('/ml',methods=['GET','POST'])
def predict():
    if request.method == 'GET':
        return render_template('form.html')
    if request.method == 'POST':
        county = ['Hampden County', 'Middlesex County', 'Suffolk County', 'Plymouth County', 
        'Franklin County', 'Bristol County', 'Norfolk County', 'Essex County', 'Worcester County', 
        'Hampshire County', 'Barnstable County', 'Berkshire County', 'Dukes County', 'Nantucket County']
        county_val = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        inp = []
        inp.extend([1 if request.form.get('marital')=='married' else 0])
        inp.extend([1 if request.form.get('eth')=='true' else 0])
        inp.extend([1 if request.form.get('gender')=='male' else 0])
        inp.extend([0])
        val = request.form.get('age')
        inp.extend([float(val)])
        race = ['white', 'native', 'asian', 'black', 'other']
        race_val = [0,0,0,0,0]
        race_val[race.index(request.form.get('race'))] = 1
        inp.extend(race_val)
        place = request.form.get('county').title()
        index = [idx for idx, s in enumerate(county) if place in s]
        if len(index)==0:
            return "Invalid County"
        county_val[index[0]] = 1
        inp.extend(county_val)
        age = [[0,20],[20,40],[40,60],[60,80],[80,100],[100,110],[110,120]]
        age_val = [0,0,0,0,0,0,0]
        for i in range(len(age)):
            if (int(val) >= age[i][0]) and (int(val) < age[i][1]):
                age_val[i] = 1
        inp.extend(age_val)
        inp = np.asarray(inp).reshape(1,-1)
        cover_model = pickle.load(open('cover.pkl','rb'))
        expense_model = pickle.load(open('expense.pkl','rb'))
        coverage = str(cover_model.predict(inp)[0])
        expense = str(expense_model.predict(inp)[0])
        return render_template('result2.html',coverage=coverage,expense=expense)

            

if __name__ == '__main__':
    app.run(debug=True)

