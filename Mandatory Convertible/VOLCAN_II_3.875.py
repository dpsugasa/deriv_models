# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 15:57:54 2017
Volcan II
VLCHLD 3.875% 04/11/2020

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
coupon_rate = .03875
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
mkt_px = 109.30

'''
Build the dividend curve
'''


div_dates = ['22,3,2018',
             '9,8,2018',
             '21,3,2019',
             '8,8,2019',
             '19,3,2020',
             '6,8,2020'
             ]
div_dates = [datetime.strptime(i, "%d,%m,%Y") for i in div_dates]
div_dates = [datetime.strftime(i, "%d,%m,%Y") for i in div_dates]

div_dates_ql = [ql.Date(i, "%d,%m,%Y") for i in div_dates]
#div_dates_ql = [todaysDate] + div_dates_ql
div_amounts = [
               0.37,
               0.37,
               0.37,
               0.37,
               0.37,
               0.37
               ]

 
'''
Build Yield Curve
retrieve GBP curve; S22 USD Swaps (30/360, S/A)
'''

ql.Settings.instance().evaluationDate = todaysDate
gbp = LocalTerminal.get_reference_data('YCSW0022 Index', 'par_curve', ).as_frame()
s22 = gbp.iloc[0].loc['par_curve']

###pull dates
dates = s22['Date'].tolist()
dates = [datetime.strftime(i, "%d,%m,%Y") for i in dates]
ql_dates = [ql.Date(i, "%d,%m,%Y") for i in dates]
ql_dates = [todaysDate] + ql_dates
###pull rates
rates = s22['Rate'].tolist()
on = LocalTerminal.get_reference_data('BP00O/N Index', 'PX_LAST').as_frame()
on = on.at['BP00O/N Index','PX_LAST']
rates = [np.round(on,decimals = 5)] + rates
rates = [i*.01 for i in rates]
###build yield curve
spotDates = ql_dates
spotRates = rates
dayCount = ql.Actual360()
calendar = ql.UnitedKingdom()
interpolation = ql.Linear()
compounding = ql.Compounded
compoundingFrequency = ql.Annual
#########################################
spotCurve = ql.ZeroCurve(spotDates, spotRates, dayCount, calendar, interpolation,
                             compounding, compoundingFrequency)
                             
spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)

'''
Modelling the 'Risk-Free' Par Value
'''

###bond terms
issueDate = issueDate
maturityDate = maturityDate
tenor = ql.Period(ql.Semiannual)
calendar = ql.UnitedKingdom()
businessConvention = ql.Unadjusted
dateGeneration = ql.DateGeneration.Backward
monthEnd = False
schedule = ql.Schedule (issueDate, maturityDate, tenor, calendar, businessConvention,
                            businessConvention , dateGeneration, monthEnd)

###Coupon stream
dayCount = ql.ActualActual()
couponRate = 0
coupons = [couponRate]

####construct the bond
settlementDays = 2
faceValue = par
fixedRateBond = ql.FixedRateBond(settlementDays, faceValue, schedule, coupons, dayCount)

bondEngine = ql.DiscountingBondEngine(spotCurveHandle)
fixedRateBond.setPricingEngine(bondEngine)

###price the bond
fixedRateBond.NPV()

'''
Modelling the 'Risky' Coupon Value
'''

settlement_days = 2
day_count = ql.ActualActual()
coupon_rate_2 = coupon_rate
coupons_2 = [coupon_rate_2]

# Now lets construct the FixedRateBond
#settlement_days = 0
face_value = par

fixed_rate_bond = ql.FixedRateBond(
    settlement_days, 
    face_value, 
    schedule, 
    coupons_2, 
    day_count)

spread21 = ql.SimpleQuote(credit_spread)
spread22 = ql.SimpleQuote(credit_spread)

start_date = issueDate
end_date = calendar.advance(start_date, ql.Period(3, ql.Years))
ts_spreaded2 = ql.SpreadedLinearZeroInterpolatedTermStructure(
    spotCurveHandle,
    [ql.QuoteHandle(spread21), ql.QuoteHandle(spread22)],
    [start_date, end_date]
)
ts_spreaded_handle2 = ql.YieldTermStructureHandle(ts_spreaded2)

bond_engine_2 = ql.DiscountingBondEngine(ts_spreaded_handle2)
fixed_rate_bond.setPricingEngine(bond_engine_2)

# Finally the price
fixed_rate_bond.NPV()

'''
Price the long call option
'''

# construct the European Option

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
#european_option = ql.DividendVanillaOption(payoff, eu_exercise, div_dates_ql, div_amounts)

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
#bs_process = ql.BlackScholesProcess(spot_handle, spotCurveHandle, flat_vol_ts)


steps = 1000
engine = ql.AnalyticDividendEuropeanEngine(bsm_process)
european_option.setPricingEngine(engine)
long_call = european_option.NPV()

'''
Price the short put option

'''

maturity_date = maturityDate
spot_price = spotPrice
strike_price_2 = min_conv_px
volatility_2 = vol_lower # the historical vols or implied vols
dividend_rate =  div_yield
option_type_2 = ql.Option.Put


day_count = ql.Actual360()
calendar = ql.UnitedKingdom()

calculation_date = todaysDate
ql.Settings.instance().evaluationDate = calculation_date

payoff_2 = ql.PlainVanillaPayoff(option_type_2, strike_price_2)
settlement = calculation_date

