# -*- coding: utf-8 -*-
from flask import Flask, request
import pandas as pd
import numpy as np
import json
import pickle

app = Flask(__name__)

MODEL_PATH = 'model/my_model.sav'
DATA_PATH = 'data/df_full.csv'
df = pd.read_csv(DATA_PATH,).sort_values(['SK_ID_CURR']).iloc[: , 1:]
model = pickle.load(open(MODEL_PATH, 'rb'))

COLS_CAT = ['NAME_CONTRACT_TYPE', 'NAME_INCOME_TYPE', 'NAME_EDUCATION_TYPE',
            'NAME_FAMILY_STATUS', 'OCCUPATION_TYPE', 'ORGANIZATION_TYPE']
FEATS = [f for f in df.columns if f not in (
        COLS_CAT+['TARGET','SK_ID_CURR','SK_ID_BUREAU','SK_ID_PREV','index'])]

@app.route("/api")
def get_infos():
    SK_ID = int(request.args.get('sk_id'))
    client_df = df[df['SK_ID_CURR']==SK_ID]
    client_df['TARGET'] = model.predict_proba(client_df[FEATS])[:,1][0]
    dict = client_df.to_json(orient="index")
    parsed = json.loads(dict)
    return parsed

if __name__ == "__main__":
    app.run(debug=True)
