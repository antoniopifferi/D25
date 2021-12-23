# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 09:18:29 2021

@author: anton
"""
from numpy import *
#from scipy import *
import matplotlib
#matplotlib.rcParams['text.usetex'] = True
from matplotlib.pyplot import *
from pandas import *
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.ticker as ticker
close("all")

# PARAMETERS
PATH_MAIN='C:\\OneDrivePolimi\\OneDrive - Politecnico di Milano\\Beta\\Projects\\Open\\SOLUS\\Deliverable\\D25\\'
PATH_DATA='Data\\'
PATH_RESULTS='Results\\'
PATH_SETTINGS='Settings\\'

FILE_DATA_Bkg='bulkDB.xlsx'
FILE_DATA_Contr='contrastDB.xlsx'
FILE_DATA_Inc='lesionDB.xlsx'
FILE_LABBOOK='Labbook1.txt'
FILE_SCENARIO='Scenario3.txt'
FILE_VARIABLE='Variable1.txt'


FIGWIDTH=15
fLambda=['l1','l2','l3','l4','l5','l6','l7','l8']
fLambda0=[640,675,830,905,930,970,1020,1050]
fComp=['Hb','HbO2','Lipid','H2O','Coll','a','b']
LesionType=['Benign','Malignant']
SAVE_FIG=True
SUP_TITLE=True
ASPECT_RATIO=True

# LOAD
DataBkg=pandas.read_excel(PATH_MAIN+PATH_DATA+FILE_DATA_Bkg,sheet_name='Sheet1')
DataContr=pandas.read_excel(PATH_MAIN+PATH_DATA+FILE_DATA_Contr,sheet_name='Sheet1')
DataInc=pandas.read_excel(PATH_MAIN+PATH_DATA+FILE_DATA_Inc,sheet_name='Sheet1')

Labbook=read_csv(PATH_MAIN+PATH_SETTINGS+FILE_LABBOOK,sep='\t')
Scenario=read_csv(PATH_MAIN+PATH_SETTINGS+FILE_SCENARIO,sep='\t')  
Variable=read_csv(PATH_MAIN+PATH_SETTINGS+FILE_VARIABLE,sep='\t')  

# # COMPLETE DATA
id_vars=[item for item in DataBkg.columns if item not in fLambda]
DataBkg=DataBkg.melt(id_vars=id_vars,value_vars=fLambda,var_name='Lambda',value_name='MuaBkg')
id_vars=[item for item in DataBkg.columns if item not in fComp]
DataBkg=DataBkg.melt(id_vars=id_vars,value_vars=fComp,var_name='Comp',value_name='ConcBkg')
id_vars=[item for item in DataContr.columns if item not in fLambda]
DataContr=DataContr.melt(id_vars=id_vars,value_vars=fLambda,var_name='Lambda',value_name='MuaContr')
id_vars=[item for item in DataContr.columns if item not in fComp]
DataContr=DataContr.melt(id_vars=id_vars,value_vars=fComp,var_name='Comp',value_name='ConcContr')
id_vars=[item for item in DataInc.columns if item not in fLambda]
DataInc=DataInc.melt(id_vars=id_vars,value_vars=fLambda,var_name='Lambda',value_name='MuaInc')
id_vars=[item for item in DataInc.columns if item not in fComp]
DataInc=DataInc.melt(id_vars=id_vars,value_vars=fComp,var_name='Comp',value_name='ConcInc')

# Data=concat([DataBkg,DataContr,DataInc],ignore_index=True,sort=False)
Data=merge(DataBkg,DataContr)
Data=merge(Data,DataInc)
Data.fillna(value=0,inplace=True)
#Data.index.name='Var'
#Data.reset_index(inplace=True)
# Data=concat([DataBkg,DataContrast,DataInc],ignore_index=True,sort=False)
# id_vars=[item for item in Data.columns if item not in fLambda]
# Data=Data.melt(id_vars=id_vars,value_vars=fLambda,var_name='Lambda',value_name='Mua')
# id_vars=[item for item in Data.columns if item not in fComp]
# Data=Data.melt(id_vars=id_vars,value_vars=fComp,var_name='Comp',value_name='Conc')
Variable.Label.fillna(Variable.NewVar,inplace=True)
dcVariable=dict(zip(Variable.OldVar, Variable.NewVar))
dcUnit=dict(zip(Variable.NewVar, Variable.Unit))
dcLabel=dict(zip(Variable.NewVar, Variable.Label))
dcLambda=dict(zip(fLambda,fLambda0))
Data.rename(columns=dcVariable,inplace=True)
Data = Data.merge(Labbook, on='PatientID')
Data['ViewBkg']=Data['hete']+"_"+Data['homo']
Data['MuaDelta']=Data['MuaInc']-Data['MuaBkg']
Data['ConcDelta']=Data['ConcInc']-Data['ConcBkg']
Data['Lambda'].replace(to_replace=fLambda,value=fLambda0,inplace=True)


# # CALC VARIABLES
# for var,fact in zip(Variable[Variable.Factor>0].NewVar,Variable[Variable.Factor>0].Factor): Data[var]=Data[var]*fact
# Data['BkgMua']=''
# Data[Data['Var']=='Inc']['BkgMua']=Data[Data['Var']=='Inc']['Mua']
# Data[Data['Var']=='Inc'].loc[:,'BkgMua']=Data[Data['Var']=='Inc'].loc[:,'Mua']

# PLOT
for i,s in Scenario.iterrows(): # iterate over the whole Scenario
    
    # extract arrays
    if notnull(s.Truth): Data[s.Truth+'1']=Data[s.Truth]
    DataE=Data
    if notnull(s.Extract1): DataE=DataE[DataE[s.Extract1]==s.eVal1]
    # aCol=DataE[DataE[s.Test]=='OK'][s.Col].unique()
    # aRow=DataE[DataE[s.Test]=='OK'][s.Row].unique()    
    aCol=DataE[s.Col].unique()
    aRow=DataE[s.Row].unique()    
    Name=s.Var+"_"+s.View

    #do plot
    nRow=len(aRow)
    nCol=len(aCol)
    aRatio = (nRow+0.5)/(nCol+1) if ASPECT_RATIO else 9/16
    figwidth = FIGWIDTH*0.6 if nCol==3 else FIGWIDTH
    # figData,axs=subplots(nRow,nCol,num='Fig'+str(Name),figsize=(figwidth,aRatio*figwidth),squeeze=False)
    figData,axs=subplots(nRow,nCol,num='Fig'+str(Name),sharex=False,sharey=False,figsize=(figwidth,aRatio*figwidth),squeeze=False)
    # subplots_adjust(hspace=0,wspace=0,left=0.09,bottom=0.09)
    subplots_adjust(hspace=0,wspace=0,left=0,bottom=0)


    if SUP_TITLE: suptitle(FILE_SCENARIO+'  _  '+FILE_DATA_Bkg+'  _  '+str(Name))
    for iCol,oCol in enumerate(aCol):
        for iRow,oRow in enumerate(aRow):
            axi=axs[iRow,iCol]
            sca(axi)

            subData=DataE[(DataE[s.Col]==oCol)&(DataE[s.Row]==oRow)]
            table=subData.pivot_table(values=s.Y,index=s.X,columns=s.Line,aggfunc='mean')
            dataX=subData.pivot_table(values=s.X,index='PatientID',aggfunc='mean').reset_index()
            dataY=subData.pivot_table(values=s.Y,index='PatientID',columns=s.Line,aggfunc='mean').reset_index()
            dataY0=subData.pivot_table(values=s.Y,index='PatientID',aggfunc='mean').reset_index()
            dataXY=merge(dataX,dataY,on='PatientID')
            dataXY.replace(to_replace=0, value='')
            table.replace(to_replace=0, value='')
            # table.style.format({'PertMua':'{0:,.0f} nm','horsepower':'{0:,.0f}hp'})
            # table.plot(ax=axi,marker='D',legend=False)
            table.plot(ax=axi,marker='D',linestyle='',fillstyle='none',legend=False)
            # dataXY.plot(x=s.X,y=LesionType,ax=axi,marker='D',linestyle='',fillstyle='none',legend=False)
            # for i in arange(14):
                # matplotlib.pyplot.annotate(str(dataXY['PatientID'][i]),(dataX[s.X][i],dataY0[s.Y][i]))
                # matplotlib.pyplot.annotate('hello',(0.1,0.1))
            # plot(dataX[LesionType],dataY[LesionType],'D')
            if((iCol==0)and(iRow==1)): legend()
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
            # if iCol==(nCol-1): gca().twinx().set_ylabel(rLab)
            
            
    figData.tight_layout()
    show()
    if SAVE_FIG: figData.savefig(PATH_MAIN+PATH_RESULTS+'Fig_'+str(Name)+'.jpg',format='jpg')
