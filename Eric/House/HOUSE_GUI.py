# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MyFrameHouse
###########################################################################

class MyFrameHouse ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"HOUSE", pos = wx.DefaultPosition, size = wx.Size( 800,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText_url = wx.StaticText( self, wx.ID_ANY, u"請輸入網址", wx.DefaultPosition, wx.Size( -1,-1 ), wx.ALIGN_CENTER_HORIZONTAL )
		self.m_staticText_url.Wrap( -1 )

		self.m_staticText_url.SetFont( wx.Font( 28, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "新細明體" ) )

		bSizer1.Add( self.m_staticText_url, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_textCtrl_url = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1.Add( self.m_textCtrl_url, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_textCtrl_status = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL|wx.TE_MULTILINE|wx.TE_READONLY )
		self.m_textCtrl_status.SetFont( wx.Font( 20, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "新細明體" ) )
		self.m_textCtrl_status.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

		bSizer1.Add( self.m_textCtrl_status, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_button_ok = wx.Button( self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1.Add( self.m_button_ok, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_button_exit = wx.Button( self, wx.ID_ANY, u"EXIT", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1.Add( self.m_button_exit, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_button_ok.Bind( wx.EVT_BUTTON, self.OK )
		self.m_button_exit.Bind( wx.EVT_BUTTON, self.EXIT )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OK( self, event ):
		event.Skip()

	def EXIT( self, event ):
		event.Skip()


