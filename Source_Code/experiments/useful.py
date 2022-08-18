import os.path
import numpy as np
import keras.backend as K
from keras import callbacks

np.random.seed(5)

def extract_neg(input_data, targets, val_percentage):
	change_every = 1/val_percentage # add to val indicies every 1/percentage 
	pos = []
	neg = []
	classes = [pos, neg]
	train_long_tensor = []
	val_long_tensor = []
	for t, target in enumerate(targets):
		int_targ = int(target[0])
		classes[int_targ].append(t)

	pos = pos[-len(neg):]
	train_long_tensor = pos + neg
 
	train_data = input_data[train_long_tensor]
	train_targets = targets[train_long_tensor]
	return train_data, train_targets

def unison_shuffled_copies(arrays):

	length = len(arrays[1])
	for x in arrays:
		assert len(x) == length
	p = np.random.permutation(length)
	return tuple([x[p] for x in arrays])

def to_numpy_tensors(x, y):
	x_shape = (len(x), len(x[0]), len(x[0][0]))
	y_shape = (len(y), 1)
	 
	if type(x) is list:
		x = np.array(x)
	if type(y) is list:
		y = np.array(y)
 
	x = x.reshape(x_shape)
	y = y.reshape(y_shape)

	return x, y

def get_mean_and_stdv(dataset):
	means = dataset.mean(0)
	stdvs = dataset.std(0)
	return means, stdvs

def scale_array(dataset, means, stdvs):
	return (dataset - means) / (stdvs + K.epsilon())

def check_filename(originalName):
	count = 1
	exists = True
	fileName = originalName
	while(exists):
		exists = os.path.exists(fileName)
		if exists:
			if "." in originalName:
				fileName = originalName.split(".")
				fileName[0] += "_" + str(count)
				fileName = ".".join(fileName)
			else: 
				fileName = originalName + "_" + str(count)
			count += 1
	return fileName

def truncate_and_tensor(dataX, dataY, length):
	new_X = []
	new_Y = []

	for x in list(range(len(dataX))):
		new_X.append(dataX[x][:length])
		new_Y.append(dataY[x][:length])

	x, y = to_numpy_tensors(new_X, new_Y)
	return x, y


def remove_short(dataX, dataY, length):
	new_X = []
	new_Y = []

	for x in list(range(len(dataX))):
		if len(dataX[x]) >= length:
			new_X.append(dataX[x][:length])
			new_Y.append(dataY[x][:length])

	x, y = to_numpy_tensors(new_X, new_Y)
	return x, y

def remove_short_idx(dataX, dataY, idxs, length):
	new_X = []
	new_Y = []
	new_idxs = []
	
	for x in list(range(len(dataX))):
		if len(dataX[x]) >= length:
			new_X.append(dataX[x][:length])
			new_Y.append(dataY[x][:length])
			new_idxs.append(idxs[x])
	
	x,y = to_numpy_tensors(new_X, new_Y)
	return x, y, np.array(new_idxs)


def timestamped_to_vector(data, vector_col=1, time_start=0, classification_col=1):
	x = []
	y = []
	temp_inputs = []
	temp_outputs = []
	for input_row in data:
		if (input_row[vector_col] == time_start):
			if (temp_inputs != [] and temp_outputs != []):
				x.append(temp_inputs)
				y.append(temp_outputs)
				temp_inputs = []
				temp_outputs = []
		keep = np.array([x for x in range(len(input_row - 1)) if x not in [classification_col, vector_col]])
		temp_inputs.append(input_row[keep])
		assert int(input_row[classification_col]) in [0,1,-1]
		temp_outputs = [int(input_row[classification_col])]

	if (temp_inputs != [] and temp_outputs != []):
		x.append(temp_inputs)
		y.append(temp_outputs)

	x = np.asarray(x)
	y = np.asarray(y)
	return x, y

def array_to_list(arr):
	try:
		return arr.tolist()
	except AttributeError:
		return arr

def to_chunks(l, num_chunks):
	counter = 0
	chunks = []
	n = len(l)//num_chunks
	for i in range(0, n*num_chunks, n):
		chunks.append(l[i:i + n])
	for i in range(n*num_chunks, len(l)):
		chunks[counter].append(l[i])
		counter = (counter + 1) % num_chunks
	return chunks


def merge_two_dicts(x, y):
	z = x.copy()
	z.update(y)
	return z

class ResetStatesCallback(callbacks.Callback):
	def __init__(self):
		self.current_epoch = 0

	def on_batch_begin(self, batch, logs={}):
		self.model.reset_states()



