import numpy as np
import matplotlib.pyplot as plt
import random
from keras.models import Model
from keras.layers import Input, Flatten, Dense, Dropout, Lambda
from keras.optimizers import RMSprop
from keras import backend as K
import cv2
import os
import numpy as np
from pydub import AudioSegment
num_classes = 4
epochs = 1000
wavsize= 117300

def euclidean_distance(vects):
 x, y = vects
 sum_square = K.sum(K.square(x - y), axis=1, keepdims=True)
 return K.sqrt(K.maximum(sum_square, K.epsilon()))


def eucl_dist_output_shape(shapes):
 #print(shape)
 shape1, shape2 = shapes
 return (shape1[0], 1)


def contrastive_loss(y_true, y_pred):
 '''Contrastive loss from Hadsell-et-al.'06
 http://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf
 '''
 margin = 1
 sqaure_pred = K.square(y_pred)
 margin_square = K.square(K.maximum(margin - y_pred, 0))
 return K.mean(y_true * sqaure_pred + (1 - y_true) * margin_square)


def create_pairs(x, digit_indices):
 '''Positive and negative pair creation.
 Alternates between positive and negative pairs.
 '''
 pairs = []
 labels = []
 #print(digit_indices)
 n = min([len(digit_indices[d]) for d in range(num_classes)]) - 1
 #print(x[0].shape)
 for d in range(num_classes):
  for i in range(n):
   z1, z2 = digit_indices[d][i], digit_indices[d][i + 1]
   pairs += [[x[z1], x[z2]]]
   print(len(pairs[0][1]))
   inc = random.randrange(1, num_classes)
   dn = (d + inc) % num_classes
   z1, z2 = digit_indices[d][i], digit_indices[dn][i]
   #print(z1, z2, 888888)
   pairs += [[x[z1], x[z2]]]
   labels += [1, 0]
 return np.array(pairs), np.array(labels)


def create_base_network(input_shape):
 '''Base network to be shared (eq. to feature extraction).
 '''
 input = Input(shape=input_shape)
# print(input.shape)
 #x = Flatten()(input)
 x = Dense(1000, activation='relu')(input)
 #x = Dropout(0.1)(x)
 x = Dense(408, activation='relu')(x)
 #x = Dropout(0.1)(x)
 x = Dense(200, activation='relu')(x)
# x = Dropout(0.1)(x)
 x = Dense(100, activation='relu')(x)
 x = Dropout(0.1)(x)
 x = Dense(60, activation='relu')(x)
 return Model(input, x)


def compute_accuracy(y_true, y_pred): # numpy上的操作
 '''Compute classification accuracy with a fixed threshold on distances.
 '''
 pred = y_pred.ravel() < 0.5
 return np.mean(pred == y_true)


def accuracy(y_true, y_pred): # Tensor上的操作
 '''Compute classification accuracy with a fixed threshold on distances.
 '''
 return K.mean(K.equal(y_true, K.cast(y_pred < 0.5, y_true.dtype)))

def plot_train_history(history, train_metrics, val_metrics):
 plt.plot(history.history.get(train_metrics), '-o')
 plt.plot(history.history.get(val_metrics), '-o')
 plt.ylabel(train_metrics)
 plt.xlabel('Epochs')
 plt.legend(['train', 'validation'])
def loadyaima(path_name):
 x_all = np.empty([1,wavsize], dtype = np.float64)
 y_all = np.empty([1], dtype = np.float64)
 k = 0
 for Dir_item in os.listdir(path_name):
  full_path = os.path.abspath(os.path.join(path_name, Dir_item))
  ssj = np.empty([1,wavsize], dtype = np.float64)
  for dir_item in os.listdir(full_path):
   wav = np.frombuffer(AudioSegment.from_mp3(full_path + "\\" + dir_item).raw_data, dtype="int16")
   wav = wav.astype("float64")
   mx = np.nanmax(wav)
   mn = np.nanmin(wav)
   wav = (wav - mn) / (mx - mn)
   #norms = np.linalg.norm(wav, axis=None)
   #wav = wav / norms
   ssj=np.insert(arr=ssj,obj=ssj.shape[0],values=wav,axis=0)
  #print(ssj.shape)
  ssj = np.delete(ssj, 0, axis=0)
  #print(ssj.shape)
  x_all=np.insert(arr=x_all,obj=x_all.shape[0],values=ssj,axis=0)
  y_all=np.insert(arr=y_all,obj=y_all.shape[0],values=np.full(shape=(ssj.shape[0]), fill_value=k),axis=0)
 # print(x_all.shape)
 # print(y_all.shape,666)
 # print("shujuji:"+str(k))
  k = k + 1
 x_all = np.delete(x_all, 0, axis=0)
 y_all = np.delete(y_all, 0, axis=0)
 y_all = y_all.astype('float64')
 return x_all, y_all


