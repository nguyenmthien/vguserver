from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.screenmanager import Screen
import email2
import csv
import database

class SRBL(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass

class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        #kek = rv.data[index]
        if is_selected:
            rv.data[index]['select'] = True
            print("selection changed to {0}".format(rv.data[index]))
        else:
            try:
                rv.data[index]['select'] = False
                print("selection removed for {0}".format(rv.data[index]))
            except:
                pass

class Email(Screen):
    def insert(self, value):
        if len(self.rv.data) == 6:
            self.error_msg.text = "Maximum emails is 6"
        else:
            if value == "":
                self.error_msg.text = "Invalid input"
            else:
                self.rv.data.insert(0, {'text': value})
                self.error_msg.text = ""

    def delete(self):
        for x in reversed(self.rv.data):
            if x['select'] == True:
                self.rv.data.pop(self.rv.data.index(x))
        self.error_msg.text = ""
        self.rv.layout_manager.clear_selection()
    
    def to_csv_email(self, list, file_csv):
        fieldnames = ['Email']
        writer = csv.DictWriter(file_csv, fieldnames=fieldnames)
        writer.writeheader()
        for k in list:
            writer.writerow({'Email': k})

    def to_csv_data(self, file_csv, num):
        fieldnames = ['Time', 'ID', 'Temperature', 'Humidity']
        writer = csv.DictWriter(file_csv, fieldnames=fieldnames)
        writer.writeheader()
        data_list = database.get_therm(num, 'vgu.db')
        for k in data_list:
            writer.writerow({'Time':k[0], 'ID':k[1],
            'Temperature':k[2], 'Humidity':k[3]})

    def send(self, mode, number):
        self.error_msg.text = ""
        select_list = []
        for x in reversed(self.rv.data):
            if x['select'] == True:
                select_list.append(x['text'])

        if number.isdigit():
            with open('result.csv', mode='w', newline='') as csv_file:
                if mode == 'Email':
                    self.to_csv_email(select_list, csv_file)
                else:
                    self.to_csv_data(csv_file, int(number))
            if len(select_list):
                email2.send_email_list(select_list, 'result.csv')
                print(select_list)
            else:
                self.error_msg.text = "Please select email to send"
        else:
            self.error_msg.text = "Invalid number"

        