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
    global total_length
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
    global current_time
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
mute=False
looping=False
shuffling=False
repeating=False
running1=False
running2=False

#定义function播放暂停音乐
def play_pause_music():
    global playing
    global selected_song_index
    global play_mode_text
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
            mixer.music.stop()
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
            music_play_mode()
        except:
            messagebox.showerror(title="无音乐文件", message='''请从左侧选择您想听的音乐，再点击播放。''')

#定义function播放下一首
def play_next():
    global running1
    global running2
    loop_play_next()
    #running1=True
    music_play_mode()

def loop_play_next():
    global selected_song_index
    global playing
    global pause
    global play_mode_text
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
    playlistbox.selection_clear(0, END)
    playlistbox.selection_set(selected_song_index)
    playlistbox.see(selected_song_index)
    playing=True
    pause=False
    music_play_mode()
    
#定义function停止播放音乐
def stop_music():
    global playing
    global pause
    global running1
    mixer.music.stop()
    playpausebutton.configure(image=playphoto)
    statusbar["text"]="已停止播放"
    playing=False
    pause=False
    
#定义function循环播放列表
def loop_playlist():
    global looping
    global playing
    while looping:
        if mixer.music.get_busy() or playing==False:
            time.sleep(1.0)
        else:
            loop_play_next()
            
#定义function循环播放音乐
def loop_music():
    global looping
    if looping:
        t2=threading.Thread(target=loop_playlist)
        t2.start()
        active_threads=threading.enumerate()
        print(active_threads)
        #threading.enumerate() returns a list of all Thread objects currently alive,
        #It excludes terminated threads and threads that have not yet been started.
   
#定义function随机播放
def random_play():
    global playing
    time.sleep(0.1)
    selected_song=playlistbox.curselection()
    selected_song_index=int(selected_song[0])
    #随机从playlist中选出一个item的index
    random_song_index=randrange(len(playlist))    
    #while loop确保随机选中的index不是正在播放歌曲的index
    while random_song_index==selected_song_index:
        random_song_index=randrange(len(playlist))
    random_song=playlist[random_song_index]
    mixer.music.load(random_song)
    mixer.music.play()
    playlistbox.selection_clear(0, END) 
    playlistbox.selection_set(random_song_index)
    playlistbox.see(random_song_index)
    statusbar["text"]="正在播放-"+os.path.basename(random_song)
    show_details(random_song)
    playpausebutton.configure(image=pausephoto)
    playing=True

#定义function随机播放列表
def shuffle_playlist():
    global shuffling
    global playing
    while shuffling:
        if mixer.music.get_busy() or playing==False:
            time.sleep(1.0)
        else:
            random_play()
            
#定义function随机播放音乐
def shuffle_music():
    global shuffling
    if shuffling:
        t3=threading.Thread(target=shuffle_playlist)
        t3.start()
        active_threads=threading.enumerate()
        print(active_threads)
    
#定义function重复播放
def repeat_play():
    global playing
    global selected_song_index
    time.sleep(0.1)
    selected_song=playlist[selected_song_index]
    mixer.music.load(selected_song)
    mixer.music.play()
    statusbar["text"]="正在播放-"+os.path.basename(selected_song)
    show_details(selected_song)
    playpausebutton.configure(image=pausephoto)
    playlistbox.selection_clear(0, END) 
    playlistbox.selection_set(selected_song_index) 
    playlistbox.see(selected_song_index)
    playing=True
            
#定义function重复播放单曲
def repeat_single():
    global repeating
    global playing
    while repeating:
        if mixer.music.get_busy() or playing==False:
            time.sleep(1.0)
        else:
            repeat_play()

#定义function
def repeat_music():
    global repeating
    if repeating:
         t4=threading.Thread(target=repeat_single)
         t4.start()
         active_threads=threading.enumerate()
         print(active_threads)
         
#定义function
def playing_one2():
    global running2
    global total_length
    global current_time
    while running2:
        if current_time<=total_length:
            time.sleep(1.0)
            print('running2')
        else:
            stop_music()
            running2=False
            print('running2=False')

