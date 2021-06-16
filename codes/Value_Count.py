
class Value_Count():
    def __init__(self):
        pass


    def total_Gains(self, NAV1, NAV2):
        '''
        输入：选定的首尾日期当天的NAV，
        返回：这段时间的累计涨幅（返回值为小数，需前端自行换算为百分比）
        '''
        return (NAV2-NAV1)/NAV1


    def annual_Yield(self, date1, NAV1, date2, NAV2):
        '''
        输入:选定的首尾日期及当天的NAV，
        返回：这段时间的年化收益率（返回值为小数，需前端自行换算为百分比）
        '''
        time = self._Date_transform(date2 - date1)
        avg_yield = ((NAV2-NAV1)/NAV1)/time
        annual_yield = avg_yield*365
        return annual_yield
    

    def max_Retracement(self, NAV, mode=0):
        '''
        输入NAV数组，
        返回：最大回撤， mode变量控制返回值，默认为0，最大回撤比例（小数），mode为1返回最大回撤的数值
        '''
        top=0
        bottom=10
        max_retrancement=0
        max_retrancement_rate=0
        find_top=False
        find_bottom=False
        it_NAV1=iter(NAV)
        mark = []
        it_mark=iter(mark)
        j = next(it_NAV1)
        try: #对NAV数据进行扫描，标记转折点
            while True:
                i=j
                j=next(it_NAV1)
                if j==None:
                    mark.append(0)
                elif j<i:
                    mark.append(-1)
                elif j==i:
                    mark.append(0)
                elif j>i:
                    mark.append(1)
        except StopIteration:
            mark.append(1)
        it_NAV2 =iter(NAV)
        for x in mark:      #找出最大回撤
            y = next(it_NAV2,0)
            if (not find_top) and (x==-1):
                top=y
                find_top=True
            elif find_top and (not find_bottom) and x==1:
                    bottom=y
                    find_bottom=True
            if find_top and find_bottom:
                if max_retrancement<top-bottom:
                    max_retrancement=top-bottom
                max_retrancement_rate=max_retrancement/top
                find_top=False
                find_bottom=False
        if mode==1:
            return max_retrancement
        elif mode==0:
            return max_retrancement_rate


    def sharpe_Ratio(self, date1, date2, NAV):
        '''
        输入：选定日期及相应时间内的NAV，
        返回：夏普比（返回小数）
        '''
        no_risk_yield=0.03045
        Sharpe_ratio = (self.annual_Yield(date1, NAV[0], date2, NAV[-1]) - no_risk_yield)/self.annual_Volatility(date1, date2, NAV)
        return Sharpe_ratio


    def annual_Volatility(self, date1, date2, NAV):
        '''
        输入：选定起止日期及这段时间内的NAV，
        返回：年化波动率（返回小数）
        '''
        time=self._Date_transform(date2 - date1)
        avg_yield=(NAV[-1]-NAV[0])/time
        print(time, avg_yield)
        dayly_yield = lambda NAV1, NAV2: (NAV2-NAV1)/NAV1
        temp=0
        it = iter(NAV)
        j=next(it)
        try:
            while True:
                i = j
                j=next(it)
                temp+=(dayly_yield(i,j)-avg_yield)**2
        except StopIteration:
            pass
        standard_deviation=(temp/time)**0.5
        annual_volatility=standard_deviation*((250)**0.5)
        return annual_volatility


    def _Date_transform(self, date):
        '''
        日期换算，输入天数对应毫秒数，返回天数
        '''
        perDay=8.64e+7
        return date/perDay
