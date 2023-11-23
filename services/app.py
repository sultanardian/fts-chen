import calendar
import io
import os
import sys
import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta 
from PIL import Image
from plotly import express as px

path_this = os.path.dirname(__file__)
path_master = os.path.abspath(os.path.join(path_this, '..'))
sys.path.append(os.path.join(path_master, 'src'))

from fts import ChenFTS

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.header('Sistem Peramalan')

    tab_data, tab_result = st.tabs(['Input data', 'Hasil forecasting'])

    with tab_data:
        file = st.file_uploader('Pilih file')
        if file is not None:
            df = pd.read_excel(file)
            col1, col2 = st.columns(2)

            with col1:
                st.table(df)
            with col2:
                x = st.selectbox(
                    'Pilih kolom Timeframe (X)',
                    set([''] + df.columns.tolist()),
                    key = 'tf'
                )
                y = st.selectbox(
                    'Pilih kolom Data (Y)',
                    set([''] + df.columns.tolist()),
                    key = 'df'
                )

                column_submit = st.button('Set', key = 'column_submit')

                if column_submit:
                    fig = px.line(df, x = x, y = y)
                    st.plotly_chart(fig, use_container_width = True)

    with tab_result:
        try:
            if column_submit:
                time = df[x].tolist()
                data = df[y].tolist()

                model = ChenFTS(data)
                result = model.forecast()
                evaluate = model.evaluate()

                last = time[-1].strftime('%Y-%m-%d')
                # current = time[-1] + timedelta(days = 1)
                current = str(time[-1] + relativedelta(months = 1))
                current = current.split(' ')[0]

                col_m1, col_m2, col_m3 = st.columns([1, 1, 3])

                with col_m1:
                    st.metric(
                        label = f"Aktual terakhir ({last})",
                        value = data[-1]
                    )

                with col_m2:
                    st.metric(
                        label = f"Prediksi selanjutnya ({current})",
                        value = result,
                        delta = result - data[-1]
                    )

                with col_m3:
                    st.metric(
                        label = "Skor evaluasi (MAPE)",
                        value = round(evaluate[0], 2),
                    )

                predicted = []
                for d, e in zip(data, evaluate[1]):
                    predicted.append(d - e[1])

                df_predicted = pd.DataFrame({
                    x : time,
                    y : predicted,
                    'status' : ['Prediksi'] * len(predicted)
                })
                df['status'] = ['Aktual'] * len(data)

                new_df = pd.concat([df, df_predicted])

                plt = px.line(new_df, x = x, y = y, color = 'status', title = 'Hasil Peramalan')
                st.plotly_chart(plt, use_container_width = True)

            else:
                st.text('Set sumbu X dan Y terlebih dahulu')
        except:
            st.text('Input dataset terlebih dahulu')
        