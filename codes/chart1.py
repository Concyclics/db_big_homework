import tkinter as tk
from tkinter import *
from tkinter import ttk
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pylab import mpl
import calendar
import time
import tkinter.font as tkFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import databaseOP

datetime = calendar.datetime.datetime
timedelta = calendar.datetime.timedelta

class Calendar:
  def __init__(s, point = None):
    s.master = tk.Toplevel()
    s.master.withdraw()
    s.master.attributes('-topmost' ,True)
    fwday = calendar.SUNDAY
    year = datetime.now().year
    month = datetime.now().month
    locale = None
    sel_bg = '#ecffc4'
    sel_fg = '#05640e'
    s._date = datetime(year, month, 1)        #每月第一日
    s._selection = None                       #设置为未选中日期
    s.G_Frame = ttk.Frame(s.master)
    s._cal = s.__get_calendar(locale, fwday)
    s.__setup_styles()        # 创建自定义样式
    s.__place_widgets()       # pack/grid 小部件
    s.__config_calendar()     # 调整日历列和安装标记
    # 配置画布和正确的绑定，以选择日期。
    s.__setup_selection(sel_bg, sel_fg)
    # 存储项ID，用于稍后插入。
    s._items = [s._calendar.insert('', 'end', values='') for _ in range(6)]
    # 在当前空日历中插入日期
    s._update()
    s.G_Frame.pack(expand = 1, fill = 'both')
    s.master.overrideredirect(1)
    s.master.update_idletasks()
    width, height = s.master.winfo_reqwidth(), s.master.winfo_reqheight()
    s.height=height
    if point:
      x, y = point[0], point[1]
    else: 
      x, y = (s.master.winfo_screenwidth() - width)/2, (s.master.winfo_screenheight() - height)/2
    s.master.geometry('%dx%d+%d+%d' % (width, height, x, y)) #窗口位置居中
    s.master.after(300, s._main_judge)
    s.master.deiconify()
    s.master.focus_set()
    s.master.wait_window() #这里应该使用wait_window挂起窗口，如果使用mainloop,可能会导致主程序很多错误

  def __get_calendar(s, locale, fwday):
    if locale is None:
      return calendar.TextCalendar(fwday)
    else:
      return calendar.LocaleTextCalendar(fwday, locale)

  def __setitem__(s, item, value):
    if item in ('year', 'month'):
      raise AttributeError("attribute '%s' is not writeable" % item)
    elif item == 'selectbackground':
      s._canvas['background'] = value
    elif item == 'selectforeground':
      s._canvas.itemconfigure(s._canvas.text, item=value)
    else:
      s.G_Frame.__setitem__(s, item, value)

  def __getitem__(s, item):
    if item in ('year', 'month'):
      return getattr(s._date, item)
    elif item == 'selectbackground':
      return s._canvas['background']
    elif item == 'selectforeground':
      return s._canvas.itemcget(s._canvas.text, 'fill')
    else:
      r = ttk.tclobjs_to_py({item: ttk.Frame.__getitem__(s, item)})
      return r[item]

  def __setup_styles(s):
    # 自定义TTK风格
    style = ttk.Style(s.master)
    arrow_layout = lambda dir: (
      [('Button.focus', {'children': [('Button.%sarrow' % dir, None)]})]
    )
    style.layout('L.TButton', arrow_layout('left'))
    style.layout('R.TButton', arrow_layout('right'))

  def __place_widgets(s):
    # 标头框架及其小部件
    Input_judgment_num = s.master.register(s.Input_judgment) # 需要将函数包装一下，必要的
    hframe = ttk.Frame(s.G_Frame)
    gframe = ttk.Frame(s.G_Frame)
    bframe = ttk.Frame(s.G_Frame)
    hframe.pack(in_=s.G_Frame, side='top', pady=5, anchor='center')
    gframe.pack(in_=s.G_Frame, fill=tk.X, pady=5)
    bframe.pack(in_=s.G_Frame, side='bottom', pady=5)
    lbtn = ttk.Button(hframe, style='L.TButton', command=s._prev_month)
    lbtn.grid(in_=hframe, column=0, row=0, padx=12)
    rbtn = ttk.Button(hframe, style='R.TButton', command=s._next_month)
    rbtn.grid(in_=hframe, column=5, row=0, padx=12)
    s.CB_year = ttk.Combobox(hframe, width = 5, values = [str(year) for year in range(datetime.now().year, datetime.now().year-11,-1)], validate = 'key', validatecommand = (Input_judgment_num, '%P'))
    s.CB_year.current(0)
    s.CB_year.grid(in_=hframe, column=1, row=0)
    s.CB_year.bind('<KeyPress>', lambda event:s._update(event, True))
    s.CB_year.bind("<<ComboboxSelected>>", s._update)
    tk.Label(hframe, text = '年', justify = 'left').grid(in_=hframe, column=2, row=0, padx=(0,5))
    s.CB_month = ttk.Combobox(hframe, width = 3, values = ['%02d' % month for month in range(1,13)], state = 'readonly')
    s.CB_month.current(datetime.now().month - 1)
    s.CB_month.grid(in_=hframe, column=3, row=0)
    s.CB_month.bind("<<ComboboxSelected>>", s._update)
    tk.Label(hframe, text = '月', justify = 'left').grid(in_=hframe, column=4, row=0)
    # 日历部件
    s._calendar = ttk.Treeview(gframe, show='', selectmode='none', height=7)
    s._calendar.pack(expand=1, fill='both', side='bottom', padx=5)
    ttk.Button(bframe, text = "确 定", width = 6, command = lambda: s._exit(True)).grid(row = 0, column = 0, sticky = 'ns', padx = 20)
    ttk.Button(bframe, text = "取 消", width = 6, command = s._exit).grid(row = 0, column = 1, sticky = 'ne', padx = 20)
    tk.Frame(s.G_Frame, bg = '#565656').place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 1, relheigh = 2/200)
    tk.Frame(s.G_Frame, bg = '#565656').place(x = 0, y = 0, relx = 0, rely = 198/200, relwidth = 1, relheigh = 2/200)
    tk.Frame(s.G_Frame, bg = '#565656').place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 2/200, relheigh = 1)
    tk.Frame(s.G_Frame, bg = '#565656').place(x = 0, y = 0, relx = 198/200, rely = 0, relwidth = 2/200, relheigh = 1)

  def __config_calendar(s):
    # cols = s._cal.formatweekheader(3).split()
    cols = ['日','一','二','三','四','五','六']
    s._calendar['columns'] = cols
    s._calendar.tag_configure('header', background='grey90')
    s._calendar.insert('', 'end', values=cols, tag='header')
    # 调整其列宽
    font = tkFont.Font()
    maxwidth = max(font.measure(col) for col in cols)
    for col in cols:
      s._calendar.column(col, width=maxwidth, minwidth=maxwidth,
        anchor='center')

  def __setup_selection(s, sel_bg, sel_fg):
    def __canvas_forget(evt):
      canvas.place_forget()
      s._selection = None

    s._font = tkFont.Font()
    s._canvas = canvas = tk.Canvas(s._calendar, background=sel_bg, borderwidth=0, highlightthickness=0)
    canvas.text = canvas.create_text(0, 0, fill=sel_fg, anchor='w')
    canvas.bind('<Button-1>', __canvas_forget)
    s._calendar.bind('<Configure>', __canvas_forget)
    s._calendar.bind('<Button-1>', s._pressed)

  def _build_calendar(s):
    year, month = s._date.year, s._date.month
    header = s._cal.formatmonthname(year, month, 0)
    # 更新日历显示的日期
    cal = s._cal.monthdayscalendar(year, month)
    for indx, item in enumerate(s._items):
      week = cal[indx] if indx < len(cal) else []
      fmt_week = [('%02d' % day) if day else '' for day in week]
      s._calendar.item(item, values=fmt_week)

  def _show_select(s, text, bbox):
    x, y, width, height = bbox
    textw = s._font.measure(text)
    canvas = s._canvas
    canvas.configure(width = width, height = height)
    canvas.coords(canvas.text, (width - textw)/2, height / 2 - 1)
    canvas.itemconfigure(canvas.text, text=text)
    canvas.place(in_=s._calendar, x=x, y=y)

  def _pressed(s, evt = None, item = None, column = None, widget = None):
    """在日历的某个地方点击。"""
    if not item:
      x, y, widget = evt.x, evt.y, evt.widget
      item = widget.identify_row(y)
      column = widget.identify_column(x)
    if not column or not item in s._items:
      # 在工作日行中单击或仅在列外单击。
      return
    item_values = widget.item(item)['values']
    if not len(item_values): # 这个月的行是空的。
      return
    text = item_values[int(column[1]) - 1]
    if not text: 
      return
    bbox = widget.bbox(item, column)
    if not bbox: # 日历尚不可见
      s.master.after(20, lambda : s._pressed(item = item, column = column, widget = widget))
      return
    text = '%02d' % text
    s._selection = (text, item, column)
    s._show_select(text, bbox)

  def _prev_month(s):
    """更新日历以显示前一个月。"""
    s._canvas.place_forget()
    s._selection = None
    s._date = s._date - timedelta(days=1)
    s._date = datetime(s._date.year, s._date.month, 1)
    s.CB_year.set(s._date.year)
    s.CB_month.set(s._date.month)
    s._update()

  def _next_month(s):
    """更新日历以显示下一个月。"""
    s._canvas.place_forget()
    s._selection = None

    year, month = s._date.year, s._date.month
    s._date = s._date + timedelta(
      days=calendar.monthrange(year, month)[1] + 1)
    s._date = datetime(s._date.year, s._date.month, 1)
    s.CB_year.set(s._date.year)
    s.CB_month.set(s._date.month)
    s._update()

  def _update(s, event = None, key = None):
    """刷新界面"""
    if key and event.keysym != 'Return': return
    year = int(s.CB_year.get())
    month = int(s.CB_month.get())
    if year == 0 or year > 9999: return
    s._canvas.place_forget()
    s._date = datetime(year, month, 1)
    s._build_calendar() # 重建日历
    if year == datetime.now().year and month == datetime.now().month:
      day = datetime.now().day
      for _item, day_list in enumerate(s._cal.monthdayscalendar(year, month)):
        if day in day_list:
          item = 'I00' + str(_item + 2)
          column = '#' + str(day_list.index(day)+1)
          s.master.after(100, lambda :s._pressed(item = item, column = column, widget = s._calendar))

  def _exit(s, confirm = False):
    if not confirm: s._selection = None
    s.master.destroy()

  def _main_judge(s):
    """判断窗口是否在最顶层"""
    try:
      if s.master.focus_displayof() == None or 'toplevel' not in str(s.master.focus_displayof()): s._exit()
      else: s.master.after(10, s._main_judge)
    except:
      s.master.after(10, s._main_judge)

  def selection(s):
    """返回表示当前选定日期的日期时间。"""
    if not s._selection: return None
    year, month = s._date.year, s._date.month
    return str(datetime(year, month, int(s._selection[0])))[:10]

  def Input_judgment(s, content):
    """输入判断"""
    if content.isdigit() or content == "":
      return True
    else:
      return False

