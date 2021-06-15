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
from tkinter.simpledialog import askstring
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from itertools import chain
from pypinyin import pinyin, Style
import fundation
import databaseOP
# import fundation
import creeper
import Tips

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
    linecoloruse = {}
    coloruse = []
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
        bottomlb = Label(s.root,text = '(点击图像 可显示离点击处最近的基金数据)',bg='black',fg='white')
        bottomlb.place(relx=0.15,rely=0.97,relwidth=0.25,relheight=0.05,anchor=CENTER)
        fm1 = Frame(s.root, bg='black', width=screenwidth*0.4, height=screenheight*0.4)
        fm2 = Frame(s.root, bg='black', width=screenwidth*0.4, height=screenheight*0.3)
        fm3 = Frame(s.root, bg='white', width=screenwidth*0.4, height=screenheight*0.3)
        fm2.place(x=0,rely=0.3,relwidth=0.3,relheight=0.41,anchor=W)
        fm3.place(x=0,rely=0.75,relwidth=0.3,relheight=0.4,anchor=W)
        fm1.place(relx=0.65,rely=0.53,relwidth=0.69,relheight=0.85,anchor=CENTER)

        s.start_date=tk.StringVar() #开始日期
        s.start_date.set(s.str_start_date)
        s.end_date=tk.StringVar()	#结束日期
        s.end_date.set(s.str_end_date)

        s.chart = Chart(fm1)
        for color in s.chart.linecolor:
            s.linecoloruse[color] = []
        s.chart.canvas.mpl_connect('button_press_event', s.viewinfo)
        s.changeViewBt = Button(fm1,text='改变视图(净值图)',bg='#c0c0c0',command=s.changeView)
        s.changeViewBt.place(relx=0,rely=0,relwidth=0.15,relheight=0.05,anchor=NW)
        s.treeview = s.tree(fm2,'基金名称','夏普率','最大回撤','年化波动率',85,20,25,40)
        s.detail = s.tree(fm3,'基金名称','日期','净值','总涨幅',85,40,25,20)
        updateinfo1 = Label(s.root,text = '若未更新x-sign,',bg='black',fg='white')
        updateinfo2 = Label(s.root,text = '更新数据前可输入新的x-sign',bg='black',fg='white')
        updatebt = Button(s.root,text='更新数据',bg='#c0c0c0',command=s.update)
        updateinfo1.place(relx=0.92,rely=0.03,relwidth=0.4,relheight=0.04,anchor=CENTER)
        updateinfo2.place(relx=0.92,rely=0.07,relwidth=0.4,relheight=0.04,anchor=CENTER)
        updatebt.place(relx=0.98,rely=0.1,relwidth=0.1,relheight=0.05,anchor=NE)
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

        delbutton = Button(s.root,text='删除上表选中基金',bg='#c0c0c0',command=s.cancelLine)
        delallbutton = Button(s.root,text='删除所有选中基金',bg='#c0c0c0',command=s.cancelallLine)
        delbutton.place(relx=0,rely=0.525,relwidth=0.1,relheight=0.04,anchor=W)
        delallbutton.place(relx=0.30,rely=0.525,relwidth=0.1,relheight=0.04,anchor=E)
        s.getdata()

    def __del__(s):
        s.root.quit()

    def tree(s,master,title1,title2,title3,title4,w1,w2,w3,w4):
        scrollBar = Scrollbar(master,orient=VERTICAL)
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
        tree.heading('1',text=title1,command=lambda:orderby(1))
        tree.heading('2',text=title2,command=lambda:orderby(2))
        tree.heading('3',text=title3,command=lambda:orderby(3))
        tree.heading('4',text=title4,command=lambda:orderby(4))
        sequence = [0,0,0,0]
        scrollBar.config(command=tree.yview)
        def to_pinyin(s):
            '''转拼音
            :param s: 字符串或列表
            :type s: str or list
            :return: 拼音字符串
            >>> to_pinyin('你好吗')
            'ni3hao3ma'
            >>> to_pinyin(['你好', '吗'])
            'ni3hao3ma'
            '''
            return ''.join(chain.from_iterable(pinyin(s, style=Style.TONE3)))
        def orderby(n:int):
            w = 1
            while w:
                w = 0
                for index in range(len(tree.get_children())):
                    if index + 1 < len(tree.get_children()):
                        if sequence[n-1]: #降序
                            if n == 1:
                                if to_pinyin(tree.item(tree.get_children()[index],'values')[n-1]) < to_pinyin(tree.item(tree.get_children()[index + 1],'values')[n-1]):
                                    tree.move(tree.get_children()[index],'',index=index+1)
                                    w = 1
                            else:
                                try:
                                    if float(tree.item(tree.get_children()[index],'values')[n-1].strip('%')) < float(tree.item(tree.get_children()[index + 1],'values')[n-1].strip('%')):
                                        tree.move(tree.get_children()[index],'',index=index+1)
                                        w = 1
                                except ValueError:
                                    if tree.item(tree.get_children()[index],'values')[n-1] < tree.item(tree.get_children()[index + 1],'values')[n-1]:
                                        tree.move(tree.get_children()[index],'',index=index+1)
                                        w = 1
                        else: #升序
                            if n == 1:
                                if to_pinyin(tree.item(tree.get_children()[index],'values')[n-1]) > to_pinyin(tree.item(tree.get_children()[index + 1],'values')[n-1]):
                                    tree.move(tree.get_children()[index],'',index=index+1)
                                    w = 1
                            else:
                                try:
                                    if float(tree.item(tree.get_children()[index],'values')[n-1].strip('%')) > float(tree.item(tree.get_children()[index + 1],'values')[n-1].strip('%')):
                                        tree.move(tree.get_children()[index],'',index=index+1)
                                        w = 1
                                except ValueError:
                                    if tree.item(tree.get_children()[index],'values')[n-1] > tree.item(tree.get_children()[index + 1],'values')[n-1]:
                                        tree.move(tree.get_children()[index],'',index=index+1)
                                        w = 1
            sequence[n-1] = 1 - sequence[n-1]
        return tree

    def _caldata(s):
        for code in s.originalfund:
            #计算最大回撤率
            max = 0
            tempmax = 0
            for index in range(len(s.coderecord[s.codekey[code]][2])):
                for i in range(index + 1,len(s.coderecord[s.codekey[code]][2])):
                    temp = 100.0*(s.coderecord[s.codekey[code]][2][index] - s.coderecord[s.codekey[code]][2][i])/s.coderecord[s.codekey[code]][2][index]
                    if temp > tempmax:
                        tempmax = temp
                if tempmax > max:
                    max = tempmax
            s.coderecord[s.codekey[code]][0][2] = '%.2f'%max+'%'
        # 更新原表    
        for child in s.treeview.get_children(): 
                s.treeview.delete(child)
        for index,code in enumerate(s.fundINview):
            s.treeview.insert('','end',values=s.coderecord[s.codekey[code]][0],tags=(s.coloruse[index],index))

    def getvaluelist(s,fund:fundation.fund,code):
        valuelist = []
        valuelist.append(fund.name)
        valuelist.append('%.2f'%fund.sharp_rate+'%')
        valuelist.append('%.2f'%fund.max_down+'%')
        valuelist.append('%.2f'%fund.volatility+'%')
        s.coderecord[s.codekey[code]].append(valuelist)
    
    def gethistory(s,DB,code):
        x = []
        y = []
        for history in databaseOP.getHistory(DB,code,s.str_start_date,s.str_end_date):
            x.append(history.day)
            y.append(history.value)
        s.coderecord[s.codekey[code]].append(x)
        s.coderecord[s.codekey[code]].append(y)
        s.coderecord[s.codekey[code]].append(s.chart.calpercent(y))

    def getdata(s):
        for code in s.originalfund:
            while len(s.coderecord[s.codekey[code]]) > 1:
                s.coderecord[s.codekey[code]].pop()
            with databaseOP.DBconnect(password='19260817') as DB:
                if len(s.coderecord[s.codekey[code]]) < 1:
                    fund = databaseOP.getFund(DB,code)
                    s.getvaluelist(fund,code)
                s.gethistory(DB,code)
        s._caldata()

    def update(s):
        xsign = askstring("请检查x-sign", "若x-sign未更新,请输入最新x-sign:")
        # print(xsign)
        if xsign != None: #点击cancel 或 关闭按钮
            if xsign != '': # 输入为空
                temp = creeper.header_for_qieman
                creeper.header_for_qieman['x-sign'] = xsign
            if creeper.getFund(creeper.qieman[0]) == False: # x-sign不正确
                Tips.failWindow("x-sign有误。")
                if xsign != '': # 输入为空
                    creeper.header_for_qieman = temp
                return False
            with databaseOP.DBconnect(password='19260817') as DB:
                databaseOP.update_mult(DB)

            s.getdata() #重新获取数据，可以优化配合update_mult只更新小部分数据，如果重新获取开销太大，运行很慢

            if len(s.fundINview) != 0:
                s.reshowGraph() #重新显示图线

    def addColor(s):
        minlen = 5
        for color in s.chart.linecolor:
            if len(s.linecoloruse[color])<minlen:
                minlen = len(s.linecoloruse[color])
        for color in s.chart.linecolor:
            if len(s.linecoloruse[color]) == minlen:
                s.coloruse.append(color)
                s.linecoloruse[color].append(s.chart.linenum)
                # print('after append:',color,self.linecoloruse[color])
                break
        # print(s.coloruse)
        # print(s.linecoloruse)

    def delColor(s,id):
        if s.chart.linenum >= 1 and id < s.chart.linenum:
            del s.coloruse[id]
            for color in s.chart.linecolor:
                w = 0
                for index,num in enumerate(s.linecoloruse[color]):
                    if num == id:
                        del s.linecoloruse[color][index]
                        # print('after delete:',color,self.linecoloruse[color])
                        w = 1
                        break
                if w == 1:
                    break
            for color in s.chart.linecolor:
                for index,num in enumerate(s.linecoloruse[color]):
                      if num > id:
                          s.linecoloruse[color][index] -= 1
        # print(s.coloruse)
        # print(s.linecoloruse)

    def viewinfo(s,event):
        if s.chart.linenum != 0 and event.xdata != None:
            if s.chart.vline != []: #清除原有竖线
                s.chart.vline[1].set_alpha(0.0)
                s.chart.vline.clear()
            for child in s.detail.get_children(): #清除表格
                s.detail.delete(child)
            vl = plt.axvline(x=event.xdata, color = "w", linestyle = "dashed")
            s.chart.vline.append(event.xdata)
            s.chart.vline.append(vl)
            # print(s.chart.vline)
            starttime=time.strptime(s.str_start_date,'%Y-%m-%d')
            starttime=dt.date(starttime[0],starttime[1],starttime[2])
            for index,code in enumerate(s.fundINview):
                for x,y,z in zip(s.coderecord[s.codekey[code]][1],s.coderecord[s.codekey[code]][2],s.coderecord[s.codekey[code]][3]):
                    # print((x - s.coderecord[s.codekey[code]][1][0]).days,int(event.xdata+0.5) - (s.coderecord[s.codekey[code]][1][0] - dt.date(1970,1,1)).days)
                    strx = dt.datetime.strftime(x, '%Y-%m-%d')
                    if (x - s.coderecord[s.codekey[code]][1][0]).days >= int(event.xdata+0.5) - (s.coderecord[s.codekey[code]][1][0] - dt.date(1970,1,1)).days:
                        s.detail.insert('','end',values=[s.coderecord[s.codekey[code]][0][0],strx,y,'%.2f'%z+'%'],tags=(s.coloruse[index],index))
                        break
            s.chart.showgraph()
      
    def reshowGraph(s):  # 重新增加图线，改变按钮文字
        s.chart.cleargraph() #清理原图
        if s.chart.view: # 比例图
            s.changeViewBt['text'] = '改变视图(比例图)'
            for code in s.fundINview: # 重新加上图线
                s.chart.addLine(s.coderecord[s.codekey[code]][1],s.coderecord[s.codekey[code]][3],s.coderecord[s.codekey[code]][0][0],s.coloruse[s.chart.linenum]) #valuelist
        else:
            s.changeViewBt['text'] = '改变视图(净值图)'
            for code in s.fundINview: # 重新加上图线
                s.chart.addLine(s.coderecord[s.codekey[code]][1],s.coderecord[s.codekey[code]][2],s.coderecord[s.codekey[code]][0][0],s.coloruse[s.chart.linenum])
        if s.chart.vline != []:
            del s.chart.vline[1]
            vl = plt.axvline(x=s.chart.vline[0], color = "w", linestyle = "dashed")
            # print('redraw')
            s.chart.vline.append(vl)
        s.chart.showgraph()

    def addGraph(s):#增加选中记录
        code = s.comboxlist.get() #选择框里的内容
        if code == '':
            return False
        if code not in s.originalfund: #不在预选基金里
            fund = creeper.getFund(code)
            if fund == False: #code不正确
                Tips.failWindow("找不到该基金！")
                return fund
            Tips.successWindow("正在写入数据……")
            s.originalfund.append(code)
            s.originalfund.sort()
            s.comboxlist["values"]=s.originalfund
            with databaseOP.DBconnect(password='19260817') as DB:
                databaseOP.addFund(DB,fund)
                s.codekey[code] = len(s.codekey)
                s.coderecord.append([])
                s.getvaluelist(fund,code)
                historylist = creeper.getHistory(code,5000)
                for history in historylist:
                    databaseOP.addHistory(DB,history)
                s.gethistory(DB,code)
                
        if code not in s.fundINview:
            s.fundINview.append(code)
            s.addColor()
            s.treeview.insert('','end',values=s.coderecord[s.codekey[code]][0],tags=(s.coloruse[s.chart.linenum],s.chart.linenum))
            if s.chart.view: #比例图啊
                s.chart.addLine(s.coderecord[s.codekey[code]][1],s.coderecord[s.codekey[code]][3],s.coderecord[s.codekey[code]][0][0],s.coloruse[s.chart.linenum])
            else:
                s.chart.addLine(s.coderecord[s.codekey[code]][1],s.coderecord[s.codekey[code]][2],s.coderecord[s.codekey[code]][0][0],s.coloruse[s.chart.linenum])
            # s.combostyle.configure('Treeview',background = 'gray',selectbackground = 'red',foreground=s.chart.linecolor[s.chart.linenum%8],fieldbackground = 'black')
            s.chart.showgraph()

    def cancelLine(s):#删除选中记录
        if s.treeview.selection() != ():
            for selected in s.treeview.selection():
                id = int(s.treeview.item(selected,'tags')[1])
                # print(i,type(i))
                s.delColor(id)
                s.chart.delLine(id)
                del s.fundINview[id]
                if s.detail.get_children() != ():
                    for child in s.detail.get_children():
                        if s.detail.item(child,'tags') == s.treeview.item(selected,'tags'):
                            s.detail.delete(child)
                        elif int(s.detail.item(child,'tags')[1]) > id:
                            s.detail.item(child,tags=(s.detail.item(child,'tags')[0],int(s.detail.item(child,'tags')[1])-1))
                s.treeview.delete(selected)
                for item in s.treeview.get_children():
                    if int(s.treeview.item(item,'tags')[1]) > id:
                        s.treeview.item(item,tags=(s.treeview.item(item,'tags')[0],int(s.treeview.item(item,'tags')[1])-1))
            if s.fundINview == []:
                s.chart.cleargraph()
            s.chart.showgraph()

    def changeView(s):
        s.chart.view = 1 - s.chart.view
        # print('view changed')
        s.reshowGraph()

    def cancelallLine(s): # 删除全部基金记录,清理图像和详细信息表格
        for item in s.treeview.get_children():
            s.treeview.delete(item)
        s.fundINview.clear()
        # 需要删除颜色了
        tmp = s.chart.linenum
        while tmp > 0: #删除所有颜色
            s.delColor(tmp - 1)
            tmp -= 1
        s.chart.cleargraph()
        s.chart.vline.clear()
        for child in s.detail.get_children(): #清除表格
            s.detail.delete(child)
        s.chart.showgraph()

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
        if sdate >= edate or (s.str_start_date == sdate and s.str_end_date == edate): #比较开始日期和结束日期的大小
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
                s.chart.vline.clear()
                for child in s.detail.get_children(): #清除表格
                    s.detail.delete(child)
                s.reshowGraph()

    def main(s):
        s.root.mainloop()
        

