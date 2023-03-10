__version__ = "1.0"

from android.permissions import request_permissions , Permission , check_permission
request_permissions( [ Permission.WRITE_EXTERNAL_STORAGE , Permission.READ_EXTERNAL_STORAGE , Permission.INTERNET ])

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager , Screen
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex as ghex
from kivy.core.image import Image as CoreImage
from kivy.core.audio import SoundLoader
from kivy.lang import Builder

from threading import Thread
from io import BytesIO
from myfunctions import AppData , DataTransfer , myInfo

#===> Exit Popup
class ExitApplication(ModalView) :
	pass

#===> Gender Buttons
class Gender(Button) :
	pressed = False
	
	def endColor(self , *args) :
		if not self.pressed :
			self.color = (0 , 0, 0 , 1)
	
	def on_press(self , *args) :
		self.color = ghex("f7ca7d")
		Clock.schedule_once(self.endColor , 2)
		

#===> Questions Buttons
class Question(Button) :
	pressed = False
	
	def endColor(self , *args) :
		if not self.pressed :
			self.color = (0 , 0, 0 , 1)
	
	def on_press(self , *args) :
		self.color = ghex("f7ca7d")
		Clock.schedule_once(self.endColor , 2)
		

#===> App Information Label Widget
class Information(Label) :
	def __init__(self , **kwargs) :
		super(Information , self).__init__(**kwargs)
		Thread(target=self.setInfo).start()
	
	def setInfo(self ) :
		self.text = myInfo()
		

#===> Show Selected
class ConfirmSelected(ModalView) :
	isOpen = False
	isProcced = False
	
	def selectedData(self , text : str) :
		self.ids["info"].text = text

#===> Finding Label
class AnimateFinding(ModalView):
	findingAnimation: Clock = None
	found = False
	isOpen = False
	run_clock = None

	def __init__(self, **kwargs):
		super(AnimateFinding, self).__init__(**kwargs)

	def on_open(self, *args):
		self.isOpen = True
		Clock.schedule_interval(self.stopAnimate, 1 / 60)
		Clock.schedule_once(self.animate, 1)

	def stopAnimate(self, *args):
		if self.found:
			self.isOpen = False
			Clock.schedule_once(self.closedPopup, 1)

	def closedPopup(self, *args):
		self.dismiss()
		Clock.schedule_once(self.resetData, 1 / 2)
		self.found = False

	def resetData(self, *args):
		self.ids["mytext"].text = "Finding"

	def animate(self, *args):
		if not self.found:
			if "Finding" in self.ids["mytext"].text:
				if self.ids["mytext"].text == "Finding . . . . .":
					self.ids["mytext"].text = "Finding"
				else:
					self.ids["mytext"].text += " ."
			Clock.schedule_once(self.animate, 1)
		
# ====> Screen 1 : Finding Partner
class FindingPartner(Screen) :

	ADDR = "localhost"
	PORT = 4567

	gender = ""
	question = ""
	
	dataIsSent = None # Result : str
	transactionComplete = False  # Check if the transaction complete
	
	dataTransfer = DataTransfer()
	
	def __init__(self , **kwargs) :
		super(FindingPartner , self).__init__(**kwargs)
		self.confirmPopup = ConfirmSelected()
		self.findingPopup = AnimateFinding()
		Clock.schedule_interval(self.checkIsReady , 1/30)
		Thread(target=self.bindingAttrib).start()
	
	def bindingAttrib(self) :
		self.confirmPopup.bind(on_dismiss=self.resetData)
	
	def checkIsReady(self , *args) :
		condition =  self.gender != "" and self.question != ""
		
		if condition and not self.confirmPopup.isOpen :
			self.confirmPopup.selectedData( f"( {self.gender} , {self.question.capitalize()} )")
			self.confirmPopup.open()
			self.confirmPopup.isOpen = True
		
		if self.confirmPopup.isProcced and not self.findingPopup.isOpen:
			self.confirmPopup.isProcced = False
			Thread( target=self.sendTheData , args=(self.gender , self.question) ).start()
			self.confirmPopup.dismiss()
			self.findingPopup.open()

		if self.dataIsSent:
			self.findingPopup.found = True
			self.findingPopup.ids["mytext"].text = self.dataIsSent
			self.dataIsSent = None

		if self.transactionComplete:
			self.parent.transition.direction = 'right'
			self.parent.current = "screen2"
	
	def resetData(self , *args) :
		self.confirmPopup.isOpen = False
		self.gender = ""
		self.question = ""
	
	def sendTheData(self , gender : str , question : str )  :
		data = { "id" : self.parent.appData.get_id() , "find" : gender , "question" : question }
		try :
			if not self.dataTransfer.connect( self.ADDR , self.PORT) :
				raise Exception("ConnectionError")
		except Exception :
			self.dataIsSent = "ConnectionError"
			self.dataTransfer.close_connection()
			return

		if not self.dataTransfer.send(data):
			self.dataIsSent = "TransferError"
			self.dataTransfer.close_connection()
			return

		self.parent.server_data = self.dataTransfer.recived()
		print(self.parent.server_data)
		if not self.parent.server_data:
			self.dataIsSent = "RecievedError"
			self.dataTransfer.close_connection()
			return

		if "find" in self.parent.server_data.keys():
			self.dataIsSent = self.parent.server_data["find"]
			self.dataTransfer.close_connection()
			return

		if self.gender == "F":
			confirmation = self.dataTransfer.recived()
			if not confirmation:
				self.dataIsSent = "RecievedError"
				self.dataTransfer.close_connection()
				self.parent.server_data = {}
				return

		self.dataTransfer.close_connection()
		self.dataIsSent = "Lets Enjoy"
		self.transactionComplete = True
	
	def on_pre_leave(self , *args):
		self.dataIsSent = None
		self.gender = ""
		self.question = ""
			
