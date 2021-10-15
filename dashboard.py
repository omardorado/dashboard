# -*- coding: utf-8 -*-
#---------------------------------
# Imports & init config
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import pickle
st.set_page_config(layout="wide")
sns.set_theme()
#---------------------------------
# Chargement des données et du modèle
MODEL_PATH = 'model/my_model.sav'
DATA_PATH = 'data/df_full.zip'

# Fonction de chargement
@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv(DATA_PATH, compression='zip').sort_values(['SK_ID_CURR']).iloc[: , 1:]
    model = pickle.load(open(MODEL_PATH, 'rb'))
    return df, model

#---------------------------------
# Affichage
FONT_COLOR = 'darkgray'
POSITIVE_COLOR = 'green'
NEUTRAL_COLOR = 'orange'
NEGATIVE_COLOR = 'red'

# Fonction pour afficher la jauge de risque de défaut
def show_gauge(val,thresh):
    # Modification de la couleur selon la comparaison ave le seuil
    if val<thresh: state_color = POSITIVE_COLOR
    else : state_color = NEGATIVE_COLOR
    #Affichage graphique
    fig = go.Figure(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = val,
    number = {'suffix':'%'},
    mode = "gauge+number+delta",
    title = {'text': "Risque de défaut",'font': {'size': 24}},
    delta = {'reference': thresh,
            'decreasing.color':'green',
            'increasing.color':'red'},
    gauge = {'axis': {'range': [None, 100]},
             'bar': {'color': state_color},
             'steps' : [
                 {'range': [0, 7.25], 'color': "lightgray"},
                 {'range': [7.25, 16.5], 'color': "gray"}],
             'threshold' : {'line': {'color': NEUTRAL_COLOR, 'width': 4}, 'thickness': 0.75, 'value': thresh}}))
    # Configuration d'affichage
    fig.update_layout(
    autosize=False,
    width=400,
    height=250,
    margin=dict(l=20, r=50, t=30, b=0),
    )
    st.write(fig)

# Fonction pour afficher un donut des annuités par rapport aux revenus
def plot_pie(data,labels=None,title=None,):
    # Affichage graphique
    fig, p = plt.subplots(subplot_kw=dict(aspect="equal"),figsize=(3,3))
    _,_,autotexts = p.pie(data,
            startangle = 90,
            radius=1.5,
            wedgeprops=dict(width=0.2,edgecolor='lightgray'),
            pctdistance=1.2,
            explode=(.1,)*len(data),
            colors=['b','r','g'],
            shadow=True,
            autopct='%.1f%%')
    # Configuration graphique
    for autotext in autotexts:
        autotext.set_color(FONT_COLOR)
        autotext.set_fontsize(8)
    p.xaxis.label.set_color(FONT_COLOR)
    p.patch.set_alpha(0)
    p.text(0,-0.1,title,
           ha='center', va='center',
           color=FONT_COLOR)
    fig.patch.set_alpha(0.0)
    # Gestion de la légende
    if labels is not None:
        legend = fig.legend(labels,
                    labelcolor=FONT_COLOR,loc='center',fontsize=6)
        legend.get_frame().set_alpha(0.0)
    st.write(fig)

