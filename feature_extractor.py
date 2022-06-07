from radiomics.featureextractor import RadiomicsFeatureExtractor
import SimpleITK as sitk
import numpy as np
import six

birads = input('birads: ')
input_path = f'/home/gabrieledimarzo/Scrivania/policlinico/dataset/crop_mask/roi_crop_path{birads}.csv'
out_path = f'/home/gabrieledimarzo/Scrivania/policlinico/dataset/crop_mask/result_B{birads}.csv'
file = open(input_path, 'r')
outfile = open(out_path, 'w')
extractor = RadiomicsFeatureExtractor()
first_line_flag = True
error_list = []

for line in file:
    try:
        path = line.split(',')
        if path[0] != 'Image':
            image = path[0]
            mask = path[1][:-1]
            print(path)
            print(image, mask)
            img = sitk.ReadImage(image)
            mk = sitk.ReadImage(mask)

            result = extractor.execute(img, mk, )

            if first_line_flag:
                outfile.write('Image,Mask')
                for key, val in six.iteritems(result):
                    outfile.write(','+key)
                outfile.write('\n')
                first_line_flag = False

            outfile.write(image+','+mask)
            for key, val in six.iteritems(result):
                print(key, val, type(val))
                if type(val) is np.ndarray :
                    outfile.write(','+val.item().__str__())
                if type(val) is dict or type(val) is tuple or type(val) is list:
                    outfile.write(',\"'+val.__str__()+'\"')
                else:
                    outfile.write(','+val.__str__())
            outfile.write('\n')
    except MemoryError as memory_err:
        error_log = image +','+mask+'\n'
        error_list.append(error_log)
        print('memory error occurance ')

file.close()
outfile.close()
