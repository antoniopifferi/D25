# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 09:18:29 2021

@author: anton
"""
from numpy import *
#from scipy import *
import matplotlib
matplotlib.rcParams['text.usetex'] = True
from matplotlib.pyplot import *
from pandas import *
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.ticker as ticker
close("all")

# PARAMETERS
PATH_D48='C:\\OneDrivePolimi\\OneDrive - Politecnico di Milano\\Beta\\Projects\\Open\\SOLUS\\Deliverable\\D48\\'
PATH_DATA='Data\\'
PATH_RESULTS='Results\\'
PATH_SETTINGS='Settings\\'

FILE_DATA='_Ecoflex_FoM_reconstructed_Gate.txt'
FILE_LABBOOK='LabbookEco3Del0Final.txt'
FILE_SCENARIO='ScenarioEco3Del0Final.txt'
FILE_VARIABLE='VariableEco3Del0Final.txt'

# FILE_DATA='_Meat_FoM_spectral_reconcurves_fromSpectralFit2_.txt'
# FILE_LABBOOK='LabbookMeat3.txt'
# FILE_SCENARIO='ScenarioMeat3.txt'
# FILE_VARIABLE='VariableMeat3.txt'

FIGWIDTH=15
aOpt=['Mua','Mus']
DMua0=0.1 # default value to estimate non-lin (working point: 'x' in def of 'SL' D4.8)
DxMua0=1 # default value to estimate non-lin ADIMENSIONAL!!! (delta step: 'Dx' in def of 'NL' D4.8)
DMus0=1 # default value to estimate non-lin (working point: 'x' in def of 'SL' D4.8)
DxMus0=1 # default value to estimate non-lin (delta step: 'Dx' in def of 'NL' D4.8)
SAVE_FIG=True
SUP_TITLE=False
ASPECT_RATIO=True
#subLambda=[930, 970, 1020, 1050]
#subLambda=[640, 675, 830, 905]

# LOAD
Data=read_csv(PATH_D48+PATH_DATA+FILE_DATA,sep='\t',index_col=False)
Labbook=read_csv(PATH_D48+PATH_SETTINGS+FILE_LABBOOK,sep='\t')
Scenario=read_csv(PATH_D48+PATH_SETTINGS+FILE_SCENARIO,sep='\t')  
Variable=read_csv(PATH_D48+PATH_SETTINGS+FILE_VARIABLE,sep='\t')  

# COMPLETE DATA
Variable.Label.fillna(Variable.NewVar,inplace=True)
dcVariable=dict(zip(Variable.OldVar, Variable.NewVar))
dcUnit=dict(zip(Variable.NewVar, Variable.Unit))
dcLabel=dict(zip(Variable.NewVar, Variable.Label))
Data.rename(columns=dcVariable,inplace=True)
Data = Data.merge(Labbook, on='Hete_Meas')
#Data.drop(Data.loc[Data['Lambda'].isin(subLambda)].index, inplace=True)

# CALC VARIABLES
Data['bkgMuaTrue']=1/(1+Data['contrMuaTrue'])*Data['incMuaTrue'] # TRUE BKG MUA
Data['deltaMuaTrue']=Data['contrMuaTrue']*Data['bkgMuaTrue'] # TRUE DELTA MUA
Data['deltaMuaMeas']=Data['contrMuaMeas']*Data['bkgMuaMeas'] # MEAS DELTA MUA
Data['bkgMusTrue']=1/(1+Data['contrMusTrue'])*Data['incMusTrue'] # TRUE BKG MUS
Data['deltaMusTrue']=Data['contrMusTrue']*Data['bkgMusTrue'] # TRUE DELTA MUS
Data['deltaMusMeas']=Data['contrMusMeas']*Data['bkgMusMeas'] # MEAS DELTA MUS
Data['SL_Mua']=0
Data['NL_Mua']=0
Data['Poly_Mua']=0
Data['SL_Mus']=0
Data['NL_Mus']=0
Data['Poly_Mus']=0
Data['One']=1.0
Data['Zero']=0.0
for var,fact in zip(Variable[Variable.Factor>0].NewVar,Variable[Variable.Factor>0].Factor): Data[var]=Data[var]*fact
# calc non-linearity
for oO in aOpt:
    DataE = Data[Data.LinMua=='OK'] if oO=='Mua' else Data[Data.LinMus=='OK']
    gamma = DMua0 if oO=='Mua' else DMus0
    Dx = DxMua0 if oO=='Mua' else DxMus0
    
    for ot in DataE.TAU.unique():
        for ol in DataE.Lambda.unique():
            for ov in DataE.incVol.unique():
                DataEE=DataE[(DataE.TAU==ot) & (DataE.Lambda==ol) & (DataE.incVol==ov)]
                x = DataEE.PertMua/gamma if oO=='Mua' else DataEE.PertMus/gamma
                y = DataEE.incMuaMeas/gamma if oO=='Mua' else DataEE.incMusMeas/gamma
                [a,b,c]=polyfit(x, y, 2)
                SL=2*a*x+b
                #NL=2*a
                NL=2*a/b*Dx
                polyF=gamma*(a*x**2+b*x+c)
                if oO=='Mua':
                    DataEE.SL_Mua=SL
                    DataEE.NL_Mua=NL
                    DataEE.Poly_Mua=polyF
                    Data[(Data.LinMua=='OK')&(DataE.TAU==ot)&(DataE.Lambda==ol)&(DataE.incVol==ov)]=DataEE.copy()
                else:            
                    DataEE.SL_Mus=SL
                    DataEE.NL_Mus=NL
                    DataEE.Poly_Mus=polyF
                    Data[(Data.LinMus=='OK')&(DataE.TAU==ot)&(DataE.Lambda==ol)&(DataE.incVol==ov)]=DataEE.copy()
# PLOT
for i,s in Scenario.iterrows(): # iterate over the whole Scenario
    
    # extract arrays
    if notnull(s.Truth): Data[s.Truth+'1']=Data[s.Truth]
    DataE=Data
    if notnull(s.Extract1): DataE=DataE[DataE[s.Extract1]==s.eVal1]
    aCol=DataE[DataE[s.Test]=='OK'][s.Col].unique()
    aRow=DataE[DataE[s.Test]=='OK'][s.Row].unique()    
    Name=s.Var+"_"+s.View+"_"+s.Test

    #do plot
    nRow=len(aRow)
    nCol=len(aCol)
    aRatio = (nRow+0.5)/(nCol+1) if ASPECT_RATIO else 9/16
    figwidth = FIGWIDTH*0.6 if nCol==3 else FIGWIDTH
    figData,axs=subplots(nRow,nCol,num='Fig'+str(Name),figsize=(figwidth,aRatio*figwidth),squeeze=False)
    if SUP_TITLE: suptitle(FILE_SCENARIO+'  #  '+FILE_DATA+'  #  '+str(Name))
    for iCol,oCol in enumerate(aCol):
        for iRow,oRow in enumerate(aRow):
            axi=axs[iRow,iCol]
            sca(axi)

            subData=DataE[(DataE[s.Col]==oCol)&(DataE[s.Row]==oRow)&(DataE[s.Test]=='OK')]
            table=subData.pivot_table(values=s.Y,index=s.X,columns=s.Line,aggfunc='mean')
            table.style.format({'PertMua':'{0:,.0f} nm','horsepower':'{0:,.0f}hp'})
            table.plot(ax=axi,marker='D',legend=False,xlabel=False)
            if((iCol==0)and(iRow==0)): legend()
            if notnull(s.Truth): truth=subData.pivot_table(values=s.Truth+'1',index=s.X,columns=s.Line,aggfunc='mean')
            if notnull(s.Truth): truth.plot(ax=axi,marker='',color='black',legend=False)
            if notnull(s.Ymin): gca().set_ylim([s.Ymin,s.Ymax]) # check if there is any value, including 0, otherwise leave autoscale
            grid(True)

            # print labels
            xLab = (dcLabel[s.X] if s.X in dcLabel else s.X) + (" ("+dcUnit[s.X]+")" if s.X in dcUnit else "")
            yLab = (dcLabel[s.Y] if s.Y in dcLabel else s.Y) + (" ("+dcUnit[s.Y]+")" if s.Y in dcUnit else "")
            rLab = (dcLabel[s.Row] if s.Row in dcLabel else s.Row)+"="+str(oRow) + (" "+dcUnit[s.Row] if s.Row in dcUnit else "")
            cLab = (dcLabel[s.Col] if s.Col in dcLabel else s.Col)+"="+str(oCol) + (" "+dcUnit[s.Col] if s.Col in dcUnit else "")    
            if iCol==0: gca().set_ylabel(yLab)
            if iRow==(nRow-1): gca().set_xlabel(xLab)           
            if iRow==0: gca().set_title(cLab)
            #if iCol==(nCol-1): gca().twinx().set_ylabel(rLab)
            
            
    figData.tight_layout()
    show()
    if SAVE_FIG: figData.savefig(PATH_D48+PATH_RESULTS+'Fig_'+str(Name)+'.jpg',format='jpg')