# Fonction pour afficher un histogramme groupé par catégorie
def plot_histogram_grouped(col,group,reversed=False,yr=False):
    # Groupement des données
    df_g = df.groupby([group])[col].mean()
    # division par 365 si c'est une colonne de type jour
    if yr: df_g = df_g/-365
    # Gestion des couleurs
    if reversed :
        pos_color = NEGATIVE_COLOR
        neg_color = POSITIVE_COLOR
    else :
        pos_color = POSITIVE_COLOR
        neg_color = NEGATIVE_COLOR
    # Récupération des catégories  est valeurs
    n_categs = df[group].nunique()
    list_categs = list(sorted(df[group].dropna().unique()))
    val_cli = client_df[col].values[0]
    if yr: val_cli = val_cli/-365 # division par 365 si colonne jour
    cat_cli = client_df[group].values[0]
    # Modification de la couleur pour la barre de catégorie du client
    col_list = ['b']*n_categs
    if isinstance(cat_cli, str):
        idx=list_categs.index(cat_cli)
        col_list[idx] = NEUTRAL_COLOR
        if val_cli > df_g[cat_cli] : BAR_COLOR = neg_color
        else : BAR_COLOR = pos_color
    else :
        st.write("Ce client n'a pas de catégorie connue ")
        BAR_COLOR = NEUTRAL_COLOR
    # Affichage graphique
    fig, p = plt.subplots(figsize=(4,3))
    p = df_g.plot.bar(color=col_list)
    p.axhline(y=val_cli,color=BAR_COLOR)
    #Configuration d'affichage
    plt.xticks(rotation=45, ha="right")
    p.grid(False)
    p.xaxis.label.set_color(FONT_COLOR)
    p.patch.set_alpha(0)
    p.tick_params(colors=FONT_COLOR, which='both')
    p.yaxis.label.set_color(FONT_COLOR)
    p.spines['bottom'].set_color(FONT_COLOR)
    p.spines['top'].set_color(FONT_COLOR)
    p.spines['left'].set_color(FONT_COLOR)
    p.spines['right'].set_color(FONT_COLOR)
    p.set_xlabel("")
    fig.patch.set_alpha(0.)
    st.write(fig)

# Fonction d'affichage d'une valeur numérique et de son titre
def display_value(value,title,yr=False):
    if yr: value=value/-365
    st.markdown(f"<h3 style='text-align: left;'>{title}</h3>", unsafe_allow_html=True)
    text = '\n'+f'{int(value):,}'
    st.markdown(f"<h4 style='text-align: left; color: {'darkorange'};'>{text}</h4>", unsafe_allow_html=True)

# Fonction d'affichage d'une valeur catégorique et de son titre
def display_string(value,title):
    st.markdown(f"<h3 style='text-align: left;'>{title}</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: left; color: {'darkorange'};'>{value}</h4>", unsafe_allow_html=True)


#---------------------------------
# Fonctions de Calculs
# Fonction renvoyant les valeurs à injecter dans le donut
def get_annuities_income_percents():
    val_2 = client_df['AMT_ANNUITY'].iloc[0]
    val_3 = client_df['B_ACTIVE_AMT_ANNUITY_SUM'].iloc[0]
    # traite les autres crédits actifs connus si conditions OK
    if val_3 >0 and active_credit :
        data = [client_df['AMT_INCOME_TOTAL'].iloc[0] - (val_2 + val_3),val_2,val_3]
    else : data = [client_df['AMT_INCOME_TOTAL'].iloc[0] - val_2 ,val_2]
    return data

#---------------------------------
# Chargement des données et dernières constantes utiles
df, model = load_data()
COLS_CAT = ['NAME_CONTRACT_TYPE', 'NAME_INCOME_TYPE', 'NAME_EDUCATION_TYPE',
            'NAME_FAMILY_STATUS', 'OCCUPATION_TYPE', 'ORGANIZATION_TYPE']
COLS_VAL = ['AMT_INCOME_TOTAL','AMT_CREDIT','AMT_ANNUITY','AMT_GOODS_PRICE',
            'DAYS_BIRTH','DAYS_EMPLOYED']
NICE_COLS_CAT = ['Type de contrat', 'Source de revenus', 'Niveau éducation',
                 'Statut familial', 'Type Emploi', 'Type Entreprise']
NICE_COLS_VAL = ['Revenus annuels','Montant Crédit','Montant des annuités',
                 'Montant du bien','Age','Années de Travail']
