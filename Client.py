import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QPushButton, QLineEdit, QTextEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from socket import *
import threading


USER_NICKNAME = None
s = None
connected = False
error_window = None


class MainWindow(QWidget):
    def __init__(self, title, width, height, parent=None):
        super().__init__(parent)
        self.main_grid = QGridLayout()
        self.nickname = QLabel()
        self.nickname_field = QLineEdit()
        self.connect_button = Button('Connect')
        self.groups_window = None
        self.setup(title, height, width)

    def setup(self, title, height, width):
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)
        self.setWindowTitle(title)

        self.nickname.setText('Nickname')

        self.main_grid.addWidget(self.nickname, 0, 0)
        self.main_grid.addWidget(self.nickname_field, 0, 1)
        self.main_grid.addWidget(self.connect_button, 1, 0, 1, 2)

        self.connect_button.clicked.connect(self.connect_button.click_action)

        self.setLayout(self.main_grid)
        self.show()


class GroupsWindow(QWidget):
    def __init__(self, title, width, height, parent=None):
        super().__init__(parent)
        self.main_grid = QGridLayout()
        self.nickname = QLabel()
        self.java_chat_button = Button('Join to Java Chat')
        self.cpp_chat_button = Button('Join to C++ Chat')
        self.python_chat_button = Button('Join to Python Chat')
        self.csharp_chat_button = Button('Join to C# Chat')
        self.chats = list()
        self.setup(title, height, width)

    def setup(self, title, height, width):
        global USER_NICKNAME
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)
        self.setWindowTitle(title)

        font = QFont()
        font.setBold(True)
        self.nickname.setFont(font)
        self.nickname.setText('Welcome, %s!' % USER_NICKNAME)

        self.main_grid.addWidget(self.nickname, 0, 0)
        self.main_grid.addWidget(self.java_chat_button, 1, 0)
        self.main_grid.addWidget(self.cpp_chat_button, 1, 1)
        self.main_grid.addWidget(self.python_chat_button, 2, 0)
        self.main_grid.addWidget(self.csharp_chat_button, 2, 1)

        self.java_chat_button.clicked.connect(self.java_chat_button.click_action)
        self.cpp_chat_button.clicked.connect(self.cpp_chat_button.click_action)
        self.python_chat_button.clicked.connect(self.python_chat_button.click_action)
        self.csharp_chat_button.clicked.connect(self.csharp_chat_button.click_action)

        self.setLayout(self.main_grid)
        self.show()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        global USER_NICKNAME, connected
        for chat in self.chats:
            chat.close()
        s.send(('CLOSE' + USER_NICKNAME).encode())


class ChatWindow(QWidget):
    def __init__(self, title, width, height, parent=None):
        super().__init__(parent)
        self.main_grid = QGridLayout()
        self.nickname = QLabel()
        self.chat = QTextEdit()
        self.msg_field = QLineEdit()
        self.send_button = Button('Send')
        self.setup(title, height, width)

    def setup(self, title, height, width):
        global USER_NICKNAME
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)
        self.setWindowTitle(title)

        font = QFont()
        font.setBold(True)
        self.nickname.setFont(font)
        self.nickname.setText('Your Nickname: %s' % USER_NICKNAME)

        self.chat.setReadOnly(True)
        self.chat.setFixedHeight(500)
        self.chat.setFocus()


        self.msg_field.setAlignment(Qt.AlignLeft)

        self.main_grid.addWidget(self.nickname, 0, 0)
        self.main_grid.addWidget(self.chat, 1, 0, 1, -1)
        self.main_grid.addWidget(self.msg_field, 2, 0)
        self.main_grid.addWidget(self.send_button, 2, 1)
        self.send_button.clicked.connect(self.send_button.click_action)

        self.setLayout(self.main_grid)
        self.show()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.windowTitle() == 'Java Chat':
            main_window.groups_window.java_chat_button.setDisabled(False)
        elif self.windowTitle() == 'C++ Chat':
            main_window.groups_window.cpp_chat_button.setDisabled(False)
        elif self.windowTitle() == 'Python Chat':
            main_window.groups_window.python_chat_button.setDisabled(False)
        elif self.windowTitle() == 'C# Chat':
            main_window.groups_window.csharp_chat_button.setDisabled(False)

    def add_message(self, msg):
        self.chat.insertPlainText("\n" + str(msg))


