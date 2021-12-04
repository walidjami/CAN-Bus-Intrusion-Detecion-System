# Raspberry Pi 
## Overview:
This project documents how to install, configure, and utilize resources on the Raspberry Pi

---

### CAN Utils Commands:
Install "can-utils":  
```
sudo apt-get install can-utils
```

Enable can0 interface:  
```
sudo /sbin/ip link set can0 up type can bitrate 500000
```

Check for can0 interface:  
```
ifconfig can0
```

Watch can0 interface for CAN feed:  
```
candump can0
```

candump -L can0 > candump-<date>.log  
(Using the "-L" adjust the can message format.)  


Set up vcan0 interface:  
Link: https://python-can.readthedocs.io/en/master/interfaces/socketcan.html  
	
```
sudo modprobe vcan
```

*(Create a vcan network interface with a specific name)  
```
sudo ip link add dev vcan0 type vcan
sudo ip link set vcan0 up
```


Verify vcan0 interface:  
```
ifconfig vcan0
```


Files in this format can be replayed in canplayer using the following commands:  
Link: https://stackoverflow.com/questions/31328302/canplayer-wont-replay-candump-files  
Format: (1436509053.050284) vcan0 17F#C7  
```
canplayer vcan0=can0 -I candump-2021-03-17_002833.log -l i -v
```
or
```
cat candump-2021-03-17_002833.log | canplayer vcan0=can0 -l i -v
```


Create files in canplayer appropriate format:  
Link: https://stackoverflow.com/questions/31328302/canplayer-wont-replay-candump-files  
```
candump -l vcan0
```
or
```
candump -L vcan0 > myfile.log
```

