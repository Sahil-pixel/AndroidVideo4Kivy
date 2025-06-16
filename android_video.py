from jnius import autoclass, PythonJavaClass, java_method
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Fbo, Callback, Rectangle

MediaPlayer=autoclass('android.media.MediaPlayer')
Surface=autoclass('android.view.Surface')
SurfaceTexture = autoclass('android.graphics.SurfaceTexture')
GL_TEXTURE_EXTERNAL_OES = autoclass(
    'android.opengl.GLES11Ext').GL_TEXTURE_EXTERNAL_OES


######Video Player implementation for Android 

class GLVideoAndroid():
    """
    Implementation of Video Player  using Android API
    """

    _update_ev = None
    _texture=None
    _mediaplayer=None
    _fbo=None

    def __init__(self,callback=None,fps=30,width=500,height=500, **kwargs):
        self.callback=callback
        self.fps=fps
        self.width=width
        self.height=height
        self._fbo=None
        self._surface_texture=None
        self._video_texture=None
        self._mediaplayer=None


    def __del__(self):
        self._release_video_player()


    def init(self,):
        self._release_video_player()
        self._mediaplayer=MediaPlayer()
        self._resolution=(self.width,self.height)

        self._video_texture = Texture(width=self.width, height=self.height,
                                       target=GL_TEXTURE_EXTERNAL_OES,
                                       colorfmt='rgba')
        
    
        self._surface_texture = SurfaceTexture(int(self._video_texture.id))
        self._surface_texture.setDefaultBufferSize(self.width,self.height)
        self._surface=Surface(self._surface_texture)
        self._mediaplayer.setSurface(self._surface)
        self._fbo = Fbo(size=self._resolution)
        self._fbo['resolution'] = (float(self.width), float(self.height))
        self._fbo.shader.fs = '''
            #extension GL_OES_EGL_image_external : require
            #ifdef GL_ES
                precision highp float;
            #endif

            /* Outputs from the vertex shader */
            varying vec4 frag_color;
            varying vec2 tex_coord0;

            /* uniform texture samplers */
            uniform sampler2D texture0;
            uniform samplerExternalOES texture1;
            uniform vec2 resolution;

            void main()
            {
                vec2 coord = vec2(tex_coord0.y * (
                    resolution.y / resolution.x), 1. -tex_coord0.x);
                gl_FragColor = texture2D(texture1, tex_coord0);
            }
        '''
        with self._fbo:
            self._texture_cb = Callback(lambda instr:
                                        self._video_texture.bind)
            Rectangle(size=self._resolution)

        

    def _release_video_player(self):
        self._stop()
        # clear texture and it'll be reset in `_update` pointing to new FBO
        self._texture = None
        del self._fbo, self._surface_texture, self._video_texture,self._mediaplayer


    def _refresh_fbo(self):
        self._texture_cb.ask_update()
        self._fbo.draw()
    


    
    def _start(self):
        #super(GLVideoAndroid, self).start()
        if self._update_ev is not None:
            self._update_ev.cancel()
        self._update_ev = Clock.schedule_interval(self._update, 1 / self.fps)

    def _stop(self):
        #super(GLVideoAndroid, self).stop()
        if self._update_ev is not None:
            self._update_ev.cancel()
            self._update_ev = None


    def _update(self, dt):
        self._surface_texture.updateTexImage()
        self._refresh_fbo()
        if self._texture is None:
            self._texture = self._fbo.texture
        if self.callback:
            self.callback(self._texture)
        if not self.is_playing():
            self._stop()
            return
         

 ##########################use this function for to control media player 
 ##https://developer.android.com/reference/android/media/MediaPlayer

    ######set data file full path 
    def set_data_source(self,file):
        self._mediaplayer.setDataSource(file)
    
    #preare media player 
    def prepare(self):
        self._mediaplayer.prepare()
    
    ###play 
    def play(self):
        self._start()
        self._mediaplayer.start()
    
    ##pause
    def pause(self):
        if self.is_playing():
            self._mediaplayer.pause()
    
    #stop media 
    def stop(self):
        self._stop()
        self._mediaplayer.stop()
    # release media player 
    def relesae(self):
        self._mediaplayer.release()

    ### get full length of video in ms 
    def get_duration(self):
        return self._mediaplayer.getDuration()
    
    #get current postion in ms 
    def get_current_postion(self):
         return self._mediaplayer.getCurrentPosition()
    
    ## get video height 
    def get_video_height(self):
        return self._mediaplayer.getVideoHeight()
   
    # get video width
    def get_video_width(self):
        return self._mediaplayer.getVideoWidth() 
    
    #get playing status
    def is_playing(self):
        return self._mediaplayer.isPlaying()
    
    #seek to any postion 
    def seek_to(self,value):
        self._mediaplayer.seekTo(value)
    
    #set volume 
    def set_volume(self,value1,value2):
        self._mediaplayer.setVolume(value1,value2)




