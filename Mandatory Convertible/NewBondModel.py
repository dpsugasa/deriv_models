# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 10:18:34 2017

@author: dsugasa
"""

#######################################################################
## 1) Global data
## 2) Date setup
## 3) Construct yield term structure
## 4) Setup initial bond
## 5) Collate results


from QuantLib import *


#######################################################################
## 1) Global data

#switch to quantlib date object
valuation_date = Date(14,4,2014)
maturity_date = Date(1,9,2041)

payment_frequency = Semiannual

#Global data defaults
day_counter = ActualActual(ActualActual.Bond)
compounding = QuantLib.SimpleThenCompounded	

settlement_days = 0

calendar = UnitedStates()
payment_convention = ModifiedFollowing

face = 100
coupon = 0.06875
market_value = 101.5

# Create a dictionary of yield quotes by tenor
zcQuotes = [	(0.0003, Period(1,Months)),
		(0.0004, Period(3,Months)),		
		(0.0006, Period(6,Months)),
		(0.0010, Period(1,Years)),
		(0.0037, Period(2,Years)),
		(0.0082, Period(3,Years)),
		(0.0161, Period(5,Years)),
		(0.0218, Period(7,Years)),
		(0.0265, Period(10,Years)),
		(0.0323, Period(20,Years)),
		(0.0333, Period(25,Years)),
		(0.0348, Period(30,Years))
	]


#######################################################################
## 2) Date setup

Settings.instance().evaluationDate = valuation_date


#######################################################################
## 3) Construct yield term structure

def getTermStructure(valuation_date, zcQuotes, calendar, payment_convention, day_counter):

	fixing_days = 0

	# Create deposit rate helpers
	zcHelpers = [ DepositRateHelper(QuoteHandle(SimpleQuote(r)),
			                tenor, 
					fixing_days,
					calendar, 
					payment_convention,
					True, 
					day_counter)
	      	for (r,tenor) in zcQuotes ]
	
	# Term structure to be used in discounting bond cash flows
	return PiecewiseFlatForward(valuation_date, zcHelpers, day_counter)
	

#######################################################################
## 4) Setup initial bond

def getBond( valuation_date, maturity_date, payment_frequency, calendar, face, coupon, payment_convention, bondDiscountingTermStructure):
	
	#move back a year in order to capture all accrued interest
	#may be caught out if there's an irregular coupon payment at beginning
	issue_date = calendar.advance(valuation_date,-1,Years)
	
	#Bond schedule T&Cs
	fixedBondSchedule = Schedule(	issue_date,
	    	                	maturity_date, 
					Period(payment_frequency),
	                     		calendar,
	                     		Unadjusted, 
					Unadjusted,
	                     		DateGeneration.Backward, 
					False)
	#Bond T&Cs
	fixedRateBond = FixedRateBond(	0,						#Settlement days
	                       		face,
	                       		fixedBondSchedule,
	                       		[coupon],
	                       	 	bondDiscountingTermStructure.dayCounter(),
	                       		payment_convention,
	                       		100,						#Principle ecovery 
					issue_date)

	discountingTermStructure = RelinkableYieldTermStructureHandle()
	discountingTermStructure.linkTo(bondDiscountingTermStructure)	
	
	bondEngine = DiscountingBondEngine(discountingTermStructure)

	#Set new bond engine
	#Ready for use
	fixedRateBond.setPricingEngine(bondEngine)
	
	return fixedRateBond


#######################################################################
## 6) Collate results

def getResults(fixedRateBond):
	
	print (fixedRateBond.NPV())
			


# Handle for the term structure linked to flat forward curve
# I think this is used so that curves can be swapped in and out
# Unsure how to do that yet though
bondDiscountingTermStructure = getTermStructure(valuation_date, zcQuotes, calendar, payment_convention, day_counter)

fixedRateBond = getBond(valuation_date, maturity_date, payment_frequency, calendar, face, coupon, payment_convention, bondDiscountingTermStructure)

getResults(fixedRateBond)
