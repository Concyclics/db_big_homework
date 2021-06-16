#by concyclics
class fund:
    def __init__(self,*,code:str,name='基金',found_date='1970-01-01',sharp_rate=0.0,max_down=0.0,volatility=0.0):
        self.code=code
        self.name=name
        self.found_date=found_date
        self.sharp_rate:float=sharp_rate
        self.max_down:float=max_down
        self.volatility:float=volatility
        
    def display(self):
        print('code:',self.code)
        print('name:',self.name)
        print('found_date:',self.found_date)
        print('sharp_rate:',self.sharp_rate)
        print('max_down:',self.max_down)
        print('volatility:',self.volatility)

class history:
    def __init__(self,*,code:str,day='1970-01-01',value=0.0):
        self.code=code
        self.day=day
        if value<0:
            print('Error! value < 0!')
            value=0.0
        self.value:float=value

    def display(self):
        print('code:',self.code)
        print('day:',self.day)
        print('value:',self.value)

if __name__=='__main__':
    X=fund(code='CS11033')
    X.display()
    Y=history(code='CS11033',value=233)
    Y.display()