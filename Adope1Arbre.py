import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import urllib.request
from PIL import Image
from csv import writer
from datetime import datetime, timedelta
from collections import defaultdict
import datetime
from streamlit_folium import folium_static
import folium
import requests
import json
import flexpolyline as fp
import qrcode
from qrcode.image.styledpil import StyledPilImage
import math

#import des fonctions depuis utils
from utils import *

if not hasattr(Image, 'Resampling'):  # Pillow<9.0
    Image.Resampling = Image

def page_Adopte():
    #optimiseur de choix d'exutoire
    col1, _, col2 = st.columns([5,1,2])
    col1.title("Adopte1Arbre 🌳🌲🎋🌴🌱🌰🌵🌿☘🏵")
    col2.header("🌳 ADOPTE 🌲")
    # col2.image(
    #     'data:image/jpeg;base64,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')
    st.subheader("Adopte un arbre de ton essence préférée près de chez toi")

    df_arbre=pd.read_csv('les-arbres-plantes-clean.csv', sep=';')
    df_arbre["Arbre Essence - Nom français"].fillna("non précisé", inplace=True)

    st.write("Il y a {} arbres plantés à ce jour dans Paris (depuis le 1er novembre 2021)".format(df_arbre.shape[0]))

    now = datetime.datetime.utcnow()
    result = now + timedelta(hours=2)
    date_heure = result.strftime("%d/%m/%Y %H:%M:%S")
    st.text("Date et heure : " + date_heure)

    col1, _, col2=st.columns([10,1,10])

    yourAdress = col1.text_input("Renseigne une adresse (dans Paris) et découvre la forêt près de chez toi", value="", max_chars=None, key=None, type="default",
                              help=None, autocomplete=None, on_change=None)

    if yourAdress != "":
        finalAdress, gps_position = GPS_from_Adress(yourAdress)
        col1.write("🏡 l'adresse identifiée est " + finalAdress)
        if gps_position != []:
            df_arbre["distance_a_position"] = \
                [distance([gps_position[0], gps_position[1]],
                          [df_arbre["lat"].iloc[i], df_arbre["lon"].iloc[i]]) for i in
                 range(df_arbre.shape[0])]
            for select_dist in [0.1,0.5,1,5]:
                df_arbre_select_moinsde=df_arbre[df_arbre.distance_a_position <= select_dist].shape[0]
                if df_arbre_select_moinsde>0:
                    col2.write("{} arbres à moins de {}km".format(df_arbre_select_moinsde,select_dist))
    else:
        gps_position=[48.855397247540466, 2.346641058380128]

    col1, _, col2=st.columns([10,1,10])

    col1.subheader('Quel arbre adopter ?')

    df_arbre_select=df_arbre.copy()
    ma_date=col1.text_input("Votre date d'anniversaire Jour Mois (exemple: 20/06)",value="", max_chars=None, key=None, type="default",
                              help=None, autocomplete=None, on_change=None)
    if ma_date!="":
        mon_mois=ma_date.split("/")[1]
        mon_jour=ma_date.split("/")[0]
        print(mon_mois,mon_jour)
        df_arbre_select_anniv=df_arbre_select[(df_arbre_select.loc[:,"mois_plantation"]==int(mon_mois)) & (df_arbre_select.loc[:,"jour_plantation"]==int(mon_jour))]
        if df_arbre_select_anniv.shape[0]>0:
            col1.write("Il y a {} arbres plantés le même jour que vous".format(df_arbre_select_anniv.shape[0]))
            df_arbre_select=df_arbre_select_anniv
        else:
            col1.write("Ah mince, aucun arbre n'a été planté votre jour de naissance")

    options_taille = col1.multiselect(
        'Quelle taille ?', df_arbre.classeTaille.unique().tolist())

    options_rare=col1.multiselect('Quelle rareté ?', df_arbre.rareOupas.unique().tolist())


    for select_taille in options_taille:
        if select_taille!="":
            df_arbre_select=df_arbre_select[df_arbre_select.loc[:,"classeTaille"]==select_taille].dropna(subset=["Arbre Essence - Nom français"], axis=0)
    for select_rare in options_rare:
        if select_rare!="":
            df_arbre_select=df_arbre_select[df_arbre_select.loc[:,"rareOupas"]==select_rare].dropna(subset=["Arbre Essence - Nom français"], axis=0)

    options_essence = col1.multiselect('Quelle essence ?', df_arbre_select.loc[:,"Arbre Essence - Nom français"].unique().tolist())
    for select_essence in options_essence:
        if select_essence!="":
            df_arbre_select=df_arbre_select[df_arbre_select.loc[:,"Arbre Essence - Nom français"]==select_essence]

    st.write("{} arbres correspondent aux critères".format(df_arbre_select.shape[0]))

    if (df_arbre_select.shape[0] > 0) and gps_position != []:
        col2.subheader("Où sont-ils ? 🔍")
        # we compute distance to the chantier

        col2.write("Le plus proche est à {}km".format(np.round(df_arbre_select.distance_a_position.min(),2)))
        df_arbre_select = df_arbre_select.sort_values(by='distance_a_position').iloc[:100, :]

        col2.write("Voir la carte pour le détail des positions et faire ton choix")

        st.subheader("La Carte des 🌳")
        st.write("Zoom et clique sur l'arbre que tu veux, et note son numéro pour tout savoir de lui")

        mon_nbr_arbre=st.text_input("Le numéro d'arbre choisi", value="", max_chars=None, key=None, type="default",
                          help=None, autocomplete=None, on_change=None)
        map = create_map_opti(df_arbre_select, gps_position)
        folium_static(map)
        col1, col2=st.columns(2)
        if mon_nbr_arbre!="":
            mon_nbr_arbre=int(mon_nbr_arbre)
            mon_arbre=df_arbre_select[df_arbre_select["Emplacement - Identifiant unique"]==mon_nbr_arbre]
            if mon_arbre.shape[0]>0:
                col1.write("Voici l'adresse de votre arbre")
                mon_arbre_adresse="{}, {} ({})".format(mon_arbre["Emplacement - Complément d'adresse"].iloc[0],mon_arbre["Emplacement - Site / Adresse"].iloc[0], mon_arbre["Emplacement - Arrondissement"].iloc[0])
                col1.subheader(mon_arbre_adresse)
                col2.write("Voici sa fiche d'identité")
                mon_arbre_id="{}, planté le {}, c'est un arbre {} et {}".format(mon_arbre["Arbre Essence - Nom français"].iloc[0],
                                                                                mon_arbre["Arbre Exploitation - Planté le"].iloc[0][:10],
                                                                                mon_arbre["rareOupas"].iloc[0],
                                                                                mon_arbre["classeTaille"].iloc[0])
                col2.subheader(mon_arbre_id)
            else:
                col2.write("Numéro d'arbre à vérifier")