COL_TO_REVERSE = ['AMT_INCOME_TOTAL','DAYS_EMPLOYED']
COL_YEARS = ['DAYS_BIRTH','DAYS_EMPLOYED']
DICT_COL = dict(zip(NICE_COLS_CAT+NICE_COLS_VAL,COLS_CAT+COLS_VAL))
REV_DICT_COL = dict(zip(COLS_CAT+COLS_VAL,NICE_COLS_CAT+NICE_COLS_VAL))
DICT_GENDER = {0:'Homme',1:'Femme'}
FEATS = [f for f in df.columns if f not in (COLS_CAT+['TARGET','SK_ID_CURR','SK_ID_BUREAU','SK_ID_PREV','index'])]
SK_ID = df['SK_ID_CURR'].iloc[0]
tresh = 16
#---------------
# MAIN
# Barre de configuration latérale
# Sélecion Identifiant
st.sidebar.write('Identifiant')
SK_ID = st.sidebar.number_input('SK_ID:',value=SK_ID)
# Sélecion Seuil
tresh = st.sidebar.slider('risque accepté',0,100,16)
# Sélection autres annuités
st.sidebar.write('Options sur les annuités')
active_credit = st.sidebar.checkbox("Inclure les autre crédits connus")
# Sélection des options de comparaison
st.sidebar.write('Options de comparaison')
col_val = DICT_COL[st.sidebar.selectbox ("Valeur à afficher", NICE_COLS_VAL,key='2')]
col_cat = DICT_COL[st.sidebar.selectbox ("Option de regroupement", NICE_COLS_CAT,key='1')]
# verification si colonnes à inverser ou à transformer en années
rev = col_val in COL_TO_REVERSE
yr = col_val in COL_YEARS

# Body
st.write("""# Home Credit Risk Dashboard""")
st.write("""
            Ce tableau met en avant les principales informations d'un client
            issu de la base de données Home Credit d'après son identifiant.
            Il illustre le risque de défaut de paiement calculé par un modèle
            prenant en compte 188 paramètres choisis. Il permet également
            de comparer certaines informations du client sélectionné par rapport
            aux différentes catégories connues en fonction du regroupement choisi.
        """)



if SK_ID in df['SK_ID_CURR'].values:
    # Séléction infos client
    client_df = df[df['SK_ID_CURR']==SK_ID]
    # Prédiction du score
    score = model.predict_proba(client_df[FEATS])[:,1][0]
    # Affichage
    row0_1, row0_2, row0_3 = st.columns((4,4,4))
    with row0_1: # Infos générales
        display_string(DICT_GENDER[client_df['CODE_GENDER'].values[0]],'Genre')
        display_string(client_df['NAME_FAMILY_STATUS'].values[0],'Statut familial')
        display_value(client_df['AMT_INCOME_TOTAL'],'Revenus')
    with row0_2: # Infos générales
        display_string(client_df['NAME_CONTRACT_TYPE'].values[0],'Type de crédit')
        display_value(client_df['AMT_CREDIT'],'Montant Crédit')
        st.markdown(f"<h3 style='text-align: left;'>{'Taux annuel'}</h3>", unsafe_allow_html=True)
        value = client_df['PAYMENT_RATE'].values[0]*100
        text = f'{value:.2f}'+'%'
        st.markdown(f"<h4 style='text-align: left; color: {'darkorange'};'>{text}</h4>", unsafe_allow_html=True)
    with row0_3: # Illustration risque de défaut
        show_gauge(score*100,tresh)

    row1_1, row1_2= st.columns((5,7)) # Titres des sections suivantes
    with row1_1: st.markdown(f"<h3 style='text-align: center;'>{'Poids des annuités sur le revenu'}</h3>", unsafe_allow_html=True)
    with row1_2: st.markdown(f"<h3 style='text-align: center;'>{'Comparaison par catégorie'}</h3>", unsafe_allow_html=True)

    row2_1, row2_2,row2_3 = st.columns((5,2,5))
    with row2_2: # comparaison annuités/revenus
        display_value(client_df[col_val],REV_DICT_COL[col_val],yr)
        display_string(client_df[col_cat].values[0],REV_DICT_COL[col_cat])
    with row2_1: # comparaison par regroupement de catégories
        if get_annuities_income_percents()[0]>0:
            plot_pie(get_annuities_income_percents(),['Income left','Home Credit Annuity','Bureau Credit Active Annuities'])
        else :
            st.write("Les annuités actives du bureau de crédit représentent {:.2f} fois les revenus annuels ".format(client_df['B_ACTIVE_AMT_ANNUITY_SUM_INCOME_PERCENT'].iloc[0]))
            st.write("Les annuités du crédit actuel représentent {:.2f} fois les revenus annuels ".format(client_df['ANNUITY_INCOME_PERC'].iloc[0]))
    with row2_3:
        plot_histogram_grouped(col_val,col_cat,rev,yr)
# Affichage d'erreur si Identifiant client non reconnu
else: st.write("SK_ID inconnu")
