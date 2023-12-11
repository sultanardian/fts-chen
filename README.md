# Clone repository
- copy url berikut 
```https://github.com/sultanardian/fts-chen.git```

- buka terminal
ketik command berikut 

```git clone https://github.com/sultanardian/fts-chen.git --branch dev```

- masuk ke folder ```fts-chen``` melalui terminal dengan command

```cd fts-chen```

# Instalasi
- Python anaconda
1. install anaconda dari ```https://www.anaconda.com/download/```
2. setelah itu cek status instalasi di terminal dengan command 

```conda -v```

jika muncul versinya, maka instalasi berhasil

- Conda environment
1. ketik command

```conda create -n skripsi python==3.8.0```

tunggu hingga instalasi berhasil

2. cek status instalasi dengan command

```python3 --version```

jika muncul versinya, maka instalasi environment berhasil

- Environment dependencies
1. masuk ke environment

```conda activate skripsi```

2. ketik command 

```cat requirements.txt | xargs -n 1 pip install```

3. tunggu hingga proses instalasi berhenti

# Menyalakan aplikasi
1. ketik command berikut 

```streamlit run services/app.py```

2. tunggu hingga memunculkan alamat ip untuk membuka aplikasi 

setelah muncul, klik ip tersebut
