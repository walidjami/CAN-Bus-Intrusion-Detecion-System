
#Author: Lia Chiflemariam

import matplotlib.pyplot as plt
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import hinge_loss


#import time
import sys
import joblib





def train(can_ids, can_messages_full, can_times):

    can_ids = [int(x, 16) for x in can_ids]    #convert ids from hex to decimal


    #Create 2D array of can id pairs:
    even_ids = []
    odd_ids = []
    for i in range(len(can_ids)):
        if i % 2 == 0:
            temp_odd = can_ids[i]
            odd_ids.append(temp_odd)
        else:
            temp_even = can_ids[i]
            even_ids.append(temp_even)

    even_odd_ids = np.column_stack((odd_ids, even_ids))  #argument order must be reversed
    #even_odd_ids = np.vstack((odd_ids, even_ids))  #argument order must be reversed
   


    #Extract the sequence of ids and ignore repetitions:
    id_no_repeat = []
    for i in can_ids:
        if i not in id_no_repeat:
            id_no_repeat.append(i)
            
   

    #Create 2D array of message lengths:
    message_lengths_odd = []
    message_lengths_even = []
    for i in range(len(can_messages_full)):
        temp_len = len(can_messages_full[i])
        if i % 2 == 0:
            message_lengths_odd.append(temp_len)
        else:    
            message_lengths_even.append(temp_len)
    message_lengths_both = np.column_stack((message_lengths_odd, message_lengths_even))  #the length of each index is always 2
    
    
    
        
    #Time difference between pairs:
    time_diff = []
    can_times = np.array(can_times)
    can_times = can_times.astype(np.float)
    for i in range(len(can_times)):
        if i % 2 != 0:
            temp_diff = can_times[i] - can_times[i-1]
            time_diff.append(temp_diff)
            
          
        
                
    #Create 2D array of message content pairs:
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
    #even_odd_messages = np.vstack((odd_messages, even_messages))  #argument order must be reversed 
    
    
    
    #there must be an even number of data pairs for this to work
    X_temp = []
    for newColumn,row in zip(message_lengths_both, even_odd_ids):
        X_temp.append(np.append(row, newColumn))
    X_temp2 = []
    for newColumn,row in zip(X_temp, time_diff):
        X_temp2.append(np.append(row, newColumn))
    X = []   #holds all the features
    for newColumn,row in zip(X_temp2, even_odd_messages):
        X.append(np.append(row, newColumn))
        
    can_fakes = []   #stores target values
    for i in range(len(can_ids)):
        if i <=10:
            temp_fake = 0   
        else:
            temp_fake = 1   #all normal data
        can_fakes.append(temp_fake)
            
        
    #Generate target values of pair based on target value of each message:
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

        if i % 2 != 0 and (i != 1 or i != 19 or i != 25):
            if y_odd[j-1] == 1 and y_even[k-1] == 1:
                y_final = 1
                y.append(y_final)
            elif y_odd[j-1] == 0 and y_even[k-1] == 0:
                y_final = 0
                y.append(y_final)
            elif (y_odd[j-1] == 0 and y_even[k-1] == 1) or (y_odd[j-1] == 1 and y_even[k-1] == 0):  
                y_final = 0
                y.append(y_final)

        #add dummy anomalies
        #elif i == 1 or i == 19 or i == 25:
        #    y_final = 0  #attack
        #    y.append(y_final)            

    #print(y) 

    
    #SVM training
    models = []
    accuracies = []
    losses = []
    for i in range(10):  
        X_train, X_test, y_train, y_test = train_test_split(X,y)
        model = SVC(kernel='rbf', gamma = 'scale', C=1)  #may want to find a way to change gamma and C in each iteration
        model.fit(X_train, y_train) 
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        loss = hinge_loss(y_test, y_pred)
        if loss == 2.0:
            loss = 0
        #print(loss)
        models.append(model)
        accuracies.append(accuracy)
        losses.append(loss)
    
    min_loss = min(losses)
    max_acc = max(accuracies)
    min_loss_index = losses.index(min_loss)
    max_acc_index = accuracies.index(max_acc)
    

    chosen_model = models[max_acc_index]  #or min_loss_index, they're the same
        
    losses_sorted = sorted(losses, reverse = True)
    acc_sorted = sorted(accuracies, reverse = False)

    
    for i in range(len(losses)):
        print("Loss:", losses_sorted[i], "Accuracy:", acc_sorted[i]) #printing index is no longer needed
    print("Maximum accuracy:", max_acc)
    print("Minimum loss:", min_loss)
    #print("Indexes:", max_acc_index, min_loss_index)
    print()

    return chosen_model









