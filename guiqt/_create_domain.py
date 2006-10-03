# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_domain.ui'
#
# Created: Pá zář 29 17:45:39 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *
from qttable import QTable


class dialog(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("dialog")



        self.textLabel3_2_6 = QLabel(self,"textLabel3_2_6")
        self.textLabel3_2_6.setGeometry(QRect(10,110,160,20))

        self.textLabel3_2_6_2 = QLabel(self,"textLabel3_2_6_2")
        self.textLabel3_2_6_2.setGeometry(QRect(10,140,160,20))

        self.textLabel3_2_6_6 = QLabel(self,"textLabel3_2_6_6")
        self.textLabel3_2_6_6.setGeometry(QRect(10,170,160,20))

        self.textLabel3_2_6_6_2 = QLabel(self,"textLabel3_2_6_6_2")
        self.textLabel3_2_6_6_2.setGeometry(QRect(10,200,160,20))

        self.textLabel3_2_6_6_2_6_2_3 = QLabel(self,"textLabel3_2_6_6_2_6_2_3")
        self.textLabel3_2_6_6_2_6_2_3.setGeometry(QRect(10,230,160,20))

        self.textLabel3_2_6_6_2_3 = QLabel(self,"textLabel3_2_6_6_2_3")
        self.textLabel3_2_6_6_2_3.setGeometry(QRect(10,330,160,20))

        self.textLabel3_2_6_6_2_6_5 = QLabel(self,"textLabel3_2_6_6_2_6_5")
        self.textLabel3_2_6_6_2_6_5.setGeometry(QRect(10,480,160,20))

        self.groupBox2_2 = QGroupBox(self,"groupBox2_2")
        self.groupBox2_2.setGeometry(QRect(180,230,360,90))

        self.textLabel3_2_6_6_2_6_2_2_2 = QLabel(self.groupBox2_2,"textLabel3_2_6_6_2_6_2_2_2")
        self.textLabel3_2_6_6_2_6_2_2_2.setGeometry(QRect(10,20,130,20))

        self.textLabel3_2_6_6_2_6_2_2_2_2 = QLabel(self.groupBox2_2,"textLabel3_2_6_6_2_6_2_2_2_2")
        self.textLabel3_2_6_6_2_6_2_2_2_2.setGeometry(QRect(10,50,130,20))

        self.period_unit = QComboBox(0,self.groupBox2_2,"period_unit")
        self.period_unit.setGeometry(QRect(150,20,85,22))

        self.period_num = QLineEdit(self.groupBox2_2,"period_num")
        self.period_num.setGeometry(QRect(150,50,200,22))

        self.textLabel3_2_6_6_2_5 = QLabel(self,"textLabel3_2_6_6_2_5")
        self.textLabel3_2_6_6_2_5.setGeometry(QRect(10,450,160,20))

        self.textLabel1_2_3_7_3_3 = QLabel(self,"textLabel1_2_3_7_3_3")
        self.textLabel1_2_3_7_3_3.setGeometry(QRect(10,10,530,90))
        self.textLabel1_2_3_7_3_3.setAlignment(QLabel.WordBreak | QLabel.AlignTop | QLabel.AlignLeft)

        self.name = QLineEdit(self,"name")
        self.name.setGeometry(QRect(180,110,360,22))

        self.registrant = QLineEdit(self,"registrant")
        self.registrant.setGeometry(QRect(180,140,360,22))

        self.pw = QLineEdit(self,"pw")
        self.pw.setGeometry(QRect(180,170,360,22))
        self.pw.setEchoMode(QLineEdit.Normal)

        self.nsset = QLineEdit(self,"nsset")
        self.nsset.setGeometry(QRect(180,200,360,22))

        self.admin = QTable(self,"admin")
        self.admin.setNumCols(self.admin.numCols() + 1)
        self.admin.horizontalHeader().setLabel(self.admin.numCols() - 1,self.__tr("admin"))
        self.admin.setNumRows(self.admin.numRows() + 1)
        self.admin.verticalHeader().setLabel(self.admin.numRows() - 1,self.__tr("1"))
        self.admin.setGeometry(QRect(180,330,360,110))
        self.admin.setNumRows(1)
        self.admin.setNumCols(1)

        self.check_val_ex_date = QCheckBox(self,"check_val_ex_date")
        self.check_val_ex_date.setGeometry(QRect(180,450,30,20))

        self.val_ex_date = QDateEdit(self,"val_ex_date")
        self.val_ex_date.setEnabled(0)
        self.val_ex_date.setGeometry(QRect(220,450,97,22))

        self.cltrid = QLineEdit(self,"cltrid")
        self.cltrid.setGeometry(QRect(180,480,360,22))

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(330,450,210,20))

        self.languageChange()

        self.resize(QSize(574,526).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.check_val_ex_date,SIGNAL("toggled(bool)"),self.val_ex_date.setEnabled)
        self.connect(self.admin,SIGNAL("valueChanged(int,int)"),self.admin_value_changed)
        self.connect(self.admin,SIGNAL("currentChanged(int,int)"),self.admin_current_changed)

        self.setTabOrder(self.name,self.registrant)
        self.setTabOrder(self.registrant,self.pw)
        self.setTabOrder(self.pw,self.nsset)
        self.setTabOrder(self.nsset,self.period_unit)
        self.setTabOrder(self.period_unit,self.period_num)
        self.setTabOrder(self.period_num,self.admin)
        self.setTabOrder(self.admin,self.check_val_ex_date)
        self.setTabOrder(self.check_val_ex_date,self.val_ex_date)
        self.setTabOrder(self.val_ex_date,self.cltrid)


    def languageChange(self):
        self.setCaption(self.__tr("Create Domain panel"))
        self.textLabel3_2_6.setText(self.__tr("<b>domain name</b>"))
        self.textLabel3_2_6_2.setText(self.__tr("<b>registrant</b>"))
        self.textLabel3_2_6_6.setText(self.__tr("password"))
        self.textLabel3_2_6_6_2.setText(self.__tr("nsset"))
        self.textLabel3_2_6_6_2_6_2_3.setText(self.__tr("period"))
        self.textLabel3_2_6_6_2_3.setText(self.__tr("admin"))
        self.textLabel3_2_6_6_2_6_5.setText(self.__tr("clTRID"))
        self.groupBox2_2.setTitle(self.__tr("period"))
        self.textLabel3_2_6_6_2_6_2_2_2.setText(self.__tr("<b>unit</b>"))
        self.textLabel3_2_6_6_2_6_2_2_2_2.setText(self.__tr("<b>number</b>"))
        self.period_unit.clear()
        self.period_unit.insertItem(self.__tr("year"))
        self.period_unit.insertItem(self.__tr("month"))
        self.textLabel3_2_6_6_2_5.setText(self.__tr("valExDate"))
        self.textLabel1_2_3_7_3_3.setText(self.__tr("<h2>create_domain</h2>\n"
"The EPP \"create\" command is used to create an instance of an object.\n"
"An object can be created for an indefinite period of time, or an\n"
"object can be created for a specific validity period."))
        self.name.setText(QString.null)
        QToolTip.add(self.nsset,self.__tr("CZ"))
        QWhatsThis.add(self.nsset,self.__tr("pokus"))
        self.admin.horizontalHeader().setLabel(0,self.__tr("admin"))
        self.admin.verticalHeader().setLabel(0,self.__tr("1"))
        self.check_val_ex_date.setText(QString.null)
        self.textLabel1.setText(self.__tr("(required for <b>enum</b> domains)"))


    def admin_value_changed(self,a0,a1):
        print "dialog.admin_value_changed(int,int): Not implemented yet"

    def admin_current_changed(self,a0,a1):
        print "dialog.admin_current_changed(int,int): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("dialog",s,c)