if __name__ == '__main__':
 x_all,y_all=loadyaima(r"E:\window\tiaoshi\pycharm\ya\nlp\1")
 print(x_all.shape)
 count = 10
 zb = int(0.8 * count)

 t=random.sample(range(0, count), count)
 x_train = np.empty([1,wavsize], dtype = np.float64)
 y_train = np.empty([1], dtype = np.float64)
 x_test = np.empty([1, wavsize], dtype=np.float64)
 y_test = np.empty([1], dtype=np.float64)
 for j in range(0,count*(num_classes-1)+1,count):
  for i1 in t[0:zb]:
   i = i1+j
   x_train = np.insert(arr=x_train , obj=x_train.shape[0], values=x_all[i,:], axis=0)
   y_train = np.insert(arr=y_train, obj=y_train.shape[0], values=y_all[i], axis=0)
  for i1 in t[zb:count]:
   i = i1 + j
   x_test = np.insert(arr=x_test , obj=x_test.shape[0], values=x_all[i, :], axis=0)
   y_test = np.insert(arr=y_test , obj=y_test.shape[0], values=y_all[i], axis=0)
 x_train = np.delete(x_train, 0, axis=0)
 y_train = np.delete(y_train, 0, axis=0)
 x_test = np.delete(x_test, 0, axis=0)
 y_test = np.delete(y_test, 0, axis=0)
 np.random.seed(116)
 np.random.shuffle(x_train)
 np.random.seed(116)
 np.random.shuffle(y_train)
 np.random.seed(116)
 np.random.shuffle(x_test)
 np.random.seed(116)
 np.random.shuffle(y_test)
 input_shape = (x_train.shape[1],)
 digit_indices = [np.where(y_train == i)[0] for i in range(num_classes)]
 tr_pairs, tr_y = create_pairs(x_train, digit_indices)

 digit_indices = [np.where(y_test == i)[0] for i in range(num_classes)]
 te_pairs, te_y = create_pairs(x_test, digit_indices)
 print(tr_pairs.shape)
 print(tr_y.shape)
 print(te_pairs.shape)
 print(te_y.shape)
 # network definition

 base_network = create_base_network(input_shape)

 input_a = Input(shape=input_shape)
 input_b = Input(shape=input_shape)

 # because we re-use the same instance `base_network`,
 # the weights of the network
 # will be shared across the two branches
 processed_a = base_network(input_a)
 processed_b = base_network(input_b)

 distance = Lambda(euclidean_distance,
      output_shape=eucl_dist_output_shape)([processed_a, processed_b])
 #print([input_a, input_b])
 model = Model([input_a, input_b], distance)
 #keras.utils.plot_model(model,"siamModel.png",show_shapes=True)
 model.summary()
 # train
 rms = RMSprop()#优化器
 model.compile(loss=contrastive_loss, optimizer=rms, metrics=[accuracy])
 #model.load_weights("my_model_weights.h5")
 history=model.fit([tr_pairs[:, 0], tr_pairs[:, 1]], tr_y,
    batch_size=104,
    epochs=200,verbose=1,
    validation_data=([te_pairs[:, 0], te_pairs[:, 1]], te_y))

 model.save_weights('my_model_weights.h5')
 plt.figure(figsize=(8, 4))
 plt.subplot(1, 2, 1)
 plot_train_history(history, 'loss', 'val_loss')
 plt.subplot(1, 2, 2)
 plot_train_history(history, 'accuracy', 'val_accuracy')
 plt.show()


 # compute final accuracy on training and test sets
 y_pred = model.predict([tr_pairs[:, 0], tr_pairs[:, 1]])
 tr_acc = compute_accuracy(tr_y, y_pred)
 y_pred = model.predict([te_pairs[:, 0], te_pairs[:, 1]])
 te_acc = compute_accuracy(te_y, y_pred)

 print('* Accuracy on training set: %0.2f%%' % (100 * tr_acc))
 print('* Accuracy on test set: %0.2f%%' % (100 * te_acc))