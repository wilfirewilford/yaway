

import serial
from serial.serialutil import SerialException
from multiprocessing.reduction import recv_handle
from _socket import timeout
from __builtin__ import True

class Interface:

    def __init__(self):
        '''(self, portdata="\\.\COM3", baudrate=9600,timeout=1,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS):'''
        ''' portdata="\\.\COM3" or portdata="/dev/ttyUSB0" '''
                
        try:
            self.device = serial.Serial('/dev/ttyUSB0',9600,timeout=2,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)
            print self.device
            self.debug = True
        except SerialException, e:
            print "Error: %s" % e    
            quit()
        
    def get_weight(self):
        data_string=""
        self.device.flushInput()
        ReadMore=True
        New_Line=False
        while ReadMore==True:
            c=None
            for c in self.device.read(1):
                if c == '\n':
                    if New_Line: 
                        ''' This will be after a reset of new_line so should be a complete line '''
                        ReadMore=False  
                        break    
                    else:  
                        ''' Read until you get \n then set newline because you may have started midway '''
                        data_string=""
                        New_Line=True
                else:
                    data_string += "%s" % c
            if c==None :
                    ReadMore=False  
                    return None
        data_string=data_string.strip()
        '''print("data: %s" % data_string)'''
        if data_string.split(',')[0]=="ST":
            settled=True
        else:
            settled=False
            
        weight=data_string.split(',')[2]
        units=weight[-2:]
        weight = weight[1:-2].strip()
        weight = float(weight)
        
        if units=="kg":
            ''' Convert to lb's if user set to kg '''
            weight=weight*2.20462
        return [weight,settled]
    
if __name__ == "__main__":
    print "compiled to bytecode!"