#===> App Information Label Widget
class ListOfQuestions(Label) :
	def __init__(self , **kwargs) :
		super(ListOfQuestions , self).__init__(**kwargs)
		
	def setQuestions(self , questions : list) :
		for n , question in enumerate(questions):
			self.text += ( f"{n+1: }. " + question + "\n" )

#===> Closed Widget
class BackButton(Button) :
	pressed = False
	
	def endColor(self , *args) :
		if not self.pressed :
			self.color = (0 , 0, 0 , 1)
	
	def on_press(self , *args) :
		self.color = ghex("f7ca7d")
		Clock.schedule_once(self.endColor , 2)
		
#===> Closed Widget
class OkeyToBack(ModalView):
	pass

# ====> Screen 2 : Talking To The Partner
class TalkingPartner(Screen) :
	seconds = 120
	isUsed = False
	displayed = False
	
	def __init__(self , **kwargs) :
		super(TalkingPartner , self).__init__(**kwargs)
		self.myPopup = OkeyToBack()
		Thread(target=self.bindingAttrib).start()
		Clock.schedule_interval(self.reduceMyTime , 1)
		Clock.schedule_interval( self.displayTheServerData , 1/30)
	
	def bindingAttrib(self) :
		self.ids["mytime"].text = f"Time : {self.seconds}s"
	
	def on_pre_enter(self , *args):
		self.isUsed = True
		self.parent.appData.leave_the_app()

	def on_pre_leave(self, *args):
		self.isUsed = False
		self.displayed = False
		self.ids["mytime"].text = f"Time : {self.seconds}s"
		self.ids["back"].disabled = True
		self.ids["back"].opacity = 0
		self.parent.server_data = {}
		self.parent.appData.complete_the_task()
	
	def reduceMyTime(self , *args) :
		if self.isUsed :
			mytime = self.ids["mytime"].text[7:][:-1]
			if mytime != "0" and self.ids["mytime"].text != "Time : Done"  :
				second = str( int(mytime) - 1 )
				self.ids["mytime"].text = f"Time : {second}s"
			if mytime == "0" :
				self.myPopup.open()
				self.ids["back"].disabled = False
				self.ids["back"].opacity = 1
				self.ids["mytime"].text = "Time : Done"
	
	def displayTheServerData(self , *args) :
		#data = { "nickname" : tuple ( finder , finding ) , "pic data" : pic_data , "pic ext" : ext , "questions" : questions [list] , "qoute" : qoute }
		if self.parent : # Check If The Screen Manager Holding This Screen
			data : dict = self.parent.server_data
		else :
			data = {}
			
		if data and not self.displayed and self.isUsed:
			
			nickname = f"{data['nickname'][0].capitalize()} finding {data['nickname'][1].capitalize()} "
			self.ids["nickname"].text = nickname
			
			buf = BytesIO(data["pic data"])
			cim = CoreImage( buf , ext=data["pic ext"])
			self.ids["place"].texture = cim.texture
			
			self.ids["questions"].setQuestions(data["questions"])
			
			self.ids["qoute"].text = data["qoute"]
			
			self.displayed = True

