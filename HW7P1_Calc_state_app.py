import numpy as np

from Hw7P1_Calc_state import Steam_SI as steam  # import any of your own classes as you wish

import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

from Calc_state_gui import Ui_Form  # from the GUI file your created


class main_window(QWidget, Ui_Form):
    def __init__(self):
        """
        Constructor for the main window of the application.  This class inherits from QWidget and Ui_Form
        """
        super().__init__()  # run constructor of parent classes
        self.setupUi(self)  # run setupUi() (see Ui_Form)
        self.le_TurbineInletCondition.setEnabled(False) # set the window title

        self.Steam = steam()  # instantiate a steam object
        # create a list of the check boxes on the main window
        self.checkBoxes = [self.chk_Press, self.chk_Temp, self.chk_Quality, self.chk_Enthalpy, self.chk_Entropy,
                           self.chk_SpV]
        self.rankine = rankine(p_low)
        self.PLow = float(self.le_PLow.text())
        self.PHigh = float(self.le_PHigh.text())
        self.rdo_Quality.clicked.connect(self.setQualityOrTHigh())
        self.rdo_THigh.clicked.connect(self.setQualityOrTHigh())
        self.TurbineInlet = float(self.le_TurbineInletCondition.text())
        self.TurbineEff = float(self.le_TurbineEff.text())
        self.rankine = rankine(self.PLow, self.PHigh, self.TurbineEff)
        self.btn_Calculate.clicked.connect(self.calcRankine)
        self.le_PHigh.editingFinished.connect(self.setPHigh)
        self.le_PLow.editingFinished.connect(self.setPLow)
        self.setPHigh()
        self.setPLow()
        self.setQualityOrTHigh()
        self.calcRankine()
        self.show()

        self.assign_widgets()  # connects signals and slots
        self.show()

    def assign_widgets(self):
        self.ui.pushButton_GetWing.clicked.connect(self.GetWing)
        self.ui.pushButton_Plot.clicked.connect(self.PlotSomething)
        self.pushButton_Exit.clicked.connect(self.ExitApp)
        self.pushButton_Calculate.clicked.connect(self.Calculate)

    def Calculate(self):
        """
        Here, we need to scan through the check boxes and ensure that only two are selected a defining properties
        for calculating the state of the steam.  Then set the properties of the steam object and calculate the
        steam state.  Finally, output the results to the line edit widgets.
        :return:
        """
        # make sure only two boxes checked
        nChecked = 0
        for c in self.checkBoxes:
            nChecked += 1 if c.isChecked() else 0
        if nChecked != 2:
            return

        self.Steam.P =  float(self.le_PHigh.text()) #  read from appropriate line edit and convert to floating point number if box checked, otherwise set to None
        self.Steam.T =  steam(pressure = self.p_high, T = self.t_high, x=1, name = 'turbine inlet')  read from appropriate line edit and convert to floating point number if box checked, otherwise set to None
        self.Steam.x =  steam(pressure = self.p_low, s=self.state1.s, name = 'turbine exit')  read from appropriate line edit and convert to floating point number if box checked, otherwise set to None
        self.Steam.h =  steam(pressure = self.p_low, x=0, name = 'pump inlet')  read from appropriate line edit and convert to floating point number if box checked, otherwise set to None
        self.Steam.s =  steam(self.p_high,s=self.state3.s, name='Pump Exit') read from appropriate line edit and convert to floating point number if box checked, otherwise set to None
        self.Steam.v =  self.state3.h+self.state3.v*(self.p_high-self.p_low)  read from appropriate line edit and convert to floating point number if box checked, otherwise set to None

        self.Steam.calc()
        state = self.Steam
        # $JES MISSING CODE HERE$  set the text in each line edit and the label should tell the state 'saturated' or 'superheated'

        return

    def ExitApp(self):
        app.exit()


if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    main_win = main_window()
    sys.exit(app.exec_())



