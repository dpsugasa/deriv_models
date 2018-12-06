# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 10:01:02 2017

Downloading rate curves for Quantlib; experimenting with vol surfaces

@author: dsugasa
"""

import pandas as pd
from tia.bbg import LocalTerminal
import numpy as np
from datetime import datetime
import QuantLib as ql
import numpy as np

#YCSW0022 Index

# retrieve GBP curve using API; S22 GBP (vs. 6M Libor)

gbp = LocalTerminal.get_reference_data('YCSW0022 Index', 'par_curve', ).as_frame()
gbp2 = gbp.iloc[0].loc['par_curve']

dates = gbp2['Date'].tolist()
disc = gbp2['Discount Factor'].tolist()

dates = [datetime.strftime(i, "%d,%m,%Y") for i in dates]
ql_dates = [ql.Date(i, "%d,%m,%Y") for i in dates]
rates = gbp2['Rate'].tolist()




#mgr = dm.BbgDataManager()
## set dates, securities, and fields
#start_date = '01/01/2010'
#end_date = "{:%m/%d/%Y}".format(datetime.now())
#IDs = ['SX5E Index', 'DAX Index', 'UKX Index', 'FTSEMIB Index', 'IBEX Index',
#       'CAC Index', 'TOP40 Index', 'XU100 Index', 'NKY Index', 'TPX Index',
#       'KOSPI2 Index', 'HSI Index', 'HSCEI Index', 'SHCOMP Index', 'TWSE Index', 
#       'AS51 Index', 'STI Index', 'NIFTY Index', 'MXAPEXA Index', 'SPX Index',
#       'NDX Index', 'RTY Index', 'IBOV Index', 'MEXBOL Index', 'SPTSX Index',
#       'RTSI$ Index'
#       ]
#sids = mgr[IDs]
#fields = ['LAST PRICE', 'HIGH', 'LOW']
#
#df = sids.get_historical(fields, start_date, end_date)

###yield curve inputs

today = datetime.date(datetime.now())
td = datetime.strftime(today, "%d,%m,%Y")
todaysDate = ql.Date(td, "%d,%m,%Y")
ql.Settings.instance().evaluationDate = todaysDate
spotDates = ql_dates
spotRates = rates
dayCount = ql.Actual360()
calendar = ql.UnitedKingdom()
interpolation = ql.Linear()
compounding = ql.Compounded
compoundingFrequency = ql.Annual

###build yield curve

#discountCurve = ql.InterpolatedDiscountCurve(spotDates, spotRates, dayCount, interpolation)

spotCurve = ql.ZeroCurve(spotDates, spotRates, dayCount, calendar, interpolation,
                             compounding, compoundingFrequency)
                             #compounding, compoundingFrequency)
spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)


'''
Dividend Curve!!!!
'''