#定义function
def playing_music2():
    global running2
    if running2:
        t6=threading.Thread(target=playing_one2)
        t6.start()
        
#定义function
def playing_one():
    global running1
    global total_length
    global current_time
    while running1:
        if current_time<=total_length:
            time.sleep(1.0)
            print('running1')
        else:
            stop_music()
            running1=False
            print('running1=False')
        
#定义function
def playing_music():
    global running1
    if running1:
        t5=threading.Thread(target=playing_one)
        t5.start()

#定义function音乐播放模式
def music_play_mode():
    global repeating
    global looping
    global shuffling
    global running1
    global running2
    global selected_song_index
    global play_mode_text
    play_mode_text=combobox.get()  #获取combobox选项里的value
    if play_mode_text=='单曲播放' and running1==False:
        repeating=False
        looping=False
        shuffling=False
        running1=True
        playing_music()
        play_mode_label.configure(image=repeatoffphoto)
    elif play_mode_text=='单曲播放' and running2==False:
        repeating=False
        looping=False
        shuffling=False
        running2=True
        playing_music2()
        play_mode_label.configure(image=repeatoffphoto)
    elif play_mode_text=='单曲循环':
        looping=False
        shuffling=False
        running1=False
        repeating=True
        repeat_music()      
        play_mode_label.configure(image=repeatonphoto)
    elif play_mode_text=='列表循环':
        repeating=False
        shuffling=False
        running1=False
        looping=True
        loop_music()
        play_mode_label.configure(image=looponphoto)
    elif play_mode_text=='随机循环':
        repeating=False
        looping=False
        running1=False
        shuffling=True
        shuffle_music()
        play_mode_label.configure(image=shuffleonphoto)
    playlistbox.selection_clear(0, END)  
    playlistbox.selection_set(selected_song_index)
    playlistbox.see(selected_song_index)
                            
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
    music_play_mode()
    
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

#创建上一首按钮
playpreviousphoto=PhotoImage(file="images/playprevious.png")
playpreviousbutton=ttk.Button(middleframe, image=playpreviousphoto, command=play_previous)
playpreviousbutton.grid(row=0, column=0, padx=10)

#创建播放/暂停按钮
playphoto=PhotoImage(file="images/play.png")
pausephoto=PhotoImage(file="images/pause.png")
playpausebutton=ttk.Button(middleframe, image=playphoto, command= play_pause_music)
playpausebutton.grid(row=0, column=1, padx=10)

#创建下一首按钮
playnextphoto=PhotoImage(file="images/playnext.png")
playnextbutton=ttk.Button(middleframe, image=playnextphoto, command=play_next)
playnextbutton.grid(row=0, column=2, padx=10)

#创建停止播放按钮
stopphoto=PhotoImage(file="images/stop.png")
stopbutton=ttk.Button(middleframe, image=stopphoto, command=stop_music)
stopbutton.grid(row=0, column=3, padx=10)

#创建播放模式combobox
play_mode=StringVar()
combobox= ttk.Combobox(bottomframe, textvariable=play_mode)
combobox.grid(row=0, column=0)
combobox['values'] = ('单曲播放', '单曲循环', '列表循环', '随机循环')
combobox.configure(state='readonly', width=8, font=('Microsoft YaHei',10))
combobox.current(newindex=0)    #设置当前默认选项
combobox.bind('<<ComboboxSelected>>', lambda x: music_play_mode())  #切换选项时激活music_play_mode

#创建播放模式Label
repeatoffphoto=PhotoImage(file="images/repeatoff.png")
repeatonphoto=PhotoImage(file="images/repeaton.png")
looponphoto=PhotoImage(file="images/loopon.png")
shuffleonphoto=PhotoImage(file="images/shuffleon.png")
play_mode_label=ttk.Label(bottomframe, image=repeatoffphoto)
play_mode_label.grid(row=0, column=1, padx=5)

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
