import copy
import json


class JsonCleaner:

    def __init__(self, path):
        self.path = path
        self.dirty_data = self._unpack_data()

    def _unpack_data(self):
        with open(self.path, 'r') as file:
            dirty_data = [json.loads(line) for line in file.readlines()]
        return dirty_data

    def create_table(self):
        records = []
        dirty_copy = copy.deepcopy(self.dirty_data)
        birads = self._choose_birads()
        for index in range(len(dirty_copy)):
            if self._valid_row(dirty_copy[index]['Proiezione'], dirty_copy[index].get('Birads'), birads):
                try:
                    records.append(str(dirty_copy[index]['PG']) + ';' +
                                   str(dirty_copy[index]['_id']) + ';' +
                                   # str(dirty_copy[index]['Proiezione']) + ', ' +
                                   str(dirty_copy[index]['Birads']) + ';' +
                                   # str(dirty_copy[index]['KeyPoints']) + ', '
                                   # non serve il get(birads
                                   self._clean_keypoints(dirty_copy[index]['KeyPoints']) + ';' +
                                   str(dirty_copy[index]['Proiezione']) + ';;' )

                except RowError:
                    pass

        return records

    def _clean_keypoints(self, keypoints):
        # keypoints is a list of dict
        for item in range(len(keypoints)-1, -1, -1):
            if self._is_null_keypoints(keypoints[item]):
                del(keypoints[item])
        if not keypoints:
            raise RowError('invalid row---> IS EMPTY')
        return self._delete_duplicate_keypoints(keypoints)
 
    def _delete_duplicate_keypoints(self, keypoints):
        for item in range(len(keypoints)):  # da dict a str
            keypoints[item] = str(keypoints[item])
        unique_keypoints = "["
        for unique_keypoint in range(len(set(keypoints))):  # rendo le stringe uniche
            unique_keypoints +=  keypoints[unique_keypoint] + ', '    # creo unica stringa
        unique_keypoints = unique_keypoints[:-2]  # rimuove l'ultima virgola del for
        unique_keypoints += ']'
        return unique_keypoints

    def _is_null_keypoints(self, single_point):
        if single_point['X'] == 0.0 and single_point['Y'] == 0.0 and single_point['Scala'] == 0.0:
            return True
        return False

    def _choose_birads(self):
        self.last_birads = int(input('inserire il valore di birads desiderato\n:'))
        return self.last_birads

    def _valid_row(self, projection, birads_value, birads_out):
        try:
            if len(birads_value) == 2 and (projection.endswith('RX') or projection.endswith('DX')):
                return self.birads_check(birads_value[1], birads_out)
            else:
                return self.birads_check(birads_value[0], birads_out)

        except TypeError:  # per i valori senza birads ---> NoneType[x] / len(None)
            return False

    def birads_check(self, birads_value, birads_out):
        try:
            if birads_out is 4:
                return int(birads_value) >= 4
            elif 1 <= birads_out <= 2:
                return 1 <= int(birads_value) <= 2
            elif birads_out == 3:
                return int(birads_value) == 3
        except ValueError:  # per i valori 4c
            return birads_out == 4

    def save_as_csv(self, table, path):
        csv = open(f'{path}{self.last_birads}.csv', 'w')
        csv.write("PG;_id;Birads;KeyPoints;Proiezione;UID;machine" + '\n')
        for line in range(len(table)):
            csv.write(table[line]+'\n')
        csv.close()


class RowError(Exception):
    pass


json_test = JsonCleaner(path="dataset/Screening_GoldStandard.json")
while True:
    json_test.save_as_csv(json_test.create_table(), 'dataset/clean_json/clean_json_birads')
    if input('vuoi creare altri csv?\nY/N:').lower() != 'y':
        print('Buon dataMining, DEMA <3')
        break

import pandas as pd
import os

path_birads_file=r"dataset/clean_json"
print(path_birads_file)
birads_file = os.listdir(path_birads_file)
dtype = 'str'

file1 = pd.read_csv(os.path.join(path_birads_file, birads_file[0]), sep=';', dtype=dtype)
file3 = pd.read_csv(os.path.join(path_birads_file, birads_file[1]), sep=';', dtype=dtype)
file4 = pd.read_csv(os.path.join(path_birads_file, birads_file[2]), sep=';', dtype=dtype)
file = pd.concat([file1, file3, file4])
