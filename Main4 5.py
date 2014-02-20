import Tkinter
import ttk

#needed in frame, task menu:
import os

#needed in detail:
import pickle

#parent object calls are statics

#revision test
class Install:
    def __init__(self):
        cf="config.ini"
        if os.path.isfile(cf):
            config=open(cf)
            #TODO: read prefered path & prefs here. unpickle?
            close(cf)
        else:
            path="Tasks"
        if not os.path.exists(path):
            os.mkdir(path)
        Install.TaskPath=path

class TaskDetail:
    """Task data class, which contains task details and self-pickling and unpickling
        methods"""
    #data and pickling method
    def __init__(self):
        self.dummyval="HEYIMHERE"
    def Save(self,path):
        destination=open(path+"\\"+self.name+".bwt",'wb')
        pickle.dump(self,destination,pickle.HIGHEST_PROTOCOL)
        destination.close()
    def Load(self,path,name):
        source=open(path+"\\"+name+".bwt",'rb')
        #not sure this will work... probably need a copy function
        #looks like this should work!
        self=pickle.load(source)
frameheight=35
plateheight=200
class TaskFrame:
    """An individual, visual frame, attached to a canvas type (either Menu or Plate),
        displays data, with expand, sort, and add-to-plate functions, and a link to a
        TaskDetail data object"""
    def __init__(self,canvas,canvastype):
        self.detail=None
        self.file=False
        self.dragging=False
        self.frame=Tkinter.Frame(canvas,height=frameheight,width=3000,relief='sunken')
        #NAME TEXT FIELD
        self.name=Tkinter.Entry(self.frame)
        self.name.bind("<Return>",self.SetName)
        self.name.bind("<FocusOut>",self.SetName)
        self.name.pack(side="left")
        #EXPAND BUTTON
        self.expand=Tkinter.Button(self.frame,text="Expand",command=self.Expand)
        self.expand.pack(side="left")
        #PRIORITY DISPLAY
        self.priority=Tkinter.Label(self.frame,text="1")
        #add explanatory mouseover text
        self.priority.pack(side="left")
        #branch here, based on canvas type
        self.order=Tkinter.Label(self.frame,text="O")
        if canvastype=="PLATE":
            self.order.bind("<ButtonPress-1>",self.StartDrag)
            self.order.bind("<ButtonRelease-1>",self.EndDrag)
            self.order.bind("<B1-Motion>",self.Drag)
        elif canvastype=="MENU":
            self.order.bind("<ButtonPress-1>",self.StartClick)
            self.order.bind("<ButtonRelease-1>",self.AddToPlate)
        self.order.pack(side="left")
        self.frame.pack()
    def StartClick(self,event):
        self.clicking=True
    def AddToPlate(self,event):
        if self.clicking:
            TaskPlate.AddTask().detail=self.detail
            self.clicking=False
    #DRAGGING
    #TODO: add highlighting ability, and position controls
    def StartDrag(self,event):
        self.dragging=True
        self.clickpos=event.y
    def EndDrag(self,event):
        self.dragging=False
        TaskPlate.resort()
    def Drag(self,event):
        if self.dragging:
            TaskPlate.move(self,event.y_root,self.clickpos)
    def SetName(self,evt):
        #if invalid, reject
        name=self.name.get()
        if len(name)<1:
            print "empty"
            return
        oldname=self.detail.name if self.detail else ""
        if name!=oldname:
            if name + ".bwt" not in os.listdir(Install.TaskPath):
                #new name != oldname, because oldname="", file doesn't exist, save
                if len(oldname)==0:
                    print "save"
                    self.Save()
                    return
                #new name !=oldname, but oldname exists, file doesn't exist, rename
                print "rename"
                return
            #file exists, names were different (old is "" if nonexistent)
            else:
                print "error - file already exists"
    def Save(self):
        #called on return from expand
        self.detail=TaskDetail()
        self.detail.Save(Install.TaskPath)
    def Expand(self):
        print "expanded"
