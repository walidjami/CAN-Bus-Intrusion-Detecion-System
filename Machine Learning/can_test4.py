
# Nonlinear SVM Example
#----------------------------------
#
# This function wll illustrate how to
# implement the gaussian kernel.
# 
#
# Gaussian Kernel:
# K(x1, x2) = exp(-gamma * abs(x1 - x2)^2)

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn import datasets
from tensorflow.python.framework import ops
ops.reset_default_graph()

import csv
sess = tf.Session()


dimension = 3   #3 features 
N = 18  
grid_step = 1  

x_dummy = np.random.random((N, dimension))
y_dummy = np.random.choice(['normal', 'attack'], (N, 1))
matrix = np.hstack((x_dummy, y_dummy))

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

#time difference between each message:
#0.000212, 0.000145, 0.000309, 0.000158, 0.000137, 0.000331, 0.000548, 0.001222, 0.000152, 0.001066, 0.005676, 0.000139,
#0.000325, 0.000201, 0.000134, 0.001005, 0.001235


can_times = np.array(can_times)
can_times = can_times.astype(np.float)



#For DOS, we want to keep track of which indexes of can_times come at irregularly small intervals:

dos_messages = []
for index, time_period in enumerate(can_times):  
    if index > 0:
        if ((can_times[index] - (can_times[index-1])) * 10**6) < 200:                       
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


for i in range(len(can_ids)):
    can_ids[i] = can_ids[i] / 100



#convert all columns into fractions
for i in range(len(can_messages_p1)):  
    can_messages_p1[i] = '' if len(str(can_messages_p1[i]))==0 else (can_messages_p1[i]) / 100
    can_messages_p2[i] = '' if len(str(can_messages_p2[i]))==0 else (can_messages_p2[i]) / 100
    can_messages_p3[i] = '' if len(str(can_messages_p3[i]))==0 else (can_messages_p3[i]) / 100
    can_messages_p4[i] = '' if len(str(can_messages_p4[i]))==0 else (can_messages_p4[i]) / 100
    can_messages_p5[i] = '' if len(str(can_messages_p5[i]))==0 else (can_messages_p5[i]) / 100
    can_messages_p6[i] = '' if len(str(can_messages_p6[i]))==0 else (can_messages_p6[i]) / 100
    


can_messages_p123 = []
#first, add the first three columns:
for i in range(len(can_messages_p1)):  
    temp_123 = can_messages_p1[i] + can_messages_p2[i] + can_messages_p3[i]
    can_messages_p123.append(temp_123)
print(can_messages_p123)    



#fuzz data = [73, 0, 0, 0, 0, 255, 0, 0, 108, 0, 0, 73, 0, 0, 0, 255, 0, 108]
#dos data = [0, 0.000357, 0, 0.000824, 0.000961, 0, 0, 0, 0.003214, 0, 0, 0.010095, 0, 0, 0.010755, 0, 0]

#time for svm:

X0, X1, X2 = can_messages_p123, can_ids, can_times  
X0 = np.array(X0)
X1 = np.array(X1)
X2 = np.array(X2)

x_vals = []
x_temp = np.column_stack((X0, X1))  

for newColumn,row in zip(x_temp, X2):
    x_vals.append(np.append(row, newColumn))    
x_vals = np.array(x_vals)


#dos data =  [0,  0, 0.000357, 0, 0.000824, 0.000961, 0, 0, 0,   0.003214, 0, 0,  0.010095, 0, 0, 0.010755, 0, 0]
#fuzz data = [73, 0, 0,        0, 0,        255,      0, 0, 108, 0,        0, 73, 0,        0, 0, 255,      0, 108]

y_vals = [1, -1, 1, -1, 1, 1, -1, -1, 1, 1, -1, 1, 1, -1, -1, 1, -1, 1]  #1 means attack, -1 means normal
y_vals = np.array(y_vals)

class1_x = [x[0] for i,x in enumerate(x_vals) if y_vals[i]==1]  #could also change to y_vals[i] = 0 or 1 like can_test1
class1_y = [x[1] for i,x in enumerate(x_vals) if y_vals[i]==1]
class2_x = [x[0] for i,x in enumerate(x_vals) if y_vals[i]==-1]
class2_y = [x[1] for i,x in enumerate(x_vals) if y_vals[i]==-1]

batch_size = N 


# Initialize placeholders
x_data = tf.placeholder(shape=[None, dimension], dtype=tf.float32)  #was None, 2
y_target = tf.placeholder(shape=[None, 1], dtype=tf.float32)
prediction_grid = tf.placeholder(shape=[None, dimension], dtype=tf.float32)  #was None, 2

