import numpy as np
from collections import Counter

class ChenFTS:
    def __init__(self, ts):
        self.ts = ts
        self.num_intervals = np.ceil(1 + 3.322 * np.log10(len(self.ts))).astype('int')
        self.discourse = [10, 12]

        self.intervals = self._create_intervals()
        self.fuzzified = self._fuzzify()
        self.flrg = self._flrg()
        self.model = self._model()


    def _create_intervals(self):
        min_val = min(self.ts) - self.discourse[0]
        max_val = max(self.ts) + self.discourse[1]
        interval_width = np.ceil((max_val - min_val) / self.num_intervals).astype('int')

        intervals = []
        for i in range(self.num_intervals):
            if i == 0:
                int_min = min_val
            else:
                int_min += interval_width

            int_min = int(round(int_min, 0))
            int_max = int(round(int_min + interval_width - 1, 0))

            median = (int_min + int_max) / 2

            intervals.append((
                f'A{i+1}',
                [int_min, int_max],
                median
            ))

        return intervals

    def _fuzzify(self):
        fuzzified = []
        intervals = self._create_intervals()

        for idx, point in enumerate(self.ts):
            for interval in self.intervals:
                if interval[1][0] <= point <= interval[1][1]:
                    fuzzified.append((point, interval[0]))
                    break

        return fuzzified


    def _flrg(self, ordo = 0):
        prop = []

        A = [f'A{i+1}' for i in range(self.num_intervals)]

        for idx, fuzzy in enumerate(self.fuzzified):
            if idx > ordo:
                lh = self.fuzzified[idx - 1][1]
                rh = fuzzy[1]
                prop.append((lh, [lh, rh]))
            else:
                prop.append((None, [None, None]))

        groups = []
        for idx, a in enumerate(A):
            rhs = []

            for p in prop:
                if p[0] == a:
                    rhs.append(p[1][1])

            unq_rhs = sorted(list(set(rhs)))
            groups.append((a, unq_rhs))

        return groups


    def _model(self):
        chen = []

        for group in self.flrg:
            sum_of_meds = 0
            for next_state in group[1]:
                for x in self.intervals:
                    if x[0] == next_state:
                        sum_of_meds += x[2]

            if sum_of_meds == 0:
                for x in self.intervals:
                    if x[0] == group[0]:
                        median = x[2]

            else:
                median = sum_of_meds/len(group[1])


            chen.append((int(round(median, 0)), group[0]))

        return chen


    def forecast(self):
        current_state = self.fuzzified[-1][1]

        for m in self.model:
            if m[1] == current_state:
                forecasts = m[0]
                break

        return forecasts


    def evaluate(self):
        diffs = []
        num_of_diffs = 0
        for f in self.fuzzified:
            for group in self.model:
                if group[1] == f[1]:
                    diff = f[0] - group[0]

                    num_of_diffs += np.absolute(diff)
                    diffs.append((f, diff))

        mape = num_of_diffs/len(diffs)
        return mape, diffs