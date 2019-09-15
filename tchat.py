# coding: latin-1

#https://python-socketio.readthedocs.io/en/latest/client.html

import time
import socketio
import curses
from curses import textpad

#message du tchat
tchatStr=""

def m_Resize(stdscr, sh, sw):
	#clear screen
	stdscr.clear()
	if sh> 10 and sw > 41:
		#redimensionnement dyn + boite d'entrée
		sh, sw = stdscr.getmaxyx()
		boxEntree = [[sh*8//10, 2], [sh-2, sw-2]]
		boxTchat = [[2, 2], [sh*8//10 -2, sw-2]]
		textpad.rectangle(stdscr, boxEntree[0][0], boxEntree[0][1], boxEntree[1][0], boxEntree[1][1])
		textpad.rectangle(stdscr, boxTchat[0][0], boxTchat[0][1], boxTchat[1][0], boxTchat[1][1])

		curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
		stdscr.attron(curses.color_pair(1))
		stdscr.addstr(sh*8//10, 5, " Message a envoyer: ")
		stdscr.addstr(2, 5, " Tchat: ")
		stdscr.attroff(curses.color_pair(1))

def m_resizeTchatMsg(message, dh, dw):
	#split message en list
	listData = message.splitlines()
	nbElemListe = len(listData)

	listFinal = []

	for i in range(nbElemListe):
		lenDataCurent = len(listData[i])
		while lenDataCurent > dw:
			listFinal.append(listData[i][:dw])
			listData[i] = listData[i][dw:]
			lenDataCurent = len(listData[i])
		listFinal.append(listData[i])

	if len(listFinal) > dh:
		del listFinal[:(len(listFinal)-dh)]
	
	return listFinal

def main(stdscr):
	sio = socketio.Client()
	sio.connect('http://localhost:2222')

	# initial settings
	curses.curs_set(0)
	stdscr.nodelay(1)
	stdscr.timeout(2)

	#dessin de la fenêtre
	sh, sw = stdscr.getmaxyx()
	m_Resize(stdscr, sh, sw)

	#chaine d'entree
	inputStr=""
	
	#quand in reçoit un message
	@sio.on('chat_message')
	def on_message(data):
		global tchatStr
		tchatStr=tchatStr+data+"\n"
		stdscr.clear()
		m_Resize(stdscr, sh, sw)


	#init listMessage
	listMessage = []
		
	while 1:

		#calcul nombre de lignes du tchat
		nombreDeLignesTchat = sh*8//10 -5

		#calcul nombre de lignes message
		nombreDeLignesMessage = sh - sh*8//10 - 3

		#calcul nombre de colonnes du tchat
		nombreDeColonnesTchat = sw-5

		if curses.is_term_resized(sh, sw) is True:
			sh, sw = stdscr.getmaxyx()
			nombreDeLignesTchat = sh*8//10 -5
			m_Resize(stdscr, sh, sw)

		# non-blocking input
		key = stdscr.getch()

		#en cas de validation
		if key == 10 and inputStr != "":
			sio.emit('chat_message', '[joueur]: ' + inputStr)
			inputStr=""
			m_Resize(stdscr, sh, sw)
			
		if key == 263:
			m_Resize(stdscr, sh, sw)
			inputStr=inputStr[0:-1]
		#stdscr.addstr(1+(sh*8//10), 3, str())
		elif key != -1 and key != curses.KEY_ENTER and key>31 and key<127 and len(inputStr) < nombreDeLignesMessage*nombreDeColonnesTchat-nombreDeLignesMessage:
			#nombreDeLignesMessage
			inputStr += str(chr(key))
			listMessage = m_resizeTchatMsg(inputStr, nombreDeLignesMessage, sw-6)
		
		#input
		if inputStr != "":
			#stdscr.addstr(1+(sh*8//10), 3, inputStr)
			listMessage = m_resizeTchatMsg(inputStr, nombreDeLignesMessage, sw-6)
			#print listTchat
			for i in range(len(listMessage)):
				stdscr.addstr(1+(sh*8//10)+i, 3, listMessage[i])
		
		#Tchat
		if tchatStr != "":
			listTchat = m_resizeTchatMsg(tchatStr, nombreDeLignesTchat, sw-6)
			#print listTchat
			#stdscr.addstr(3, 3, str(listTchat))
			for i in range(len(listTchat)):
				stdscr.addstr(3+i, 3, listTchat[i])

		stdscr.refresh()


curses.wrapper(main)


