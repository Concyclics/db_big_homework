import tkinter as tk
from tkinter import *
from tkinter import ttk
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pylab import mpl
import calendar
import time
import datetime as dt
import tkinter.font as tkFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import databaseOP
# import fundation
import creeper

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

class Window: # 窗口类
    originalfund = []
    fundINview = []
    codekey = {}
    str_start_date = '2018-01-01'
    str_end_date = time.strftime("%Y-%m-%d",time.localtime())
    root = Tk()
    coderecord = []
    comvalue=StringVar()#窗体自带的文本，新建一个值
    comboxlist=ttk.Combobox(root,textvariable=comvalue) 
    combostyle = ttk.Style()
    combostyle.theme_create('combostyle', parent='alt',
                    settings={'TCombobox':
                                  {'configure':
                                        {
                                        'foreground': 'black',
                                        'selectbackground': 'gray',   # 选择后的背景颜色
                                        'fieldbackground': 'white',  #  下拉框颜色
                                        'background': '#c0c0c0',     # 下拉按钮颜色
                                        "font":10,   # 字体大小
                                        "font-weight": "bold"
                                        }}})
    combostyle.theme_use('combostyle')

    def __init__(s, master = None): #初始化
        s.master = master
        with databaseOP.DBconnect(password='19260817') as DB:
            codelist = databaseOP.getFundlist(DB)
            for codeitem in codelist:
                s.originalfund.append(codeitem[0])
        for index,code in enumerate(s.originalfund):
              s.codekey[code] = index
        for i in range(len(s.originalfund)):
            s.coderecord.append([])
        s.root.title('投资组合比较器')
        s.root.protocol("WM_DELETE_WINDOW", s.__del__)
        s.root['bg'] = '#000000'
        screenwidth = s.root.winfo_screenwidth() 
        screenheight = s.root.winfo_screenheight()
        # print(s.root.winfo_screenheight())
        alignstr = '%dx%d+%d+%d' % (screenwidth*0.7, screenheight*0.7, screenwidth*0.3/2, screenheight*0.3/2)
        s.root.geometry(alignstr)
        s.comboxlist["values"]=s.originalfund
        s.comboxlist.current(0) #选择第一个
        s.comboxlist.place(relx=0.5,rely=0.05,relwidth=0.4,relheight=0.05,anchor=CENTER)

        toplb = Label(s.root,text = '请选择要比较的基金(可以手动输入想要查看的基金编号)',bg='black',fg='white')
        toplb.place(relx=0.15,rely=0.05,relwidth=0.28,relheight=0.05,anchor=CENTER)
        bottomlb = Label(s.root,text = '(若值为null,则为无数据或休息日)',bg='black',fg='white')
        bottomlb.place(relx=0.15,rely=0.97,relwidth=0.2,relheight=0.05,anchor=CENTER)
        fm1 = Frame(s.root, bg='black', width=screenwidth*0.4, height=screenheight*0.4)
        fm2 = Frame(s.root, bg='black', width=screenwidth*0.4, height=screenheight*0.3)
        fm3 = Frame(s.root, bg='white', width=screenwidth*0.4, height=screenheight*0.3)
        fm2.place(x=0,rely=0.29,relwidth=0.3,relheight=0.4,anchor=W)
        fm3.place(x=0,rely=0.75,relwidth=0.3,relheight=0.4,anchor=W)
        fm1.place(relx=0.65,rely=0.53,relwidth=0.69,relheight=0.85,anchor=CENTER)

        s.start_date=tk.StringVar() #开始日期
        s.start_date.set(s.str_start_date)
        s.end_date=tk.StringVar()	#结束日期
        s.end_date.set(s.str_end_date)

        s.chart = Chart(fm1)
        s.chart.canvas.mpl_connect('button_press_event', s.viewinfo)
        s.treeview = s.tree(fm2,'基金名称','夏普率','最大回撤','年化波动率',85,20,25,40)
        s.detail = s.tree(fm3,'基金名称','日期','当日净值','当日涨幅',85,40,25,20)
        confirm = Button(s.root,text = '确定',bg='#c0c0c0',fg='black',command=s.addGraph)
        confirm.place(relx=0.75,rely=0.05,relwidth=0.07,relheight=0.05,anchor=CENTER)
        #选择日期的按钮
        startbutton = Button(s.root,text='选择开始日期',bg='#c0c0c0',command=lambda:s.choosedate('start'))
        startEntry=Entry(s.root,textvariable=s.start_date)	#开始输入框
        endbutton = Button(s.root,text='选择结束日期',bg='#c0c0c0',command=lambda:s.choosedate('end'))
        endEntry=Entry(s.root,textvariable=s.end_date)	#结束输入框
        verifybt=Button(s.root,text='确定',bg='#c0c0c0',command=s.verify)
        startbutton.place(relx=0.31,rely=1,relwidth=0.09,relheight=0.05,anchor=SW)
        startEntry.place(relx=0.4,rely=1,relwidth=0.08,relheight=0.05,anchor=SW)
        endbutton.place(relx=0.51,rely=1,relwidth=0.09,relheight=0.05,anchor=SW)
        endEntry.place(relx=0.6,rely=1,relwidth=0.08,relheight=0.05,anchor=SW)
        verifybt.place(relx=0.91,rely=1,relwidth=0.09,relheight=0.05,anchor=SW)

        delbutton = Button(s.root,text='删除选中基金',bg='#c0c0c0',command=s.cancelLine)
        delallbutton = Button(s.root,text='删除所有选中基金',bg='#c0c0c0',command=s.cancelallLine)
        delbutton.place(relx=0,rely=0.51,relwidth=0.08,relheight=0.04,anchor=W)
        delallbutton.place(relx=0.30,rely=0.51,relwidth=0.1,relheight=0.04,anchor=E)
        s.getdata()

    def __del__(s):
        s.root.quit()
        s.root.destroy()

    def viewinfo(s,event):
        if s.chart.linenum != 0:
            if s.chart.vline != []: #清除原有竖线
                s.chart.vline[0].set_alpha(0.0)
                s.chart.vline.clear()
            # if s.chart.linelabel != []: #清除原有图例
            #     for lb in s.chart.linelabel:
            #         lb.set_text('')
            #     s.chart.linelabel.clear()
            for child in s.detail.get_children(): #清除表格
                s.detail.delete(child)
            fig = s.chart.graph[0]
            vl = fig.axvline(x=event.xdata, color = "w", linestyle = "dashed")
            s.chart.vline.append(vl)
            starttime=time.strptime(s.str_start_date,'%Y-%m-%d')
            starttime=dt.date(starttime[0],starttime[1],starttime[2])
            for index,code in enumerate(s.fundINview):
                for x,y,z in zip(s.coderecord[s.codekey[code]][1],s.coderecord[s.codekey[code]][2],s.coderecord[s.codekey[code]][3]):
                    # print((x - s.coderecord[s.codekey[code]][1][0]).days,int(event.xdata+0.5) - (s.coderecord[s.codekey[code]][1][0] - dt.date(1970,1,1)).days)
                    strx = dt.datetime.strftime(x, '%Y-%m-%d')
                    if (x - s.coderecord[s.codekey[code]][1][0]).days == int(event.xdata+0.5) - (s.coderecord[s.codekey[code]][1][0] - dt.date(1970,1,1)).days:
                        # label = plt.text(x, y, (strx,y),ha='center', va='top', fontsize=15)
                        # print('show!')
                        s.detail.insert('','end',values=[s.coderecord[s.codekey[code]][0][0],strx,y,z],tags=(s.chart.coloruse[index],))
                        # s.chart.linelabel.append(label)
                        break
                    elif (x - s.coderecord[s.codekey[code]][1][0]).days > int(event.xdata+0.5) - (s.coderecord[s.codekey[code]][1][0] - dt.date(1970,1,1)).days:
                        s.detail.insert('','end',values=[s.coderecord[s.codekey[code]][0][0],strx,'null','null'],tags=(s.chart.coloruse[index],))
                        break
            s.chart.showGraph()

    def tree(s,master,title1,title2,title3,title4,w1,w2,w3,w4):
        scrollBar = Scrollbar(master)
        scrollBar.pack(side=RIGHT, fill=Y)
        style=ttk.Style(master)
        # style.theme_use('clam')
        style.configure('Treeview',background = 'white',selectbackground = 'black',fieldbackground = 'black')
        tree = ttk.Treeview(master,columns=['1','2','3','4'],show='headings',selectmode='extended',yscrollcommand=scrollBar.set)
        tree.pack(side=TOP, fill=BOTH,expand=Y)
        for color in s.chart.linecolor:
            tree.tag_configure(color,background='gray',foreground=color)
        tree.column('1',width=w1,anchor='center')
        tree.column('2',width=w2,anchor='center')
        tree.column('3',width=w3,anchor='center')
        tree.column('4',width=w4,anchor='center')
        tree.heading('1',text=title1)
        tree.heading('2',text=title2)
        tree.heading('3',text=title3)
        tree.heading('4',text=title4)
        scrollBar.config(command=tree.yview)
        return tree

    def getdata(s):
        for code in s.originalfund:
            while len(s.coderecord[s.codekey[code]]) > 1:
                s.coderecord[s.codekey[code]].pop()
            valuelist = []
            x = []
            y = []
            with databaseOP.DBconnect(password='19260817') as DB:
                if len(s.coderecord[s.codekey[code]]) < 1:
                    fund = databaseOP.getFund(DB,code)
                    valuelist.append(fund.name)
                    valuelist.append(fund.sharp_rate)
                    valuelist.append(fund.max_down)
                    valuelist.append(fund.volatility)
                    s.coderecord[s.codekey[code]].append(valuelist)
                for history in databaseOP.getHistory(DB,code,s.str_start_date,s.str_end_date):
                    x.append(history.day)
                    y.append(history.value)
            s.coderecord[s.codekey[code]].append(x)
            s.coderecord[s.codekey[code]].append(y)
            s.coderecord[s.codekey[code]].append(s.chart.calpercent(y))
      
    def addGraph(s):#增加选中记录
        code = s.comboxlist.get() #选择框里的内容
        if code == '':
            return False
        if code not in s.originalfund: #不在预选基金里
            fund = creeper.getFund(code)
            if fund == False: #code不正确
                return fund
            s.originalfund.append(code)
            with databaseOP.DBconnect(password='19260817') as DB:
                valuelist = []
                x = []
                y = []
                databaseOP.addFund(DB,fund)
                valuelist.append(fund.name)
                valuelist.append(fund.sharp_rate)
                valuelist.append(fund.max_down)
                valuelist.append(fund.volatility)
                s.codekey[code] = len(s.codekey)
                s.coderecord.append([])
                s.coderecord[s.codekey[code]].append(valuelist)
                historylist = creeper.getHistory(code,5000)
                for history in historylist:
                    databaseOP.addHistory(DB,history)
                for history in databaseOP.getHistory(DB,code,s.str_start_date,s.str_end_date):
                    x.append(history.day)
                    y.append(history.value)
                s.coderecord[s.codekey[code]].append(x)
                s.coderecord[s.codekey[code]].append(y)
        if code not in s.fundINview:
            s.fundINview.append(code)
            s.chart.addLine(s.coderecord[s.codekey[code]][1],s.coderecord[s.codekey[code]][2],s.coderecord[s.codekey[code]][3],s.coderecord[s.codekey[code]][0][0]) #valuelist
            s.chart.showGraph()
            s.treeview.insert('','end',values=s.coderecord[s.codekey[code]][0],tags=(s.chart.coloruse[s.chart.linenum-1],))
            # s.combostyle.configure('Treeview',background = 'gray',selectbackground = 'red',foreground=s.chart.linecolor[s.chart.linenum%8],fieldbackground = 'black')

    def cancelLine(s):#删除选中记录
        if s.treeview.selection() != ():
            j = i = 0
            for index,item in enumerate(s.treeview.get_children()):
                w = 0
                for selected in s.treeview.selection():
                    if item == selected:
                        s.treeview.delete(item)
                        s.detail.delete(s.detail.get_children()[index])
                        s.chart.delLine(i)
                        del s.fundINview[j]
                        w = 1
                        break
                j += 1
                if w == 0:
                    i += 1
            s.chart.showGraph()

    def clearGraph(s):
        while s.chart.linenum > 0:
            s.chart.delLine(s.chart.linenum - 1)
        plt.clf()
        # 重新创建子图
        f1 = plt.subplot(111)
        f1.set_yticks(range(-6,6,1))#设置y轴的刻度范围
        plt.yticks([-5,-4,-3,-2,-1,0,1,2,3,4,5],['-5%','-4%','-3%','-2%','-1%','0%','1%','2%','3%','4%','5%'])
        plt.xlabel('日期')
        plt.ylabel('涨幅百分比')
        f2 = f1.twinx()
        s.chart.graph[0] = f2
        s.chart.graph[1] = f1
        f2.set_yticks(range(0,5,1))#设置y轴的刻度范围
        plt.ylabel('净值')
        f1.spines['top'].set_visible(False)
        f2.spines['top'].set_visible(False)
        for child in s.detail.get_children(): #清除表格
            s.detail.delete(child)
        s.chart.showGraph()
        for code in s.fundINview:
            s.chart.addLine(s.coderecord[s.codekey[code]][1],s.coderecord[s.codekey[code]][2],s.coderecord[s.codekey[code]][3],s.coderecord[s.codekey[code]][0][0]) #valuelist

    def cancelallLine(s):#删除选中记录
        for item in s.treeview.get_children():
            s.treeview.delete(item)
        while s.chart.linenum > 0:
            s.chart.delLine(s.chart.linenum - 1)
        s.fundINview.clear()
        plt.clf()
        # 重新创建子图
        f1 = plt.subplot(111)
        f1.set_yticks(range(-6,6,1))#设置y轴的刻度范围
        plt.yticks([-5,-4,-3,-2,-1,0,1,2,3,4,5],['-5%','-4%','-3%','-2%','-1%','0%','1%','2%','3%','4%','5%'])
        plt.xlabel('日期')
        plt.ylabel('涨幅百分比')
        f2 = f1.twinx()
        s.chart.graph[0] = f2
        s.chart.graph[1] = f1
        plt.ylabel('净值')
        f2.set_yticks(range(0,5,1))#设置y轴的刻度范围
        f1.spines['top'].set_visible(False)
        f2.spines['top'].set_visible(False)
        s.chart.showGraph()
        for child in s.detail.get_children(): #清除表格
                s.detail.delete(child)

    def choosedate(s,type):
        for date in [Calendar().selection()]:
            if date:
                if type=='start':	#如果是开始按钮，就赋值给开始日期
                    s.start_date.set(date)
                elif type=='end':
                    s.end_date.set(date)

    def verify(s):
        sdate = s.start_date.get()
        edate = s.end_date.get()
        if sdate >= edate: #比较开始日期和结束日期的大小
            del sdate
            del edate
            return False
        else:
            s.str_start_date = sdate
            s.str_end_date = edate
            s.getdata()
            if len(s.fundINview) == 0: #如果已经有图表，则重新生成
                return True
            else:
                s.clearGraph()
                s.chart.showGraph()

    def main(s):
        s.root.mainloop()
        

