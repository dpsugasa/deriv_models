# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 16:02:27 2017

Trying to create a Mandatory Convertible Model Using Quantlib; tired of dealing with other models

@author: dsugasa
"""

import QuantLib as ql
import numpy as np

ratio_up = 100000/13.6914
ratio_down = 100000/12.4467


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

'''
Modelling the 'Risk-Free' Par Value
'''

###bond terms
issueDate = ql.Date(20,9,2017)
maturityDate = ql.Date(10,10,2020)
tenor = ql.Period(ql.Semiannual)
calendar = ql.UnitedStates()
businessConvention = ql.Unadjusted
dateGeneration = ql.DateGeneration.Backward
monthEnd = False
schedule = ql.Schedule (issueDate, maturityDate, tenor, calendar, businessConvention,
                            businessConvention , dateGeneration, monthEnd)

###Coupon stream
dayCount = ql.Actual360()
couponRate = 0
coupons = [couponRate]

####construct the bond
settlementDays = 0
faceValue = 100000
fixedRateBond = ql.FixedRateBond(settlementDays, faceValue, schedule, coupons, dayCount)

bondEngine = ql.DiscountingBondEngine(spotCurveHandle)
fixedRateBond.setPricingEngine(bondEngine)

###price the bond
fixedRateBond.NPV()

'''
Modelling the 'Risky' Coupon Value
'''

settlement_days = 2
day_count = ql.Actual360()
coupon_rate = .04125
coupons = [coupon_rate]

# Now lets construct the FixedRateBond
settlement_days = 0
face_value = 100000

fixed_rate_bond = ql.FixedRateBond(
    settlement_days, 
    face_value, 
    schedule, 
    coupons, 
    day_count)

spread21 = ql.SimpleQuote(0.0025)
spread22 = ql.SimpleQuote(0.0025)

start_date = issueDate
end_date = calendar.advance(start_date, ql.Period(5, ql.Years))
ts_spreaded2 = ql.SpreadedLinearZeroInterpolatedTermStructure(
    spotCurveHandle,
    [ql.QuoteHandle(spread21), ql.QuoteHandle(spread22)],
    [start_date, end_date]
)
ts_spreaded_handle2 = ql.YieldTermStructureHandle(ts_spreaded2)

bond_engine = ql.DiscountingBondEngine(ts_spreaded_handle2)
fixed_rate_bond.setPricingEngine(bond_engine)

# Finally the price
fixed_rate_bond.NPV()

'''
Price the long call option
'''

# construct the European Option
# option data

maturity_date = maturityDate
spot_price = 14.45
strike_price = 13.6914
volatility = 0.35 # the historical vols or implied vols
dividend_rate =  .01
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
dividend_yield = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count)
)
flat_vol_ts = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(calculation_date, calendar, volatility, day_count)
)
bsm_process = ql.BlackScholesMertonProcess(spot_handle, 
                                           dividend_yield, 
                                           spotCurveHandle, 
                                           flat_vol_ts)

steps = 1000
binomial_engine = ql.AnalyticDividendEuropeanEngine(bsm_process)
european_option.setPricingEngine(binomial_engine)
#print (european_option.NPV()*ratio_up)

#AnalyticDividendEuropeanEngine
#BinomialVanillaEngine


'''
Price the short put option

'''

maturity_date = maturityDate
spot_price = 14.455
strike_price_2 = 12.4467
volatility_2 = 0.37 # the historical vols or implied vols
dividend_rate =  .01
option_type_2 = ql.Option.Put

risk_free_rate = 0.001
day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()

calculation_date = todaysDate
ql.Settings.instance().evaluationDate = calculation_date

payoff_2 = ql.PlainVanillaPayoff(option_type_2, strike_price_2)
settlement = calculation_date

eu_exercise = ql.EuropeanExercise(maturity_date)
european_option_2 = ql.VanillaOption(payoff_2, eu_exercise)

spot_handle = ql.QuoteHandle(
    ql.SimpleQuote(spot_price)
)
flat_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count)
)
dividend_yield = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count)
)
flat_vol_ts_2 = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(calculation_date, calendar, volatility_2, day_count)
)
bsm_process_2 = ql.BlackScholesMertonProcess(spot_handle, 
                                           dividend_yield, 
                                           spotCurveHandle, 
                                           flat_vol_ts_2)

steps = 1000
binomial_engine_2 = ql.BinomialVanillaEngine(bsm_process_2, "crr", steps)
european_option_2.setPricingEngine(binomial_engine_2)

booty_jams = european_option.NPV()*ratio_up
booty_jayz = european_option_2.NPV()*ratio_down
risky_coupons = fixed_rate_bond.NPV() - fixedRateBond.NPV()
bond = fixedRateBond.NPV()
mando = (risky_coupons+bond+booty_jams) - booty_jayz

print (booty_jams)
print (booty_jayz)
print (risky_coupons)
print (bond)
print (mando)


put_d = np.abs(european_option_2.delta()*ratio_up)
call_d = np.abs(european_option.delta()*ratio_down)

print (put_d)
print (call_d)
print ((put_d + call_d)*10)



