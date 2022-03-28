from HW7P2_Rankine_GUI import Ui_Form
from HW7P2_Rankine import rankine
from HW7P2_steam import steam
from PyQt5 import uic
import sys
from PyQt5 import QtWidgets as qtw

class MainWindow(qtw.QWidget, Ui_Form, rankine):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.le_TurbineInletCondition.setEnabled(False)

        self.figure=Figure(figsize=(5,10),tight_layout=True, frameon=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot()
        self.gb_Output.layout().addWidget(self.canvas,6,0,1,6)
        #slots
        self.le_PHigh.editingFinished.connect(self.setPHigh) #triggered by hitting enter or leaving editing box
        self.le_PLow.editingFinished.connect(self.setPLow) #same as line above
        self.le_TurbineEff.editingFinished.connect(self.checkTurbineEffRange)
        self.rdo_Quality.toggled.connect(self.setQualityOrTHigh)#triggered when state of the radio button changes
        self.btn_Calculate.clicked.connect(self.calcRankine)

        self.RC=rankine(8,8000,name='Default Rankine Cycle')
        #steam object
        self.satsteam=steam(8000,x=1.0)
        self.TsatHigh=0
       #high low
        self.setPHigh()
        self.setPLow()

        #show the form
        self.show()

    def clamped(self, val, low, high):
        if self.isfloat(val):
            val=float(val)
            if val > high:
                return float(high)
            if val < low:
                return float(low)
            return val
        return float(low)

    def float(self, value):
        '''
        this function is a check to verify that a string can be converted to a float
        :return:
        '''
        if value=='NaN': return False
        try:
            float(value)
            return True
        except ValueError:
            return False

    def P_High(self):
        #this makes sure its a number
        ph=self.le_PHigh.text()
        if not self.isfloat(ph):
            ph='80'
            self.le_PHigh.setText(ph)
        PHigh = float(ph) #this converts text to number
        sat_high = self.satsteam.getSatProp(P_Bar=PHigh)
        #(Tsat, hf, hg, sf, sg, vf, vg)
        self.TSatHigh=self.satsteam.satProps.Tsat
        st_high = 'PSat = {:0.2f} bar, TSat = {:0.2f} C'.format(PHigh, self.satsteam.satProps.Tsat)
        st_high += '\nhf = {:0.2} kJ/kg, hg = {:0.2f} kJ/kg'.format(self.satsteam.satProps.hf, self.satsteam.satProps.hg) #displays following vals onto the UI window
        st_high += '\nsf = {:0.2f} kJ/kg*K, sg = {:0.2f} kJ/kg*K'.format(self.satsteam.satProps.sf, self.satsteam.satProps.sg)
        st_high += '\nvf = {:0.4f} m^3/kg, vg = {:0.2f} m^3/kg'.format(self.satsteam.satProps.vf, self.satsteam.satProps.vg)
        self.lbl_SatPropHigh.setText(st_high)

    def P_Low(self):
        pl = self.le_Plow.text()
        if not self.isfloat(pl):
            pl='80'
            self.le_PLow.setText(pl)
        PLow=float(self.le_PLow.text()) #convert text to number
        sat_low = self.satsteam.getSatProp(P_Bar=PLow)
        #(Tsat, hf, hg, sf, sg, vf, vg
        st_low = 'PSat = {:0.2f} bar, TSat = {:0.2f} C'.format(PLow, self.satsteam.satProps.Tsat) #displays follwoing vals onto the UI window
        st_low += '\nhf = {:0.2} kJ/kg, hg = {:0.2f} kJ/kg'.format(self.satsteam.satProps.hf, self.satsteam.satProps.hg)
        st_low += '\nsf = {:0.2f} kJ/kg*K, sg = {:0.2f}kJ/kg*k'.format(self.satsteam.satProps.sf, self.satsteam.satProps.sg)
        st_low += '\nvf = {:0.4f} m^3/Kg, vg = {:0.2f} m^3/kg'.format(self.satsteam.satProps.vf, self.satsteam.satProps.vg)
        self.lbl_SatPropLow.setText(st_low)

    def EffRange(self):
        e = self.clamp(self.le_TurbineEff.text(), 0.0, 1.0)
        self.le_TurbineEff.setText(str(e))

    def QualityOrTHigh(self):
        if self.rdo_Quality.isChecked():
            self.le_TurbineInletCondition.setText('1')
        else:
            self.lbl_TurbineInletCondition.setText('Turbine Inlet: T High =')
            self.le_TurbineInletCondition.setText('{:0.2f}'.format(self.TsatHigh+1))
            self.le_TurbineInletCondition.setEnabled(True)

    def calcRankine(self, rankine):
        PHigh = float(self.le_PHigh.text())
        PLow = float(self.le_PLow.text())
        if(self.rdo_Quality.isChecked()):
            self.RC.set(P_low=PLow*100, P_high=PHigh*100, eff_turbine=float(self.le_TurbineEff.text()))
        else:
            self.RC.set(P_low=PLow*100, P_high=PHigh*100, eff_turbine=float(self.le_TurbineEff.text(), T_high=float(self.le_TurbineInletCondition.text())))
        self.RC.calc_efficiency()

        #enthalpy values
        self.le_H1.setText('{:0.2f}'.format(self.RC.state1.h))
        self.le_H2.setText('{:0.2f}'.format(self.RC.state2.h))
        self.le_H3.setText('{:0.2f}'.format(self.RC.state3.h))
        self.le_H4.setText('{:0.2f}'.format(self.RC.state4.h))

        # rankine cycle
        self.le_Efficiency.setText('{:0.2f}'.format(self.RC.efficiency))
        self.le_TurbineWork.setText('{:0.2f}'.format(self.RC.turbine_work))
        self.le_PumpWork.setText('{:0.2f}'.format(self.RC.pump_work))
        self.le_HeatAdded.setText('{:0.2f}'.format(self.RC.heat_added))

        self.ax.clear()
        self.RC.plot_cycle_XY(self.ax)
        self.canvas.draw()


if __name__=='__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    mw.setWindowTitle('Rankine Cycle Calculator')
    sys.exit(app.exec())