classicfund = ['CSI1033','CSI1032','CSI1038','CSI1029','CSI1006','CSI1065','ZH001798','ZH012926','ZH039471','ZH010246','ZH006498','ZH000193','ZH009664','ZH030684','ZH017252','ZH007973','ZH037807','ZH007974','ZH017409','ZH035411','ZH043108','ZH043126']
classicfund.sort()

fundINview = []
str_start_date = '2010-01-01'
str_end_date = time.strftime("%Y-%m-%d",time.localtime())
codekey = {
    'CSI1033':0,
    'CSI1032':1,
    'CSI1038':2,
    'CSI1029':3,
    'CSI1006':4,
    'CSI1065':5,
    'ZH001798':6,
    'ZH012926':7,
    'ZH039471':8,
    'ZH010246':9,
    'ZH006498':10,
    'ZH000193':11,
    'ZH009664':12,
    'ZH030684':13,
    'ZH017252':14,
    'ZH007973':15,
    'ZH037807':16,
    'ZH007974':17,
    'ZH017409':18,
    'ZH035411':19,
    'ZH043108':20,
    'ZH043126':21
}
coderecord = []
for i in range(len(classicfund)):
    coderecord.append([])

def getdata():
    for code in classicfund:
        while len(coderecord[codekey[code]]) > 1:
            coderecord[codekey[code]].pop()
        valuelist = []
        x = []
        y = []
        # print(len(coderecord[codekey[code]]))
        # print(coderecord[codekey[code]])
        with databaseOP.DBconnect(password='asd841123001%%') as DB:
            if len(coderecord[codekey[code]]) < 1:
                fund = databaseOP.getFund(DB,code)
                valuelist.append(fund.name)
                valuelist.append(fund.sharp_rate)
                valuelist.append(fund.max_down)
                valuelist.append(fund.volatility)
                coderecord[codekey[code]].append(valuelist)
            for history in databaseOP.getHistory(DB,code,str_start_date,str_end_date):
                x.append(history.day)
                y.append(history.value)
            coderecord[codekey[code]].append(x)
            coderecord[codekey[code]].append(y)
        # print(len(coderecord[codekey[code]]))


