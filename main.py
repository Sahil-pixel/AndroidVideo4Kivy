from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty,StringProperty,ObjectProperty
from kivy.utils import platform
from kivy.clock import Clock , mainthread
import requests
from threading import Thread
if platform=='android':
	from android.storage import app_storage_path

class VLayout(FloatLayout):
	_tex=ObjectProperty(None)
	def on_kv_post(self,*args):
		## it will download sample video from my github and play for testing perpose
		Thread(target=self.download_test_video,daemon=True).start()
	def download_test_video(self):
		self.target = join(app_storage_path(),'vid.mp4')
		r = requests.get('https://sahil-pixel.github.io/AssetsHost/vid60fps.mp4')
		with open(self.target, 'wb') as fd:
			for chunk in r.iter_content(chunk_size=128):
				fd.write(chunk)
		
		print('Downloaded done')
	
	def _init_button(self):
		if platform=='android':
			from android_video import GLVideoAndroid
			## set size and call back to get texure data 
			self._mp=GLVideoAndroid(callback=self.call,width=900,height=1280,fps=60)
			## init() initialised all surface and surface texture and fbo 
			self._mp.init()
			######set data source file
			self._mp.set_data_source(self.target)
			## preparing to play 
			self._mp.prepare()
			#self._mp.play()
			
			
			

		
		else:
			print('its linux')
	
	### i am getting all frame texture data by this call back 

	@mainthread
	def call(self,texture):
		##we are getting texture data from gpu 
		self._tex=texture
		## ask update need to update in kivy's canvas 
		self.ids.img.canvas.ask_update()

		## Getting all updates in this call back 
		print('#'*100)
		print('Get duration =',self._mp.get_duration())
		print('Get video size =',self._mp.get_video_height(),self._mp.get_video_height())
		print('Get video is playing =',self._mp.is_playing())
		print('Get cp, gd  =',self._mp.get_current_postion(),self._mp.get_duration())


	def _play(self):
		
		self._mp.seek_to(0)
		self._mp.play()
	

	def _play_pause(self):
		if self._mp.is_playing():
			self._mp.pause()
		else:
			self._mp.play()
	

	def _stop(self):
		self._mp.stop()
		### PREPARE REQUIRED BEFORE PLAYING AFTER STOP
		self._mp.prepare()
				





class MyApp(App):
	def build(self):
		return VLayout()

if __name__=="__main__":
	MyApp().run()