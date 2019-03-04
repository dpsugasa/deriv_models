# -*- coding: utf-8 -*-
"""

Altice 7.25% 05/15/2022

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
import plotly.tools as tls
import plotly.figure_factory as ff
import credentials

#ql.Settings.instance().evaluationDate = calc_date

'''
Input Bond Terms

'''
par = 100
coupon_rate = .0725
issueDate = ql.Date(23,4,2014)
maturityDate = ql.Date(15,5,2022)

'''
adding call schedule
***I suspect there is a simpler better way to do this***
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

'''
setting bond terms:
pricing with no call schedule; no credit risk

'''

###bond terms
issueDate = issueDate
maturityDate = maturityDate
tenor = ql.Period(ql.Quarterly)
calendar = ql.UnitedStates()
businessConvention = ql.Unadjusted
dateGeneration = ql.DateGeneration.Backward
monthEnd = False
schedule = ql.Schedule (issueDate, maturityDate, tenor, calendar, businessConvention,
                            businessConvention , dateGeneration, monthEnd)

###Coupon stream
dayCount = ql.Actual360()
couponRate = coupon_rate
coupons = [couponRate]

####construct the bond
settlementDays = 0
faceValue = par
fixedRateBond = ql.FixedRateBond(settlementDays, faceValue, schedule, coupons, dayCount)

bondEngine = ql.DiscountingBondEngine(spotCurveHandle)
fixedRateBond.setPricingEngine(bondEngine)

###price the bond
print ("No calls/no credit Bond price: ", fixedRateBond.NPV())

'''
setting bond terms:
pricing with call schedule; no credit risk

'''

settlement_days = 3
face_amount = 100
accrual_daycount = ql.ActualActual(ql.ActualActual.Bond)
coupon = coupon_rate


bond = ql.CallableFixedRateBond(
    settlement_days, face_amount,
    schedule, [coupon], accrual_daycount,
    ql.Following, face_amount, issueDate,
    callability_schedule)

def value_bond(a, s, grid_points, bond):
    model = ql.HullWhite(spotCurveHandle, a, s)
    engine = ql.TreeCallableFixedRateBondEngine(model, grid_points)
    bond.setPricingEngine(engine)
    return bond

value_bond(0.01, 0.08, 40, bond)
print ("Calls/no credit Bond price: ",bond.NPV())

'''
setting bond terms:
pricing with no call schedule; simple credit risk

'''

settlement_days = 2
day_count = ql.Actual360()
coupon_rate_2 = coupon_rate
coupons_2 = [coupon_rate_2]

# Now lets construct the FixedRateBond
settlement_days = 0
face_value = par

fixed_rate_bond = ql.FixedRateBond(
    settlement_days, 
    face_value, 
    schedule, 
    coupons_2, 
    day_count)

spread21 = ql.SimpleQuote(0.0120)
spread22 = ql.SimpleQuote(0.045)

spread_date = calendar.advance(todaysDate, ql.Period(1, ql.Years))
end_date = calendar.advance(todaysDate, ql.Period(5, ql.Years))
ts_spreaded2 = ql.SpreadedLinearZeroInterpolatedTermStructure(
    spotCurveHandle,
    [ql.QuoteHandle(spread21), ql.QuoteHandle(spread22)],
    [spread_date, end_date]
)
ts_spreaded_handle2 = ql.YieldTermStructureHandle(ts_spreaded2)

bond_engine_2 = ql.DiscountingBondEngine(ts_spreaded_handle2)
fixed_rate_bond.setPricingEngine(bond_engine_2)

def value_bond_2(a, s, grid_points, bond):
    model = ql.HullWhite(ts_spreaded_handle2, a, s)
    engine = ql.TreeCallableFixedRateBondEngine(model, grid_points)
    bond.setPricingEngine(engine)
    return bond

value_bond_2(0.01, 0.08, 40, bond)
print ("No calls/simple credit Bond price: ",bond.NPV())


'''
setting bond terms:
pricing with call schedule; more advanced credit risk

'''
altice = LocalTerminal.get_reference_data('YCCD2204 Index', 'CURVE_TENOR_RATES', ).as_frame()
curve = altice.iloc[0].loc['CURVE_TENOR_RATES']
memb = curve['Tenor Ticker'].tolist()
memb = memb[1:]
tenor = curve['Tenor'].tolist()
tenor =  tenor[1:]
rates = []

#y = LocalTerminal.get_historical('CY188822 Curncy', 'LAST PRICE' ).as_frame()
for i in memb:
    z = LocalTerminal.get_reference_data(i, 'CDS_FLAT_SPREAD', ).as_frame()
    rates.append(z.loc[i].item())
    
    
print ("Altice CDS curve:", rates)
    