class Chart(Frame):
    """一个经典的GUI写法"""
    linenum = 0
    linecolor = ['r','g','b','c','m','y','k','w']
    valuelines = []
    percentlines = []
    graph = []
    linelabel = []
    view = 0

    def __init__(self, master=None):
        '''初始化方法'''
        super().__init__(master)  # 调用父类的初始化方法
        self.master = master
        self.pack(side=TOP, fill=BOTH, expand=1)  # 此处填充父窗体
        self.create_matplotlib()
        self.createWidget(self.figure)

    def createWidget(self, figure):
        # 创建改变视图按钮
        self.button = Button(master=self.master,text='改变视图(净值图)',command=self.changeview)
        # 创建画布
        self.canvas = FigureCanvasTkAgg(figure, self)
        self.showGraph()
        self.button.place(relx=0,rely=0,relwidth=0.15,relheight=0.05,anchor=NW)

    def showGraph(self): #将图像映射到窗口
        for vline in self.valuelines:
            vline[0].set_alpha(1.0*(1 - self.view))
        for pline in self.percentlines:
            pline[0].set_alpha(1.0*self.view)
        if self.view:
            self.button['text'] = '改变视图(比例图)'
        else:
            self.button['text'] = '改变视图(净值图)'
        self.canvas.draw()
        # self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        # self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        self.canvas.get_tk_widget().place(relx=0.5,rely=0.5,relwidth=1,relheight=1,anchor=CENTER)
        self.canvas._tkcanvas.place(relx=0.5,rely=0.5,relwidth=1,relheight=1,anchor=CENTER)

    def create_matplotlib(self):
        """创建绘图对象"""
        # 设置中文显示字体
        mpl.rcParams['font.sans-serif'] = ['SimHei']  # 中文显示
        mpl.rcParams['axes.unicode_minus'] = False  # 负号显示
        # 创建绘图对象f figsize的单位是英寸 像素 = 英寸*分辨率
        plt.style.use('dark_background')
        self.figure = plt.figure(num=2, figsize=(10, 5), dpi=80,facecolor='black', edgecolor='black', frameon=True)
        # 创建一副子图
        fig1 = plt.subplot(111)
        fig1.set_yticks(range(-6,6,1))#设置y轴的刻度范围
        fig2 = fig1.twinx()
        self.graph.append(fig2)
        self.graph.append(fig1)
        fig2.set_yticks(range(0,5,1))#设置y轴的刻度范围
        fig1.spines['top'].set_visible(False)
        fig2.spines['top'].set_visible(False)
        # .axis("off") #不显示坐标轴


    def changeview(self):
        self.view = 1 - self.view
        self.showGraph()

    def calpercent(self,yy):
        tmp = [0.0]
        for index in range(len(yy)):
            if index >= 1:
                if yy[index-1] != 0:
                    t = 100.0*((yy[index]-yy[index-1])/yy[index-1])
                else:
                    t = 0
                tmp.append(1.0*t)
        return tmp
        
    def addLine(self,dat,yy,name):
        # plt.style.use('dark_background')
        fig1 = self.graph[0]
        fig2 = self.graph[1]
        # fig1.axis("off") #不显示坐标轴
        valueline = fig1.plot(dat, yy, color=self.linecolor[self.linenum%8], label=name,linewidth=1, linestyle='-')
        percentline = fig2.plot(dat, self.calpercent(yy), color=self.linecolor[self.linenum%8], label=name,linewidth=1, linestyle='-')
        self.valuelines.append(valueline)
        self.percentlines.append(percentline)
        self.linelabel.append(name)
        self.linenum += 1

    def delLine(self,id):
        if self.linenum >= 1 and id < self.linenum:
            if self.view == 0:
                for index,vl in enumerate(self.valuelines):
                    vl[0].set_alpha(1.0*(index != id))
            else:
                for index,pl in enumerate(self.percentlines):
                    pl[0].set_alpha(1.0*(index != id))
            del self.valuelines[id]
            del self.percentlines[id]
            del self.linelabel[id]
            # fig1 = plt.subplot(111)
            # plt.legend(self.linelabel,frameon=False)
            self.linenum -= 1
        else:
            print('out of range')

    def clearGraph(self):
        for i in range(self.linenum):
              self.delLine(0)
        # print(self.linenum)
        # for gra in self.graph:
        #       del gra
        self.showGraph()
        plt.clf()
        print(self.graph)
        # 重新创建子图
        f1 = plt.subplot(111)
        f1.set_yticks(range(-6,6,1))#设置y轴的刻度范围
        f2 = f1.twinx()
        self.graph[0] = f2
        self.graph[1] = f1
        f2.set_yticks(range(0,5,1))#设置y轴的刻度范围
        f1.spines['top'].set_visible(False)
        f2.spines['top'].set_visible(False)
        # self.canvas = FigureCanvasTkAgg(self.figure, self)
        # print(self.graph)
        self.showGraph()
        for code in fundINview:
              # print(coderecord[codekey[code]][0][0])
              self.addLine(coderecord[codekey[code]][1],coderecord[codekey[code]][2],coderecord[codekey[code]][0][0]) #valuelist

    def destroy(self):
        """重写destroy方法"""
        super().destroy()
        quit()

    def quit():
        """点击退出按钮时调用这个函数"""
        root.quit()  # 结束主循环
        root.destroy()  # 销毁窗口


