import numpy as np
from scipy.interpolate import griddata
from copy import deepcopy as dc

class saturatedData():
    def __init__(self):
        self.Table()

    def Table(self):

        self.TCol, self.PCol, self.hfCol, self.hgCol, self.sfCol, self.sgCol, self.vfCol, self.vgCol = np.loadtxt('sat_water_table.txt', skiprows=1, unpack=True)

    def getSatProps(self, P_Bar=None, P_kPa=None, T=None, method='linear'):

        if P_Bar is not None:
            P=P_Bar
        else:
            P=P_kPa/100.0

        sats = satProps()
        if P is not None:
            sats.Psat = P
            sats.Tsat = float(griddata((self.PCol), self.TCol, (P),method=method))
            sats.hf = float(griddata((self.PCol), self.hfCol, (P),method=method))
            sats.hg = float(griddata((self.PCol), self.hgCol, (P),method=method))
            sats.sf = float(griddata((self.PCol), self.sfCol, (P),method=method))
            sats.sg = float(griddata((self.PCol), self.sgCol, (P),method=method))
            sats.vf = float(griddata((self.PCol), self.vfCol, (P),method=method))
            sats.vg = float(griddata((self.PCol), self.vgCol, (P),method=method))
            sats.hgf = sats.hg - sats.hf
            sats.sgf = sats.sg - sats.sf
            sats.vgf = sats.vg - sats.vf
            sats.Psat *= 100.0  # convert to kPa
            return sats
        # given TSat, calc props
        if T is not None:
            sats.Tsat = T
            sats.Psat = float(griddata((self.TCol), self.PCol, (T),method=method))
            sats.hf = float(griddata((self.TCol), self.hfCol, (T),method=method))
            sats.hg = float(griddata((self.TCol), self.hgCol, (T),method=method))
            sats.sf = float(griddata((self.TCol), self.sfCol, (T),method=method))
            sats.sg = float(griddata((self.TCol), self.sgCol, (T),method=method))
            sats.vf = float(griddata((self.TCol), self.vfCol, (T),method=method))
            sats.vg = float(griddata((self.TCol), self.vgCol, (T),method=method))
            sats.hgf = sats.hg - sats.hf
            sats.sgf = sats.sg - sats.sf
            sats.vgf = sats.vg - sats.vf
            sats.Psat*=100.0  # convert to kPa
            return sats

    def getState(self, P_Bar=None, P_kPa=None, T=None, h=None, s=None, v=None, x=None):

        state = stateProps()
        state.region = 'saturated'
        sats=satProps()

        if P_Bar is not None:
            sats = self.getSatProps(P_Bar=P_Bar)
        if P_kPa is not None:
            sats=self.getSatProps(P_kPa=P_Bar)
        if T is not None:
            sats = self.getSatProps(T=T)
        state.P = sats.Psat
        state.T = sats.Tsat
        if h is not None:
            state.h = h
            state.x = (state.h - sats.hf) / sats.hgf
            state.s = sats.sf + state.x * sats.sgf
            state.v = sats.vf + state.x * sats.vgf
        elif s is not None:
            state.s = s
            state.x = (state.s - sats.sf) / sats.sgf
            state.h = sats.hf + state.x * sats.hgf
            state.v = sats.vf + state.x * sats.vgf
        elif v is not None:
            state.v = v
            state.x = (state.v - sats.vf) / sats.vgf
            state.h = sats.hf + state.x * sats.hgf
            state.s = sats.sf + state.x * sats.sgf
        elif x is not None:
            state.x = x
            state.h = sats.hf + state.x * sats.hgf
            state.s = sats.sf + state.x * sats.sgf
            state.v = sats.vf + state.x * sats.vgf
        return dc(state)