def evaluation(model_1, model_2, model_3, model_4, model_5):
    #import online model 
    online_model = joblib.load('online_model')

    #average intercepts
    avg_intercept = (model_1.intercept_ + model_2.intercept_ + model_3.intercept_ + model_4.intercept_ + 
                     model_5.intercept_ + online_model.intercept_) / 6

    
    #average the dual coefficients of the support vector in the decision function multiplied by their targets
    avg_dual_coef = []
    #print(model_1.dual_coef_.shape)
    #print(model_2.dual_coef_.shape)
    #print(model_3.dual_coef_.shape)
    #print(model_4.dual_coef_.shape)
    #print(model_5.dual_coef_.shape)

    model1_dual_tp = np.transpose(model_1.dual_coef_)  
    model2_dual_tp = np.transpose(model_2.dual_coef_)
    model3_dual_tp = np.transpose(model_3.dual_coef_)
    model4_dual_tp = np.transpose(model_4.dual_coef_)
    model5_dual_tp = np.transpose(model_5.dual_coef_)
    online_model_tp = np.transpose(online_model.dual_coef_)

    min_dual = min(len(model1_dual_tp), len(model2_dual_tp), len(model3_dual_tp), len(model4_dual_tp), len(model5_dual_tp), len(online_model_tp))
    for i in range(min_dual):   #size of min dual_coef_
        temp_dc = (model_1.dual_coef_[0][i] + model_2.dual_coef_[0][i] + model_3.dual_coef_[0][i] + 
                   model_4.dual_coef_[0][i] + model_5.dual_coef_[0][i] + online_model.dual_coef_[0][i]) / 6
        avg_dual_coef.append(temp_dc)

        
    #average support vectors
    avg_sv = []
    #print(model_1.support_vectors_.shape)
    #print(model_2.support_vectors_.shape)
    #print(model_3.support_vectors_.shape)
    #print(model_4.support_vectors_.shape)
    #print(model_5.support_vectors_.shape)

    model1_sv = model_1.support_vectors_.shape[0]
    model2_sv = model_2.support_vectors_.shape[0]
    model3_sv = model_3.support_vectors_.shape[0]
    model4_sv = model_4.support_vectors_.shape[0]
    model5_sv = model_5.support_vectors_.shape[0]
    online_model_sv = online_model.support_vectors_.shape[0]

    min_sv = min(model1_sv, model2_sv, model3_sv, model4_sv, model5_sv, online_model_sv)
    for i in range(min_sv):
        for j in range(7):
            temp_sv = (model_1.support_vectors_[i][j] + model_2.support_vectors_[i][j] + model_3.support_vectors_[i][j] +
                       model_4.support_vectors_[i][j] + model_5.support_vectors_[i][j] + 
                       online_model.support_vectors_[i][j]) / 6
            
            avg_sv.append(temp_sv)


    #replace values in one of the models with the averaged values
    model_5.intercept_ = avg_intercept
    
    for i in range(min_dual):
        model_5.dual_coef_[0][i] = avg_dual_coef[i]

    h = 0    
    for i in range(min_sv):
        for j in range(7):
            model_5.support_vectors_[i][j] = avg_sv[h]
            h += 1

    
    #export good model
    joblib.dump(model_5, 'offline_model_3')


    
    print()
    print()
    print()
    print("Offline model generated")
    print()
    print()
    print()
    
    










#To clear data from previous buffer:
def clear(can_ids, can_messages_full, can_times):
    del can_ids[:]
    del can_messages_full[:]
    del can_times[:]













#To clear data from previous buffer:
def clear_bytes(can_messages_p1, can_messages_p2, can_messages_p3, can_messages_p4, can_messages_p5, can_messages_p6, can_messages_p7, can_messages_p8):
    del can_messages_p1[:]
    del can_messages_p2[:]
    del can_messages_p3[:]
    del can_messages_p4[:]
    del can_messages_p5[:]
    del can_messages_p6[:] 
    del can_messages_p7[:]
    del can_messages_p8[:]












# -------------------------------
# Start of main
# -------------------------------



