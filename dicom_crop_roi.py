import pandas as pd
import pydicom as dcm
import numpy as np
import nrrd
import ast
import os
import copy
import matplotlib.pyplot as plt


print(os.getcwd())
birads = input('inserire il numero del birads:')
final_dataset = pd.read_csv(r"/home/gabrieledimarzo/Scrivania/policlinico/dataset/path/final.csv", sep=';', dtype='str')
dicom_path_file = open(f"/home/gabrieledimarzo/Scrivania/policlinico/dataset/path/birads{birads}.csv", 'r')
database_def = '/run/user/1001/gvfs/sftp:host=imac-di-lablagrutta.local/Volumes/LAB/DBDefinitivo'
out_file = open(f'dataset/crop_mask/roi_crop_path{birads}.csv', 'w')

error_CROP_list = []
error_ROI_list = []
monochrome_list = []
count_path = 1
not_square_list = []

for line in dicom_path_file:
    print(f"birads input{birads}, count_path {count_path}")

    split_line = line.split('/')  # split_line[9] = PG, split_line[10] = uid
    split_line[10] = split_line[10][:-1]
    index = final_dataset[final_dataset['UID'] == split_line[10]].index.values
    print(split_line[9:], index, index[0])
    keypoints = ast.literal_eval(final_dataset.iloc[index[0]][3])

    target_PG = os.path.join(r'/home/gabrieledimarzo/Scrivania/policlinico', 'dataset', 'crop_mask', f'crop_mask_birads{birads}', split_line[9])
    if not os.path.exists(target_PG):
        os.mkdir(target_PG)
    # sub dir
    if not os.path.exists(os.path.join(target_PG, split_line[10])):
        os.mkdir(os.path.join(target_PG, split_line[10]))

    dicom = dcm.read_file(line[:-1])
    original_shape = dicom.pixel_array.shape
    for i in range(len(keypoints)):
        not_square_flage = False
        deep_crop = copy.deepcopy(dicom)
        deep_roi = copy.deepcopy(dicom)

        try:
            x = (keypoints[i]['X'] - keypoints[i]['Scala'])
            y = (keypoints[i]['Y'] - keypoints[i]['Scala'])
            delta = keypoints[i]['Scala']*2
            parts = [int(y), int(y+delta), int(x), int(x+delta)]
            if parts[1] > original_shape[0]:
                parts[1] = original_shape[0]
                not_square_flage = True
            if parts[3] > original_shape[1]:
                parts[3] = original_shape[1]-1
                not_square_flage = True
            for j in range(len(parts)):
                if parts[j] < 0:
                    not_square_flage = True
                    parts[j] = 0
            deep_crop.PixelData = deep_crop.pixel_array[parts[0]:parts[1], parts[2]:parts[3]].tobytes()
            deep_crop.Rows = parts[1] - parts[0]
            deep_crop.Columns = parts[3] - parts[2]
            save_name = f'crop_{i}.nrrd'
            nrrd.write(os.path.join(target_PG, split_line[10], save_name), deep_crop.pixel_array)
            out_file.write(os.path.join(target_PG, split_line[10], save_name)+',')#crop_path
            print(os.path.join(target_PG, split_line[10], save_name))

        except ValueError as error:
            print(f'VALUE ERROR: CROP', error)
            error_CROP_list.append(os.path.join(split_line[9],split_line[10])+'\t CROP ERROR')
            # split_line[9] = PG, split_line[10] = uid

        try:
            arr = np.zeros((parts[1]-parts[0], parts[3]-parts[2]),dtype=np.uint16)
            arr.fill(1)
            arr[0, 0] = 0
            deep_roi.PixelData = arr.tobytes()
            deep_roi.Rows = parts[1] - parts[0]
            deep_roi.Columns = parts[3] - parts[2]
            save_name = f'roi_{i}.nrrd'
            nrrd.write(os.path.join(target_PG, split_line[10], save_name), deep_roi.pixel_array)
            out_file.write(os.path.join(target_PG, split_line[10], save_name)+'\n')#roi_path
            print(os.path.join(target_PG, split_line[10], save_name))


        except ValueError as error:
            print(f'VALUE ERROR: ROI', error)
            error_ROI_list.append(os.path.join(split_line[9],split_line[10])+'\t ROI ERROR')

        if not_square_flage:
            not_square_list.append(f'PG:{split_line[9]}, UID:{split_line[10]} ')
    count_path += 1

out_file.close()

error_file = open(f'PG_value_error___{birads}.txt', 'w')
for i in range(len(error_CROP_list)):
    error_file.write(error_CROP_list[i]+ '\n')
error_file.write('\n')
for i in range(len(error_ROI_list)):
    error_file.write(error_ROI_list[i]+ '\n')
error_file.close()
with open(f'not_square_list{birads}.txt', 'a') as file_not_square:
    for i in range(len(not_square_list)):
        file_not_square.write(not_square_list[i]+ '\n')



