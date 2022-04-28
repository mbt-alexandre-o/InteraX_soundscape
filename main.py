import json
import tkinter as tk
import wave
from tkinter import ttk
from threading import Thread
import numpy
import pyaudio
from time import ctime,time
import random


sounds_file = [
    "sounds/ambiance_grotte.wav",
    "sounds/ambiance_nature.wav",
    "sounds/ambiance_plage.wav"
]

random.shuffle(sounds_file)

start_time = time()
start_ctime = str(ctime()).replace(" ","_")
saved_json = {}

def save_json():
    json_object = json.dumps(saved_json, indent = 0)
    with open("results/"+start_ctime+"_InteraX_test.json", "w") as outfile:
        outfile.write(json_object)

CHUNK = 1024

class StringQuestion(ttk.Frame):
    def __init__(self, frame, text,values):
        super().__init__(frame)

        label = ttk.Label(self,text=text)
        label.pack()
        self.answer = ttk.Combobox(self)
        self.answer['values'] = values
        self.answer['state'] = 'readonly'
        self.answer.pack()

    def get(self):
        return self.answer.get()

class IntQuestion(ttk.Frame):
    def __init__(self, frame, text,from_,to,set_ = 0):
        super().__init__(frame)

        label = ttk.Label(self,text=text)
        label.pack()
        self.answer = tk.Spinbox(self,from_=from_,to=to,wrap=True)
        self.answer.delete(0,"end")
        self.answer.insert(0,max(from_,set_))
        self.answer.pack()

    def get(self):
        return self.answer.get()

class Question(ttk.Frame):

    def __init__(self, frame, text,number_row = 2):
        super().__init__(frame)

        label = ttk.Label(self,anchor=tk.E,text=text)
        label.pack()
        self.answer = tk.Text(self,height=number_row)
        self.answer.pack(expand=True,fill='x')

    def get(self):
        return self.answer.get('1.0','end')

class Eva(ttk.Frame):

    def __init__(self, frame, top_text, left_text, right_text,command_ = None,from_ = 0, to_ = 100, set_ = 50):
        super().__init__(frame)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=1)

        top_label = ttk.Label(self,text=top_text,anchor=tk.CENTER)
        top_label.grid(row=0,column=0,sticky=tk.EW,columnspan=3)

        left_label = ttk.Label(self,anchor=tk.W,text=left_text)
        left_label.grid(row=1,column=0,sticky=tk.W)

        right_label = ttk.Label(self,anchor=tk.E,text=right_text)
        right_label.grid(row=1,column=2,sticky=tk.E)

        self.slider = ttk.Scale(self,from_=from_,to=to_,orient='horizontal',command=command_)
        self.slider.set(set_)
        self.slider.grid(row=2,column=0,sticky=tk.EW,columnspan=3)

    def get(self):
        return self.slider.get()

class SoundScapeSurveyFrame(ttk.Frame):

    def __init__(self, app, file):
        super().__init__(app)

        if file == sounds_file[2]:
            next_string = "Next"
        else:
            next_string = "Next soundscape"

        self.app = app
        self.file = file.replace(".wav","")

        self.appreciation = Eva(self,"How pleasant did you find this soundscape ?","Unpleasant","Very pleasant")
        self.appreciation.place(relx=0.2,rely=0.1,relwidth=0.6)

        self.relax = Eva(self,"How relaxing did you find this soundscape?","Not relaxing at all","Very relaxing")
        self.relax.place(relx=0.2,rely=0.2,relwidth=0.6)

        self.ennui = Eva(self,"How interesting did you find this soundscape?","Boring","Very interesting")
        self.ennui.place(relx=0.2,rely=0.3,relwidth=0.6)

        self.question_1 = Question(self,"Could you identify the different sounds composing the soundscape ? If so, could you tell us ?",number_row=5)
        self.question_1.place(relx=0.2,rely=0.4,relwidth=0.6) 

        self.question_2 = Question(self,"Did the soundscape evoked a mental image (projection in a space) ? If so, can you tell us which one?",number_row=5)
        self.question_2.place(relx=0.2,rely=0.5,relwidth=0.6) 

        self.question_3 = Question(self,"We would like to make this soundscape as pleasant and relaxing as possible. Do you have any suggestion to make it happen?",number_row=5)
        self.question_3.place(relx=0.2,rely=0.6,relwidth=0.6) 

        self.next_button = ttk.Button(self,text=next_string,command=self.stop)
        self.next_button.place(relx=0.65,rely=0.85,relwidth=0.3,relheight=0.1) 

    def begin(self):
        self.place(x=0,rely=0,relwidth=1.0,relheight=1.0)

    def stop(self):
        saved_json[self.file+"_ennui"]=self.ennui.get()
        saved_json[self.file+"_relax"]=self.relax.get()
        saved_json[self.file+"_appreciation"]=self.appreciation.get()
        saved_json[self.file+"_diff_sounds"]=self.question_1.get()
        saved_json[self.file+"_comments"]=self.question_2.get()
        saved_json[self.file+"_mental_image"]=self.question_3.get()
        saved_json[self.file+"_survey_end"]=time()-start_time
        save_json()
        self.pack_forget()
        self.app.next_frame()

