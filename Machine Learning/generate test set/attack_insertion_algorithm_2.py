
#Author: Lia Chiflemariam


#Reference:
#https://ieeexplore-ieee-org.mutex.gmu.edu/document/9216166

#---------------
#Fuzzing dataset
#This creates log file for vehicle 2 (candump-09-13-2021_vehicle_2.log)
#---------------

import random


# In[7]:


original_log = []   #can_frames
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
can_messages_p9 = []  #new line

with open("candump-09-13-2021.log", "r") as file:
    log_file = file.readlines()

    
for line in log_file:
    #print(line)
    original_log.append(line)
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
    p9 = line[45:47]
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
    can_messages_p9.append(p9)
    
file.close()
        


# In[8]:


from random import randrange

#fuzzing

fuzz_values = ["AAA", "BBB", "CCC", "DDD"]

#paper indicates 5 seconds of fuzzing, 5 seconds of normal, and 5 seconds of fuzzing again, interval time is 1 ms

for i in range(7280):  #5 sec
    # if 1 ms of attack has passed
    if i % 4 == 0 and i % 8 != 0:  #if i = 4, 12, ...
            for j in range(4):  #j spans 1 ms
                can_ids[1000 + i - j] = fuzz_values[randrange(4)]   #first 1000 message must pass first
"""    
    # if 1 ms of normal has passed
    elif i % 8 == 0    #if i = 8, 16, ...
            for j in range(4):
                can_ids[1000 + i - j] = can_ids[1000 + i - j]
"""                


#total attack messages = 7280 / 2 = 3640

#from 10 to 15 ms:
for i in range(7280):  #5 sec
    # if 1 ms of attack has passed
    if i % 4 == 0 and i % 8 != 0:  #if i = 4, 12, ...
            for j in range(4):  #j spans 1 ms
                can_ids[(1000 + 14560) + i - j] = fuzz_values[randrange(4)]   #first 1000 message must pass first
"""    
    # if 1 ms of normal has passed
    elif i % 8 == 0    #if i = 8, 16, ...
            for j in range(4):
                can_ids[(1000 + 14560) + i - j] = can_ids[1000 + i - j]
"""                


#total attack messages = 7280


# In[9]:


#so far, 7280 attack messages


fuzz_values2 = ["012", "345", "678", "901"]

#paper indicates 5 seconds of fuzzing, 5 seconds of normal, and 5 seconds of fuzzing again, interval time is 1 ms
count = 0
for i in range(7280):  #5 sec
    # if 1 ms of attack has passed
    if i % 4 == 0 and i % 8 != 0:  #if i = 4, 12, ...
            for j in range(4):
                can_ids[100000 + i - j] = fuzz_values2[randrange(4)]   #first 100000 message must pass first
"""    
    # if 1 ms of normal has passed
    elif i % 8 == 0    #if i = 8, 16, ...
            for j in range(4):
                can_ids[1000 + i - j] = can_ids[i - j]
"""                



#from 10 to 15 ms:
for i in range(7280):  #5 sec
    # if 1 ms of attack has passed
    if i % 4 == 0 and i % 8 != 0:  #if i = 4, 12, ...
            for j in range(4):
                can_ids[(100000 + 14560) + i - j] = fuzz_values2[randrange(4)]   #first 100000 message must pass first
"""    
    # if 1 ms of normal has passed
    elif i % 8 == 0    #if i = 8, 16, ...
            for j in range(4):
                can_ids[(1000 + 14560) + i - j] = can_ids[i - j]
"""                


#14560 attack messages total


# In[10]:


random_index = list(range(1,860684)) # list of integers from 1 to 860684
                    
random.shuffle(random_index)


# In[11]:



