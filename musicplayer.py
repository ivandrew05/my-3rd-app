from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from pygame import mixer
import os
import time
import threading
from mutagen.mp3 import MP3

#创建主窗口
root = Tk()
root.title("音乐播放器")
root.iconbitmap(r'images/icon.ico')
root.resizable(False,False)
mixer.init()    #initializing the mixer

#创建主菜单
menubar=Menu(root)
root.config(menu=menubar)

#定义function浏览文件
def browse_file():
    global filename_path
    filename_path=filedialog.askopenfilename()
    add_to_playlist(filename_path)
    
#创建子菜单
submenu=Menu(menubar, tearoff=0)
menubar.add_cascade(label="文件", menu=submenu)
submenu.add_command(label="打开", command=browse_file)
submenu.add_command(label="退出", command=root.destroy)

#定义function关于
def about():
    messagebox.showinfo(title="关于音乐播放器", message="这是一款使用Python tkinter编写的音乐播放器, by ivandrew05.")

#创建子菜单下选项 
submenu=Menu(menubar, tearoff=0)
menubar.add_cascade(label="帮助", menu=submenu)
submenu.add_command(label="关于", command=about)

#创建左下角状态栏
statusbar=ttk.Label(root, text="欢迎来到音乐播放器", relief=SUNKEN, anchor=W)
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
playlistbox=Listbox(ltopframe, width=24, yscrollcommand=scrollbar.set)
playlistbox.pack()
playlistbox.config(activestyle=DOTBOX)    #选中playlistbox的item时，四周有点框
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
    
#创建+添加-删除按钮
addbutton=ttk.Button(lbottomframe, text="+ 添加", command=browse_file)
addbutton.pack(side=LEFT)

delbutton=ttk.Button(lbottomframe, text="- 删除", command=delete_song)
delbutton.pack(side=LEFT)

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

#定义function，计算当前播放时间
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
playing=FALSE
pause=FALSE
selectedsong_index=0
repeat=FALSE
mute=FALSE

#定义function播放暂停音乐
def playpause_music():
    global playing
    global selectedsong_index
    global repeat
    repeatbutton.configure(image=repeatphoto)
    repeat=FALSE
    if playing: #if playing=TRUE
        global pause
        if pause: #if pause=TRUE
            mixer.music.unpause()
            playpausebutton.configure(image=pausephoto)
            statusbar["text"]="正在播放-"+os.path.basename(playlist[selectedsong_index])
            pause=FALSE
        else:  #if pause=FALSE
            mixer.music.pause()
            playpausebutton.configure(image=playphoto)
            statusbar["text"]="已暂停播放-"+os.path.basename(playlist[selectedsong_index])
            pause=TRUE
    else:  #if playing=FALSE
        try:
            stop_music()
            time.sleep(0.1)
            selected_song=playlistbox.curselection()
            selectedsong_index=int(selected_song[0])
            play_it=playlist[selectedsong_index]
            mixer.music.load(play_it)
            mixer.music.play()
            statusbar["text"]="正在播放-"+os.path.basename(play_it)
            show_details(play_it)
            playpausebutton.configure(image=pausephoto)
            playing=TRUE
        except:
            messagebox.showerror(title="无音乐文件", message='''请从左侧选择您想听的音乐，再点击播放。''')

#定义function播放上一首
def play_previous():
    global selectedsong_index
    global playing
    global pause
    global repeat
    stop_music()
    time.sleep(0.1)
    a=len(playlist)-1
    if selectedsong_index==0:
        mixer.music.load(playlist[-1])
        mixer.music.play()
        statusbar["text"]="正在播放-"+os.path.basename(playlist[-1])
        show_details(playlist[-1])
        selectedsong_index=a
    elif selectedsong_index<a or selectedsong_index==a:
        selectedsong_index=selectedsong_index-1
        mixer.music.load(playlist[selectedsong_index])
        mixer.music.play()
        statusbar["text"]="正在播放-"+os.path.basename(playlist[selectedsong_index])
        show_details(playlist[selectedsong_index])
    playpausebutton.configure(image=pausephoto)
    repeatbutton.configure(image=repeatphoto)
    playlistbox.selection_clear(0, END)    #清空playlistbox的选择
    playlistbox.selection_set(selectedsong_index)    #设置playlistbox的选择
    playlistbox.see(selectedsong_index)    #保证选择的item在playlistbox中可见
    playing=TRUE
    pause=FALSE
    repeat=FALSE
    
#定义function播放下一首
def play_next():
    global selectedsong_index
    global playing
    global pause
    global repeat
    stop_music()
    time.sleep(0.1)
    a=len(playlist)-1
    if selectedsong_index<a:
        selectedsong_index=selectedsong_index+1
        mixer.music.load(playlist[selectedsong_index])
        mixer.music.play()
        statusbar["text"]="正在播放-"+os.path.basename(playlist[selectedsong_index])
        show_details(playlist[selectedsong_index])
    elif selectedsong_index==a:
        mixer.music.load(playlist[0])
        mixer.music.play()
        statusbar["text"]="正在播放-"+os.path.basename(playlist[0])
        show_details(playlist[0])
        selectedsong_index=0
    playpausebutton.configure(image=pausephoto)
    repeatbutton.configure(image=repeatphoto)
    playlistbox.selection_clear(0, END)    #清空playlistbox的选择
    playlistbox.selection_set(selectedsong_index)    #设置playlistbox的选择
    playlistbox.see(selectedsong_index)    #保证选择的item在playlistbox中可见
    playing=TRUE
    pause=FALSE
    repeat=FALSE