print()
print("Reading data...")
print()
print()
print()
print()




can_frames = []   #entire line
can_ids = []
can_messages = []   #message content
can_times = []     #timestamps
can_messages_p1 = []  #byte 1
can_messages_p2 = []  #byte 2
can_messages_p3 = []  #byte 3
can_messages_p4 = []  #byte 4
can_messages_p5 = []  #byte 5 
can_messages_p6 = []  #byte 6
can_messages_p7 = []  #byte 7
can_messages_p8 = []  #byte 8




num_batches = 0  
count = 0
five_rounds = 1
# Command: cat candump-09-13-2021_vehicle_3.log | python -W ignore vehicle_3.py
for line in sys.stdin:
    temp_time = line[1:18]
    temp_id = line[25:28]
    temp_mess = line[29:]
    p1 = line[29:31]
    p2 = line[31:33]
    p3 = line[33:35]
    p4 = line[35:37]
    p5 = line[37:39]
    p6 = line[39:41]
    p7 = line[41:43]
    p8 = line[43:45]
    can_times.append(temp_time)
    can_ids.append(temp_id)
    can_messages.append(temp_mess)
    can_messages_p1.append(p1)
    can_messages_p2.append(p2)
    can_messages_p3.append(p3)
    can_messages_p4.append(p4)
    can_messages_p5.append(p5)
    can_messages_p6.append(p6)
    can_messages_p7.append(p7)
    can_messages_p8.append(p8)
    
    count += 1
    
    if count == 200:   
        print("Buffer full...")
        print()
        
        
        #Format message content:
        
        can_messages = [x.strip(' ') for x in can_messages]
        
        for i in range(len(can_messages_p1)):
            can_messages_p1[i] = '' if len(can_messages_p1[i])==0 or (can_messages_p1[i])=='\n' else int(str(can_messages_p1[i]), 16)
            can_messages_p2[i] = '' if len(can_messages_p2[i])==0 or (can_messages_p2[i])=='\n' else int(str(can_messages_p2[i]), 16)
            can_messages_p3[i] = '' if len(can_messages_p3[i])==0 or (can_messages_p3[i])=='\n' else int(str(can_messages_p3[i]), 16)
            can_messages_p4[i] = '' if len(can_messages_p4[i])==0 or (can_messages_p4[i])=='\n' else int(str(can_messages_p4[i]), 16) 
            can_messages_p5[i] = '' if len(can_messages_p5[i])==0 or (can_messages_p5[i])=='\n' else int(str(can_messages_p5[i]), 16)  
            can_messages_p6[i] = '' if len(can_messages_p6[i])==0 or (can_messages_p6[i])=='\n' else int(str(can_messages_p6[i]), 16)
            can_messages_p7[i] = '' if len(can_messages_p7[i])==0 or (can_messages_p7[i])=='\n' else int(str(can_messages_p7[i]), 16)
            can_messages_p8[i] = '' if len(can_messages_p8[i])==0 or (can_messages_p8[i])=='\n' else int(str(can_messages_p8[i]), 16)
        
        can_messages_full = []
        for i in range(len(can_messages_p1)):
            temp_full = str(can_messages_p1[i]) + str(can_messages_p2[i]) + str(can_messages_p3[i]) + str(can_messages_p4[i]) + str(can_messages_p5[i]) + str(can_messages_p6[i])
            can_messages_full.append(temp_full)
        

        #training
        
        if five_rounds == 1:
            model_1 = train(can_ids, can_messages_full, can_times)   

        elif five_rounds == 2:
            model_2 = train(can_ids, can_messages_full, can_times)   
            
        elif five_rounds == 3:
            model_3 = train(can_ids, can_messages_full, can_times)   

        elif five_rounds == 4:
            model_4 = train(can_ids, can_messages_full, can_times)   
            
        elif five_rounds == 5:
            model_5 = train(can_ids, can_messages_full, can_times)   
            evaluation(model_1, model_2, model_3, model_4, model_5)
            five_rounds = 0   
        
            
        clear(can_ids, can_messages_full, can_times)   #clear data
        clear_bytes(can_messages_p1, can_messages_p2, can_messages_p3, can_messages_p4, can_messages_p5, can_messages_p6, can_messages_p7, can_messages_p8)   #clear data

        num_batches += 1
        print("Number of batches:", num_batches)
        count = 0
        five_rounds += 1





