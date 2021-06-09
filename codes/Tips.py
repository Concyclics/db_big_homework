#by concyclics
#Tips

import PySimpleGUI as sg

gameID='投资组合评比器'
author='制作者：陈涵、梁永豪、廖宇延'
gameVersion='版本号：2021.06.09.Beta'
#初始化的欢迎弹窗
def welcomeWindow():
	layout4welcome = [[sg.Text("欢迎使用投资组合评比器！")],
					[sg.Text(author)],
					[sg.Text(gameVersion)],
					[sg.Button("进入",key='submit'),sg.Text('   ',key='blank',size=(15,2)),sg.Quit("退出",key='quit')]]
	window=sg.Window(gameID,layout4welcome,font='微软雅黑')
	while True:
		event,value=window.Read()
		if event=='quit' or event==sg.WIN_CLOSED:
			window.Close()
			return False
		elif event=='submit':
			window.Close()
			return True
	window.Close()	


#操作成功提示弹窗
def successWindow(tips:str='获取基金成功。'):
	window=sg.Window("成功",[[sg.Text(tips)]],font='微软雅黑')
	event=window.Read()
	window.Close()

#操作失败提示弹窗
def failWindow(tips:str='获取基金失败！'):
	window=sg.Window("失败",[[sg.Text(tips)]],font='微软雅黑')
	event=window.Read()
	window.Close()





if __name__=='__main__':
#	ensure('搞比例')
#	print(conscriptWindow(100))
	welcomeWindow()
	failWindow()
	successWindow()