class superheated():

    def __init__(self):
        self.readTable()

    def readTable(self):
        self.TCol, self.hCol, self.sCol, self.PCol = np.loadtxt('superheated_water_table.txt', skiprows=1, unpack=True)

        # no specific volume data in this table, so assume ideal gas behavior and calculate specific volume in SI
        self.vCol = np.ndarray(np.shape(self.TCol))
        MW = 18.0  # kg/kmol
        R = 8.31446 / MW  # kJ/kg*K ->kN*m/kg*K
        # P in kPa->kN/m^2
        # T in K
        # v =RT/p ->m^3/kg
        for i in range(len(self.TCol)):
            self.vCol[i] = R * (self.TCol[i] + 273.15) / self.PCol[i]

    def getState(self, P=None, T=None, h=None, s=None, v=None):

        state = stateProps()
        state.x=1.0 #if superheated, mass fraction vapor is 1.0
        state.region = 'superheated'
        #combo 1
        if P is not None and T is not None:
            state.T=T
            state.P=P
            state.h=float(griddata((self.TCol,self.PCol), self.hCol, (state.T, state.P)))
            state.s=float(griddata((self.TCol,self.PCol), self.sCol, (state.T, state.P)))
            state.v=float(griddata((self.TCol,self.PCol), self.vCol, (state.T, state.P)))
        #combo 2
        elif P is not None and h is not None:
            state.h=h
            state.P=P
            state.T=float(griddata((self.hCol,self.PCol), self.TCol, (state.h, state.P)))
            state.s=float(griddata((self.hCol,self.PCol), self.sCol, (state.h, state.P)))
            state.v=float(griddata((self.hCol,self.PCol), self.vCol, (state.h, state.P)))
        #combo 3
        elif P is not None and s is not None:
            state.s=s
            state.P=P
            state.T=float(griddata((self.sCol,self.PCol), self.TCol, (state.s, state.P)))
            state.h=float(griddata((self.sCol,self.PCol), self.hCol, (state.s, state.P)))
            state.v=float(griddata((self.sCol,self.PCol), self.vCol, (state.s, state.P)))
        #combo 4
        elif P is not None and v is not None:
            state.v=v
            state.P=P
            state.T=float(griddata((self.vCol,self.PCol), self.TCol, (state.v, state.P)))
            state.s=float(griddata((self.vCol,self.PCol), self.sCol, (state.v, state.P)))
            state.h=float(griddata((self.vCol,self.PCol), self.hCol, (state.v, state.P)))
        #combo 5
        elif T is not None and h is not None:
            state.h=h
            state.T=T
            state.p=float(griddata((self.hCol,self.TCol), self.PCol, (state.h, state.T)))
            state.s=float(griddata((self.hCol,self.TCol), self.sCol, (state.h, state.T)))
            state.v=float(griddata((self.hCol,self.TCol), self.vCol, (state.h, state.T)))
        # combo 6
        elif T is not None and s is not None:
            state.s = s
            state.T = T
            state.P = float(griddata((self.sCol, self.TCol), self.PCol, (state.s, state.T)))
            state.h = float(griddata((self.sCol, self.TCol), self.hCol, (state.s, state.T)))
            state.v = float(griddata((self.sCol, self.TCol), self.vCol, (state.s, state.T)))
        # combo 7
        elif T is not None and v is not None:
            state.v = v
            state.T = T
            state.P = float(griddata((self.vCol, self.TCol), self.PCol, (state.v, state.T)))
            state.s = float(griddata((self.vCol, self.TCol), self.sCol, (state.v, state.T)))
            state.h = float(griddata((self.vCol, self.TCol), self.hCol, (state.v, state.T)))
        # combo 8
        elif h is not None and s is not None:
            state.s = s
            state.h = h
            state.P = float(griddata((self.sCol, self.hCol), self.PCol, (state.s, state.h)))
            state.T = float(griddata((self.sCol, self.hCol), self.TCol, (state.s, state.h)))
            state.v = float(griddata((self.sCol, self.hCol), self.vCol, (state.s, state.h)))
        # combo 9
        elif h is not None and v is not None:
            state.v = v
            state.h = h
            state.P = float(griddata((self.vCol, self.hCol), self.PCol, (state.v, state.h)))
            state.T = float(griddata((self.vCol, self.hCol), self.TCol, (state.v, state.h)))
            state.s = float(griddata((self.vCol, self.hCol), self.sCol, (state.v, state.h)))
        # combo 10
        elif s is not None and v is not None:
            state.v = v
            state.s = s
            state.P = float(griddata((self.vCol, self.sCol), self.PCol, (state.v, state.s)))
            state.T = float(griddata((self.vCol, self.sCol), self.TCol, (state.v, state.s)))
            state.h = float(griddata((self.vCol, self.sCol), self.sCol, (state.v, state.s)))
        return dc(state)

