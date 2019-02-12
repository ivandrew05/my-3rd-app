import os
import time
import threading

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from random import randrange

from pygame import mixer
from mutagen.mp3 import MP3
from ttkthemes import themed_tk as tk

#创建主窗口并设置主题
#root = Tk()
root = tk.ThemedTk()
root.get_themes()    # Returns a list of all themes that can be set
root.set_theme("clearlooks")    # Sets an available theme: "clearlooks", "radiance", "arc", "blue"
root.title("音乐播放器")
root.iconbitmap(r'images/icon.ico')
root.resizable(False,False)
root.configure(background='#efebe7')
mixer.init()    # initializing the mixer

#设置风格
style=ttk.Style()
style.configure('TButton', font=('Microsoft YaHei',11))
style.configure('TLabel', font=('Microsoft YaHei',11))

#创建菜单栏
menubar=Menu(root)
root.config(menu=menubar)

#定义function浏览文件
def browse_file():
    global filename_path
    filename_path=filedialog.askopenfilename()
    add_to_playlist(filename_path)
    
#创建菜单和菜单下items
submenu=Menu(menubar, tearoff=0)
menubar.add_cascade(label="文件", font=('Microsoft YaHei',9), menu=submenu)
submenu.add_command(label="打开", font=('Microsoft YaHei',9), command=browse_file)
submenu.add_command(label="退出", font=('Microsoft YaHei',9), command=root.destroy)

#定义function关于
def about():
    messagebox.showinfo(title="关于音乐播放器", message="这是一款使用Python tkinter编写的音乐播放器, by ivandrew05.")

#创建菜单和菜单下item
submenu=Menu(menubar, tearoff=0)
menubar.add_cascade(label="帮助", font=('Microsoft YaHei',9), menu=submenu)
submenu.add_command(label="关于", font=('Microsoft YaHei',9), command=about)

#创建左下角状态栏
statusbar=ttk.Label(root, text="欢迎来到音乐播放器", relief=SUNKEN, anchor=W)
statusbar.config(font=('Microsoft YaHei',10))
statusbar.pack(side=BOTTOM, fill=X)

#创建左右两个主frames, 左边的主frame包含两个子frames，
#ltopframe包含playlistbox和scrollbar, lbottomframe包含+添加-删除按钮，
#右边的主frame包含三个子frames, topframe包含文件名标签，总时长标签和当前播放时间标签，
#middleframe包含4个主要的按钮，bottomframe包含单曲循环按钮，消音按钮和音量条。
leftframe=ttk.Frame(root)
leftframe.pack(side=LEFT, padx=30)
rightframe=ttk.Frame(root)
rightframe.pack()

ltopframe=ttk.Frame(leftframe)
ltopframe.pack()
lbottomframe=ttk.Frame(leftframe)
lbottomframe.pack(side=LEFT)

topframe=ttk.Frame(rightframe)
topframe.pack()
middleframe=ttk.Frame(rightframe)
middleframe.pack(padx=10, pady=10)
bottomframe=ttk.Frame(rightframe)
bottomframe.pack(padx=10, pady=10)

#创建scrollbar
scrollbar=ttk.Scrollbar(ltopframe, orient=VERTICAL)
scrollbar.pack(side=RIGHT, fill=Y)

#创建playlistbox和playlist
#change listbox width to 24 characters
#给playlistbox添加scrollbar
playlistbox=Listbox(ltopframe, width=24, height=10, yscrollcommand=scrollbar.set)
playlistbox.pack()
playlistbox.config(activestyle=DOTBOX, font=('Microsoft YaHei',10))    #选中playlistbox的item时，四周有点框
scrollbar.config(command=playlistbox.yview)

playlist=[]
#playlist contains the full path and the filename
#playlistbox contains just the filename
#fullpath and filename are required to play the music inside playpause_music load function

#定义function添加到播放列表
def add_to_playlist(filename):
    filename=os.path.basename(filename)
    index=0
    playlistbox.insert(index, filename)
    playlist.insert(index, filename_path)
    index=index+1
    if playlist[0]=='':    #如果playlist中带有'', 移除它并删除playlistbox中对应的item
        playlist.pop(0)
        playlistbox.delete(0)
    
