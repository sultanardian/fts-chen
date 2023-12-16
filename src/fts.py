# import library yang dibutuhkan
import numpy as np
from collections import Counter

# membuat object class yang akan diimport dengan aplikasi web nantinya
class ChenFTS:
    
    # inisialisasi variabel awal terhadap object, wajib menerima parameter data timeseries
    def __init__(self, ts):
        # inisialisasi variabel global object ditandai dengan self. variabel ini akan digunakan di lingkup object ini
        self.ts = ts

        # mencari banyaknya interval berdasarkan data timeseriesnya
        """
        persamaan :
        interval = 1+3.3 × log𝑛
        dengan n adalah panjang datanya
        """
        self.num_intervals = np.ceil(1 + 3.322 * np.log10(len(self.ts))).astype('int')

        # menentukan himpunan semesta (discourse) dengan nilai sembarang
        self.discourse = [10, 12]

        # membuat data interval
        self.intervals = self._create_intervals()

        # membuat inferensi fuzzifikasi
        self.fuzzified = self._fuzzify()

        # menentukan Fuzzy Logical Reationship Group (FLRG)
        self.flrg = self._flrg()

        # membuat model forecasting
        self.model = self._model()


    def _create_intervals(self):
        # menentukan nilai terkecil dan terbesar data dengan diferensial dari discourse
        min_val = min(self.ts) - self.discourse[0]
        max_val = max(self.ts) + self.discourse[1]

        # menentukan lebar interval
        """
        persamaan :
        lebar = (nilai max - nilai min)/banyak interval
        """
        interval_width = np.ceil((max_val - min_val) / self.num_intervals).astype('int')

        # melakukan iterasi untuk mencari interval pada tiap kelasnya berdasarkan banyaknya interval
        intervals = []
        for i in range(self.num_intervals):
            # menentukan nilai min dari satu kelas. jika index adalah 0 maka nilai min = nilai terkecil
            if i == 0:
                int_min = min_val
            # jika index bukan 0 maka nilai min = nilai min + lebar interval
            else:
                int_min += interval_width

            # nilai min dan max harus bulat dan integer
            int_min = int(round(int_min, 0))
            # menentukan nilai max dari nilai min + lebar interval - 1
            int_max = int(round(int_min + interval_width - 1, 0))

            # mencari median dari nilai min dan nilai max
            median = (int_min + int_max) / 2

            # mengumpulkan interval dan ditampung dalam variabel
            intervals.append((
                f'A{i+1}',
                [int_min, int_max],
                median
            ))

        # mengembalikan kumpulan interval
        """
        contoh :
        [
            ("A1", [1, 10], 5.5),
            ("A2", [11, 20], 15.5),
            .
            .
            .
            ("A𝑛", [D0𝑛, D1𝑛], med𝑛)
        ]
        """
        return intervals

    
    def _fuzzify(self):
        # membuat variabel list kosong untuk menampung himpunan fuzzifikasi
        fuzzified = []

        # melakukan iterasi pada data timeseries
        for idx, point in enumerate(self.ts):
            
            # melakukan iterasi pada kumpulan interval
            for interval in self.intervals:

                # jika data timeseries berada pada kondisi lebih dari samadengan interval rendah dan kurang dari samadengan interval tinggi maka akan dimasukkan ke dalam list fuzzifikasi
                if interval[1][0] <= point <= interval[1][1]:
                    fuzzified.append((point, interval[0]))
                    break

        # mengembalikan list fuzzifikasi
        """
        contoh :
        [
            (5, "A1"),
            (6, "A1"),
            (12, "A2"),
            .
            .
            .
            (Data ke-𝑛, "A𝑛")
        ]
        """
        return fuzzified


    def _flrg(self):
        # membuat list kosong untuk menampung kumpulan properti
        prop = []

        # mengambil semua grup
        A = [f'A{i+1}' for i in range(self.num_intervals)]

        # melakukan iterasi terhadap kumpulan grup fuzzifikasi
        for idx, fuzzy in enumerate(self.fuzzified):
            # melakukan kondisi untuk mengetahui apakah index di nilai lebih dari 0 atau tidak
            if idx > 0: 
                # mengambil grup kiri nilai fuzzy saat ini, yaitu dari nilai fuzzy index sebelumnya
                lh = self.fuzzified[idx - 1][1]
                # mengambil grup kanan nilai fuzzy saat ini, yaitu dari nilai fuzzy saat ini
                rh = fuzzy[1]
                # mengumpulkan ke list properti
                prop.append((lh, [lh, rh]))
            else:
                # jika kondisi salah maka akan mengumpulkan nilai None
                prop.append((None, [None, None]))

        # membuat list kosong untuk menampung kumpulan flrg
        groups = []

        # melakukan iterasi terhadap grup interval
        for idx, a in enumerate(A):
            # membuat list kosong untuk menampung kumpulan grup kanan nilai fuzzy
            rhs = []

            # melakukan iterasi pada kumpulan properti
            for p in prop:
                # jika grup kiri sama dengan iterasi grup interval saat ini maka diproses
                if p[0] == a:
                    # menampung grup kanan
                    rhs.append(p[1][1])

            # mencari nilai unik dari grup kanan karena banyak yang duplikat
            unq_rhs = sorted(list(set(rhs)))

            # menampung kumpulan grup kanan ke list grup
            groups.append((a, unq_rhs))

        # mengembalikan kumpulan grup
        """
        contoh :
        [
            ("A1", ["A1", "A2", "A4", "A6"]),
            ("A2", ["A3", "A4", "A6"]),
            ("A3", ["A1", "A3", "A5", "A6"]),
            .
            .
            .
            (A𝑛, grup ke-𝑛)
        ]
        """
        return groups


    def _model(self):
        # membuat list kosong untuk menampung kumpulan chen
        chen = []

        # melakukan iterasi terhadap flrg
        for group in self.flrg:
            # inisialisasi total median diawali dengan 0
            sum_of_meds = 0

            # melakukan iterasi terhadap kumpulan grup flrg tiap grup interval
            for next_state in group[1]:
                # melakukan iterasi terhadap kumpulan interval
                for x in self.intervals:
                    # melakukan kondisi jika grup interval sama dengan grup flrg
                    if x[0] == next_state:
                        # menambahkan median dari grup interval
                        sum_of_meds += x[2]

            # melakukan kondisi jika total median sama dengan 0
            if sum_of_meds == 0:
                # melakukan iterasi terhadap kumpulan interval
                for x in self.intervals:
                    # melakukan kondisi jika grup interval sama dengan grup induk flrg
                    if x[0] == group[0]:
                        # inisialisasi median akhir yang serupa dengan median dari grup interval
                        median = x[2]

            else:
                # inisialisasi median akhir
                median = sum_of_meds/len(group[1])

            # mengumpulkan nilai median akhir 
            chen.append((int(round(median, 0)), group[0]))

        # mengembalikan variabel chen
        """
        contoh :
        [
            (21.5, "A1"),
            (17.5, "A2"),
            .
            .
            .
            (median akhir ke-𝑛, "A𝑛")
        ]
        """
        return chen

    # function untuk memproses forecasting datanya
    def forecast(self):
        # mencari state akhir dari inferensi fuzzifikasi
        current_state = self.fuzzified[-1][1]

        # melakukan iterasi pada model chen
        for m in self.model:
            # melakukan kondisi jika grup chen sama dengan state akhir
            if m[1] == current_state:
                # hasil forecast adalah median dari grup chen
                forecasts = m[0]
                break
                
        # mengembalikan hasil akhir forecasting
        return forecasts


    def evaluate(self):
        # membuat list kosong untuk menampung diferensial dari nilai aktual dan prediksi
        diffs = []

        # menginisialisasi total diferensial dengan nilai awal 0
        num_of_diffs = 0

        # melakukan iterasi terhadap nilai inferensi fuzzifikasi
        for f in self.fuzzified:

            # melakukan iterasi terhadap model chen
            for group in self.model:

                # melakukan kondisi jika grup chen sama dengan grup fuzzifikasi
                if group[1] == f[1]:
                    # mencari diferensial dari nilai chen dengan nilai fuzzifikasi
                    diff = f[0] - group[0]

                    # menjumlahkan nilai diferensial dengan total diferensial
                    num_of_diffs += np.absolute(diff)

                    # menampung diferensial
                    diffs.append((f, diff))

        # menghitung mape
        """
        persamaan :
        Σ|xt−ft/Xt|/n x 100%
        """
        mape = num_of_diffs/len(diffs)

        # mengembalikan nilai mape dan diferensial
        """
        contoh:
        (13.7, [1.4, 5.1, -0.4, ..., diff ke-𝑛])
        """
        return mape, diffs
