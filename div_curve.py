# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 11:46:33 2017

@author: dsugasa
"""

import pandas as pd
from tia.bbg import LocalTerminal
import numpy as np
from datetime import datetime
import QuantLib as ql
import numpy as np


td = datetime.strftime(today, "%d,%m,%Y")
todaysDate = ql.Date(td, "%d,%m,%Y")

div_dates = ['22,3,2018',
             '9,8,2018',
             '21,3,2019',
             '8,8,2019',
             '19,3,2020'
             ]
div_dates = [datetime.strptime(i, "%d,%m,%Y") for i in div_dates]
div_dates = [datetime.strftime(i, "%d,%m,%Y") for i in div_dates]

div_dates_ql = [ql.Date(i, "%d,%m,%Y") for i in div_dates]
div_dates_ql = [todaysDate] + div_dates_ql
div_amounts = [0.00,
               0.37,
               0.37,
               0.37,
               0.37,
               0.37
               ]


divs = [ql.FixedDividend(0.37, ql.Date(22,3,2018)),
       ql.FixedDividend(0.37, ql.Date(9,8,2018)),
       ql.FixedDividend(0.37, ql.Date(21,3,2019)),
       ql.FixedDividend(0.37, ql.Date(8,8,2019)),
       ql.FixedDividend(0.37, ql.Date(19,3,2020))]

#today = datetime.date(datetime.now())
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
divCurve = ql.ZeroCurve(div_dates_ql, div_amounts, dayCount, calendar, interpolation,
                             compounding, compoundingFrequency)
                             
spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)

d_vector = ql.DividendVector(divs)

'''
Price the long call option
'''

# construct the European Option
# option data


###yield curve inputs
todaysDate = ql.Date(24,10,2017)
ql.Settings.instance().evaluationDate = todaysDate
spotDates = [ql.Date(24, 10, 2017), ql.Date(1, 5, 2018), ql.Date(1, 5, 2019), ql.Date(1,5,2021)]
spotRates = [0.0, 0.0125, 0.015, 0.02]
dayCount = ql.Actual360()
calendar = ql.UnitedStates()
interpolation = ql.Linear()
compounding = ql.Compounded
compoundingFrequency = ql.Annual

###build yield curve
spotCurve = ql.ZeroCurve(spotDates, spotRates, dayCount, calendar, interpolation,
                             compounding, compoundingFrequency)
spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)


today = datetime.date(datetime.now())
td = datetime.strftime(today, "%d,%m,%Y")
todaysDate = ql.Date(td, "%d,%m,%Y")
maturity_date = ql.Date(10,10,2020)
spot_price = 14.45
strike_price = 13.6914
volatility = 0.35 # the historical vols or implied vols
dividend_rate =  divs
option_type = ql.Option.Call

risk_free_rate = 0.001
day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()

calculation_date = todaysDate
ql.Settings.instance().evaluationDate = calculation_date

payoff = ql.PlainVanillaPayoff(option_type, strike_price)
settlement = calculation_date

eu_exercise = ql.EuropeanExercise(maturity_date)
european_option = ql.VanillaOption(payoff, eu_exercise)

spot_handle = ql.QuoteHandle(
    ql.SimpleQuote(spot_price)
)
flat_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count)
)
#dividend_yield = ql.YieldTermStructureHandle(
#    ql.FlatForward(calculation_date, dividend_rate, day_count)
#)
flat_vol_ts = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(calculation_date, calendar, volatility, day_count)
)
bsm_process = ql.BlackScholesMertonProcess(spot_handle, 
                                           divs, 
                                           spotCurveHandle, 
                                           flat_vol_ts)

steps = 1000
binomial_engine = ql.AnalyticDividendEuropeanEngine(bsm_process)
european_option.setPricingEngine(binomial_engine)
#print (european_option.NPV()*ratio_up)

#AnalyticDividendEuropeanEngine
#BinomialVanillaEngine