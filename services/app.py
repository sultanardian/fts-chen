# import library yang dibutuhkan
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

# mengambil direktori file saat ini
path_this = os.path.dirname(__file__)
# mengambil direktori utama project
path_master = os.path.abspath(os.path.join(path_this, '..'))
# menambahkan direktori modul tambahan yang dibuat sendiri
sys.path.append(os.path.join(path_master, 'src'))

from fts import ChenFTS

if __name__ == '__main__':
    # konfigurasi layout web
    st.set_page_config(layout="wide")

    
    st.header('Sistem Peramalan')
    
    # membuat container untuk tampilan tab
    tab_data, tab_result = st.tabs(['Input data', 'Hasil forecasting'])

    # membuat tampilan tab untuk bagian input data
    with tab_data:

        # membuat tombol upload file
        file = st.file_uploader('Pilih file')

        # eksekusi jika file sudah diupload
        if file is not None:

            # membaca file excel
            df = pd.read_excel(file)

            # membuat container untuk tampilan kolom dengan 2 kolom
            col1, col2 = st.columns(2)

            # membuat tampilan kolom pertama untuk menampilkan data dari file yang diupload sebelumnya
            with col1:
                st.table(df)

            # membuat tampilan kolom kedua untuk memilih kolom data yang akan digunakan nantinya
            with col2:

                # membuat input berupa selectbox pilih kolom timeframe untuk sumbu X
                x = st.selectbox(
                    'Pilih kolom Timeframe (X)',
                    set([''] + df.columns.tolist()),
                    key = 'tf'
                )

                # membuat input berupa selectbox pilih kolom data numerik untuk sumbu Y
                y = st.selectbox(
                    'Pilih kolom Data (Y)',
                    set([''] + df.columns.tolist()),
                    key = 'df'
                )

                # membuat tombol submit form
                column_submit = st.button('Set', key = 'column_submit')

                # eksekusi jika tombol submit ditekan
                if column_submit:

                    # menampilkan chart preview data dengan sumbu X dan Y yang telah dipilih sebelumnya
                    fig = px.line(df, x = x, y = y)
                    st.plotly_chart(fig, use_container_width = True)

    # membuat tampilan tab untuk menampilkan hasil forecasting
    with tab_result:
        # menggunakan try except untuk kondisi file sudah diupload atau belum
        try:
            # eksekusi jika tombol submit ditekan
            if column_submit:
                # konversi data yang sebelumnya berbentuk pandas.Series menjadi list
                time = df[x].tolist()
                data = df[y].tolist()

                # menginisialisasi model forecasting dengan modul yang telah dibuat dan diimport sebelumnya dengan menginputkan parameter data
                model = ChenFTS(data)

                # mengambil hasil forecasting
                result = model.forecast()

                # mengevaluasi hasil forecasting
                evaluate = model.evaluate()

                # mengambil hari terakhir dari timeframe pada data yang dipilih sebelumnya
                last = time[-1].strftime('%Y-%m-%d')

                # mengambil tanggal pada 1 hari setelah hari terakhir
                current = str(time[-1] + relativedelta(months = 1))
                current = current.split(' ')[0]

                # membuat container untuk membuat tampilan kolom dengan 3 kolom
                col_m1, col_m2, col_m3 = st.columns([1, 1, 3])

                # membuat tampilan untuk kolom pertama dengan menampilkan metrik aktual terakhir atau data numerik pada tanggal terakhir
                with col_m1:
                    st.metric(
                        label = f"Aktual terakhir ({last})",
                        value = data[-1]
                    )

                # membuat tampilan untuk kolom kedua dengan menampilkan metrik hasil prediksi 1 hari selanjutnya dari hari terakhir
                with col_m2:
                    st.metric(
                        label = f"Prediksi selanjutnya ({current})",
                        value = result,
                        delta = result - data[-1]
                    )

                # membuat tampilan untuk kolom ketiga dengan menampilkan metrik skor evaluasi
                with col_m3:
                    st.metric(
                        label = "Skor evaluasi (MAPE)",
                        value = round(evaluate[0], 2),
                    )

                # memproses data prediksi per hari pada semua timeframe yang diambil dari variabel evaluate indeks ke-1. disitu datanya berupa selisih dari hasil prediksi dan aktual
                predicted = []
                for d, e in zip(data, evaluate[1]):
                    predicted.append(d - e[1])

                # membuat dataframe untuk data prediksi berdasarkan timeframenya
                df_predicted = pd.DataFrame({
                    x : time,
                    y : predicted,
                    'status' : ['Prediksi'] * len(predicted)
                })

                # menambahkan status pada dataframe aktual berisi "Aktual" sebanyak datanya
                df['status'] = ['Aktual'] * len(data)

                # menggabungkan dataframe aktual dan dataframe prediksi
                new_df = pd.concat([df, df_predicted])

                # menampilkan linechart dataframe gabungan dengan legends kolom statusnya
                plt = px.line(new_df, x = x, y = y, color = 'status', title = 'Hasil Peramalan')
                st.plotly_chart(plt, use_container_width = True)

            else:
                st.text('Set sumbu X dan Y terlebih dahulu')
                
        # handler jika dataset belum diinputkan
        except:
            st.text('Input dataset terlebih dahulu')
        