# Create variables for svm
b = tf.Variable(tf.random_normal(shape=[1,batch_size]))

# Gaussian (RBF) kernel
gamma = tf.constant(-12.0)  #was -25
sq_dists = tf.multiply(2., tf.matmul(x_data, tf.transpose(x_data)))
my_kernel = tf.exp(tf.multiply(gamma, tf.abs(sq_dists)))

# Compute SVM Model
first_term = tf.reduce_sum(b)
b_vec_cross = tf.matmul(tf.transpose(b), b)
y_target_cross = tf.matmul(y_target, tf.transpose(y_target))
second_term = tf.reduce_sum(tf.multiply(my_kernel, tf.multiply(b_vec_cross, y_target_cross)))
loss = tf.negative(tf.subtract(first_term, second_term))

# Gaussian (RBF) prediction kernel
# Create a prediction kernel function
rA = tf.reshape(tf.reduce_sum(tf.square(x_data), 1),[-1,1])
rB = tf.reshape(tf.reduce_sum(tf.square(prediction_grid), 1),[-1,1])
pred_sq_dist = tf.add(tf.subtract(rA, tf.multiply(2., tf.matmul(x_data, tf.transpose(prediction_grid)))), tf.transpose(rB))
pred_kernel = tf.exp(tf.multiply(gamma, tf.abs(pred_sq_dist)))

# Declare an accuracy function, which is the percentage of correctly classified data points
prediction_output = tf.matmul(tf.multiply(tf.transpose(y_target),b), pred_kernel)
prediction = tf.sign(prediction_output-tf.reduce_mean(prediction_output))
accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.squeeze(prediction), tf.squeeze(y_target)), tf.float32))

# Declare optimizer
my_opt = tf.train.GradientDescentOptimizer(0.01)
train_step = my_opt.minimize(loss)

# Initialize variables
init = tf.global_variables_initializer()
sess.run(init)

# Training loop
loss_vec = []
batch_accuracy = []
for i in range(1000): #was 300
    rand_index = np.random.choice(len(x_vals), size=batch_size)
    rand_x = x_vals[rand_index]
    rand_y = np.transpose([y_vals[rand_index]])
    sess.run(train_step, feed_dict={x_data: rand_x, y_target: rand_y})

    temp_loss = sess.run(loss, feed_dict={x_data: rand_x, y_target: rand_y})
    loss_vec.append(temp_loss)

    acc_temp = sess.run(accuracy, feed_dict={x_data: rand_x,
                                             y_target: rand_y,
                                             prediction_grid:rand_x})
    batch_accuracy.append(acc_temp)

    if (i+1)%75==0:
        print('Step #' + str(i+1))
        print('Loss = ' + str(temp_loss))


# Create mesh to plot points in
x_vals = x_vals.astype(np.float)
x_ranges = np.vstack((x_vals.min(axis=0) - 1, x_vals.max(axis=0) + 1)).T
aranges = [np.arange(x_range[0], x_range[1], grid_step) for x_range in x_ranges]
print('grid size:', np.power(len(aranges[0]), dimension))
meshes = np.meshgrid(*aranges)
grid_points = np.vstack(tuple([mesh.ravel() for mesh in meshes])).T
print('grid size:', grid_points.shape)
[grid_predictions] = sess.run(prediction, feed_dict={x_data: x_vals,
                                                     y_target: np.transpose([y_vals]),
                                                     prediction_grid: grid_points})


x_min, x_max = x_vals[:, 0].min() - 1, x_vals[:, 0].max() + 1
y_min, y_max = x_vals[:, 1].min() - 1, x_vals[:, 1].max() + 1
xx_arange = np.arange(x_min, x_max, grid_step)
yy_arange = np.arange(y_min, y_max, grid_step)
xx, yy = np.meshgrid(xx_arange,yy_arange)
size = np.power(len(xx), 2)  
size = int(size / 2)  #to remove reshape error
grid_predictions = grid_predictions[0:size].reshape(xx.shape)   



# Plot batch accuracy
plt.plot(batch_accuracy, 'k-', label='Accuracy')
plt.title('Batch Accuracy')
plt.xlabel('Generation')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.show()

# Plot loss over time
plt.plot(loss_vec, 'k-')
plt.title('Loss per Generation')
plt.xlabel('Generation')
plt.ylabel('Loss')
plt.show()