class subcooled():

    def __init__(self):
        self.satData=None

    def getState(self, PLowSat, PHighSat, P, T):

        state=stateProps()
        case = 1 if (T<=PLowSat.Tsat) else 2
        if case ==1:
            z=(P-PLowSat.Psat)/(PHighSat.Psat-PLowSat.Psat)
            state.h=PLowSat.hf+z*(PHighSat.Psat-PLowSat.Psat)*PLowSat.vf
            state.s=PLowSat.sf
            state.v=PLowSat.vf
            state.T=PLowSat.Tsat
            state.P=P
        else:
            z=(T-PLowSat.Tsat)/(PHighSat.Tsat-PLowSat.Tsat)
            h4=PLowSat.hf+(PHighSat.Psat-PLowSat.Psat)*PLowSat.vf
            s4=PLowSat.sf
            v4=PLowSat.vf
            h5=PHighSat.hf
            s5=PHighSat.sf
            v5=PHighSat.vf
            state.h=h4+z*(h5-h4)
            state.s=s4+z*(s5-s4)
            state.v=v4+z*(v5-v4)
            state.P=P
            state.T=T
        name='subcooled'
        state.x=-0.1
        return dc(state)

class satProps():

    def __init__(self):
        self.tsat = None
        self.Ppsat = None
        self.hf = None
        self.hg = None
        self.hgf = None
        self.sf = None
        self.sg = None
        self.sgf = None
        self.vf = None
        self.vg = None
        self.vgf = None

    def set(self, vals):
        self.tsat, self.psat, self.hf, self.hg, self.sf, self.sg, self.vf, self.vg = vals
        self.hgf = self.hg - self.hf
        self.sgf = self.sg - self.sf
        self.vgf = self.vg - self.vf

    def get(self):
        return (self.tsat, self.psat, self.hf, self.hg, self.hgf, self.sf, self.sg, self.sgf, self.vf, self.vg, self.vgf)

class stateProps():

    def __init__(self):
        self.name = None
        self.T = None
        self.P = None
        self.h = None
        self.s = None
        self.v = None
        self.x = None
        self.region = None
    def getVal(self, name='T'):
        n=name.lower()
        if n == 't':
            return self.T
        if n == 'h':
            return self.h
        if n == 's':
            return self.s
        if n == 'v':
            return self.v
        if n == 'p':
            return self.P

    def print(self):
        if self.name is not None:
            print(self.name)
        if self.x is None or self.x < 0.0:
            print('Region: compressed liquid')
            print('p = {:0.2f} kPa'.format(self.P))
            print('h = {:0.2f} kJ/kg'.format(self.h))
        else:
            print('Region: ', self.region)
            print('p = {:0.2f} kPa'.format(self.P))
            print('T = {:0.1f} degrees C'.format(self.T))
            print('h = {:0.2f} kJ/kg'.format(self.h))
            print('s = {:0.4f} kJ/(kg K)'.format(self.s))
            print('v = {:0.6f} m^3/kg'.format(self.v))
            print('x = {:0.4f}'.format(self.x))
        print()

