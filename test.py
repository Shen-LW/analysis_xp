import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


from myMessage import MyMessageBox, MessageReply
if __name__ == "__main__":
    app = QApplication(sys.argv)
    aa = MessageReply()
    w = MyMessageBox(aa, '请等待爬虫完成')
    w.show()
    # print(aa.reply())
    sys.exit(app.exec_())
