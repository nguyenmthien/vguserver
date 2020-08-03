#!/usr/bin/env python3
# *_* coding: utf-8 *_*

import multiprocessing
import blynklibrary as blynklib
import WidgetLCD
import database

READ_PRINT_MSG = "[READ_VIRTUAL_PIN_EVENT] Pin: V{}"

class BlynkClient(object):
    def __init__ (self,
                  tcp_queue:multiprocessing.Queue,
                  authentication_key:str,
                  database_name):
        self.tcp_queue = tcp_queue
        self.authentication_key = authentication_key
        self.database_name = database_name
        
        self.blynk = blynklib.Blynk(self.authentication_key,
                                    server='127.0.0.1',
                                    port=8080)
        self.lcd = WidgetLCD.WidgetLCD(self.blynk, 0)
        
        self.temp = database.fetchnewest(self.database_name,'therm')[2]
        self.humid = database.fetchnewest(self.database_name,'therm')[3]
        
        self.threshold_temp = 30
        self.threshold_humid = 80
        
        self.virtual_pin_handler()
    
    def virtual_pin_handler(self):
        @self.blynk.handle_event('write V7')
        def write_virtual_pin_handler(pin, value):
            print(READ_PRINT_MSG.format(pin))
            #global threshold_temp
            self.threshold_temp = float(value[0])

        @self.blynk.handle_event('write V8')
        def write_virtual_pin_handler(pin, value):
            print(READ_PRINT_MSG.format(pin))
            #global threshold_humid
            self.threshold_humid = float(value[0])

        @self.blynk.handle_event('read V1')
        def read_virtual_pin_handler(pin):
            #global temp, threshold_temp
            self.temp = database.fetchnewest(self.database_name,'therm')[2]
            print(READ_PRINT_MSG.format(pin))
            self.blynk.virtual_write(pin, self.temp)
            
            if (self.temp < self.threshold_temp):
                self.lcd.clear()
                self.lcd.printlcd(0, 0, "Temp: OK")
                #print("Temp: Ok")
            else:
                self.lcd.clear()
                self.lcd.printlcd(0, 0, "Temp: Warning")
                self.blynk.notify('Temp: Warning')

        @self.blynk.handle_event('read V2')
        def read_virtual_pin_handler(pin):
            #global humid, threshold_humid
            self.humid = database.fetchnewest(self.database_name,'therm')[3]
            print(READ_PRINT_MSG.format(pin))
            self.blynk.virtual_write(pin, self.humid)

            if (self.humid < self.threshold_humid):
                self.lcd.printlcd(0, 1, "Humid: OK")
            else:
                self.lcd.printlcd(0, 1, "Humid: Warning")
                self.blynk.notify('Humid: Warning')

        #Preset1
        @self.blynk.handle_event('write V3')
        def write_virtual_pin_handler(pin, value):
            if int(value[0]) == 1:
                print(1)
                self.tcp_queue.put(["AC","11"])

        #Preset2
        @self.blynk.handle_event('write V4')
        def write_virtual_pin_handler(pin, value):
            if int(value[0]) == 1:
                print(2)
                self.tcp_queue.put(["AC","21"])

        #Preset3
        @self.blynk.handle_event('write V5')
        def write_virtual_pin_handler(pin, value):
            if int(value[0]) == 1:
                print(3)
                self.tcp_queue.put(["AC","31"])

        #Preset4
        @self.blynk.handle_event('write V6')
        def write_virtual_pin_handler(pin, value):
            if int(value[0]) == 1:
                print(4)
                self.tcp_queue.put(["AC","41"])
                
    def main(self):
        while True:
            self.blynk.run()