class Chart(Frame):
    linenum = 0
    linecolor = ['red','lime','blue','cyan','magenta','yellow','purple','white']
    linecoloruse = {}
    valuelines = []
    coloruse = []
    vline = []
    percentlines = []
    graph = []
    linelabel = []
    view = 0
    def __init__(self, master=None):
        super().__init__(master)  # 调用父类的初始化方法
        self.master = master
        self.pack(side=TOP, fill=BOTH, expand=1)  # 此处填充父窗体
        for color in self.linecolor:
            self.linecoloruse[color] = []
        self.create_matplotlib()
        self.createWidget(self.figure)

    def createWidget(self, figure):
        # 创建改变视图按钮
        self.button = Button(master=self.master,text='改变视图(净值图)',bg='#c0c0c0',command=self.changeview)
        # 创建画布
        self.canvas = FigureCanvasTkAgg(figure, self)
        self.showGraph()
        self.button.place(relx=0,rely=0,relwidth=0.15,relheight=0.05,anchor=NW)

    def showGraph(self): #将图像映射到窗口
        for vline in self.valuelines:
            vline[0].set_alpha(1.0*(1 - self.view))
        for pline in self.percentlines:
            pline[0].set_alpha(1.0*self.view)
        fig1 = self.graph[0]
        fig2 = self.graph[1]
        if self.view:
            self.button['text'] = '改变视图(比例图)'
            # fig1.spines['right'].set_visible(False)
            # fig2.spines['right'].set_visible(False)
        else:
            self.button['text'] = '改变视图(净值图)'
            # fig1.spines['left'].set_visible(False)
            # fig2.spines['left'].set_visible(False)
        self.canvas.draw()
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
        plt.yticks([-5,-4,-3,-2,-1,0,1,2,3,4,5],['-5%','-4%','-3%','-2%','-1%','0%','1%','2%','3%','4%','5%'])
        plt.xlabel('日期')
        plt.ylabel('涨幅百分比')
        fig2 = fig1.twinx()
        self.graph.append(fig2)
        self.graph.append(fig1)
        plt.ylabel('净值')
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
                tmp.append(t)
        return tmp
        
    def addLine(self,dat,yy,percenty,name):
        # plt.style.use('dark_background')
        fig1 = self.graph[0]
        fig2 = self.graph[1]
        # fig1.axis("off") #不显示坐标轴
        minlen = 5
        for color in self.linecolor:
            if len(self.linecoloruse[color])<minlen:
                minlen = len(self.linecoloruse[color])
        for color in self.linecolor:
            if len(self.linecoloruse[color]) == minlen:
                self.coloruse.append(color)
                self.linecoloruse[color].append(self.linenum)
                # print('after append:',color,self.linecoloruse[color])
                break
        valueline = fig1.plot(dat, yy, color=self.coloruse[self.linenum], label=name,linewidth=1, linestyle='-')
        percentline = fig2.plot(dat, percenty, color=self.coloruse[self.linenum], label=name,linewidth=1, linestyle='-')
        self.valuelines.append(valueline)
        self.percentlines.append(percentline)
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
            del self.coloruse[id]
            if self.linelabel != []:
                del self.linelabel[id]
            for color in self.linecolor:
                w = 0
                for index,num in enumerate(self.linecoloruse[color]):
                    if num == id:
                        del self.linecoloruse[color][index]
                        # print('after delete:',color,self.linecoloruse[color])
                        w = 1
                        break
                if w == 1:
                    break
            # plt.legend(self.linelabel,frameon=False)
            self.linenum -= 1
        else:
            print('out of range')

    def destroy(self):
        """重写destroy方法"""
        super().destroy()

if __name__ == '__main__':
    win = Window()
    win.main() #直接调用

    #def connect(self,Window)
    #connect  lambda:viewinfo(Window)
    