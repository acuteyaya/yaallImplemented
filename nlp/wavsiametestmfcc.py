import time

from keras.models import Model
from keras.layers import Input, Flatten, Dense, Dropout, Lambda
from keras.optimizers import RMSprop,SGD
from keras import backend as K
import pyaudio
import threading
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader
import wave
import pyttsx3
import queue
import numpy as np
from pydub import AudioSegment
import librosa
from playsound import playsound

wavsize= 4600
engine = pyttsx3.init()
FORMAT = pyaudio.paInt16
stats = ''
path = ''
yastarttag = 1
count=10
num_classes = 4
class Stats:
    def __init__(self):
        self.ui = QUiLoader().load(r"E:\window\tiaoshi\pycharm\ya\GUI\mkf.ui")
        self.ui.pushButton.clicked.connect(self.yastart)
        self.ui.label.setStyleSheet('''
                     QLabel{
                     color:white;
                     font: bold;
                     font-size:30px;}
                ''')
        self.ui.pushButton.setStyleSheet('''
                         QPushButton{
                         color:black;
                         border:1px ridge pink;
                         background-color:

                            qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0.5 #faf0e6, stop: 0.8 #faf0e6,
                                    stop: 0.5 #faf0e6, stop: 1.0 #faf0e6);
                         }
                    ''')
        self.ui.groupBox.setStyleSheet('''
                                 QGroupBox{
                                 color:white;
                                 background-color:
                                    qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                    stop: 0.5 #ffb3e6, stop: 0.8 #faf0e6,
                                    stop: 0.5 #ffb3e6, stop: 1.0 #faf0e6);}  ## “#”号后面为色值！
                                 }
                            ''')
        self.ui.label.setText("请选择路径")

    def yastart(self):
        global yastarttag, path
        path = self.ui.lineEdit.text()  # 写
        self.ui.label.setText("系统正在运行")
        yastarttag = 0


def yaui():
    global stats
    app = QApplication([])
    stats = Stats()
    stats.ui.show()
    app.exec_()
listssj = np.empty([1,wavsize], dtype = np.float64)
def init():
    global listssj
    for i in range(1, num_classes+1):
        for j in range(1, count+1):
            yastr = r'E:\window\tiaoshi\pycharm\ya\nlp\2\\' + str(i) + r"\ya"+str(j)+r".wav"
            y, sr = librosa.load(yastr, sr=140000)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, S=None, n_mfcc=20, dct_type=2, norm='ortho')
            # print(mfcc.shape)
            wav = np.transpose(mfcc).reshape(1, wavsize)
            mx = np.nanmax(wav)
            mn = np.nanmin(wav)
            wav = (wav - mn) / (mx - mn)
            wav = wav.reshape(1, wavsize)
            listssj=np.insert(arr=listssj,obj=listssj.shape[0],values=wav,axis=0)
    listssj = np.delete(listssj, 0, axis=0)
    print(listssj.shape)

def yapre(y1):
    ku = []
    k = 0
    #print(listssj[1, :].reshape(1, wavsize))
    for i in range(1, num_classes + 1):
        ltemp=[]
        for j in range(1, count + 1):
            #print(k)
            p = [y1, listssj[k, :].reshape(1, wavsize)]
            ltemp.append(model.predict(p)[0][0])
            k=k+1
        #ku.append(np.sum(ltemp)-min(ltemp)-max(ltemp))
        #ku.append(np.mean(ltemp))
        ku.append(min(ltemp))
        #ku.append(max(ltemp))
    print(ku)
    if(0):
    #if (min(ku) >= 4):
        yastr = '听不到'
    else:
        c = ku.index(min(ku))
        if (c == 0):
            yastr = '后退'
        elif (c == 1):
            yastr = '前进'
        elif (c == 2):
            yastr = '右转'
        elif (c == 3):
            yastr = '左转'
    return yastr


def yamkf():
    while (yastarttag):
        pass
    print(path)
    model.load_weights(path)
    CHUNK = 100
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 140000
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,  # 采样深度
                    channels=CHANNELS,  # 采样通道
                    rate=RATE,  # 采样率
                    input=True,
                    frames_per_buffer=CHUNK)  # 缓存

    frames = []
    yalen1 = 100
    yalen2 = 1200
    t = queue.Queue(yalen1)  # 如果不设置长度,默认为无限长
    for i in range(0, yalen1):
        data = stream.read(CHUNK)
        t.put(data)
    j = 0
    print("开始缓存录音")
    while (True):
        data = stream.read(CHUNK)
        t.get()
        t.put(data)
        audio_data = np.frombuffer(data, dtype=np.int16)
        temp = np.max(audio_data)
        # print(temp)
        if temp > 2000:
            print("检测到信号")
            q = queue.Queue(yalen2)  # 如果不设置长度,默认为无限长
            for i in range(0, yalen2):
                data = stream.read(CHUNK)
                q.put(data)
            for i in range(0, yalen1):
                frames.append(t.get())

            for i in range(0, yalen2):
                if (i <= yalen2 // 9.5):
                    q.get()
                else:
                    frames.append(q.get())
            j = j + 1
            wf = wave.open("temp.wav", 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            playsound("temp.wav")
            y, sr = librosa.load("temp.wav", sr=140000)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, S=None, n_mfcc=20, dct_type=2, norm='ortho')
            # print(mfcc.shape)
            wav = np.transpose(mfcc).reshape(1, wavsize)
            mx = np.nanmax(wav)
            mn = np.nanmin(wav)
            wav = (wav - mn) / (mx - mn)
            wav = wav.reshape(1, wavsize)
            re  = yapre(wav)
            stats.ui.label.setText("预测结果:" + re + "(" + str(j) + ")")
            engine.say(re)
            engine.runAndWait()
            #engine.endLoop()
            time.sleep(0.1)
            frames = []
            for i in range(0, yalen1):
                data = stream.read(CHUNK,exception_on_overflow=False)
                t.put(data)
            #print("已录音" + str(j))
            if (j % 30 == 0):
                break
        else:
            t.get()
            t.put(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    stats.ui.label.setText("运行完毕")

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

def create_base_network(input_shape):
 input = Input(shape=input_shape)
 x = Dense(600, activation='relu')(input)
 #x = Dropout(0.01)(x)
 x = Dense(600, activation='relu')(x)
 #x = Dropout(0.01)(x)
 x = Dense(300, activation='relu')(x)
 x = Dropout(0.03)(x)
 x = Dense(100, activation='relu')(x)
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

if __name__ == '__main__':
    init()

    input_shape = (wavsize,)
    base_network = create_base_network(input_shape)
    input_a = Input(shape=input_shape)
    input_b = Input(shape=input_shape)
    processed_a = base_network(input_a)
    processed_b = base_network(input_b)
    distance = Lambda(euclidean_distance,
                      output_shape=eucl_dist_output_shape)([processed_a, processed_b])
    model = Model([input_a, input_b], distance)
    sgd = SGD(lr=0.01, momentum=0.9, nesterov=True)
    #rms = RMSprop()  # 优化器
    model.compile(loss=contrastive_loss, optimizer=sgd, metrics=[accuracy])
    model.summary()
    threadLock = threading.Lock()
    threads = []
    thread2 = threading.Thread(target=yaui)
    thread2.start()
    yamkf()
    threads.append(thread2)
    for t in threads:
        t.join()
    print("Exiting")
