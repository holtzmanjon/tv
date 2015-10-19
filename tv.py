import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib
from astropy.wcs import wcs
import cmap
import mmm
import pdb
 
class TV:
 
    """
    A "TV" figure
    
    Usage: import tv
           tv=TV()  to set up a new TV object (display window)
    """
 
    def __init__(self, img=np.ones([10,10]), fig=None):
    
        """
        Initialize TV object
        """
    
        # create new figure,set title, margins, and facecolor
        tv = plt.figure(figsize=(8,8.5))
        self.fig = tv
        tv.canvas.set_window_title('Image display window')
        tv.set_facecolor('darkred')

        # set up initial img and header lists
        self.current = -1
        self.images = 0
        #self.img = img
        #self.imglist = [img, img, img, img]
        self.img = None
        self.imglist = [None, None, None, None]
        self.hdr = None
        self.hdrlist = [None, None, None, None]
        self.scale = [0.,1.]
        self.scalelist = [[0.,1.],[0.,1.],[0.,1.],[0.,1.]]
        self.cmap = 'Greys_r'
        self.axlist = [None, None, None, None]

        # display image and colorbar, set colorbar default limits
        plt.axis('off')
        #self.aximage=plt.imshow(self.img,vmin=self.scale[0],vmax=self.scale[1],cmap=self.cmap,interpolation='none')
        #self.cb=tv.colorbar(self.aximage,orientation='horizontal',shrink=0.7,pad=0)
        self.cb = None
        self.cblist = [None, None, None, None]
        #plt.subplots_adjust(bottom=0.0,top=1.0,left=0.0,right=1.0)
        plt.subplots_adjust(left=-0.15,right=1.15,bottom=-0.10,top=1.00)
        self.bottom = 0.
        self.top = 1.

        # function to show image values, etc.
        def format_coord(x, y):
            x = int(x + 0.5)
            y = int(y + 0.5)

            try:
                self.img
                try:
                    hdr=self.hdr
                    mywcs=wcs.WCS(hdr)
                    pixcrd = np.array([[x,y]])
                    world=mywcs.wcs_pix2world(pixcrd,1)
                    try:
                       object=self.hdr['object']
                    except:
                       object=None
                    return "[x,y]=[%4d, %4d] val=%8.1f   [%s %s]=[%10.6f,%10.6f]   OBJECT: %s" % (x,y, self.img[y, x], mywcs.wcs.ctype[0],mywcs.wcs.ctype[1],world[0,0], world[0,1], object)
		except:
                    mywcs=None
                try:
                    return "[x,y]\n [%4i, %4i] val=%8.1f OBJECT: %s" % (x,y, self.img[y, x], object)
                except IndexError:
                    return ""
            except:
                return " [%4i, %4i]" % (x, y)

        # set this routine up for format
        ax = plt.axes()
        self.ax = ax
        ax.format_coord = format_coord

        #event handling 
        self.event = None
        self.cid = self.fig.canvas.mpl_connect('key_press_event', self.onEvent)
        self.cid2 = self.fig.canvas.mpl_connect('button_press_event', self.onEvent)
        self.cid3 = self.fig.canvas.mpl_connect('button_release_event', self.onEvent)
        self.cid4 = self.fig.canvas.mpl_connect('motion_notify_event', self.onEvent)
        self.button = False
        self.blocking = 0

    def onEvent(self, event):
        """
        Handler for all trapped events. 
        
        Arguments:
        event -- a KeyEvent
        """
        self.event = event
        subPlotNr = self.getSubPlotNr(event)        

        if event.name == 'key_press_event' :
            # keypress events: '-', '+/=', 'r'
            self.key = event.key
            if event.key == '-' or event.key == '+' or event.key == '=':
                if event.key == '-' :
                    self.current = (self.current-1) % self.images
                elif event.key == '+' or event.key == '=':
                    self.current = (self.current+1) % self.images
                self.img = self.imglist[self.current]
                self.hdr = self.hdrlist[self.current]
                self.scale = self.scalelist[self.current]
                for i in range(self.images) :
                    if i == self.current :
                        self.axlist[i].set_visible(True)
                    else :
                        self.axlist[i].set_visible(False)
                self.aximage=self.axlist[self.current]
                self.cb=self.cblist[self.current]
                #self.aximage = self.ax.imshow(self.img,
                #  vmin=self.scale[0],vmax=self.scale[1],cmap=self.cmap,interpolation='none')
                #self.cb.ax.clear()
                #self.cb = self.ax.get_figure().colorbar(self.aximage,cax=self.cb.ax,orientation='horizontal')
                #cm=cmap.remap(self.cmap,self.bottom,self.top)
                #self.aximage.set_cmap(cm)
                plt.draw()

            elif event.key == 'r' and subPlotNr == 0 :
                dim=np.shape(self.img)
                self.ax.set_xlim(-0.5,dim[1]-0.5)
                self.ax.set_ylim(-0.5,dim[0]-0.5)
                plt.draw()

            elif event.key == 'r' and subPlotNr == 1 :
                self.bottom=0.
                self.top=1.
                cm=cmap.remap(self.cmap,self.bottom,self.top)
                self.aximage.set_cmap(cm)
                plt.draw()

            if self.blocking == 1 : self.stopBlock()

        elif event.name == 'button_press_event' :
            if subPlotNr == 0 :
                # button press in image window to zoom/pan
                xlim = self.ax.get_xlim()
                ylim = self.ax.get_ylim()
                if event.button == 1 :
                    # zoom in
                    xrange = ( xlim[1]-xlim[0] )/ 2.
                    yrange = ( ylim[1]-ylim[0] )/ 2.
                elif event.button == 2 :
                    # zoom out
                    xrange = ( xlim[1]-xlim[0] )* 2.
                    yrange = ( ylim[1]-ylim[0] )* 2.
                else :
                    # pan
                    xrange = xlim[1]-xlim[0]
                    yrange = ylim[1]-ylim[0]
                if xrange < yrange and xrange < 512 : xrange = 512
                if yrange < xrange and yrange < 512 : yrange = 512
                self.ax.set_xlim(event.xdata-xrange/2.,event.xdata+xrange/2.)
                self.ax.set_ylim(event.ydata-yrange/2.,event.ydata+yrange/2.)
                plt.draw()
            elif subPlotNr == 1 :
                # flag button press in colorbar
                self.button = True
                self.xstart = event.xdata

        elif event.name == 'button_release_event' :
            self.button = False

        elif event.name == 'motion_notify_event'  and self.button :
            # if motion in colorbar with key pressed in colorbar, adjust colorbar
            if subPlotNr == 1 :
                xend = event.xdata
                if event.button == 2 :
                    diff = (xend - self.xstart)
                    self.top = self.top + diff
                    self.bottom = self.bottom + diff
                    self.xstart = xend
                else :
                    if self.xstart > 0.5 :
                      if xend > self.bottom :
                          self.top = xend
                      else :
                          self.top = self.bottom
                    else :
                      if xend < self.top :
                          self.bottom = xend
                      else :
                          self.bottom = self.top
                cm=cmap.remap(self.cmap,self.bottom,self.top)
                self.aximage.set_cmap(cm)
                plt.draw()

        
    def getSubPlotNr(self, event):
    
        """
        Get the nr of the subplot that has been clicked
        
        Arguments:
        event -- an event
        
        Returns:
        A number or None if no subplot has been clicked
        """
    
        i = 0
        axisNr = None
        for axis in self.fig.axes:
            if axis == event.inaxes:
                axisNr = i        
                break
            i += 1
        return axisNr
        
    def stopBlock(self) :
        """
        stops blocking for keypress event
        """
        if self.blocking == 1 :
            self.fig.canvas.stop_event_loop()

    def startBlock(self) :
        """
        starts blocking for keypress event
        """
        self.blocking = 1
        self.fig.canvas.start_event_loop(-1)

    def tv(self,img,min=None,max=None,cmap=None) :
        """
        main display routine: displays image with optional scaling

        Arguments:
           img: a numpy array OR a fits HDU
           min=, max= : option scaling arguments
        """

        # load data array depending on input type
        if isinstance(img, (np.ndarray)) :
            data = img
        elif isinstance(img.data, (np.ndarray)) :
            data = img.data
        else :
            print 'input must be numpy array or have data attribute that is'
            return

        # set figure and axes
        plt.figure(self.fig.number)
        plt.axes(self.ax)
        #self.fig.clf()

        # load new image data onto rolling stack
        current= (self.current+1) % 4
        self.images += 1
        if self.images > 4 : self.images = 4
        self.current = current
        self.imglist.pop(current)
        self.imglist.insert(current,data)
        self.img = data

        # save the header if we have one
        if hasattr(img,'header') :
            self.hdrlist.pop(current)
            self.hdrlist.insert(current,img.header)
            self.hdr=img.header
        else :
            self.hdr=None
      
        # get autodisplay parameters if needed, and save display params
        if min is None : 
           min = 0.
        if max is None : 
           sky = mmm.mmm(data)
           min = sky[0]-5*sky[1]
           max = sky[0]+20*sky[1]
        self.scale = [min,max]
        self.scalelist.pop(current)
        self.scalelist.insert(current,self.scale)

        if cmap != None :
           self.cmap = cmap
 
        # display image and new colorbar 
        dim=np.shape(self.img)
        self.ax.set_xlim(-0.5,dim[1]-0.5)
        self.ax.set_ylim(-0.5,dim[0]-0.5)
        self.aximage = self.ax.imshow(data,vmin=min,vmax=max,cmap=self.cmap,interpolation='nearest')
        self.axlist.pop(current)
        self.axlist.insert(current,self.aximage)
        if self.cb is None :
            self.cb = self.fig.colorbar(self.aximage,orientation='horizontal',shrink=0.7,pad=0)
            #plt.subplots_adjust(left=-0.15,right=1.15,bottom=-0.10,top=1.00)
        else :
            self.cb.ax.clear()
            self.cb = self.fig.colorbar(self.aximage,cax=self.cb.ax,orientation='horizontal')
        self.cblist.pop(current)
        self.cblist.insert(current,self.cb)

        plt.draw()
        # instead of redraw color, could replace data, but not if sizes change?
        # img.set_data()
        # img.changed()
        # plt.draw()

            
    def tvbox(self,x,y,size=None,color=None) :
        """
        displays a patch (box by default) on an image

        Args:
           x,y : center position of patch
           size : (optional) patch size
           color : (optional) patch color
        """
        plt.figure(self.fig.number)
        if size == None : size = 3
        if color == None : color = 'm'
        self.ax.add_patch(patches.Rectangle((x-size/2-0.5,y-size/2-0.5),size,size,fill=False,color=color))
        plt.draw()

    def tvclear(self) :
        """
        clears patches from image
        """
        plt.figure(self.fig.number)
        for i in range(len(self.ax.patches)) : self.ax.patches[0].remove()
        plt.draw()

    def tvmark(self) :
        """
        blocking input waits for key press in display and returns key and 
        data pixel location of keypress
        Args:
              none

        Return:
              key pressed, x data position, y data position
        """
        self.startBlock()
        return self.event.key, self.event.xdata, self.event.ydata

