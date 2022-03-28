from HW7P2_steam import *
from matplotlib import pyplot as plt

class Plotting:
    def __init__(self):
        self.T = []
        self.P = []
        self.h = []
        self.s = []
        self.v = []

    def clear(self):
        self.T.clear()
        self.P.clear()
        self.h.clear()
        self.s.clear()
        self.v.clear()

    def add(self, vals):
        T, P, h, s, v = vals
        self.T.append(T)
        self.P.append(P)
        self.h.append(h)
        self.s.append(s)
        self.v.append(v)

    def getAxis(self, W='T'):
        w=W.lower()
        if w == 't':
            return r'T $\left(^oC\right)$'
        if w == 'h':
            return r'h $\left(\frac{kJ}{kg}\right)$'
        if w == 's':
            return r'S $\left(\frac{kJ}{kg\cdot K}\right)$'
        if w == 'v':
            return r'v $\left(\frac{m^3}{kg}]right)$'
        if w == 'p':
            return r'P $\left(kPa\right)$'

    def getDataCol(self, W='T'):
        w=W.lower()
        if w=='t':
            return self.T
        if w=='h':
            return self.h
        if w=='s':
            return self.s
        if w=='v':
            return self.v
        if w=='p':
            return self.P

class rankine():
    def __init__(self, p_low=8, p_high=8000, t_high=None, eff_turbine=1.0, name='Rankine Cycle'):

        self.steam = steam(8000)
        self.set(P_low=p_low, P_high=p_high, T_high=t_high, eff_turbine=eff_turbine, name=name)
        self.scl = subcooled()
        #  storing the state data
        self.satLiqPlotData = Plotting()
        self.satVapPlotData = Plotting()
        self.buildVaporDomeData()
        self.upperCurve = Plotting()
        self.lowerCurve = Plotting()

    def set(self, P_low=8, P_high=8000, T_high=None, eff_turbine=1.0, name='Rankine Cycle'):
        self.P_low = P_low
        self.P_high = P_high
        self.T_high = T_high
        self.name = name
        self.efficiency = None
        self.eff_turbine = eff_turbine
        self.turbine_work = 0
        self.pump_work = 0
        self.heat_added = 0
        # these will be thermodynamic state objects
        self.state1 = None
        self.state2s = None
        self.state2 = None
        self.state3 = None
        self.state4 = None
        self.satPLow = self.steam.getSatProp(P_KPa=self.P_low)
        self.satPHigh = self.steam.getSatProp(P_KPa=self.P_high)

    def calc_efficiency(self):
        # calculate the 4 states
        # state 1:) superheated or saturated vapor
        if self.T_high is None:
            self.state1 = self.steam.set(self.P_high, x=1.0, name='Turbine Inlet')
        else:
            self.state1 = self.steam.set(self.P_high, T=self.T_high, name='Turbine Inlet')
        # state 2: turbine exit
        # create state 2 efficient turbine
        self.state2s = self.steam.set(self.P_low, s=self.state1.s, name="Turbine Exit")
        # use turbine efficiency to calculate h2
        h2 = self.state1.h - (self.state1.h - self.state2s.h) * self.eff_turbine
        # state 2
        self.state2 = self.steam.set(self.P_low, h=h2, name="Turbine Exit")
        # state 3: pump inlet
        self.state3 = self.steam.set(self.T_low, x=0, name='Pump Inlet')
        # state 4: pump exit
        self.state4 = self.scl.getState(PLowSat=self.satPLow, PHighSat=self.satPHigh, P=self.P_high,
                                        T=self.satPLow.Tsat)
        self.state4.name = 'Pump Exit'

        self.turbine_work = self.state1.h - self.state2.h
        self.pump_work = self.state4.h - self.state3.h
        self.heat_added = self.state1.h - self.state4.h
        self.efficiency = 100.0 * (self.turbine_work - self.pump_work) / self.heat_added

        self.Plotting()
        return self.efficiency

    def print_summary(self):
        if self.efficiency == None:
            self.calc_efficiency()
        print('Cycle Summary for: ', self.name)
        print('\tEfficiency: {:0.3f}%'.format(self.efficiency))
        print('\tTurbine Work: {:0.3f} kJ/kg'.format(self.turbine_work))
        print('\tPump Work: {:0.3f} kJ/kg'.format(self.pump_work))
        print('\tHeat Added: {:0.3f} kJ/kg'.format(self.heat_added))
        self.state1.print()
        self.state2.print()
        self.state3.print()
        self.state4.print()

    def get_summary(self):

        if self.efficiency == None:
            self.calc_efficiency()
        s = r'Summary:'
        s += '\n$\eta$: {:0.1f}% '.format(self.efficiency)
        s += '\n$\eta_{turbine}$: ' + '{:0.2f}'.format(self.eff_turbine) if self.eff_turbine < 1.0 else ''
        s += '\n$W_{turbine}$: ' + '{:0.1f} kJ/k'.format(self.turbine_work)
        s += '\n$W_{pump}$: ' + '{:0.1f} kJ/kg'.format(self.pump_work)
        s += '\n$Q_{boiler}$: ' + '{:0.1f} kJ/kg'.format(self.heat_added)
        return s

    def buildVaporDomeData(self, nPts=150):
        SS=self.steam.SatSteam
        for row in range(len(self.steam.SatSteam.TCol)):
            T=SS.TCol[row]
            P=SS.PCol[row]*100 #kPa
            self.satLiqPlotData.add((T,P, SS.hfCol[row], SS.sfCol[row], SS.vfCol[row]))
            self.satVapPlotData.add((T,P, SS.hgCol[row], SS.sgCol[row], SS.vgCol[row]))

    def Plotting(self):

        self.upperCurve.clear()
        self.lowerCurve.clear()

        nPts = 15
        for n in range(nPts):
            z = n * 1.0 / (nPts - 1)
            DeltaP = (self.satPHigh.Psat - self.satPLow.Psat)
            state = self.scl.getState(self.satPLow, self.satPHigh, P=(self.satPLow.Psat + z * DeltaP), T=self.satPLow.Tsat)
            self.upperCurve.add((state.T, state.P, state.h, state.s, state.v))

        T4 = self.satPLow.Tsat
        T5 = self.satPHigh.Tsat
        DeltaT = (T5 - T4)
        nPts = 20
        for n in range(nPts):
            z = n * 1.0 / (nPts - 1)
            P = self.satPHigh.Psat
            T = T4 + z * DeltaT
            state = self.scl.getState(self.satPLow, self.satPHigh, P, T)
            self.upperCurve.add((state.T, state.P, state.h, state.s, state.v))
        for n in range(nPts):
            z = n * 1.0 / (nPts - 1)
            state = self.steam.getState(self.satPHigh.Psat,x=z)
            self.upperCurve.add((state.T, state.P, state.h, state.s, state.v))
        if self.state1.T>(self.satPHigh.Tsat+1):
            T6 = self.satPHigh.Tsat
            DeltaT = self.state1.T - T6
            for n in range(nPts):
                z = n * 1.0 / (nPts - 1)
                state = self.steam.getState(self.satPHigh.Psat, T=T6+z*DeltaT)
                self.upperCurve.add((state.T, state.P, state.h, state.s, state.v))

        s1=self.state1.s
        s2=self.state2.s
        P1=self.state1.P
        P2=self.state2.P
        Deltas=s2-s1
        DeltaP=P2-P1
        for n in range(nPts):
            z = n * 1.0 / (nPts - 1)
            state = self.steam.getState(P1+z*DeltaP, s=s1+z*Deltas)
            self.upperCurve.add((state.T, state.P, state.h, state.s, state.v))

        x2=self.state2.x
        nPts= len(self.upperCurve.T)
        for n in range(nPts):
            z = n * 1.0 / (nPts - 1)
            state=self.steam.getState(self.satPLow.Psat, x=(1.0-z)*x2)
            self.lowerCurve.add((state.T, state.P, state.h, state.s, state.v))


    def plot_cycle_XY(self, X='s', Y='T', ax=None):

        if X==Y:
            return
        QTPlotting = True  # assumes we are plotting onto a QT GUI form
        if ax == None:
            ax = plt.subplot()
            QTPlotting = False  # actually, we are just using CLI and showing the plot

        YF= self.satLiqPlotData.getDataCol(Y)
        YG= self.satVapPlotData.getDataCol(Y)
        XF = self.satLiqPlotData.getDataCol(X)
        XG = self.satVapPlotData.getDataCol(X)
        # plot
        ax.plot(XF, YF, color='b')
        ax.plot(XG, YG, color='r')
        # plot the upper and lower curves
        ax.plot(self.lowerCurve.getDataCol(X), self.lowerCurve.getDataCol(Y), color='k')
        ax.plot(self.upperCurve.getDataCol(X), self.upperCurve.getDataCol(Y), color='g')

        # add axis
        ax.set_ylabel(self.lowerCurve.getAxis(Y), fontsize='large' if QTPlotting else 'medium')
        ax.set_xlabel(self.lowerCurve.getAxis(X), fontsize='large' if QTPlotting else 'medium')
        # title on the plot
        self.name = 'Rankine Cycle - ' + self.state1.region + ' at Turbine Inlet'
        ax.set_title(self.name, fontsize='large' if QTPlotting else 'medium')

        #tick marks
        ax.tick_params(axis='both', which='both', direction='in', top=True, right=True,
                       labelsize='large' if QTPlotting else 'medium')  # format tick marks

        # plot the circles for states 1, 2, 3, and 4
        ax.plot(self.state1.getVal(X), self.state1.getVal(Y), marker='o', markerfacecolor='w', markeredgecolor='k')
        ax.plot(self.state2.getVal(X), self.state2.getVal(Y), marker='o', markerfacecolor='w', markeredgecolor='k')
        ax.plot(self.state3.getVal(X), self.state3.getVal(Y), marker='o', markerfacecolor='w', markeredgecolor='k')
        ax.plot(self.state4.getVal(X), self.state3.getVal(Y), marker='o', markerfacecolor='w', markeredgecolor='k')
        # x and y limits
        X_min = min(min(XF), min(XG), min(self.upperCurve.getDataCol(X)), max(self.lowerCurve.getDataCol(X)))
        X_max = max(max(XF), max(XG), max(self.upperCurve.getDataCol(X)), max(self.lowerCurve.getDataCol(X)))
        Y_min=min(min(YF), min(YG), min(self.upperCurve.getDataCol(Y)), max(self.lowerCurve.getDataCol(Y)))
        Y_max=max(max(YF), max(YG), max(self.upperCurve.getDataCol(Y)), max(self.lowerCurve.getDataCol(Y)))*1.1
        ax.set_xlim(X_min,X_max)
        ax.set_ylim(Y_min,ymax)
        deltax=X_max-X_min
        deltay=Y_max-Y_min

        ax.text(xmin+0.05*deltax, Y_min+0.7*deltay, self.get_summary())


        if QTPlotting == False:
            plt.show()


def main():
    rankine1 = rankine(8, 8000, t_high=500, eff_turbine=0.95, name='Rankine Cycle - Superheated at turbine inlet')
    eff = rankine1.calc_efficiency()
    print(eff)
    rankine1.state3.print()
    rankine1.print_summary()
    rankine1.plot_cycle_XY(X='s', Y='T')

    rankine2 = rankine(8, 8000, eff_turbine=0.95, name='Rankine Cycle - Saturated at turbine inlet')
    eff2 = rankine2.calc_efficiency()
    rankine2.plot_cycle_XY(X='s', Y='T')
    print(eff2)

    rankine2.print_summary()

if __name__ == "__main__":
    main()
