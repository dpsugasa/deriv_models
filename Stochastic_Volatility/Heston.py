# -*- coding: utf-8 -*-
"""
Created on Thu Dec  6 23:34:44 2018

@author: dpsugasa
"""

from numpy import sqrt, exp
import numpy as np

def mc_heston(option_type,S0,K,T,initial_var,long_term_var,rate_reversion,vol_of_vol,corr,r,num_reps,steps):
    """
    option_type:    'p' put option 'c' call option
    S0:              the spot price of underlying stock
    K:              the strike price
    T:              the maturity of options
    initial_var:    the initial value of variance
    long_term_var:  the long term average of price variance
    rate_reversion: the mean reversion rate for the variance
    vol_of_vol:     the volatility of volatility(the variance of the variance of stock price)
    corr:           the correlation between the standard normal random variables W1 and W2
    r:              the risk free rate
    reps:           the number of repeat for monte carlo simulation
    steps:          the number of steps in each simulation
    """
    delta_t = T/float(steps)
    payoff = 0
    for i in range(num_reps):
        vt = initial_var
        st = S0
        for j in range(steps):
            w1 = np.random.normal(0, 1)
            w2 = corr*w1+sqrt(1-corr**2)*np.random.normal(0, 1)
            vt = (sqrt(vt) + 0.5 * vol_of_vol * sqrt(delta_t) * w1)**2  \
                 - rate_reversion * (vt - long_term_var) * delta_t \
                 - 0.25 * vol_of_vol**2 * delta_t
            st = st * exp((r - 0.5*vt)*delta_t + sqrt(vt*delta_t) * w2)
        if option_type == 'c':
                payoff += max(st - K, 0)
        elif option_type == 'p':
                payoff += max(K - st, 0)

    return (payoff/float(num_reps)) * (exp(-r*T))