class InfoFrame(ttk.Frame):

    def __init__(self, app):
        super().__init__(app)

        self.app = app

        label = ttk.Label(self,anchor=tk.CENTER,text="But first, we would like to know some information about you. These are the only personal data that will be stored.")
        label.place(relx = 0.2,rely=0.2,relwidth=0.6,relheight=0.1)

        self.age_question = IntQuestion(self,"What's your age?",0,99,18)
        self.age_question.place(relx = 0.2,rely=0.3,relwidth=0.6,relheight=0.1)

        self.sex_question = StringQuestion(self,"What's your sex?",("Male","Female","Other"))
        self.sex_question.place(relx = 0.2,rely=0.4,relwidth=0.6,relheight=0.1)

        self.next_button = ttk.Button(self,text="Start the first\nSoundscape",command=self.stop)
        self.next_button.place(relx=0.65,rely=0.85,relwidth=0.3,relheight=0.1) 

    def begin(self):
        self.place(x=0,rely=0,relwidth=1.0,relheight=1.0)

    def stop(self):
        saved_json["age"]=self.age_question.get()
        saved_json["sex"]=self.sex_question.get()
        saved_json["end_phase_2"]=time()-start_time
        save_json()
        self.pack_forget()
        self.app.next_frame()

class LastFrame(ttk.Frame):

    def __init__(self, app):
        super().__init__(app)

        self.app = app

        label = ttk.Label(self,anchor=tk.CENTER,text="The test is over.\nThank you again for your help.")
        label.place(relx = 0.2,rely=0.2,relwidth=0.6,relheight=0.6)

        self.stop_button = ttk.Button(self,text="Finish",command=self.stop)
        self.stop_button.place(relx=0.65,rely=0.85,relwidth=0.3,relheight=0.1) 

    def begin(self):
        self.place(x=0,rely=0,relwidth=1.0,relheight=1.0)

    def stop(self):
        saved_json["end"]=time()-start_time
        save_json()
        self.app.destroy()

class FirstFrame(ttk.Frame):

    def __init__(self, app):
        super().__init__(app)

        self.app = app

        label = ttk.Label(self,anchor=tk.CENTER,text="Hello to you and thank you for participating in this test to improve the InteraX project.\nThis test consists of listening to 3 soundscapes and giving your opinion on them.")
        label.place(relx = 0.2,rely=0.2,relwidth=0.6,relheight=0.6)

        self.next_button = ttk.Button(self,text="Next",command=self.stop)
        self.next_button.place(relx=0.65,rely=0.85,relwidth=0.3,relheight=0.1) 

    def begin(self):
        self.place(x=0,rely=0,relwidth=1.0,relheight=1.0)

    def stop(self):
        saved_json["sounds_order"]=sounds_file
        saved_json["end_phase_1"]=time()-start_time
        save_json()
        self.pack_forget()
        self.app.next_frame()

class SoundscapeVolumeFrame(ttk.Frame):

    def __init__(self, app,dir):
        super().__init__(app)

        self.dir = dir
        self.thread = Thread(target=self.play_wav)
        self.stop_thread = False
        self.app = app
        self.volume_1 = 0.0
        self.volume_2 = 0.0
        self.volume_3 = 0.0

        self.volume_scale_1 = Eva(
            self,
            "Please, select the volume of the sound in order to have a good experience.",
            "Low",
            "High",
            to_= 1.0,
            set_= 0.5,
            command_=self.update_volume)
        self.volume_scale_1.place(relx=0.2,rely=0.3,relwidth=0.6)

        self.volume_scale_2 = Eva(
            self,
            "Please, select the volume of the sound in order to have a good experience.",
            "Low",
            "High",
            to_= 1.0,
            set_= 0.5,
            command_=self.update_volume)
        self.volume_scale_2.place(relx=0.2,rely=0.4,relwidth=0.6)

        self.volume_scale_3 = Eva(
            self,
            "Please, select the volume of the sound in order to have a good experience.",
            "Low",
            "High",
            to_= 1.0,
            set_= 0.5,
            command_=self.update_volume)
        self.volume_scale_3.place(relx=0.2,rely=0.5,relwidth=0.6)

        self.stop_button = ttk.Button(self,text="Save volume",command=self.stop)
        self.stop_button.place(relx=0.65,rely=0.85,relwidth=0.3,relheight=0.1)

    def update_volume(self,event):
        self.volume_1 = self.volume_scale_1.get()
        self.volume_2 = self.volume_scale_2.get()
        self.volume_3 = self.volume_scale_3.get()

    def play_wav(self):

        def get_data(wfs):
            data0 = wfs[0].readframes(CHUNK)
            data1 = wfs[1].readframes(CHUNK)
            data2 = wfs[2].readframes(CHUNK)
            decodeddata0 = numpy.fromstring(data0, numpy.int16)
            decodeddata1 = numpy.fromstring(data1, numpy.int16)
            decodeddata2 = numpy.fromstring(data2, numpy.int16)
            newdata = (
                (decodeddata0*self.volume_1)*0.33+(decodeddata1*self.volume_2)*0.33+(decodeddata2*self.volume_3)*0.33
                ).astype(numpy.int16)
            return newdata.tostring()

        wf0 = wave.open(self.dir+"gastric_mod.wav", 'rb')
        wf1 = wave.open(self.dir+"resp_mod.wav", 'rb')
        wf2 = wave.open(self.dir+"cardiac_mod.wav", 'rb')

        wfs = [wf0,wf1,wf2]

        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf0.getsampwidth()),
                    channels=wf0.getnchannels(),
                    rate=wf0.getframerate(),
                    output=True)

        data = get_data(wfs)

        while data != b'' and not self.stop_thread:
            stream.write(data)
            data = get_data(wfs)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def begin(self):
        self.place(x=0,rely=0,relwidth=1.0,relheight=1.0)
        self.thread.start()

    def stop(self):
        if self.thread.is_alive():
            self.stop_thread = True
            self.thread.join()
        #saved_json["volume"]=self.volume
        #saved_json["volume_end"]=time()-start_time
        #save_json()
        self.pack_forget()
        self.app.next_frame()

