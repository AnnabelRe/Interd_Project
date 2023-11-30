import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def calc_windows(event_day,dr,L1,L2):
    
    if event_day not in dr:
        print("event day not in dr: "+str(event_day))
        return pd.DataFrame(np.zeros((1, 200))).astype("float32"),pd.DataFrame(np.zeros((1, 41))).astype("float32")
        
    #same index for market and company
    event_index = dr.columns.get_loc(event_day)

    T1_index = (event_index-1)-L2
    T2_index = (event_index)+L2
    T0_index = T1_index-L1
    T3_index = T2_index+L1
    #print(event_day,T0_index, T1_index,T2_index,T3_index) 

    
    # Estimation window
    estimation_window = dr.iloc[:,T0_index:T1_index]
    
    if (estimation_window.transpose().isna().sum().all()>100):
        return pd.DataFrame(np.zeros((1, 200))).astype("float32"),pd.DataFrame(np.zeros((1, 41))).astype("float32")
    estimation_window.transpose().fillna(0.0,inplace=True)
    
    # Event-Window
    event_window = dr.iloc[:,T1_index:T2_index]
    if (event_window.transpose().isna().sum().all()>19):
        return pd.DataFrame(np.zeros((1, 200))).astype("float32"),pd.DataFrame(np.zeros((1, 41))).astype("float32")
    event_window.transpose().fillna(0.0,inplace=True)
    #print(event_window.shape)
    
    return estimation_window,event_window


def calc_linreg(X_train,y_train,X_test,y_test):

    xmean= np.mean(X_train)
    ymean= np.mean(y_train)
    X_train = np.c_[np.ones(X_train.shape[0]), X_train]
    
    model = LinearRegression(fit_intercept=False)
   
    model.fit(X_train,y_train)
    
    X_test = np.c_[np.ones(X_test.shape[0]), X_test]
    
    y_pred = model.predict(X_test)
    
    b = model.coef_[1]
    residuals = (y_test-y_pred)
    a = (xmean)-(b*ymean)

    return a,b,residuals


def gunnar_run(X,Y):
    # add a constant to the X matrix
    X = np.c_[np.ones(X.shape[0]), X]

    # calculate the coefficients
    beta = np.linalg.inv(X.T @ X) @ X.T @ Y

    # calculate the residuals
    eps = Y - X @ beta

    return beta[0], beta[1], eps

def run_calculation_AR(date,cr,mr, L1 = 200, L2 = 20):
    
    cr = pd.DataFrame(cr).transpose()
    
    est_window_market,event_window_market = calc_windows(date,mr,L1,L2)
    est_window_comp,event_window_comp = calc_windows(date,cr,L1,L2)
    
    if (est_window_market.iloc[:,-1:].isnull().values.any() or est_window_comp.iloc[:,-1:].isnull().values.any()):
        return pd.DataFrame(np.zeros((1, 41))).astype("float32")
    
    a,b,eps = calc_linreg(est_window_market.values[0,:],est_window_comp.values[0,:],event_window_market.values[0,:],event_window_comp.values[0,:])

    #a,b,eps = gunnar_run(est_window_market.values[0,:],est_window_comp.values[0,:])
    
    AR = event_window_comp.values - a - (b*event_window_market.values)
    
    return AR,eps
    