#定义从播放列表删除歌曲
def delete_song():
    selected_song=playlistbox.curselection()
    selected_song=int(selected_song[0])
    playlistbox.delete(selected_song)
    playlist.pop(selected_song)
    
#创建文件名标签，总时长标签和当前播放时间标签
filelabel=ttk.Label(topframe, text="Let's Make Some Noise!")
filelabel.pack(pady=10)

lengthlabel=ttk.Label(topframe, text="总时长 : --:--")
lengthlabel.pack()

currenttimelabel=ttk.Label(topframe, text="已播放 : --:--")
currenttimelabel.pack()

#定义function显示细节，计算总时长，开启线程
def show_details(play_song):
    filelabel["text"]=os.path.basename(play_song)

    file_data=os.path.splitext(play_song)

    if file_data[1]=='.mp3':
        audio=MP3(play_song)
        total_length=audio.info.length
    else:
        a=mixer.Sound(play_song)
        total_length=a.get_length()

    #div - total_length/60,  mod - total_length % 60
    mins, secs =divmod(total_length, 60)
    mins =round(mins)
    secs=round(secs)
    timeformat= "{:02d}:{:02d}".format(mins, secs)
    lengthlabel["text"]="总时长 - "+timeformat
    
    t1=threading.Thread(target=start_count, args=(total_length,))
    t1.start()

#定义function计算当前播放时间
def start_count(t):
    global pause
    current_time=0
    while current_time<=t and mixer.music.get_busy():
        if pause:
            continue
        else:
            mins, secs =divmod(current_time, 60)
            mins =round(mins)
            secs=round(secs)
            timeformat= "{:02d}:{:02d}".format(mins, secs)
            currenttimelabel['text']="已播放 - " + timeformat
            time.sleep(0.1)
            current_time=current_time+0.1

#创建几个global variables
playing=False
pause=False
selected_song_index=0
loop=False
mute=False
running=False
shuffle=False

#定义function播放暂停音乐
def play_pause_music():
    global playing
    global selected_song_index
    if playing: #if playing=True
        global pause
        if pause: #if pause=True
            mixer.music.unpause()
            playpausebutton.configure(image=pausephoto)
            statusbar["text"]="正在播放-"+os.path.basename(playlist[selected_song_index])
            pause=False
        else:  #if pause=False
            mixer.music.pause()
            playpausebutton.configure(image=playphoto)
            statusbar["text"]="已暂停播放-"+os.path.basename(playlist[selected_song_index])
            pause=True
    else:  #if playing=False
        try:
            stop_music()
            time.sleep(0.1)
            selected_song=playlistbox.curselection()
            selected_song_index=int(selected_song[0])
            play_it=playlist[selected_song_index]
            mixer.music.load(play_it)
            mixer.music.play()
            statusbar["text"]="正在播放-"+os.path.basename(play_it)
            show_details(play_it)
            playpausebutton.configure(image=pausephoto)
            playing=True
        except:
            messagebox.showerror(title="无音乐文件", message='''请从左侧选择您想听的音乐，再点击播放。''')

#定义function播放下一首
def play_next():
    global selected_song_index
    global playing
    global pause
    mixer.music.stop()
    time.sleep(0.1)
    a=len(playlist)-1
    if selected_song_index<a:
        selected_song_index=selected_song_index+1
        mixer.music.load(playlist[selected_song_index])
        mixer.music.play()
        statusbar["text"]="正在播放-"+os.path.basename(playlist[selected_song_index])
        show_details(playlist[selected_song_index])
    else:
        mixer.music.load(playlist[0])
        mixer.music.play()
        statusbar["text"]="正在播放-"+os.path.basename(playlist[0])
        show_details(playlist[0])
        selected_song_index=0
    playpausebutton.configure(image=pausephoto)
    playlistbox.selection_clear(0, END)    #清空playlistbox的选择
    playlistbox.selection_set(selected_song_index)    #设置playlistbox的选择
    playlistbox.see(selected_song_index)    #保证选择的item在playlistbox中可见
    playing=True
    pause=False

