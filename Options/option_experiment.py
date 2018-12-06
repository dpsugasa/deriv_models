# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 16:53:54 2017

@author: dsugasa
"""

import pandas as pd
from tia.bbg import LocalTerminal
import numpy as np
from datetime import datetime
import QuantLib as ql
import plotly
import plotly.plotly as py #for plotting
import plotly.offline as offline
import plotly.graph_objs as go
import plotly.dashboard_objs as dashboard
plotly.tools.set_credentials_file(username='dpsugasa', api_key='yuwwkc1sb0')
import plotly.tools as tls
import plotly.figure_factory as ff
tls.embed('https://plot.ly/~dpsugasa/1/')

today = datetime.date(datetime.now())
td = datetime.strftime(today, "%d,%m,%Y")
todaysDate = ql.Date(td, "%d,%m,%Y")

'''
Input Bond Terms

'''
spotPrice = 14.95
par = 100000
coupon_rate = .04125
min_conv_px = 13.4992
max_conv_px = 14.8491
max_ratio = par/min_conv_px
min_ratio = par/max_conv_px
issueDate = ql.Date(10,10,2017)
maturityDate = ql.Date(10,10,2020)
vol_upper = .35
vol_lower = .365
div_yield = .04
ratio_up = par/max_conv_px
ratio_down = par/min_conv_px
ttm_financing_rate = 0.0075
credit_spread = .0025

'''
Current Px & Sizes
'''

size = 850000000
mkt_px = 115.253

'''
Build the dividend curve
'''


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

 
'''
Build Yield Curve
retrieve USD curve; S23 USD Swaps (30/360, S/A)
'''

ql.Settings.instance().evaluationDate = todaysDate
usd = LocalTerminal.get_reference_data('YCSW0022 Index', 'par_curve', ).as_frame()
s22 = usd.iloc[0].loc['par_curve']

###pull dates
dates = s22['Date'].tolist()
dates = [datetime.strftime(i, "%d,%m,%Y") for i in dates]
ql_dates = [ql.Date(i, "%d,%m,%Y") for i in dates]
ql_dates = [todaysDate] + ql_dates
###pull rates
rates = s22['Rate'].tolist()
on = LocalTerminal.get_reference_data('US00O/N Index', 'PX_LAST').as_frame()
on = on.at['US00O/N Index','PX_LAST']
rates = [np.round(on,decimals = 5)] + rates
rates = [i*.01 for i in rates]
###build yield curve
spotDates = ql_dates
spotRates = rates
dayCount = ql.Actual365Fixed()
calendar = ql.UnitedKingdom()
interpolation = ql.Linear()
compounding = ql.Compounded
compoundingFrequency = ql.Semiannual
#########################################
spotCurve = ql.ZeroCurve(spotDates, spotRates, dayCount, calendar, interpolation,
                             compounding, compoundingFrequency)
                             
spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)

'''
Price the long call option
'''

# construct the European Option
# option data

maturity_date = maturityDate
spot_price = spotPrice
strike_price = max_conv_px
volatility = vol_upper
dividend_rate =  div_yield
option_type = ql.Option.Call

day_count = ql.Actual360()
calendar = ql.UnitedKingdom()

calculation_date = todaysDate
ql.Settings.instance().evaluationDate = calculation_date

payoff = ql.PlainVanillaPayoff(option_type, strike_price)
settlement = calculation_date

eu_exercise = ql.EuropeanExercise(maturity_date)
european_option = ql.VanillaOption(payoff, eu_exercise)

spot_handle = ql.QuoteHandle(
    ql.SimpleQuote(spot_price))

dividend_yield = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count))

flat_vol_ts = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(calculation_date, calendar, volatility, day_count))

bsm_process = ql.BlackScholesMertonProcess(spot_handle, 
                                           dividend_yield, 
                                           spotCurveHandle, 
                                           flat_vol_ts)

bs_process = ql.BlackScholesProcess(spot_handle, spotCurveHandle, flat_vol_ts)

steps = 1000
engine = ql.AnalyticDividendEuropeanEngine(bsm_process)
european_option.setPricingEngine(engine)
long_call = european_option.NPV()