def page_Decouvrir():
    col1, _, col2 = st.columns([5, 1, 2])
    col1.title("Adopte1Arbre 🌳🌲🎋🌴🌱🌰🌵🌿☘🏵")
    col2.header("🌳 DECOUVRE 🌲")
    st.subheader("🌳 Découvre les arbres de Paris 🌲")
    df_arbre = pd.read_csv('les-arbres-plantes-clean.csv', sep=';').dropna(subset=["Arbre Essence - Nom français"],axis=0)
    st.write("Il y a {} arbres plantés à ce jour dans Paris (depuis le 1er novembre 2021)".format(df_arbre.shape[0]))

    col1,col2=st.columns(2)
    col1.write("- Le détail par arrondissements de Paris-")
    col1.dataframe(df_arbre["Emplacement - Arrondissement"].value_counts())
    col2.write("- Le détail par essences -")
    col2.dataframe(df_arbre["Arbre Essence - Nom français"].value_counts())

    st.write("- La carte de tous les arbres plantés -")
    st.map(df_arbre[["lat","lon"]])

    st.write("- le nombre d'arbres plantés par jour")
    hist_values_jour = pd.Series(
        df_arbre.groupby(by=['Arbre Exploitation - Planté le']).count().loc[:,
        'classeTaille'], name='nombre')
    st.write('En moyenne, {} arbres sont plantés chaque jour'.format(round(pd.Series(
        df_arbre.groupby(by=['Arbre Exploitation - Planté le']).count().loc[:,
        'classeTaille'], name='nombre').mean(),0)))
    st.bar_chart(hist_values_jour)

    st.caption("lien vers les données sources : https://opendata.paris.fr/explore/dataset/les-arbres-plantes/information/")


#put all pages together
page_names_to_funcs = {
    " 🌳 Adopter": page_Adopte,
    " 🌴 Découvrir": page_Decouvrir}

selected_page = st.sidebar.radio("Bienvenue chez Adopte1Arbre", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()