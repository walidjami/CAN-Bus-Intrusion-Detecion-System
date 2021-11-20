import matplotlib.pyplot as plt
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
import csv


can_frames = []
can_ids = []
can_messages = []
can_times = []
can_fakes = []
with open('candump-09-13-2021_200_fake.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)    
    for row in reader:
        can_frame = row['Info']   
        can_time = row['Time']
        can_fake = row['Fake']
        can_frames.append(can_frame)
        can_times.append(can_time)
        can_fakes.append(can_fake)
        temp_id = can_frame[12:15]  
        temp_mess = can_frame[16:]   
        can_ids.append(temp_id)
        can_messages.append(temp_mess)
    
can_messages = [x.strip(' ') for x in can_messages]
can_ids = [int(x, 16) for x in can_ids]  
#print(can_ids)


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



even_ids = []
odd_ids = []

for i in range(len(can_ids)):
    if i % 2 == 0:
        temp_odd = can_ids[i]
        odd_ids.append(temp_odd)
    else:
        temp_even = can_ids[i]
        even_ids.append(temp_even)
        

even_odd_ids = np.column_stack((odd_ids, even_ids))  

for i in range(len(can_messages_p1)):
    can_messages_p1[i] = '' if len(can_messages_p1[i])==0 else int(str(can_messages_p1[i]), 16)
    can_messages_p2[i] = '' if len(can_messages_p2[i])==0 else int(str(can_messages_p2[i]), 16)
    can_messages_p3[i] = '' if len(can_messages_p3[i])==0 else int(str(can_messages_p3[i]), 16)
    can_messages_p4[i] = '' if len(can_messages_p4[i])==0 else int(str(can_messages_p4[i]), 16) 
    can_messages_p5[i] = '' if len(can_messages_p5[i])==0 else int(str(can_messages_p5[i]), 16)  
    can_messages_p6[i] = '' if len(can_messages_p6[i])==0 else int(str(can_messages_p6[i]), 16)

can_messages_full = []
for i in range(len(can_messages_p1)):
    temp_full = str(can_messages_p1[i]) + str(can_messages_p2[i]) + str(can_messages_p3[i]) + str(can_messages_p4[i]) + str(can_messages_p5[i]) + str(can_messages_p6[i])
    can_messages_full.append(temp_full)



#get sequence for each id
id_no_repeat = []
for i in can_ids:
    if i not in id_no_repeat:
        id_no_repeat.append(i)
#print(len(id_no_repeat))   #30 different ids



#lengths:
message_lengths_odd = []
message_lengths_even = []
for i in range(len(can_messages_full)):
    temp_len = len(can_messages_full[i])
    if i % 2 == 0:
        message_lengths_odd.append(temp_len)
    else:    
        message_lengths_even.append(temp_len)

message_lengths_both = np.column_stack((message_lengths_odd, message_lengths_even))  #the length of each index is always 2




#time difference

time_diff = []
can_times = np.array(can_times)
can_times = can_times.astype(np.float)
for i in range(len(can_times)):
    if i % 2 != 0:
        temp_diff = can_times[i] - can_times[i-1]
        time_diff.append(temp_diff)




even_messages = []
odd_messages = []

for i in range(len(can_ids)):
    if i % 2 == 0:
        temp_odd = can_messages_full[i]
        odd_messages.append(temp_odd)
    else:
        temp_even = can_messages_full[i]
        even_messages.append(temp_even)
        
even_odd_messages = np.column_stack((odd_messages, even_messages))  #argument order must be reversed




X_temp = []
for newColumn,row in zip(message_lengths_both, even_odd_ids):
    X_temp.append(np.append(row, newColumn))

X_temp2 = []
for newColumn,row in zip(X_temp, time_diff):
    X_temp2.append(np.append(row, newColumn))

X = []
for newColumn,row in zip(X_temp2, even_odd_messages):
    X.append(np.append(row, newColumn))

for i in range(len(can_ids)):
    can_fakes[i] = 0 if can_fakes[i] == 'fake' else 1

y_even = []
y_odd = []
j = 0
k = 0
y = []
for i in range(len(can_fakes)):
    temp_y = can_fakes[i]
    if i % 2 == 0:  #left number
        y_odd.append(temp_y)
        j += 1
    else:   #right number
        y_even.append(temp_y)
        k += 1
    
    if i % 2 != 0:
        if y_odd[j-1] == 1 and y_even[k-1] == 1:
            y_final = 1
            y.append(y_final)
        elif y_odd[j-1] == 0 and y_even[k-1] == 0:
            y_final = 0
            y.append(y_final)
        elif (y_odd[j-1] == 0 and y_even[k-1] == 1) or (y_odd[j-1] == 1 and y_even[k-1] == 0):  
            y_final = 0
            y.append(y_final)




X_train, X_test, y_train, y_test=train_test_split(X,y)

model = SVC(kernel='rbf', gamma = 0.09, C=0.01)  #was SVC(kernel='linear', C=1.0), gamma was 0.09
model.fit(X_train, y_train) # `C` is the penalty parameter of the error term

from sklearn.metrics import accuracy_score
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(accuracy)

import joblib
joblib.dump(model, 'svm_model')