count = 0
for i in range(430342):  #860684 / 2
    temp = random_index[i]
    
    if count == 0 or count == 32:  #replace id with 0
        can_ids[temp] = "000"
    
    
    elif count == 1:  #repeat id
        can_ids[temp] = can_ids[temp - 1]
    
    
    elif count == 17:  #repeat byte 1
        can_messages_p1[temp] = can_messages_p1[temp - 1]
    
    
    elif count == 4:  #repeat byte 2    
        can_messages_p2[temp] = can_messages_p2[temp - 1]
    
   
    elif count == 15:  #repeat byte 3 
        if can_messages_p4[temp - 1] != '' and can_messages_p4[temp] != '':
            can_messages_p3[temp] = can_messages_p3[temp - 1]   
        
    
    elif count == 6:  #repeat byte 1 and 2
        can_messages_p1[temp] = can_messages_p1[temp - 1]
        can_messages_p2[temp] = can_messages_p2[temp - 1]
        
        
    elif count == 7:  #repeat byte 1 and 3
        if can_messages_p4[temp - 1] != '' and can_messages_p4[temp] != '':
            can_messages_p1[temp] = can_messages_p1[temp - 1]
            can_messages_p3[temp] = can_messages_p3[temp - 1]
    

    elif count == 9:  #fuzzing 1
        can_ids[temp] = "18F"  #from 18E
        can_ids[temp - 1] = "1A5"  #succeeding + 1 (from 1A4)

        
    elif count == 10:  #fuzzing 2
        can_ids[temp] = "092"  #from 091
        can_ids[temp - 1] = "13D"  #succeeding + 1 (from 13C)

        
    elif count == 11:  #fuzzing 3
        can_ids[temp] = "13D"  #from 13C
        can_ids[temp - 1] = "159"

        
    elif count == 12:  #fuzzing 4
        can_ids[temp - 1] = "999"   #to prevent out of bounds error
        can_ids[temp] = "243"

        
    elif count == 13:  #fuzzing 5
        can_ids[temp] = "FFF"
    
    
    elif (count == 14 or count == 18 or count == 35 or count == 46): #shift sequence
        can_ids[temp] = can_ids[temp - 1]
        can_ids[temp - 1] = can_ids[temp - 2]
        can_ids[temp - 2] = can_ids[temp - 3]
        can_ids[temp - 3] = can_ids[temp - 4]
        can_ids[temp - 4] = can_ids[temp - 5]
        can_ids[temp - 5] = can_ids[temp - 6]
        can_ids[temp - 6] = can_ids[temp - 7]
        can_ids[temp - 7] = can_ids[temp - 8]
        
    
    elif (count == 21 or count == 23 or count == 38 or count == 48): #shift sequence
        can_ids[temp] = can_ids[temp - 1]
        can_ids[temp - 1] = can_ids[temp - 2]
        can_ids[temp - 2] = can_ids[temp - 3]
        can_ids[temp - 3] = can_ids[temp - 4]
        can_ids[temp - 4] = can_ids[temp - 5]
        can_ids[temp - 5] = can_ids[temp - 6]
        can_ids[temp - 6] = can_ids[temp - 7]

    
     #'18e', '1a4', '091', '13c', '158', '17c', '191', '19b', '1aa', '1b0', '1d0', '1dc', '1ea', '1ed', '156' is
#most common sequence (repeats back to 18e)
    
    elif count == 3 or count == 5 or count == 49:
        if can_ids[temp] == "18E":
            can_ids[temp] = "091"
        elif can_ids[temp] == "13C":
            can_ids[temp] = "17C"
        elif can_ids[temp] == "191":
            can_ids[temp] = "1AA"
        elif can_ids[temp] == "1B0":
            can_ids[temp] = "1DC"
        elif can_ids[temp] == "1EA":
            can_ids[temp] = "156"
    
    
    elif (count == 18 or count == 19 or count == 30 or count == 44):  #spoofing
        can_ids[temp] = can_ids[temp + 1]
        can_ids[temp + 2] = can_ids[temp + 1]
        can_ids[temp + 3] = can_ids[temp + 1]   
    
    
    
    count += 1
    
    if count == 50:
        count = 0


# In[12]:


#verify that all arrays are still the same length

print(len(can_ids))
print(len(can_times))
print(len(can_messages_p1))
print(len(can_messages_p2))
print(len(can_messages_p3))
print(len(can_messages_p4))
print(len(can_messages_p5))
print(len(can_messages_p6))
print(len(can_messages_p7))
print(len(can_messages_p8))


# In[13]:


can_messages_full = []
for i in range(len(can_messages_p1)):
    temp_full = str(can_messages_p1[i]) + str(can_messages_p2[i]) + str(can_messages_p3[i]) + str(can_messages_p4[i]) + str(can_messages_p5[i]) + str(can_messages_p6[i]) + str(can_messages_p7[i]) + str(can_messages_p8[i]) + str(can_messages_p9[i])
    
    can_messages_full.append(temp_full)
        
#print(can_messages_full[:10])    

new_log = []

for i in range(860684):
    temp_new = ("(" + can_times[i] + ") " + "can0 " + can_ids[i] + "#" + can_messages_full[i])
    new_log.append(temp_new)

#print(new_log[0])    

with open("candump-09-13-2021_vehicle_2.log", 'w') as newfile:    
    for i in range(860684):
        newfile.write(new_log[i])    
        
newfile.close()        


# In[ ]:




