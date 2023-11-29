from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np


def linearReg(x,y):
    x = sm.add_constant(x)
    model = LinearRegression(x,y).fit()
    
    print(model.summary())
    
    # Remove the constant
    x = x[:,1]
    return model.params[0], model.params[1]



