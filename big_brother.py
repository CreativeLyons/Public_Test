from Queue import LifoQueue
import time
from threading import Timer,Thread,Event
from PySide2.QtWidgets import QApplication
import os,datetime,nuke

qNuke = None

def getMousePos():
   # When the main window doesn' t have focus getting the activeWindow throws
   # and error that we use in our advantage.

   try:
       qNuke = QApplication.activeWindow()
       #qNuke.setWindowTitle('NUKE 7 | QT Window')
       tlw = qNuke.topLevelWidget()
    
       mouse_cursor = tlw.cursor()
       mouse_pos = [mouse_cursor.pos().x(),mouse_cursor.pos().y()]
       return mouse_pos

   except:
       return None



def activity(event,out_q):

    total_time = 0
    old_mouse_pos = [-1,-1]
    time_period = 30
    old_nuke_script = ""

    while not event.wait(time_period):
        try:
            mouse_pos = getMousePos()
            nukescript=nuke.root().name()

            if mouse_pos is not None:
                if not old_mouse_pos == mouse_pos:
                    if not nukescript == old_nuke_script:
                        total_time = 0


                    if not nukescript == "Root":
                        total_time+=time_period
                    print 'TOTAL TIME', total_time
                    

                old_mouse_pos = mouse_pos
                old_nuke_script = nukescript
                out_q.put(total_time)
        except:
            pass


def logger(event,in_q):

    while not event.wait(30):
        h = in_q.get()
        write_file(h)
        in_q.task_done()


def get_root_path():
    return os.path.expanduser("~/.nuke/BigBrother/logs/")


def create_output_folder():

    root_path = get_root_path()
    
    nukescript=nuke.root().name()
    now = datetime.datetime.now()
    date = '%0.2d%0.2d%0.2d' % (now.year,now.month,now.day)
    
    output_path = os.path.join(root_path,date,os.path.basename(nukescript).replace('.','_'))

    if nukescript:
        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        return output_path


def write_file(total_time):

    try:
        folder=create_output_folder()
        pid = os.getpid()
    
        file_path = "%s/%s" % (folder,pid)
    
        f = open(file_path,"w+")
        print file_path
        f.write(str(total_time))
        f.close()
    except:
        pass


def conform_logs(datetime):

    root_path=get_root_path()

    date = '%0.2d%0.2d%0.2d' % (datetime.year,datetime.month,datetime.day)
    date_folder = os.path.join(root_path, date)
    data_dict = {}

    if os.path.isdir(date_folder):

        date_nukescripts = os.listdir(date_folder)

        for nukescript in date_nukescripts:
    
            total_time = 0

            pid_files = os.listdir(os.path.join(date_folder,nukescript))

            for file in pid_files:
                f = open(os.path.join(date_folder,nukescript,file),"r")
                time = f.read()
                f.close()
                total_time+=float(time)

            data_dict[nukescript] = total_time

    return data_dict

def conform_today_logs():
    return conform_logs(datetime.datetime.now())


def print_today_logs():
    print conform_today_logs()

def run():
    stopFlag = Event()
    
    q = LifoQueue(maxsize=1)
    t1 = Thread(target=activity, args=(stopFlag,q,))
    t2 = Thread(target=logger, args=(stopFlag,q,))
    
    t1.start()
    t2.start()



#stopFlag.set()