class TaskPlate:
    #STATIC#
    @staticmethod
    def __init__(x,y):
        TaskPlate.taskframelist=[]
        TaskPlate.ycursor=0
        frame=Tkinter.Frame(TkInst,width=650,borderwidth=1,relief='sunken')
        scroll=Tkinter.Scrollbar(frame,orient="vertical")
        scroll.pack(fill="y",side="right",expand="false")
        canvas=Tkinter.Canvas(frame,yscrollcommand=scroll.set)
        canvas.pack(side="left",fill="both",expand="true")
        scroll.config(command=canvas.yview)
        frame.place(relx=x,rely=y,anchor='nw')
        TaskPlate.canvas=canvas
        TaskPlate.scroll=scroll
    @staticmethod
    def AddTask():
        taskframe=TaskFrame(TaskPlate.canvas,"PLATE")
        ypos=frameheight*len(TaskPlate.taskframelist)
        taskframe.framehandle=(TaskPlate.canvas.create_window(0,ypos,anchor="nw",window=taskframe.frame))
        if ypos>plateheight:
            TaskPlate.canvas.config(scrollregion=(0,0,300,ypos+frameheight))
        TaskPlate.taskframelist.append(taskframe)
        return taskframe
    @staticmethod
    def move(frame,yroot,clickpos):
        #Top,Bottom=TaskPlate.scroll.get()
        #scrollamt=Top/(Top+Bottom)
        yroot=TaskPlate.canvas.canvasy(yroot)
        y=yroot-TaskPlate.canvas.winfo_rooty()-clickpos
        TaskPlate.canvas.coords(frame.framehandle,0,y)
        newindex=int(y/frameheight)
        oldindex=TaskPlate.taskframelist.index(frame)
        if newindex!=oldindex:
            if newindex<len(TaskPlate.taskframelist):
                TaskPlate.taskframelist.remove(frame)
                TaskPlate.taskframelist.insert(newindex,frame)
                TaskPlate.resort()
                frame.frame.lift()
    @staticmethod
    def resort():
        i=0
        for f in TaskPlate.taskframelist:
            TaskPlate.canvas.coords(f.framehandle,0,i*frameheight)
            i+=1
    #sort by priority
class TaskMenu:
    #STATIC#
    @staticmethod
    def __init__(x,y):
        TaskMenu.taskframelist=[]
        TaskMenu.ycursor=0
        frame=Tkinter.Frame(TkInst,width=650,borderwidth=1,relief='sunken')
        scroll=Tkinter.Scrollbar(frame,orient="vertical")
        scroll.pack(fill="y",side="right",expand="false")
        canvas=Tkinter.Canvas(frame,yscrollcommand=scroll.set)
        canvas.pack(side="left",fill="both",expand="true")
        scroll.config(command=canvas.yview)
        frame.place(relx=x,rely=y,anchor='nw')
        TaskMenu.canvas=canvas
        TaskMenu.LoadTasks()
    @staticmethod
    def LoadTasks():
        #enumerate files in install task folder, open a frame for each:
        files=os.listdir(Install.TaskPath)
        for f in files:
            if f.endswith(".bwt"):
                TaskMenu.LoadTask(Install.TaskPath+"\\"+f)
    @staticmethod
    def LoadTask(filepath):
        taskframe=TaskFrame(TaskMenu.canvas,"MENU")
        ypos=frameheight*len(TaskMenu.taskframelist)
        taskframe.framehandle=(TaskMenu.canvas.create_window(0,ypos,anchor="nw",window=taskframe.frame))
        if ypos>plateheight:
            TaskMenu.canvas.config(scrollregion=(0,0,300,ypos+frameheight))
        TaskMenu.taskframelist.append(taskframe)
class TaskApp:
    def __init__(self):
        Install()
        TaskMenu(0.5,0.2)
        TaskPlate(0,0.2)      
        Tkinter.Button(TkInst,text="Enter Task",command=TaskPlate.AddTask).place(relx=.25,rely=1,anchor='s')
        Tkinter.Button(TkInst,text="Add to Plate").place(relx=0.75,rely=1,anchor='s')
TkInst=Tkinter.Tk()
TkInst.geometry("400x400+200+0")
TaskApp()
TkInst.mainloop()
