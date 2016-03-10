'''
Created on Dec 20, 2015

@author: Chris Wilford
'''

'''Coil Weighing Program'''

from Tkinter import Tk, Button,Label,Entry, StringVar,SUNKEN,FLAT,PhotoImage

import psycopg2
from Scale import Interface
from Tkconstants import RIGHT
from time import sleep


class WayWindow:
    def __init__(self, master):
        self.master = master
        master.title("YaWay!")
        
        global jive_conn
        global root3_conn
        global yaway_conn
        global target_weight
        global target_weight_string
        global wtnow
        global stable_weight
        global stable_and_loaded
        global update_display
        global delay_refresh
        
        
        ''' Setup Global Variables '''
        self.status_colour=StringVar()
        self.status_colour.set("white")
        
        self.wtnow=StringVar()
        self.wtnow.set("0000.0 kg")
        
        self.target_weight_string=StringVar()
        self.target_weight_string.set("")
        
        self.stable_weight=float(0.00)
        self.target_weight=float(0.00)
        
        self.stable_and_loaded = False
        self.update_display = True
        self.delay_refresh=False
        
        
        self.coilnumber=StringVar()
        self.coilnumber.set("   <scan>")
    
        ''' CT Logo '''
        self.photo=PhotoImage(file="ct.gif")
        self.ct_logo=Button(master, text="YaWaY!",image=self.photo,height=51,width=76,bd=0,highlightthickness=0,font=("Helvetica", 16, "bold"),relief=FLAT)
        self.ct_logo.place(x=2, y=20)
        self.ct_logo.pack
        
        ''' Realtime Weight Box '''
        self.wt = Entry(master,textvariable=self.wtnow,width=8,font=("Helvetica", 36),fg="black",bg="green",bd=8,highlightbackground="black",highlightthickness=2,relief=FLAT,justify=RIGHT)
        self.wt.place(x=80,y=2)
        self.wt.pack
        
        ''' Quit/Reset Button '''
        self.quitButton = Button(master, text="Quit", command=self.quit_reset,height = 1, width = 9,font=("Helvetica", 16, "bold"))
        self.quitButton.place(x=190, y=175)
        self.quitButton.pack
        
        ''' Status Light ''' 
        self.statusButton = Button(master, text="!", height = 1, width = 2,relief=FLAT,bg="yellow",font=("Helvetica", 30, "bold"))
        self.statusButton.place(x=258, y=82)
        self.statusButton.pack
        
        ''' Status Msg Label '''
        self.the_message=StringVar()
        self.the_message.set("Hello...")
        self.msg_label = Label(master, textvariable=self.the_message, relief=SUNKEN,font=("Courier", 12))
        self.msg_label.place(x=0,y=220)
        self.msg_label.pack
        
        ''' Ser Number Label '''
        self.label = Label(master, text='Ser:', font=("Helvetica", 18),bg="white")
        self.label.place(x=25,y=85)
        self.label.pack
        
        ''' Ser Box '''
        self.JobBox = Entry(master,width=14,font=("Helvetica", 16),fg="dark blue",bg="light grey",highlightbackground="black",highlightthickness=1,relief=FLAT)
        self.JobBox.bind("<Return>",self.JobEntered)
        self.JobBox.place(x=80,y=85)
        self.JobBox.focus_set()
        self.JobBox.pack
        
        ''' Coil Label '''
        self.label2 = Label(master, text='Coil:', font=("Helvetica", 18),bg="white")
        self.label2.place(x=25,y=120)
        self.label2.pack
        
        ''' Target Label '''
        self.Target_Label = Label(master, text='Target:', font=("Helvetica", 16),bg="white")
        self.Target_Label.place(x=8,y=155)
        self.Target_Label.pack
                
        ''' Coil Box '''
        self.CoilBox = Entry(master,textvariable=self.coilnumber,width=14,font=("Helvetica", 16),fg="black",bg="light grey",highlightbackground="black",highlightthickness=1,relief=FLAT)
        self.CoilBox.place(x=80,y=120)
        self.CoilBox.pack
        
        ''' Target Box '''
        self.Target = Entry(master,textvariable=self.target_weight_string,width=10,font=("Helvetica",12),fg="black",bg="light grey",highlightbackground="black",highlightthickness=1,relief=FLAT)
        self.Target.place(x=80,y=155)
        self.Target.pack

        ''' Connect to Jive '''
        try:
            jive_conn = psycopg2.connect("dbname='jive' user='postgres' host='192.168.0.73' password='xxx'")
            
        except psycopg2.DatabaseError, e:
            print "Error Connecting to Jive!"
            print 'Error %s' % e    
            quit()
            
        ''' Connect to Root 3 '''
        try:
            root3_conn = psycopg2.connect("dbname='transformer' user='jiveuser' host='192.168.0.72' password='xxx'")
            
        except psycopg2.DatabaseError, e:
            print "Error Connecting to Root3!"
            print 'Error %s' % e   
            quit()
            
        ''' Connect to YaWaY Table in the Juice Postgres Database '''
        try:
            yaway_conn = psycopg2.connect("dbname='Juice' user='yaway_user' host='192.168.0.72' password='xxx'")
            
        except psycopg2.DatabaseError, e:
            print "Error Connecting to Yaway!"
            print 'Error %s' % e    
            quit()
            
        ''' connect to Scale RS-232 '''
        self.scale_conn = Interface()
        
      
    def yaway(self): 
        
        if self.delay_refresh :
            sleep(5)  
            self.delay_refresh=False
            
        self.JobBox.focus_set()
        wt=self.scale_conn.get_weight() 
        
        '''No RS-232 or Scale OFF!'''
        if wt==None:
            self.signals("RS232_ERR","Error! No Scale Detected!" )
            
        else:
            wt_part=wt[0]
            stable=wt[1]
            wt_string="%6.1f lb" % wt_part
            self.wtnow.set(wt_string) 
 
            if stable:
                self.stable_weight=wt_part
                if wt_part > 1 :
                    self.stable_and_loaded=True
                    self.signals("stable","Scan Coil Barcode")

                else:
                    self.signals("zero")
                    self.stable_and_loaded=False
            else:
                self.stable_and_loaded=False
                self.signals("unstable")
                
            self.master.after(500, self.yaway)
            
                
        
    def JobEntered(self,myevent):
        print "jobeneter"
        if self.update_display :
            if self.stable_and_loaded:
                self.signals("stable")           
                ser_num=self.JobBox.get()
                job_num=self.parse_job(ser_num)
                cur = jive_conn.cursor()
                sql_string='''SELECT number,"coilNumber" FROM view_jobs WHERE number='%s';''' % job_num
                cur.execute(sql_string)
                jive_conn.commit()
                try:
                    sql_result = cur.fetchone()
                
                except psycopg2.DatabaseError, e:
                    print 'Error %s' % e  
                    self.msg(self.master,e)  
                    quit()
            
                if sql_result is not None:
                    (return_job_num,coil_num)=sql_result
                    print "Job: %s , Coil: %s" % (return_job_num,coil_num)
                    self.get_root3_weight(coil_num)
                    self.coilnumber.set(coil_num)
                
                    if self.tolerance_ok():
                        self.store_weight(job_num,ser_num)
                    else:
                        self.signals("ERR", "Out of Tolerance! Re-Scan")
                    
                    '''print "Scaled: %5.1f Root3: %5.1f Tol: %s" % (self.stable_weight,self.target_weight,Tol_OK)'''
                        
                else:
                    msg_string="%s Not Found. Re-Scan!" % job_num
                    self.signals("job_not_found",msg_string)
                
                cur.close() 
                
            else:
                self.signals("ZERO_ERR","Error! Load Scale and Re-Scan")
            
        else:
            self.update_display=True
            self.signals("ERR","Error! Reset Scale To Clear Error!")
            
    def get_root3_weight (self,coil_num):
        cur = root3_conn.cursor()
        sql_string='''SELECT transformer_number, coil_weight FROM r3_weights WHERE transformer_number='%s';''' % coil_num
        cur.execute(sql_string)
        root3_conn.commit()

        try:
            sql_result = cur.fetchone()
            
        except psycopg2.DatabaseError, e:
            print 'Error %s' % e  
            self.msg(self.master,e)  
            cur.close
            quit()
        
        if sql_result is not None:
            (return_coilnum,coil_weight)=sql_result
            self.target_weight = float(coil_weight)
            self.target_weight_string.set("%5.1f lb" % self.target_weight)
            print "Coil: %s, Target Weight: %s lb" % (return_coilnum,self.target_weight)

        else:
            self.signal("job_not_found","Coil#: %s Not Found in Root3!" % coil_num)
        cur.close()
    
    def tolerance_ok(self):
        Target=float(self.target_weight)
        Scaled=float(self.stable_weight)
        OT=((Target - Scaled)/Target)*100
                
        if abs(OT) > 25 :
            return False
        else :   
            return True
        
    def store_weight(self,job_num,serial_num):  
        print "Storing: %s, Ser#: %s" % (job_num,serial_num)
        cur = yaway_conn.cursor()
        winder="NA"
        machine="NA"
        plant="CTP"
        
        sql_string='''INSERT INTO yaway (coil_number, job_number,serial_number,weightkg,winder,machine,plant) VALUES ('%s', '%s', '%s', %5.2f,'%s','%s','%s');''' % (self.coilnumber.get(),job_num,serial_num,self.stable_weight,winder,machine,plant)
        print sql_string
        
        try:
            cur.execute(sql_string)
            
        except psycopg2.DatabaseError, e:
            yaway_conn.rollback()
            if e.pgcode=='23505' :
                self.signals("ERR", "Error! Duplicate Serial Number")
                cur.close
                return
            else:
                print 'Err#: %s' % e.pgcode
                print 'Error %s' % e  
                err_msg="Err: %s" % e
                self.signals("ERR", err_msg)  
                cur.close
                return
        yaway_conn.commit()
        cur.close
        msg_txt="%s Saved! Unload Coil" % serial_num
        self.signals("job_ok", msg_txt)

    def parse_job(self,serial_num):
        job_num=""
        for c in serial_num :
            if c=="-" :
                break
            else:
                job_num += "%s" % c
        return job_num
    
    def quit_reset(self):
        if self.update_display:
            self.master.quit()
        else:
            self.signals("zero")
    
    def signals(self,status_key,msg_text=""):
        ''' Sets up the Colors and Icon Warnings '''
        ''' status_key= zero, unstable, stable, job_ok, job_not_found, RS232_ERR, ZERO_ERR, ERR'''
        
        if status_key=="zero" :
            self.the_message.set("Place Coil on Scale             ")
            self.statusButton.configure(bg="white",text="")
            self.quitButton.configure(text="Quit")
            self.wt.configure(bg="yellow") 
            self.coilnumber.set("  <Load Scale>")
            self.target_weight_string.set("")
            self.JobBox.delete(0, 'end')
            self.update_display=True
        
        
        if self.update_display :
            if status_key=="RS232_ERR" :
                self.the_message.set(msg_text.ljust(32))
                self.statusButton.configure(bg="red",text="X")
                self.wtnow.set("Scale On?")
                self.wt.configure(bg="red") 
                self.coilnumber.set("  <ERROR>")
                self.target_weight_string.set("")
                self.update_display=True
                
            if status_key=="ZERO_ERR" :
                self.the_message.set(msg_text.ljust(32))
                self.statusButton.configure(bg="red",text="X")
                self.wt.configure(bg="red") 
                self.coilnumber.set("  <ERROR>")
                self.target_weight_string.set("")
                self.JobBox.delete(0, 'end')
                self.quitButton.configure(text="Reset")
                self.delay_refresh=True
                print "refresh"
                
            if status_key=="ERR" :
                self.the_message.set(msg_text.ljust(32))
                self.statusButton.configure(bg="red",text="X")
                self.wt.configure(bg="red") 
                self.coilnumber.set("  <ERROR>")
                self.target_weight_string.set("")
                '''self.JobBox.delete(0, 'end')'''
                self.update_display=False
                self.quitButton.configure(text="Reset")
    
            if status_key=="stable" :
                self.the_message.set(msg_text.ljust(32))
                self.statusButton.configure(bg="white",text="")
                self.wt.configure(bg="light green") 
                self.coilnumber.set("   <Scan Coil>")
                self.target_weight_string.set("")
            
            if status_key=="unstable" :
                self.the_message.set(msg_text.ljust(32))
                self.statusButton.configure(bg="orange",text="~")
                self.wt.configure(bg="orange") 
                self.coilnumber.set("   <Un-Stable>")
                self.target_weight_string.set("")
                self.JobBox.delete(0, 'end')
            
            if status_key=="job_ok" :
                self.the_message.set(msg_text.ljust(32))
                self.statusButton.configure(bg="green",text="Ya")
                self.wt.configure(bg="green") 
                self.coilnumber.set(self.coilnumber.get())
                self.target_weight_string.set(self.target_weight_string.get())
                self.update_display=False
            
            if status_key=="job_not_found" :
                self.the_message.set(msg_text.ljust(32))
                self.statusButton.configure(bg="red",text="!") 
                self.coilnumber.set("")
                self.target_weight_string.set("")
                self.JobBox.delete(0, 'end')
                self.update_display=False
                self.quitButton.configure(text="Reset")
   

        self.master.update_idletasks()
        
        
def main():

    root = Tk()
    root.geometry("320x240+0+0")
    root.configure(background='white')
    app = WayWindow(root)
    app.yaway()
    root.mainloop()
    try:
        root.destroy()
    except:
        pass
main()