class Chart(Frame):
    linenum = 0
    linecolor = ['red','lime','blue','cyan','magenta','yellow','purple','white']
    linelabel = [[],[]]
    lines = []
    vline = []
    percentlines = []
    graph = []
    view = 0
    def __init__(self, master=None):
        super().__init__(master)  # 调用父类的初始化方法
        self.master = master
        self.pack(side=TOP, fill=BOTH, expand=1)  # 此处填充父窗体
        self.getlabel()
        self.create_matplotlib()
        self.createWidget(self.figure)

    def createWidget(self, figure):
        # 创建画布
        self.canvas = FigureCanvasTkAgg(figure, self)
        self.showgraph()

    def cleargraph(self): #清理原图，建立新的坐标系
        while self.linenum > 0: #删除原有的图线
            self.delLine(self.linenum - 1)
        # print(self.lines)
        self.graph.clear()
        plt.clf()
        # 重新创建一副子图
        fig = plt.subplot(111)
        if self.view:
            fig.set_yticks(range(-40,200,20))#设置比例图y轴的刻度范围
            plt.yticks(self.linelabel[0],self.linelabel[1])
        fig.spines['top'].set_visible(False)
        fig.spines['right'].set_visible(False)
        fig.grid(which='major', axis='y',color='gray',linestyle='--')
        self.graph.append(fig)

    def showgraph(self): #将图像映射到画布上
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
        self.cleargraph()

    def getlabel(self):
        for i in range(-40,200,20):
            self.linelabel[0].append(i)
            self.linelabel[1].append('%d'%i+'%')
        # print(self.linelabel)

    def calpercent(self,yy):
        if yy[0] == 0:
            print('False')
            return False
        tmp = [0.0]
        first = yy[0]
        for index in range(len(yy)):
            if index >= 1:
                t = 100.0*((yy[index]-first)/first)
                t = round(t+0.005,2)
                tmp.append(t)
        # print(len(yy),len(tmp))
        return tmp
        
    def addLine(self,dat,yy,name,coloruse):
        # plt.style.use('dark_background')
        fig = self.graph[0]
        line = fig.plot(dat, yy, color=coloruse, label=name,linewidth=1, linestyle='-')
        self.lines.append(line)
        self.linenum += 1

    def delLine(self,id):
        if self.linenum >= 1 and id < self.linenum:
            for index,line in enumerate(self.lines):
                line[0].set_alpha(1.0*(index != id))
            del self.lines[id]
            self.linenum -= 1
        else:
            print('out of range')

    def destroy(self):
        """重写destroy方法"""
        super().destroy()

if __name__ == '__main__':
    win = Window()
    win.main() #直接调用