# ====> Penalized Widget
class Penalized(ModalView) :
	second = 120
	isReady = False
	
	def __init__(self , **kwargs) :
		super(Penalized , self).__init__(**kwargs)
		Clock.schedule_interval(self.reducedTheTime , 1)
	
	def reducedTheTime(self , *args) :
		if self.isReady:
			second = int(self.ids["mytime"].text[12:][:-1])
			if second != 0 :
				self.ids["mytime"].text = f"Penalized : {second - 1}s"
			else :
				self.dismiss()

# ====> Penalized Widget
class CheckPermission(ModalView) :
	isOpen = False

# ====> ScreenManager
class MainWidget(ScreenManager) :
	appData = AppData()

	granted = False
	manage_data = False
	server_data : dict = {}
	sound = None
	sound_stop = False
	
	def __init__(self , **kwargs) :
		super(MainWidget , self).__init__(**kwargs)
		self.closePopup = ExitApplication()
		self.penalizedPopup = Penalized()
		self.penalizedPopup.bind( on_dismiss = self.completePenalized )
		self.permissionPopup = CheckPermission()

		self.add_widget( FindingPartner( name = "screen1"))
		self.add_widget( TalkingPartner( name = "screen2"))
		Clock.schedule_interval(self.starting , 1 / 50)
		
	def starting(self, interval ):
		self.checkingPermission()
		if self.granted and not self.manage_data :
			self.manage_data = True
			Clock.schedule_once(self.startPlayingMusic)
			Clock.schedule_once(self.appData.create_secured )
			Clock.schedule_once(self.appData.used_the_app , 3)
			Clock.schedule_once(self.isPenalized , .5)

	def isPenalized(self , *args) :
		if self.appData.get_penalized_info() == 1 :
			self.penalizedPopup.isReady = True
			self.penalizedPopup.open()
	
	def completePenalized(self , *args) :
		self.appData.complete_the_task()
		self.appData.save_data()
	
	def closeApplication(self) :
		if self.current == "screen1" and not self.get_screen("screen1").findingPopup.isOpen :
			self.closePopup.open()

	def checkingPermission(self):
		if self.granted:
			return
		if check_permission('android.permission.WRITE_EXTERNAL_STORAGE') and check_permission('android.permission.READ_EXTERNAL_STORAGE') :
			self.granted = True
		if self.granted:
			if self.permissionPopup.isOpen:
				self.permissionPopup.isOpen = False
				self.permissionPopup.dismiss()
			return
		if not self.permissionPopup.isOpen:
			self.permissionPopup.isOpen = True
			self.permissionPopup.open()

	def startPlayingMusic(self, *args):
		try:
			self.sound = SoundLoader.load("Osmenian.mp3")
		except (AttributeError, OSError, Exception) as err:
			return
		if self.sound:
			print(self.sound)
			self.sound.loop = True
			self.sound.volume = .5
			self.sound.play()

	def stopPlayingMusic(self , *args):
		if self.sound and not self.sound_stop :
			self.sound.stop()
			self.sound_stop = True

	def resumeMusic(self , *args):
		if self.sound and self.sound_stop :
			self.sound.play()
			self.sound_stop = False


# ====> App
class MyOsmenianApp(App) :
	
	def on_pause(self) :
		self.root.stopPlayingMusic()
		if self.root.granted:
			Clock.schedule_interval(self.root.get_screen("screen2").reduceMyTime , 1)

	def on_resume(self):
		self.root.resumeMusic()
		
	def on_stop(self) :
		if self.root.granted :
			self.root.appData.save_data_secured()

	def on_start(self):
		request_permissions( [ Permission.INTERNET , Permission.READ_EXTERNAL_STORAGE , Permission.WRITE_EXTERNAL_STORAGE ])

	def build(self) :
		Window.bind(on_keyboard=self.key_input)
		return Builder.load_file("MyDesign.kv")
	
	def key_input(self , window , key , scancode , codepoint , modifier) :
		if key == 27 :
			self.root.closeApplication()
			return True
		else :
			return False
	
MyOsmenianApp().run()