#! /usr/bin/python
# TODO move me to an investment excel helper

def raw_investment_return(time_year, initial_investment, rate):
    return initial_investment * (1 + rate) ** time_year


def yearly_installment(time_year, initial_investment, rate):
    total = 0
    while t > 0:
        total += raw_investment_return(time_year, initial_investment, rate)
        t -= 1
    return total


def return_on_investment(time_year, initial_investment, rate):
    return yearly_installment(t, inv, r) - (t * inv)