def tree(master):
    scrollBar = Scrollbar(master)
    scrollBar.pack(side=RIGHT, fill=Y)
    style=ttk.Style(master)
    style.theme_use('clam')
    style.configure('Treeview',background = 'blue',selectbackground = 'red',foreground='green',fieldbackground = 'black')
    tree = ttk.Treeview(master,columns=['1','2','3','4'],show='headings',selectmode='extended',yscrollcommand=scrollBar.set)
    tree.pack(side=TOP, fill=BOTH,expand=Y)
    tree.column('1',width=85,anchor='center')
    tree.column('2',width=20,anchor='center')
    tree.column('3',width=25,anchor='center')
    tree.column('4',width=40,anchor='center')
    tree.heading('1',text='基金名称')
    tree.heading('2',text='夏普率')
    tree.heading('3',text='最大回撤')
    tree.heading('4',text='年化波动率')
    scrollBar.config(command=tree.yview)
    return tree

def addGraph(Chart,Treeview):#增加选中记录
    code = comboxlist.get()
    if code not in fundINview:
        fundINview.append(code) #增加所选记录
        Chart.addLine(coderecord[codekey[code]][1],coderecord[codekey[code]][2],coderecord[codekey[code]][0][0]) #valuelist
        Chart.showGraph()
        Treeview.insert('','end',values=coderecord[codekey[code]][0])

