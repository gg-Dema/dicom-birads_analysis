import pandas as pd
import pydicom
import os


class Extractor:

    def __init__(self, path_dicom_file, path_birads_file, path_birads_sum_file):
        self.path_birads_file = path_birads_file
        self.path_dicom_file = path_dicom_file
        birads_file = path_birads_sum_file
        self.birads_file = pd.read_csv(birads_file, sep=';', dtype='str')

        self.accepted_string_MLO_RIGHT = ['MLO RX', 'OBL RX', 'SENO D,OBL', 'SENO D,MLO', 'R', 'MLO', 'OBL', 'ML RX', 'SENO D,ML']
        self.accepted_string_MLO_LEFT = ['MLO LX', 'OBL LX', 'SENO S,OBL', 'SENO S,MLO', 'L', 'MLO', 'OBL', 'ML LX', 'SENO S, ML']
        self.accepted_string_CC_LEFT = ['CC LX', 'SENO S,CC', 'CC', 'L']
        self.accepted_string_CC_RIGT = ['CC RX', 'SENO D,CC', 'CC', 'R']

    def start_analisys(self, destination_path, write=1, index_split=0, *args):

        count = 1
        for dir in os.listdir(self.path_dicom_file):
            dicom_list = os.listdir(os.path.join(self.path_dicom_file, dir))
            for dicom in dicom_list:
                print(f'\n\nnumero cartella esaminate : {count} / 5000\t A.K.A. {(count/50):.2f}%')
                self.elab_UID_and_machine(os.path.join(self.path_dicom_file, dir, dicom), PG=str(dir))
            count += 1

        if write:
            self.file1 = open(os.path.join(destination_path, 'birads1.csv'), 'w')
            self.file2 = open(os.path.join(destination_path, 'birads3.csv'), 'w')
            self.file3 = open(os.path.join(destination_path, 'birads4.csv'), 'w')
            self.split_and_write_csv()
            print('file con path generati correttamente')
            self.file1.close()
            self.file2.close()
            self.file3.close()

        elif write and index_split:
            self.file1 = open(os.path.join(destination_path, 'birads1.csv'), 'w')
            self.file2 = open(os.path.join(destination_path, 'birads3.csv'), 'w')
            self.file3 = open(os.path.join(destination_path, 'birads4.csv'), 'w')
            self.split_and_write_csv(args[0], args[1], args[2])
            print('file con path generati correttamente')
            self.file1.close()
            self.file2.close()
            self.file3.close()

    def elab_UID_and_machine(self, dicom_file, PG):
        print(PG)
        index = self.find_index(PG)
        if index.size > 0:
            dicom = pydicom.filereader.dcmread(dicom_file, force=True)
            UID = dicom.file_meta[0x002, 0x003].value
            machine = dicom[0x0008, 0x0070].value
            if machine == 'FUJIFILM Corporation':
                proiezione = dicom[0x0018, 0x1400].value
                self.add_element(UID, machine, index, proiezione)
            else:
                laterality = dicom[0x0020, 0x0062].value
                view_position = dicom[0x0018, 0x5101].value
                self.add_element(UID, machine, index, laterality, view_position)
        else:
            print('no index match')

    def find_index(self, PG):
        index = self.birads_file[self.birads_file['PG'] == PG].index.values
        print(f'index  in find_index : {index}')
        return index

    def add_element(self, UID, machine, index, *args):

        args = list(args)
        machine_code = [1 if machine == 'FUJIFILM Corporation' else 0]

        print(f'for: {UID}:')
        print(f'___________________{machine}_______________________')
        print(index)
        for i in index:
            sub_par = [self.birads_file.iloc[i][4]]
            sub_par.extend(args)
            print(f'proiezione at index {i}:\t{self.birads_file.iloc[i][4]}')
            print(f"proiezione d'input:\t{args}")

            if (set(sub_par).issubset(set(self.accepted_string_MLO_RIGHT))):
                print('------------match---------------')
                self.birads_file.iloc[i][5] = str(UID)
                self.birads_file.iloc[i][6] = machine_code

            elif (set(sub_par).issubset(set(self.accepted_string_MLO_LEFT))):
                print('------------match---------------')
                self.birads_file.iloc[i][5] = str(UID)
                self.birads_file.iloc[i][6] = machine_code

            elif (set(sub_par).issubset(set(self.accepted_string_CC_RIGT))):
                print('------------match---------------')
                self.birads_file.iloc[i][5] = str(UID)
                self.birads_file.iloc[i][6] = machine_code

            elif (set(sub_par).issubset(set(self.accepted_string_CC_LEFT))):
                print('------------match---------------')
                self.birads_file.iloc[i][5] = str(UID)
                self.birads_file.iloc[i][6] = machine_code
            else:
                print('NO MATCH')

    def split_and_write_csv(self, first_index=339, second_index=267, third_index=128):

        df3 = self.birads_file[:third_index]
        df2 = self.birads_file[third_index+1:second_index+third_index]
        df1 = self.birads_file[len(self.birads_file) - first_index:]

        for i in range(len(df1)):
            self.file1.write(os.path.join(self.path_dicom_file, str(df1.iloc[i, 0]), str(df1.iloc[i, 5])) + '\n')

        for i in range(len(df2)):
            self.file2.write(os.path.join(self.path_dicom_file, str(df2.iloc[i, 0]), str(df2.iloc[i, 5])) + '\n')

        for i in range(len(df3)):
            self.file3.write(os.path.join(self.path_dicom_file, str(df3.iloc[i, 0]), str(df3.iloc[i, 5])) + '\n')

    def complete_write(self, destination_path):
        self.birads_file.to_csv(os.path.join(destination_path, 'dataset/path/final.csv'), sep=';')
        print('file salvato correttamente')


if __name__ == '__main__':

    print('\n', os.getcwd())
    path_birads_file = "/home/gabrieledimarzo/Scrivania/policlinico/dataset/clean_json"
    path_birads_sum_file = "/home/gabrieledimarzo/Scrivania/policlinico/dataset/file_JsonBirads_sum.csv"
    path_dicom = "/run/user/1001/gvfs/sftp:host=imac-di-lablagrutta.local/Volumes/LAB/DBDefinitivo"
    ex = Extractor(path_dicom_file=path_dicom, path_birads_file=path_birads_file, path_birads_sum_file=path_birads_sum_file)
    ex.start_analisys('/home/gabrieledimarzo/Scrivania/policlinico/dataset/path')
    ex.complete_write('../dataset/path')