#定义function播放上一首
def play_previous():
    global selected_song_index
    global playing
    global pause
    mixer.music.stop()
    time.sleep(0.1)
    a=len(playlist)-1
    if selected_song_index==0:
        mixer.music.load(playlist[-1])
        mixer.music.play()
        statusbar["text"]="正在播放-"+os.path.basename(playlist[-1])
        show_details(playlist[-1])
        selected_song_index=a
    else:
        selected_song_index=selected_song_index-1
        mixer.music.load(playlist[selected_song_index])
        mixer.music.play()
        statusbar["text"]="正在播放-"+os.path.basename(playlist[selected_song_index])
        show_details(playlist[selected_song_index])
    playpausebutton.configure(image=pausephoto)
    playlistbox.selection_clear(0, END)    #清空playlistbox的选择
    playlistbox.selection_set(selected_song_index)    #设置playlistbox的选择
    playlistbox.see(selected_song_index)    #保证选择的item在playlistbox中可见
    playing=True
    pause=False
    
#定义function停止播放音乐
def stop_music():
    global playing
    global pause
    mixer.music.stop()
    playpausebutton.configure(image=playphoto)
    statusbar["text"]="已停止播放"
    playing=False
    pause=False

#定义function循环播放列表
def loop_playlist():
    global running
    global playing
    while running:
        if mixer.music.get_busy() or playing==False:
            time.sleep(1.0)
        else:
            play_next()
            
#定义function循环播放音乐
def loop_music():
    global loop
    global running
    if loop==False:
        running=True
        loopbutton.configure(image=looponphoto)
        t2=threading.Thread(target=loop_playlist)
        t2.start()
        loop=True
    else:    # if loop==True
        running=False
        loopbutton.configure(image=loopoffphoto)
        loop=False
        a=threading.enumerate()
        print(a)
        #threading.enumerate() returns a list of all Thread objects currently alive,
        #It excludes terminated threads and threads that have not yet been started.

#定义function随机播放
def random_play():
    global playing
    time.sleep(0.1)
    selected_song=playlistbox.curselection()
    selected_song_index=int(selected_song[0])
    random_song_index=randrange(len(playlist))    #随机从playlist中选出一个item的index
    #while loop确保随机选中的index不是正在播放歌曲的index
    while random_song_index==selected_song_index:
        random_song_index=randrange(len(playlist))
    random_song=playlist[random_song_index]
    mixer.music.load(random_song)
    mixer.music.play()
    playlistbox.selection_clear(0, END)    #清空playlistbox的选择
    playlistbox.selection_set(random_song_index)    #设置playlistbox的选择
    playlistbox.see(random_song_index)    #保证选择的item在playlistbox中可见
    statusbar["text"]="正在播放-"+os.path.basename(random_song)
    show_details(random_song)
    playpausebutton.configure(image=pausephoto)
    playing=True

#定义function随机播放列表
def shuffle_playlist():
    global running
    global playing
    while running:
        if mixer.music.get_busy() or playing==False:
            time.sleep(1.0)
        else:
            random_play()
            
#定义function随机播放音乐
def shuffle_music():
    global shuffle
    global running
    if shuffle==False:
        running=True
        shufflebutton.configure(image=shuffleonphoto)
        t3=threading.Thread(target=shuffle_playlist)
        t3.start()
        shuffle=True
    else:    # if shuffle==True
        running=False
        shufflebutton.configure(image=shuffleoffphoto)
        shuffle=False
        a=threading.enumerate()
        print(a)
        #threading.enumerate() returns a list of all Thread objects currently alive,
        #It excludes terminated threads and threads that have not yet been started.
        
#定义function双击播放
def double_click(event):
    global selected_song_index
    global playing
    global pause
    stop_music()
    time.sleep(0.1)
    selected_song=playlistbox.curselection()
    selected_song_index=int(selected_song[0])
    mixer.music.load(playlist[selected_song_index])
    mixer.music.play()
    statusbar["text"]="正在播放-"+os.path.basename(playlist[selected_song_index])
    show_details(playlist[selected_song_index])
    playpausebutton.configure(image=pausephoto)
    playing=True
    pause=False

