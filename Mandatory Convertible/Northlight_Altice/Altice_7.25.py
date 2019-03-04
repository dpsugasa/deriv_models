# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 10:28:14 2019

Altice 7.25%


@author: dpsugasa
"""

import pandas as pd
from tia.bbg import LocalTerminal
import numpy as np
from datetime import datetime
import QuantLib as ql
#import plotly
#import plotly.plotly as py #for plotting
#import plotly.offline as offline
#import plotly.graph_objs as go
#import plotly.dashboard_objs as dashboard
#import plotly.tools as tls
#import plotly.figure_factory as ff
import credentials

calc_date = ql.Date(1,1,2019)
ql.Settings.instance().evaluationDate = calc_date

'''
Input Bond Terms

'''
spotPrice = 190
par = 100
coupon_rate = .0575
min_conv_px = 76.6871
max_conv_px = 90.1144
max_ratio = par/min_conv_px
min_ratio = par/max_conv_px
issueDate = ql.Date(10,6,2016)
maturityDate = ql.Date(3,6,2019)
vol_upper = .38
vol_lower = .395
div_yield = 0
ratio_up = par/max_conv_px
ratio_down = par/min_conv_px
ttm_financing_rate = 0.0070
credit_spread = .0025

'''
Current Px & Sizes
'''

size = 160000000
mkt_px = 215.24

'''
Set call schedule
'''

callability_schedule = ql.CallabilitySchedule()
call_price = 103.88
call_date = ql.Date(15,ql.April,2019);
null_calendar = ql.NullCalendar();
for i in range(0,12):
    callability_price  = ql.CallabilityPrice(
        call_price, ql.CallabilityPrice.Clean)
    callability_schedule.append(
            ql.Callability(callability_price, 
                           ql.Callability.Call,
                           call_date))

    call_date = null_calendar.advance(call_date, 3, ql.Months)


'''
Build Yield Curve
retrieve USD curve; S23 USD Swaps (30/360, S/A)
'''
today = datetime.date(datetime.now())
td = datetime.strftime(today, "%d,%m,%Y")
todaysDate = ql.Date(td, "%d,%m,%Y")
ql.Settings.instance().evaluationDate = todaysDate
usd = LocalTerminal.get_reference_data('YCSW0023 Index', 'par_curve', ).as_frame()
s23 = usd.iloc[0].loc['par_curve']

###pull dates
dates = s23['Date'].tolist()
dates = [datetime.strftime(i, "%d,%m,%Y") for i in dates]
ql_dates = [ql.Date(i, "%d,%m,%Y") for i in dates]
ql_dates = [todaysDate] + ql_dates
###pull rates
rates = s23['Rate'].tolist()
on = LocalTerminal.get_reference_data('US00O/N Index', 'PX_LAST').as_frame()
on = on.at['US00O/N Index','PX_LAST']
rates = [np.round(on,decimals = 5)] + rates
rates = [i*.01 for i in rates]
###build yield curve
spotDates = ql_dates
spotRates = rates
dayCount = ql.Actual360()
calendar = ql.UnitedStates()
interpolation = ql.Linear()
compounding = ql.Compounded
compoundingFrequency = ql.Annual
#########################################
spotCurve = ql.ZeroCurve(spotDates, spotRates, dayCount, calendar, interpolation,
                             compounding, compoundingFrequency)
                             
spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)