class Button(QPushButton):
    def __init__(self, text):
        super().__init__()
        self.setup(text)

    def setup(self, text):
        self.setText(text)

    def click_action(self):
        global USER_NICKNAME, s, connected
        if self.text() == 'Connect' \
                and main_window.nickname_field.text() != '':
            if ' ' in main_window.nickname_field.text():
                self.create_error_window('Your nickname cannot have any spaces!')
            else:
                USER_NICKNAME = main_window.nickname_field.text()
                s = socket(AF_INET, SOCK_STREAM)
                s.connect(('localhost', 8888))
                s.send(USER_NICKNAME.encode())
                while True:
                    data = s.recv(1024)
                    msg = data.decode()
                    if msg == 'Deliced':
                        self.create_error_window('Your nickname is already taken!')
                        s.close()
                        break
                    elif msg == 'Accepted':
                        main_window.connect_button.setDisabled(True)
                        main_window.groups_window = GroupsWindow('Client-Server Chat', 600, 150)
                        main_window.close()
                        connected = True
                        break
        elif self.text() == 'Send':
            for chat in main_window.groups_window.chats:
                if chat.send_button == self:
                    if chat.msg_field.text() != '':
                        s.send(('COMMAND ' + chat.windowTitle().split(' ')[0] + ' ' + USER_NICKNAME + ': ' + chat.msg_field.text()).encode())
                        chat.msg_field.clear()
        elif self.text() == 'Join to Java Chat':
            new_window = ChatWindow('Java Chat', 600, 600)
            main_window.groups_window.chats.append(new_window)
            main_window.groups_window.java_chat_button.setDisabled(True)
            s.send(('Java OPEN ' + USER_NICKNAME).encode())
        elif self.text() == 'Join to C++ Chat':
            new_window = ChatWindow('C++ Chat', 600, 600)
            main_window.groups_window.chats.append(new_window)
            main_window.groups_window.cpp_chat_button.setDisabled(True)
            s.send(('C++ OPEN ' + USER_NICKNAME).encode())
        elif self.text() == 'Join to Python Chat':
            new_window = ChatWindow('Python Chat', 600, 600)
            main_window.groups_window.chats.append(new_window)
            main_window.groups_window.python_chat_button.setDisabled(True)
            s.send(('Python OPEN ' + USER_NICKNAME).encode())
        elif self.text() == 'Join to C# Chat':
            new_window = ChatWindow('C# Chat', 600, 600)
            main_window.groups_window.chats.append(new_window)
            main_window.groups_window.csharp_chat_button.setDisabled(True)
            s.send(('C# OPEN ' + USER_NICKNAME).encode())

    def create_error_window(self, msg):
        global error_window
        error_window = QtWidgets.QErrorMessage()
        error_window.setWindowTitle('Error')
        error_window.showMessage(msg)


def manage_signals():
    global s, connected
    while True:
        if connected and s is not None:
            data = s.recv(1024)
            msg = data.decode(encoding='UTF=8')
            if str(msg).startswith('CLOSE'):
                connected = False
                s.close()
                break
            elif str(msg).startswith('COMMAND Java'):
                for chat in main_window.groups_window.chats:
                    if chat.windowTitle() == 'Java Chat':
                        chat.add_message(msg[12:])
            elif str(msg).startswith('COMMAND C++'):
                for chat in main_window.groups_window.chats:
                    if chat.windowTitle() == 'C++ Chat':
                        chat.add_message(msg[11:])
            elif str(msg).startswith('COMMAND Python'):
                for chat in main_window.groups_window.chats:
                    if chat.windowTitle() == 'Python Chat':
                        chat.add_message(msg[14:])
            elif str(msg).startswith('COMMAND C#'):
                for chat in main_window.groups_window.chats:
                    if chat.windowTitle() == 'C# Chat':
                        chat.add_message(msg[10:])
    app.quit()
    sys.exit()


app = QApplication(sys.argv)
main_window = MainWindow('Chat', 250, 125)
client_thread = threading.Thread(target=manage_signals)
client_thread.start()
sys.exit(app.exec_())