#定义function设置音量
def set_vol(val):
    global mute
    volume= float(val)/100
    mixer.music.set_volume(volume)    #mixer set_volume only takes value from 0 to 1
    if volume==0:
        volumebutton.configure(image=volmutephoto)
        mute=True
    elif 0<volume<0.33 or volume==0.33:
        volumebutton.configure(image=volminphoto)
        mute=False
    elif 0.33<volume<0.66 or volume==0.66:
        volumebutton.configure(image=volmidphoto)
        mute=False
    else: # if volume>0.66
        volumebutton.configure(image=volmaxphoto)
        mute=False
        
#定义消音  
def mute_music():
    global mute
    if mute:
        mixer.music.set_volume(0.7)
        volumebutton.configure(image=volmidphoto)
        scale.set(70)
        mute=False
    else:
        mixer.music.set_volume(0)
        volumebutton.configure(image=volmutephoto)
        scale.set(0)
        mute=True

#创建+添加-删除按钮
addbutton=ttk.Button(lbottomframe, text="+ 添加", width=5, command=browse_file)
addbutton.pack(side=LEFT)
delbutton=ttk.Button(lbottomframe, text="- 删除", width=5, command=delete_song)
delbutton.pack(side=LEFT, padx=3)

#创建播放/暂停按钮
playphoto=PhotoImage(file="images/play.png")
pausephoto=PhotoImage(file="images/pause.png")
playpausebutton=ttk.Button(middleframe, image=playphoto, command= play_pause_music)
playpausebutton.grid(row=0, column=1, padx=10)

#创建上一首按钮
playpreviousphoto=PhotoImage(file="images/playprevious.png")
playpreviousbutton=ttk.Button(middleframe, image=playpreviousphoto, command=play_previous)
playpreviousbutton.grid(row=0, column=0, padx=10)

#创建下一首按钮
playnextphoto=PhotoImage(file="images/playnext.png")
playnextbutton=ttk.Button(middleframe, image=playnextphoto, command=play_next)
playnextbutton.grid(row=0, column=2, padx=10)

#创建停止播放按钮
stopphoto=PhotoImage(file="images/stop.png")
stopbutton=ttk.Button(middleframe, image=stopphoto, command=stop_music)
stopbutton.grid(row=0, column=3, padx=10)

#创建列表循环按钮
loopoffphoto=PhotoImage(file="images/loopoff.png")
looponphoto=PhotoImage(file="images/loopon.png")
loopbutton=ttk.Button(bottomframe, image=loopoffphoto, command=loop_music)
loopbutton.grid(row=0, column=0)

#创建随机播放按钮
shuffleoffphoto=PhotoImage(file="images/shuffleoff.png")
shuffleonphoto=PhotoImage(file="images/shuffleon.png")
shufflebutton=ttk.Button(bottomframe, image=shuffleoffphoto, command=shuffle_music)
shufflebutton.grid(row=0, column=1, padx=6)

#创建消音按钮和4个音量图标
volmutephoto=PhotoImage(file="images/volmute.png")
volminphoto=PhotoImage(file="images/volmin.png")
volmidphoto=PhotoImage(file="images/volmid.png")
volmaxphoto=PhotoImage(file="images/volmax.png")
volumebutton=ttk.Button(bottomframe, image=volmidphoto, command=mute_music)
volumebutton.grid(row=0, column=2)

#创建音量条并设置默认音量
scale=ttk.Scale(bottomframe, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale.config(length=130)    #设置scale的长度
scale.set(70)
mixer.music.set_volume(0.7)
scale.grid(row=0, column=3)

#绑定双击playlistbox时，执行double_click
playlistbox.bind('<Double-1>', double_click)

#关闭时摧毁主窗口
def on_closing():
    stop_music()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)

#循环显示主窗口
root.mainloop()