def cancelLine(Chart,Treeview):#删除选中记录
    if Treeview.selection() != ():
        j = i = 0
        for item in Treeview.get_children():
            w = 0
            for selected in Treeview.selection():
                if item == selected:
                    Treeview.delete(item)
                    Chart.delLine(i)
                    del fundINview[j]
                    w = 1
                    break
            j += 1
            if w == 0:
                i += 1
        Chart.showGraph()

def choosedate(type):
    for date in [Calendar().selection()]:
        if date:
            if type=='start':	#如果是开始按钮，就赋值给开始日期
                start_date.set(date)
            elif type=='end':
                end_date.set(date)

def verify(Chart):
    sdate = start_date.get()
    edate = end_date.get()
    if sdate >= edate:
      del sdate
      del edate
      return False
    else:
      global str_start_date
      str_start_date = sdate
      global str_end_date
      str_end_date = edate
      getdata()
      if len(fundINview) == 0:
        return False
      else:
        Chart.clearGraph()
        Chart.showGraph()

      

if __name__ == '__main__':
    getdata()
    root = Tk()
    root.title('投资组合比较器')
    root['bg'] = '#000033'
    screenwidth = root.winfo_screenwidth() 
    screenheight = root.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (screenwidth*0.7, screenheight*0.7, screenwidth*0.3/2, screenheight*0.3/2)
    root.geometry(alignstr)
    comvalue=StringVar()#窗体自带的文本，新建一个值
    comboxlist=ttk.Combobox(root,textvariable=comvalue) #初始化
    comboxlist["values"]=classicfund
    comboxlist.current(0) #选择第一个
    comboxlist.place(relx=0.5,rely=0.05,relwidth=0.4,relheight=0.05,anchor=CENTER)
    
    fm1 = Frame(root, bg='black', width=screenwidth*0.4, height=screenheight*0.4)
    fm2 = Frame(root, bg='black', width=screenwidth*0.4, height=screenheight*0.3)
    fm2.place(x=0,rely=0.29,relwidth=0.3,relheight=0.4,anchor=W)
    fm1.place(relx=0.65,rely=0.53,relwidth=0.69,relheight=0.85,anchor=CENTER)
    fundinfo = ['螺丝钉主动优选组合','3.14','0.99','0.21']

    x1 = ['2000','2001','2002','2003','2004','2005','2006','2007','2008', '2009',
    '2010','2011','2012','2013','2014','2015','2016','2017','2018', '2019', '2020', '2021', '2022']
    y = [1,3,0.95,1.47,3,1,3,4,2.98,3,1,3,0.95,1.47,3,1,3,4,2.98,3,3,1.25,0.124]
    y1 = [1,0,0.95,1.47,3,1,2.5,3.8,2.98,3,1,3,0.95,1.47,3,1,-2,4,2.98,3,3,1.25,0.124]
    fundname = '无敌基金'

    start_date=tk.StringVar() #开始日期
    start_date.set(str_start_date)
    end_date=tk.StringVar()	#结束日期
    end_date.set(str_end_date)

    chart = Chart(fm1)
    t = tree(fm2)
    confirm = Button(root,text = '确定',command=lambda:addGraph(chart,t))
    confirm.place(relx=0.75,rely=0.05,relwidth=0.07,relheight=0.05,anchor=CENTER)

    #选择日期的按钮
    startbutton = Button(root,text='选择开始日期',command=lambda:choosedate('start'))
    startEntry=Entry(root,textvariable=start_date)	#开始输入框
    endbutton = Button(root,text='选择结束日期',command=lambda:choosedate('end'))
    endEntry=Entry(root,textvariable=end_date)	#结束输入框
    verifybt=Button(root,text='确定',command=lambda:verify(chart))
    startbutton.place(relx=0.31,rely=1,relwidth=0.09,relheight=0.05,anchor=SW)
    startEntry.place(relx=0.4,rely=1,relwidth=0.1,relheight=0.05,anchor=SW)
    endbutton.place(relx=0.51,rely=1,relwidth=0.09,relheight=0.05,anchor=SW)
    endEntry.place(relx=0.60,rely=1,relwidth=0.1,relheight=0.05,anchor=SW)
    verifybt.place(relx=0.91,rely=1,relwidth=0.09,relheight=0.05,anchor=SW)

    delbutton = Button(root,text='删除选中基金',command=lambda:cancelLine(chart,t))
    delbutton.place(relx=0.15,rely=0.51,relwidth=0.08,relheight=0.04,anchor=CENTER)
    # delbutton.pack(side=BOTTOM,anchor=S)
    #主窗口进入循环
    root.mainloop()
