# Grafica di un file csv con una web-app streamlit
# Lo script è finalizzato a caricare le registrazioni csv di un datalogger 
# per visualizzare l'andamento nel tempo delle grandezze registrate
#
# L. Vanni, vers.0, 29/10/2026
# 

# Librerie
import numpy as np
import streamlit as st
import pandas as pd
from datetime import timedelta as td
# import datetime
import plotly.express as px

# Funzioni ausiliarie
def converti_data(valore_stringa):
    # funzione per convertire la stringa con data-ora in np.datetime64
    s = valore_stringa.strip()
    # Se per caso la riga è vuota (es. test di NumPy), restituisce NaT
    if not s or s == '1':
        return np.datetime64('NaT')
    # Ricostruisce la stringa nel formato ISO accettato da NumPy
    data_iso = f"{s[6:10]}-{s[3:5]}-{s[0:2]}T{s[11:19]}.{s[20:]}"
    return np.datetime64(data_iso)

# Intestazione interfaccia
"""
Visualizzazione registrazioni datalogger
============================
"""

# Acquisizione dei dati in pandas dataframe
# l'oggetto file_caricato è un oggetto nativo streamlit per i file
file_caricato = st.file_uploader("Carica il file csv con i dati", type=["csv"])
if file_caricato is not None:
    dati = pd.read_csv(
        file_caricato,
        delimiter=',',
        skiprows=13,
        # header=None,
        names=['Scan', 'Tempo', 'Temperatura', 'Alarm 110','Corrente','Alarm 114', 'Tensione alimentatore','Alarm 119','Potenziale', 'Alarm 120'],
        #Alarm 114,119 <Tensione capi alimentatore> (VDC),Alarm 119,120 <Tensione elettrodo riferimento> (VDC),Alarm 120
        converters={'Tempo': converti_data},
        encoding='utf-16'
    )
    dati['Tempo'] = pd.to_datetime(dati['Tempo']) # conversione del formato
    
    # visualizzazione dei 'dati' caricati
    st.subheader("Riepilogo dati")
    st.dataframe(
    dati.drop(columns=['Alarm 110','Alarm 114', 'Alarm 119','Alarm 120']), # nascondo queste colonne
    height=200,
    use_container_width=True,
    hide_index=True,
    key="tabella",
)

    # GRAFICA DEI DATI
    ## grafico andamento temporale potenziale e corrente
    fig = px.line(dati, 
        x='Tempo', 
        y=['Potenziale', 'Corrente'], 
        title='Potenziale e Corrente vs Tempo',
        labels={
        'value': 'Potenziale [V], Corrente [A]', # Cambia il titolo dell'asse Y
        'variable': 'andamento nel tempo:'            # Cambia il titolo della legenda
    }
        )
    fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig.update_layout(hovermode='x unified')  # mostra tutti i valori alla stessa x in un unico tooltip
    st.plotly_chart(fig)
    
    ## grafico potenziale vs corrente anodica
    fig3 = px.scatter(
        dati.loc[
            (dati["Corrente"] >= 0) &
            (dati["Potenziale"] <= -1.8)
        ], 
        x='Corrente', 
        y='Potenziale', 
        title='Potenziale vs Corrente anodica',
        labels={
        'Potenziale': 'Potenziale [V]', # Cambia il titolo dell'asse Y
        'Corrente': 'Corrente anodica [A]' # Cambia il titolo della legenda
        }
        )
    fig3.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig3.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig3.update_layout(hovermode='x unified')  # mostra tutti i valori alla stessa x in un unico tooltip
    st.plotly_chart(fig3)
    
    ## grafico potenziale vs corrente catodica
    dati_catodici = dati.loc[dati["Corrente"] <= 0]
    dati_catodici['Corrente'] = - dati_catodici['Corrente']
    fig4 = px.scatter(
        dati_catodici, 
        x='Corrente', 
        y='Potenziale', 
        title='Potenziale vs Corrente catodica',
        labels={
        'Potenziale': 'Potenziale [V]', # Cambia il titolo dell'asse Y
        'Corrente': 'Corrente catodica [A]' # Cambia il titolo della legenda
    }
        )
    fig4.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig4.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig4.update_layout(hovermode='x unified')  # mostra tutti i valori alla stessa x in un unico tooltip
    st.plotly_chart(fig4)    


    ## grafico della temperatura
    fig2 = px.scatter(dati, 
                      x='Tempo', 
                      y='Temperatura', 
                      title='Temperatura vs Tempo', 
                      color_discrete_sequence=["red"],
                      labels={
                      'Temperatura': 'Temperatura [°C]', # Cambia il titolo dell'asse Y
                       }                      
                      )
    eventi_fig2 = st.plotly_chart(
                fig2,
                key="grafico_temperatura",
                on_select="rerun",
                selection_mode=["box"]
                )
    if eventi_fig2.selection:
        indici_righe_selez = eventi_fig2.selection.point_indices
        dati_selez = dati.iloc[indici_righe_selez]
        T_m = dati_selez.Temperatura.mean()
        if type(T_m) is np.float64:
            st.write(f"T media in box = {T_m:.1f} °C")
    st.write("(Usa il box di selezione sul grafico per calcolarne la temperatura media)")

