
#no tensorflow

from sklearn import datasets
import matplotlib.pyplot as plt
import numpy as np
import csv


can_frames = []
can_ids = []
can_messages = []
can_times = []
with open('can_wire_fake5.csv', newline='') as csvfile:   
    reader = csv.DictReader(csvfile)    
    for row in reader:
        can_frame = row['Info']   
        can_time = row['Time']
        can_frames.append(can_frame)
        can_times.append(can_time)
        temp_id = can_frame[12:15]  
        temp_mess = can_frame[16:]   
        can_ids.append(temp_id)
        can_messages.append(temp_mess)


can_messages = [x.strip(' ') for x in can_messages]

can_ids = [int(x, 16) for x in can_ids]  #convert from hex to dec 

can_times = np.array(can_times)
can_times = can_times.astype(np.float)

#time difference between each message:
#0.000212, 0.000145, 0.000309, 0.000158, 0.000137, 0.000331, 0.000548, 0.001222, 0.000152, 0.001066, 0.005676, 0.000139,
#0.000325, 0.000201, 0.000134, 0.001005, 0.001235


#For DOS, we want to keep track of which indexes of can_times come at irregularly small intervals:

dos_messages = []
for index, time_period in enumerate(can_times):  
    if index > 0:  
        if ((can_times[index] - (can_times[index-1])) * 10**6) < 200:                         
            #print(time_period)  
            temp_dos = time_period   
            dos_messages.append(temp_dos)
        else:            
            temp_dos = 0   #normal data
            dos_messages.append(temp_dos)
    else:
        temp_dos = 0   #normal data
        dos_messages.append(temp_dos)


max_columns = 0
can_messages_list = []
for message in can_messages:
    values = message.split()
    if max_columns < len(values):
        max_columns = len(values)
    can_messages_list.append(values)
# create list of empty column lists
list_columns = []
for i in range(max_columns):
   list_columns.append([])
   
for row_list in can_messages_list:
    for i in range(len(row_list)):
        list_columns[i].append(row_list[i])
    for i in range(len(row_list), max_columns):
        list_columns[i].append('')
#print(list_columns)

can_messages_p1 = list_columns[0]
can_messages_p2 = list_columns[1]
can_messages_p3 = list_columns[2]
can_messages_p4 = list_columns[3]
can_messages_p5 = list_columns[4]
can_messages_p6 = list_columns[5]


for i in range(len(can_messages_p1)):
    can_messages_p1[i] = '' if len(can_messages_p1[i])==0 else int(str(can_messages_p1[i]), 16)
    can_messages_p2[i] = '' if len(can_messages_p2[i])==0 else int(str(can_messages_p2[i]), 16)
    can_messages_p3[i] = '' if len(can_messages_p3[i])==0 else int(str(can_messages_p3[i]), 16)
    can_messages_p4[i] = '' if len(can_messages_p4[i])==0 else int(str(can_messages_p4[i]), 16) 
    can_messages_p5[i] = '' if len(can_messages_p5[i])==0 else int(str(can_messages_p5[i]), 16)  
    can_messages_p6[i] = '' if len(can_messages_p6[i])==0 else int(str(can_messages_p6[i]), 16)



#For fuzzing, we want to keep track of which indexes of can_messages and can_times have strange values.
#Check anomalies in second column of message:

fuzz_data = []
for i in range(len(can_messages_p2)):
    if (can_messages_p2[i] > 10):
        temp_fuzz = can_messages_p2[i]
        fuzz_data.append(temp_fuzz)
    else:
        temp_fuzz = 0
        fuzz_data.append(temp_fuzz)
#print(len(fuzz_data))     

#convert to fractions
for i in range(len(can_ids)):
    can_ids[i] = can_ids[i] / 100

can_ids = np.array(can_ids)


#convert all columns into fractions
for i in range(len(can_messages_p1)):  
    can_messages_p1[i] = '' if len(str(can_messages_p1[i]))==0 else (can_messages_p1[i]) / 100
    can_messages_p2[i] = '' if len(str(can_messages_p2[i]))==0 else (can_messages_p2[i]) / 100
    can_messages_p3[i] = '' if len(str(can_messages_p3[i]))==0 else (can_messages_p3[i]) / 100
    can_messages_p4[i] = '' if len(str(can_messages_p4[i]))==0 else (can_messages_p4[i]) / 100
    can_messages_p5[i] = '' if len(str(can_messages_p5[i]))==0 else (can_messages_p5[i]) / 100
    can_messages_p6[i] = '' if len(str(can_messages_p6[i]))==0 else (can_messages_p6[i]) / 100    



#the four features we will be using are the can times, can ids, can_messages_p1, and can_messages_p2
#in the future, more features or less features can be tested as well

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split


x_temp = np.column_stack((can_messages_p1, can_messages_p2))
print(x_temp)

x_temp2 = []  
x = []  

for newColumn,row in zip(x_temp, can_ids):
    x_temp2.append(np.append(row, newColumn))

    
print(x_temp2)  

for newColumn,row in zip(x_temp2, can_times):
    x.append(np.append(row, newColumn))



#fuzz data = [73, 0, 0,        0, 0,        255,      0, 0, 108, 0,        0, 73, 0,        0, 0, 255,      0, 108]
#dos data =  [0,  0, 0.000357, 0, 0.000824, 0.000961, 0, 0, 0,   0.003214, 0, 0,  0.010095, 0, 0, 0.010755, 0, 0]

y = [1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1]  #1 means attack, 0 means normal
y = np.array(y)

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.20)

# SVM Classifier model
svm_clf = SVC(kernel='rbf', gamma=1, C=100)  #was SVC(kernel='linear', C=1.0), gamma was 0.09
svm_clf.fit(X_train, y_train) # `C` is the penalty parameter of the error term

# Testing and checking the accuracy
from sklearn.metrics import accuracy_score
y_pred = svm_clf.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(accuracy)