#定义function停止播放音乐
def stop_music():
    global playing
    global pause
    global repeat
    mixer.music.stop()
    playpausebutton.configure(image=playphoto)
    repeatbutton.configure(image=repeatphoto)
    statusbar["text"]="已停止播放"
    playing=FALSE
    pause=FALSE
    repeat=FALSE

#定义function重新播放音乐(并未使用)
def replay_music():
    global selectedsong_index
    global playing
    global pause
    global repeat
    stop_music()
    time.sleep(0.1)
    selected_song=playlistbox.curselection()
    selectedsong_index=int(selected_song[0])
    mixer.music.load(playlist[selectedsong_index])
    mixer.music.play()
    statusbar["text"]="正在播放-"+os.path.basename(playlist[selectedsong_index])
    show_details(playlist[selectedsong_index])
    playpausebutton.configure(image=pausephoto)
    repeatbutton.configure(image=repeatphoto)
    playing=TRUE
    pause=FALSE
    repeat=FALSE

#定义function单曲循环播放
def repeat_music():
    global selectedsong_index
    global playing
    global pause
    global repeat
    if repeat:    # if repeat=TRUE
        stop_music()
        time.sleep(0.1)
        selected_song=playlistbox.curselection()
        selectedsong_index=int(selected_song[0])
        mixer.music.load(playlist[selectedsong_index])
        mixer.music.play()
        statusbar["text"]="正在播放-"+os.path.basename(playlist[selectedsong_index])
        show_details(playlist[selectedsong_index])
        playpausebutton.configure(image=pausephoto)
        repeatbutton.configure(image=repeatphoto)
        playing=TRUE
        pause=FALSE
        repeat=FALSE
    else:    # if repeat=FALSE
        stop_music()
        time.sleep(0.1)
        selected_song=playlistbox.curselection()
        selectedsong_index=int(selected_song[0])
        mixer.music.load(playlist[selectedsong_index])
        mixer.music.play(-1)    #播放无限次
        statusbar["text"]="正在播放-"+os.path.basename(playlist[selectedsong_index])
        show_details(playlist[selectedsong_index])
        playpausebutton.configure(image=pausephoto)
        repeatbutton.configure(image=repeatonphoto)
        playing=TRUE
        pause=FALSE
        repeat=TRUE
        
#定义function双击播放
def double_click(event):
    global selectedsong_index
    global playing
    global pause
    global repeat
    stop_music()
    time.sleep(0.1)
    selected_song=playlistbox.curselection()
    selectedsong_index=int(selected_song[0])
    mixer.music.load(playlist[selectedsong_index])
    mixer.music.play()
    statusbar["text"]="正在播放-"+os.path.basename(playlist[selectedsong_index])
    show_details(playlist[selectedsong_index])
    playpausebutton.configure(image=pausephoto)
    repeatbutton.configure(image=repeatphoto)
    playing=TRUE
    pause=FALSE
    repeat=FALSE

#定义function设置音量
def set_vol(val):
    global mute
    volume= float(val)/100
    mixer.music.set_volume(volume)    #mixer set_volume only takes value from 0 to 1
    if volume==0:
        volumebutton.configure(image=volmutephoto)
        mute=TRUE
    elif 0<volume<0.33 or volume==0.33:
        volumebutton.configure(image=volminphoto)
        mute=FALSE
    elif 0.33<volume<0.66 or volume==0.66:
        volumebutton.configure(image=volmidphoto)
        mute=FALSE
    else: # if volume>0.66
        volumebutton.configure(image=volmaxphoto)
        mute=FALSE
        
#定义消音  
def mute_music():
    global mute
    if mute:
        mixer.music.set_volume(0.7)
        volumebutton.configure(image=volmidphoto)
        scale.set(70)
        mute=FALSE
    else:
        mixer.music.set_volume(0)
        volumebutton.configure(image=volmutephoto)
        scale.set(0)
        mute=TRUE

#创建播放/暂停按钮
playphoto=PhotoImage(file="images/play.png")
pausephoto=PhotoImage(file="images/pause.png")
playpausebutton=ttk.Button(middleframe, image=playphoto, command= playpause_music)
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

#创建重新播放按钮(并未使用)
replayphoto=PhotoImage(file="images/replay.png")
replaybutton=ttk.Button(middleframe, image=replayphoto, command=replay_music)
#replaybutton.grid(row=0, column=4, padx=10)

#创建单曲循环按钮
repeatphoto=PhotoImage(file="images/repeat.png")
repeatonphoto=PhotoImage(file="images/repeaton.png")
repeatbutton=ttk.Button(bottomframe, image=repeatphoto, command=repeat_music)
repeatbutton.grid(row=0, column=0, padx=10)

#创建消音按钮和4个音量图标
volmutephoto=PhotoImage(file="images/volmute.png")
volminphoto=PhotoImage(file="images/volmin.png")
volmidphoto=PhotoImage(file="images/volmid.png")
volmaxphoto=PhotoImage(file="images/volmax.png")
volumebutton=ttk.Button(bottomframe, image=volmidphoto, command=mute_music)
volumebutton.grid(row=0, column=1)

#创建音量条并设置默认音量
scale=ttk.Scale(bottomframe, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale.set(70)
mixer.music.set_volume(0.7)
scale.grid(row=0, column=2)

#绑定双击playlistbox时，执行double_click
playlistbox.bind('<Double-1>', double_click)

#关闭时摧毁主窗口
def on_closing():
    stop_music()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)

#循环显示主窗口
root.mainloop()
