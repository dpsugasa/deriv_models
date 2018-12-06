# -*- coding: utf-8 -*-
"""
Created on Thu Dec  6 23:36:56 2018

@author: dpsugasa
"""

import pandas as pd
from numpy import sqrt,mean,log,diff
import QuantLib as ql
from pandas_datareader.data import Options
import pandas_datareader.data as web
import datetime

opt = Options('spy', 'google')
expiration_dates = [ql.Date(i.day, i.month, i.year) for i in opt.expiry_dates]
expiry_index = 14 # choose the contracts expire on 11/17/2017
data = opt.get_call_data(expiry=opt.expiry_dates[expiry_index])
strikes = list(data.index.get_level_values('Strike'))
premium = list(data['Last'])
day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()
calculation_date = ql.Date(opt._quote_time.day,opt._quote_time.month,opt._quote_time.year) # 08/10/2017
spot = opt.underlying_price  # spot price is 244.82
ql.Settings.instance().evaluationDate = calculation_date
dividend_yield = ql.QuoteHandle(ql.SimpleQuote(0.0))
risk_free_rate = 0.01
dividend_rate = 0.0
flat_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count))
dividend_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count))
# dummy parameters
initial_var = 0.2; rate_reversion = 0.5; long_term_var = 0.2; corr = -0.75; vol_of_vol = 0.2;
# initial_var = 0.2; rate_reversion = 0.15; long_term_var = 0.6; corr = -0.75; vol_of_vol = 0.2;
process = ql.HestonProcess(flat_ts, dividend_ts,
                           ql.QuoteHandle(ql.SimpleQuote(spot)),
                           initial_var, rate_reversion, long_term_var, vol_of_vol, corr)
model = ql.HestonModel(process)
engine = ql.AnalyticHestonEngine(model)
heston_helpers = []
date = expiration_dates[expiry_index]
for j, s in enumerate(strikes):
    t = (date - calculation_date)
    p = ql.Period(t, ql.Days)
    sigma = premium[j]
    helper = ql.HestonModelHelper(p, calendar, spot, s,
                                  ql.QuoteHandle(ql.SimpleQuote(sigma)),
                                  flat_ts,
                                  dividend_ts)
    helper.setPricingEngine(engine)
    heston_helpers.append(helper)
lm = ql.LevenbergMarquardt(1e-8, 1e-8, 1e-8)
model.calibrate(heston_helpers, lm,
                 ql.EndCriteria(500, 50, 1.0e-8,1.0e-8, 1.0e-8))
long_term_var, rate_reversion, vol_of_vol, corr, initial_var = model.params()
print ("long_term_var = %f, rate_reversion = %f, vol_of_vol = %f, corr = %f, initial_var = %f" % (long_term_var, rate_reversion, vol_of_vol, corr, initial_var))