class VolumeFrame(ttk.Frame):

    def __init__(self, app,file):
        super().__init__(app)

        self.file = file
        self.thread = Thread(target=self.play_wav)
        self.stop_thread = False
        self.app = app
        self.volume = 0.0

        self.volume_scale = Eva(
            self,
            "Please, select the volume of the sound in order to have a good experience.",
            "Low",
            "High",
            to_= 1.0,
            set_= 0.0,
            command_=self.update_volume)
        self.volume_scale.place(relx=0.2,rely=0.3,relwidth=0.6)

        self.stop_button = ttk.Button(self,text="Save volume",command=self.stop)
        self.stop_button.place(relx=0.65,rely=0.85,relwidth=0.3,relheight=0.1)

    def update_volume(self,event):
        self.volume = self.volume_scale.get()

    def play_wav(self):

        def get_data(wf,volume):
            data = wf.readframes(CHUNK)
            decodeddata = numpy.fromstring(data, numpy.int16)
            newdata = (decodeddata*0.5*volume).astype(numpy.int16)
            return newdata.tostring()

        wf = wave.open(self.file, 'rb')

        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

        data = get_data(wf,self.volume)

        while data != b'' and not self.stop_thread:
            stream.write(data)
            data = get_data(wf,self.volume)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def begin(self):
        self.place(x=0,rely=0,relwidth=1.0,relheight=1.0)
        self.thread.start()

    def stop(self):
        if self.thread.is_alive():
            self.stop_thread = True
            self.thread.join()
        saved_json["volume"]=self.volume
        self.app.volume = self.volume
        saved_json["volume_end"]=time()-start_time
        save_json()
        self.pack_forget()
        self.app.next_frame()

class SoundFrame(ttk.Frame):

    def __init__(self, app,file):
        super().__init__(app)

        self.file = file
        self.thread = Thread(target=self.play_wav)
        self.app = app

        label = ttk.Label(self,anchor=tk.CENTER,text="Listen to this sound")
        label.place(relx = 0.4,rely=0.4,relwidth=0.2,relheight=0.2)

    def play_wav(self):

        def get_data(wf):
            data = wf.readframes(CHUNK)
            decodeddata = numpy.fromstring(data, numpy.int16)
            return decodeddata.tostring()

        wf = wave.open(self.file, 'rb')

        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

        data = get_data(wf)

        while data != b'':
            stream.write(data)
            data = get_data(wf)

        stream.stop_stream()
        stream.close()
        p.terminate()
        self.stop()

    def begin(self):
        self.place(x=0,rely=0,relwidth=1.0,relheight=1.0)
        self.thread.start()

    def stop(self):
        saved_json[self.file+"_end"]=time()-start_time
        save_json()
        self.pack_forget()
        self.app.next_frame()

class App(tk.Tk):

    def __init__(self):
        super().__init__()

        # Window
        width= self.winfo_screenwidth() 
        height= self.winfo_screenheight()
        self.geometry(f'{width}x{height}+{0}+{0}')
        self.title("InteraX tests")

        # Style
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Sounds

        self.volume = 0.0

        # Frame

        self.frame_index = 0
        self.frames = [
            FirstFrame(self),
            SoundscapeVolumeFrame(self,dir = "sounds/ambiance_1/"),
            InfoFrame(self),
            SoundFrame(self,file = sounds_file[0]),
            SoundScapeSurveyFrame(self,file = sounds_file[0]),
            SoundFrame(self,file = sounds_file[1]),
            SoundScapeSurveyFrame(self,file = sounds_file[1]),
            SoundFrame(self,file = sounds_file[2]),
            SoundScapeSurveyFrame(self,file = sounds_file[2]),
            LastFrame(self)
        ]
        self.frames[0].begin()

    def next_frame(self):
        self.frame_index+=1
        self.frames[self.frame_index].begin()

if __name__ == "__main__":
    app = App()
    app.mainloop()