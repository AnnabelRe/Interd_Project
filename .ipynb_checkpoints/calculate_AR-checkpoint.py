import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def calc_windows(event_day,dr,L1,L2):
    
    if event_day not in dr:
        #print("event day not in daily return: "+str(event_day)+" " +str(dr.index[-1]))
        return pd.DataFrame(np.zeros((1, 200))).astype("float32"),pd.DataFrame(np.zeros((1, 41))).astype("float32")
        
    #same index for market and company
    event_index = dr.columns.get_loc(event_day)

    T1_index = (event_index-1)-L2
    T2_index = (event_index)+L2
    T0_index = T1_index-L1
    #print(event_day,T0_index, T1_index,T2_index,T3_index) 

    # Estimation window
    estimation_window = dr.iloc[:,T0_index:T1_index]
    
    count = estimation_window.transpose().value_counts()
    if 0.000000 in count: 
        if count[0.000000]>100:
            #print("More than 100 entries with 0.0 in estimation window: "+str(event_day)+" " +str(dr.index[-1]))
            return pd.DataFrame(np.zeros((1, 200))).astype("float32"),pd.DataFrame(np.zeros((1, 41))).astype("float32")
        #estimation_window.transpose().fillna(0.0,inplace=True)
    
    # Event-Window
    event_window = dr.iloc[:,T1_index:T2_index]
    count = event_window.transpose().value_counts()
    if 0.000000 in count:
        if count[0.000000]>19:
            #print("More than 19 entries with 0.0 in event window: "+str(event_day)+" " +str(dr.index[-1]))
            return pd.DataFrame(np.zeros((1, 200))).astype("float32"),pd.DataFrame(np.zeros((1, 41))).astype("float32")
    #event_window.transpose().fillna(0.0,inplace=True)
    #print(event_window.shape)
    
    return estimation_window,event_window


def calc_linreg(X_train,y_train):

    xmean= np.mean(X_train)
    ymean= np.mean(y_train)
    
    X_train = np.c_[np.ones(X_train.shape[0]), X_train]
    
    model = LinearRegression(fit_intercept=False)
   
    model.fit(X_train,y_train)
    
    b = model.coef_[1]

    a = (xmean)-(b*ymean)

    return a,b

def run_calculation_AR(date,cr,mr, L1 = 200, L2 = 20):
    
    cr = pd.DataFrame(cr).transpose()
    
    est_window_market,event_window_market = calc_windows(date,mr,L1,L2)
    est_window_comp,event_window_comp = calc_windows(date,cr,L1,L2)
    
    count_1 = est_window_market.transpose().value_counts()
    count_2 = event_window_market.transpose().value_counts()
    count_3 = est_window_comp.transpose().value_counts()
    count_4 = event_window_comp.transpose().value_counts()
        
    if ((len(count_1) > 1)&(len(count_2) > 1)&(len(count_3) > 1)&(len(count_4) > 1)):
        
        a,b = calc_linreg(est_window_market.values[0,:],est_window_comp.values[0,:])

        AR = event_window_comp.values + a - (b*event_window_market.values)
        eps = est_window_comp.values - (est_window_market.values*b)
        return AR, est_window_market,event_window_market,eps

    else:
        return pd.DataFrame(np.zeros((1, 41))).astype("float32"),est_window_market,event_window_market,pd.DataFrame(np.zeros((1, 200))).astype("float32")
    