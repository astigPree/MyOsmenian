
from plyer import storagepath
import json
from uuid import uuid4
import os
import socket
from typing import Union
import pickle


def myInfo() -> str :
	sentences = [ 
		"My Osmenia App Is For Fun Only So Be Careful Of What You Does Because We Are Not Responsible Of What Happen To You While Using This App" ,
		"" ,
		"Directions :" ,
		"   - Click The Gender You Want To Meet" ,
		"   - Click The Type Of Question You Want To Ask" ,
		"   - There Is Popup Will Appear " ,
		"   - Click Continue " ,
		"   - Wait For A Second" ,
		"   - Find The Place Where The Picture Taken" ,
		"   - Find The Person Who Has The Nickname" ,
		"   - Ask Him/Her The Question You Recieved" ,
		"   - And Goodluck : >"
		"\n" ,
		"Developer  : Ericson Mark A. Guanzon" ,
		"Setup Dev : Jeremiah B. Aguilar" ,
		"Designer    : Joshua R. Ametin",
		"Year Level : 3rd Year / B.S.C.S.",
		""
		]
	
	paragraph = ""
	for sentence in sentences :
		paragraph += ( "\n" + sentence )
	return paragraph
	

class DataTransfer :
	#client_info : { "id" : uuid4() , "find" : ( "M" , "F" ) , "question" : ( "love" , "friend" , "talk")
	BYTES = 32_768
	client: socket.socket = None

	def connect(self , addr : str , port : int) -> bool :
		try :
			self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.client.connect((addr , port))
		except Exception :
			return False
		return True
	
	def send(self , data : dict) -> bool :
		try :
			self.client.sendall(pickle.dumps(data))
		except (BrokenPipeError, ConnectionResetError, TimeoutError, BlockingIOError):
			return False
		except Exception :
			return False
		return True
	
	@staticmethod
	def turn_to_dict(data : list[bytes]) -> Union[ None , dict] :
		try :
			return pickle.loads(b"".join(data))
		except pickle.UnpicklingError :
			return None
		except Exception:
			return None
		
	def recived(self) -> Union[None , dict] :
		datas : list[bytes] = []
		try :
			while True:
				data : bytes = self.client.recv(self.BYTES)
				datas.append(data)
				if need_data := self.turn_to_dict(datas):
					return need_data
		except (ConnectionRefusedError, ConnectionAbortedError, TimeoutError, BlockingIOError) :
			return None
		except Exception :
			return None

	
	def close_connection(self) :
		self.client.close()

class AppData :
	__app_data = { "id" : str(uuid4()) , "used" : 0 , "leave" : 0 }
	path = os.path.join(storagepath.get_external_storage_dir() , "My Osmenia" )
	other_path = os.path.join(storagepath.get_application_dir() , "My Osmenia" )
	filename = "osmenia.ericson"
	
	inMainDir = True # if the file created in main directory
	
	def content(self , *args) :
		print(self.__app_data)
	
	def get_the_past_data(self , *args) :
		filename = os.path.join(self.path , self.filename) if self.inMainDir else os.path.join(self.other_path , self.filename)
		with open(filename , "r") as jf :
			self.__app_data = json.load(jf)

	def get_the_past_data_secured(self , *args ):
		filename = os.path.join(self.path , self.filename) if self.inMainDir else os.path.join(self.other_path , self.filename)
		os.chmod(filename, 0o444)  #  for permission
		with open(filename, "rb") as pf:
			self.__app_data = pickle.load(pf)
	
	def create(self , *args) :
		os.makedirs(self.path , exist_ok=True)
		filename = os.path.join(self.path , self.filename)
		try : 
			if not os.path.exists(filename) :
				self.save_data()
			self.get_the_past_data()
		except PermissionError : # change to other path
			self.inMainDir = False
			if not os.path.exists(filename) :
				self.save_data()
			self.get_the_past_data()

	def create_secured(self , *args):
		os.makedirs(self.path, exist_ok=True)
		filename = os.path.join(self.path, self.filename)
		try :
			if not os.path.exists(filename):
				self.save_data_secured()
			self.get_the_past_data_secured()
		except PermissionError : # change to other path
			self.inMainDir = False
			if not os.path.exists(filename):
				self.save_data_secured()
			self.get_the_past_data_secured()

	def save_data(self , *args) :
		filename = os.path.join(self.path , self.filename) if self.inMainDir else os.path.join(self.other_path , self.filename)
		with open(filename , "w") as jf:
			json.dump(self.__app_data , jf)

	def save_data_secured(self , *args):
		filename = os.path.join(self.path , self.filename) if self.inMainDir else os.path.join(self.other_path , self.filename)
		os.chmod(filename, 0o666) #  for permission
		with open(filename, "wb") as pf:
			pickle.dump(self.__app_data, pf)
	
	# ---->  list of activities 
	def get_id(self , *args) :
		return self.__app_data["id"]
		
	def used_the_app(self , *args) :
		self.__app_data["used"] += 1
	
	def leave_the_app(self , *args) :
		self.__app_data["leave"] = 1
	
	def complete_the_task(self , *args) :
		self.__app_data["leave"] = 0
	
	def get_penalized_info(self ) :
		return self.__app_data["leave"]

if __name__ == "__main__" :
	addr = "0.tcp.ap.ngrok.io"
	#addr = "localhost"
	port = 13697
	#port = 999
	client = socket.socket( socket.AF_INET , socket.SOCK_STREAM)
	try :
		print("connecting...")
		client.connect(( addr , port ))
	except Exception as e :
		print(e)



	