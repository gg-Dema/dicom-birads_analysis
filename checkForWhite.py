from matplotlib.widgets import Button
import matplotlib.pyplot as plt
import nrrd

class ButtonFunction:
	def __init__(self):
		self.good = []
		self.white = []

	def set_line(self, line):
		self.line = line

	def save(self, event):
		self.good.append(self.line)
		plt.close()

	def not_save(self, event):
		self.white.append(self.line)
		plt.close()

file_list = open('dataset/crop_mask/crop_birads3_supervisonato/good_file_list.csv', 'r')
callback = ButtonFunction()

for line in file_list:
	roi, crop = line.split(',')
	roi_parts = roi.split('/')
	sub_path = '\\'.join(roi_parts)
	print(sub_path)

	callback.set_line(line)
	img, header = nrrd.read(sub_path)
	plt.imshow(img, cmap=plt.cm.bone)
	ax_save_path = plt.axes([0.53, 0.05, 0.1, 0.075])
	ax_white = plt.axes([0.64, 0.05, 0.1, 0.075])

	button_save = Button(ax_save_path, 'SAVE')
	button_save.on_clicked(callback.save)

	button_maybe = Button(ax_white, 'WHITE')
	button_maybe.on_clicked(callback.not_save)

	plt.show()

good = open("dataset/crop_mask/crop_birads3_supervisonato/good_file_list_2.csv", 'w')
for item in callback.good:
	good.write(item)
good.close()

white = open("dataset/crop_mask/crop_birads3_supervisonato/white.csv", 'w')
for item in callback.white:
	white.write(item)
white.close()