eu_exercise = ql.EuropeanExercise(maturity_date)
european_option_2 = ql.VanillaOption(payoff_2, eu_exercise)
#european_option_2 = ql.DividendVanillaOption(payoff_2, eu_exercise, div_dates_ql, div_amounts)

spot_handle = ql.QuoteHandle(
    ql.SimpleQuote(spot_price))

dividend_yield = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count))

flat_vol_ts_2 = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(calculation_date, calendar, volatility_2, day_count))

bsm_process_2 = ql.BlackScholesMertonProcess(spot_handle, 
                                           dividend_yield, 
                                           spotCurveHandle, 
                                           flat_vol_ts_2)
#bs_process_2 = ql.BlackScholesProcess(spot_handle, spotCurveHandle, flat_vol_ts_2)

steps = 1000
engine_2 = ql.AnalyticDividendEuropeanEngine(bsm_process_2)
european_option_2.setPricingEngine(engine_2)
short_put = european_option_2.NPV()

'''
Prices and Greeks
'''

def current_parity():
    if spotPrice > max_conv_px:
        return spotPrice*min_ratio
    elif spotPrice < min_conv_px:
        return spotPrice*max_ratio
    elif min_conv_px <= spotPrice <= max_conv_px:
        return (par/spotPrice)*spotPrice

call_ratio = np.round(long_call*ratio_up, 3)
put_ratio = np.round(short_put*ratio_down, 3)
risky_coupons = np.round((fixed_rate_bond.NPV() - fixedRateBond.NPV()), 3)
bond = np.round(fixedRateBond.NPV(), 3)
mando_px = np.round(((risky_coupons+bond+call_ratio) - put_ratio)/1000, 3)

###Price with financing included
Boro = ql.InterestRate(ttm_financing_rate, dayCount, compounding, compoundingFrequency)
years = (maturityDate - todaysDate)/365
df = Boro.discountFactor(years)
fin_mando_px = np.round((mando_px*df), 3)

points_cheap = np.round((fin_mando_px - mkt_px), 3)
pts_cheap_year = np.round((points_cheap/years), 3)
tot_carry = np.round((points_cheap/100)*size, 3)
carry_yr = np.round((pts_cheap_year/100)*size, 3)
parity_points = np.round(mkt_px-(current_parity()/1000), 3)
carry_mat = np.round(((maturityDate - todaysDate)*(coupon_rate/365)*100),3)   


print ('################################')
print ('Call Ratio: %s' % call_ratio)
print ('Put Ratio: %s' % put_ratio)
print ('Risky Coupons: %s' % risky_coupons)
print ('Bond: %s' % bond)
print ('Mando Px: %s' % mando_px)
print ('Mando Px w/ Fin: %s' % fin_mando_px)


put_d = np.abs(european_option_2.delta()*ratio_down)
call_d = np.abs(european_option.delta()*ratio_up)
put_g = np.abs(european_option_2.gamma()*ratio_down)
call_g = np.abs(european_option.gamma()*ratio_up)
#put_v = np.abs(european_option_2.vega()*ratio_down)
#call_v = np.abs(european_option.vega()*ratio_up)
#put_t = np.abs(european_option_2.thetaPerDay()*ratio_down)
#call_t = np.abs(european_option.theta()*ratio_up)
print ('################################')
#print (put_d)
#print (call_d)
print ('Delta (shares per bond): %s' % np.round((put_d + call_d),3))
print ('Gamma: %s' % np.round((put_g + call_g),3))
#print ('Vega: %s' % (put_v + call_v))
#print ('Theta Per Day: %s' % (put_t + call_t)
print ('################################')
print ('Parity: %s' % np.round(current_parity()/1000,3))
print ('Points Above Parity: %s' % parity_points)
print ('Carry to Maturity (pts./no financing): %s' % carry_mat)       
print ('Years: %s' % np.round(years,3))       
print ('Points Cheap: %s' % np.round(points_cheap,3))
print ('Pts. Cheap Per Year: %s' % np.round(pts_cheap_year,3))
print ('Total Carry: %s' % tot_carry) 
print ('Yearly Carry: %s' % carry_yr)       

data_matrix = [['Volcan I 3.875% 2020 Mandatory', ''],
               ['Mando Price', mando_px],
               ['Mando Price w/ Fin', fin_mando_px],
               ['Delta', np.round((put_d + call_d),3)],
               ['Parity', np.round(current_parity(),3)],
               ['Points Above Parity', parity_points],
               ['Carry to Mat.', carry_mat],
               ['Points Cheap', points_cheap],
               ['Pts. Cheap Per Year', pts_cheap_year],
               ]

colorscale = [[0, '#4d004c'],[.5, '#f2e5ff'],[1, '#ffffff']]
table = ff.create_table(data_matrix, height_constant = 20)
py.iplot(table, filename='Mandatory_Convertibles/Volcan_II')

#dboard = dashboard.Dashboard()
#
#box_1 = {
#        'type' : 'box',
#        'boxType':'plot',
#        'fileId': 'dpsugasa:683',
#        'shareKey': None,
#        'title': 'Volcan I'
#}

#dboard.insert(box_1)
#dboard['settings']['title'] = 'BABA 5.75% 2019 Details'
#py.dashboard_ops.upload(dboard, 'BABA 2019 Mandatory')