class steam():
    def __init__(self, pressure, T=None, x=None, v=None, h=None, s=None, name=None):
        self.satProps = satProps()
        self.SHSteam = superheatedData()
        self.SatSteam = saturatedData()
        self.State = stateProps()
        self.name=name
        self.set(pressure, T=T, x=x, v=v, h=h, s=s, name=name)

    def set(self, pressure, T=None, x=None, v=None, h=None, s=None, name=None):

        self.State.P = pressure  # pressure - kPa
        self.State.T = T  # Temperature - degrees C
        self.State.x = x  # quality
        self.State.v = v  # specific volume - m^3/kg
        self.State.h = h  # specific enthalpy - kj/kg
        self.State.s = s  # entropy - kj/(kg*K)
        self.State.name = name if name is not None else self.name # a useful identifier
        self.State.region = None  # 'superheated' or 'saturated' or 'two-phase'
        if T == None and x == None and v == None and h == None and s == None:
            return
        else:
            self.calc()
        return dc(self.State)  # need to deep copy so not passing just a reference back

    def getState(self, pressure, T=None, x=None, v=None, h=None, s=None, name=None):
        return self.set(pressure, T=T, x=x, v=v, h=h, s=s, name=name)

    def calc(self):
        '''
        The Rankine cycle operates between two isobars (i.e., p_high (Turbine inlet state 1) & p_low (Turbine exit state 2)
        So, given a pressure, we need to determine if the other given property puts
        us in the saturated or superheated regime.
        :return: a deep copy of the state
        '''

        Pbar = self.State.P / 100  # pressure in bar
        name=self.name
        self.satProps=self.SatSteam.getSatProps(P_Bar=Pbar)

        if self.State.T is not None:
            if self.State.T>(self.satProps.tsat+1): # superheated
                self.State=self.SHSteam.getState(P=self.State.P, T=self.State.T)
            else:  # Assume this means saturated vapor
                self.State=self.SatSteam.getState(P_Bar=Pbar, x=1.0)
        # case 2
        elif self.State.h is not None:
            if self.State.h>self.satProps.hg:  # superheated
                self.State=self.SHSteam.getState(P=self.State.P, h=self.State.h)
            elif self.State.h<=self.satProps.hg and self.State.h>=self.satProps.hf: #saturated or 2-phase
                self.State=self.SatSteam.getState(P_Bar=Pbar, h=self.State.h)
            else:  # subcooled state
                pass
        #case 3
        elif self.State.s is not None:
            if self.State.s>self.satProps.sg:  # superheated
                self.State=self.SHSteam.getState(P=self.State.P, s=self.State.s)
            elif self.State.s<=self.satProps.sg and self.State.s>=self.satProps.sf: #saturated or 2-phase
                self.State=self.SatSteam.getState(P_Bar=Pbar, s=self.State.s)
            else: #subcooled state
                pass
        #case 4
        elif self.State.v is not None:
            if self.State.v>self.satProps.vg:  # superheated
                self.State=self.SHSteam.getState(P=self.State.P, v=self.State.v)
            elif self.State.v<=self.satProps.vg and self.State.v>=self.satProps.vf: #saturated or 2-phase
                self.State=self.SatSteam.getState(P_Bar=Pbar, v=self.State.v)
            else: #subcooled state
                pass
        # case 5
        elif self.State.x is not None:  # saturated
            self.State=self.SatSteam.getState(P_Bar=Pbar, x=self.State.x)
        self.name=name
        return dc(self.State)

    def getVaporDome_TS(self, points=500):


        ts, ps, hfs, hgs, sfs, sgs, vfs, vgs = self.SatSteam.getCols()
        T_min = ts.min()
        T_max = ts.max()
        TSData = np.empty((0, 3))  #  array
        T = np.linspace(T_min, T_max, points)
        for t in T:
            dat = np.array(
                [[t, float(griddata((ts), sfs, (t), method='cubic')), float(griddata((ts), sgs, (t), method='cubic'))]])
            TSData = np.append(TSData, dat, axis=0)
        return TSData

    def getVaporDome_TS2(self):

        ts, ps, hfs, hgs, sfs, sgs, vfs, vgs = self.SatSteam.getCols()
        return (ts, sfs, sgs)

    def getSatProp(self, P_KPa=None, P_Bar=None):
        Pbar = P_Bar if P_Bar is not None else P_KPa / 100  # get pressure in bar
        self.satProps=self.SatSteam.getSatProps(P_Bar=Pbar)
        return dc(self.satProps)

    def print(self):
        print(self.name)
        self.State.print()


def main():
    inlet=steam(7350,name='Turbine Inlet') #not enough information to calculate
    inlet.x=0.9 #90 percent quality
    inlet.calc()
    inlet.print()

    h1=inlet.h
    s1=inlet.s
    print(h1,s1,'\n')

    outlet=steam(100, s=inlet.s, name='Turbine Exit')
    outlet.print()

    another=steam(8575, h=2050, name='State 3')
    another.print()

    yetanother = steam(8575, h=3125, name='State 4')
    yetanother.print()

#the following if statement causes main() to run
#only if this file is being run explicitly, not if it is
#being imported into another Python program as a module
if __name__=="__main__":
    main()
