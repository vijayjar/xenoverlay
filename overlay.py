import wx
import wx.xrc
from tcp_latency import measure_latency
import http.client
import json
import _thread as thread


###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):

    def __init__( self ):
        wx.Frame.__init__ ( self, None, title = u"Latency", pos = wx.Point( 0,100 ), size = wx.Size( 220 , 65 ), 
        style = wx.FRAME_SHAPED | wx.STAY_ON_TOP | wx.BORDER_NONE | wx.CLIP_CHILDREN
        )
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        self.Centre( wx.BOTH )
        self.SetPosition(wx.Point( 150, 25 ))
        self.SetTransparent( 150 )
        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWFRAME ) )
### Implement Dragging        
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown) 
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp) 
        self.Bind(wx.EVT_MOTION, self.OnMouseMove) 
        self.Bind(wx.EVT_RIGHT_UP, self.OnExit) 

        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        self.Latency = wx.StaticText( self, wx.ID_ANY, "Starting Up" , wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
        self.Latency.Wrap( -1 )
        self.Latency.SetForegroundColour( wx.Colour( 255, 255, 255 ) )
        bSizer1.Add( self.Latency, 0,wx.BOTTOM|wx.LEFT|wx.RIGHT , 7 )
        self.EventTimer = wx.StaticText( self, wx.ID_ANY, "..." , wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
        self.EventTimer.Wrap( -1 )
        self.EventTimer.SetForegroundColour( wx.Colour( 255, 255, 255 ) )
        bSizer1.Add( self.EventTimer, 0, wx.ALL, 7 )


        self.SetSizer( bSizer1 )
        self.Layout()
        self.delta = wx.Point( 150, 25 )
        self.Show(True)
        self.on_timer()
        self.on_timer_1()

    def on_timer(self):
        #text_box = self.latency_measure()
        #self.Latency.SetLabel(text_box)
        thread.start_new_thread(self.latency_measure, ())
        wx.CallLater(1000, self.on_timer)

    def on_timer_1(self):
        #event_text = self.event_timer()
        #self.EventTimer.SetLabel(event_text)
        thread.start_new_thread(self.event_timer, ())
        wx.CallLater(1000, self.on_timer_1)

    def __del__( self ):
        pass

    def event_timer(self):
        event_name = ''
        timeleft = ''
        message = ''
        try:
            connection = http.client.HTTPSConnection("www.xenrebirth.com")
            connection.request("GET", "/events.php")
            response = connection.getresponse()
            json_doc = json.loads(response.read())
            connection.close()
            keys = json_doc.keys()
            next_timestamp = min(keys)
            timeleft = json_doc[next_timestamp]['timeleft']
            event_name = json_doc[next_timestamp]['name']
            if (timeleft > 0 ) :
                hours = str(int((timeleft % (60 * 60 * 24)) / (60 * 60)))
                minutes = str(int(((timeleft % (60 * 60)) / (60))))
                seconds = str(int(((timeleft % (60)))))
                message = hours + "h , " + minutes + "m , " + seconds + "s"
            else :
                message = "SPAWNED"
        except:
            event_name = 'ERROR'
            timeleft = ''
            message = ''
        status_string = "Event Name : " + str(event_name) + "\nEvent Time : " + str(message)
        self.EventTimer.SetLabel(status_string)
        #return(status_string)


    def latency_measure(self):
        ### Ping Google Here is Internet is disconnected then Dont Proceed Further 
        status_string = ''
        google_latency = measure_latency(host='www.google.com')
        if google_latency[0] == None :
            status_string = "Internet Disconnected"
            self.SetBackgroundColour( wx.Colour( 255, 128, 128 ) )
        else :
            game_latency = measure_latency(host='74.208.168.94')
            if game_latency[0] == None :
                status_string ="Internet : " + str(int(google_latency[0])) + " ms\nGame Server Not Reachable"
                self.SetBackgroundColour( wx.Colour( 255, 128, 128 ) )
            else :    
                latency_value = str(int(game_latency[0]))
                status_string = "Internet : " + str(int(google_latency[0])) + " ms\nGame : " + latency_value + " ms"
                self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWFRAME ) )
        self.Latency.SetLabel(status_string)
        
        #return(status_string)

    def OnExit(self, evt): 
        self.Close()
    
    def OnLeftDown(self, evt): 
        self.CaptureMouse()
        pos = self.ClientToScreen(evt.GetPosition()) 
        origin = self.GetPosition()
        self.delta = wx.Point(pos.x - origin.x, pos.y - origin.y)

    def OnMouseMove(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            pos = self.ClientToScreen(evt.GetPosition()) 
            newPos = (pos.x - self.delta.x, pos.y - self.delta.y)
            self.Move(newPos)

    def OnLeftUp(self, evt): 
        if self.HasCapture(): 
            self.ReleaseMouse()

app = wx.App()
f = MyFrame1()
app.MainLoop()