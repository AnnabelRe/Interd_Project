import pandas as pd
import numpy as np
import pickle
from scipy.stats import ttest_ind
import seaborn as sns
import matplotlib.pyplot as plt
from IPython.display import clear_output

path = "/Users/admin/Documents/Interd Project/data/"

np.random.seed(11914287)
    
ARs = pd.DataFrame()

for i in range(4):
    part = pd.read_pickle(path+"/ARs/" +f"ARs_{i}.pkl")
    ARs = pd.concat([ARs,part])

ARs = ARs.reset_index(drop=True)

# TBD : DROP FOLLOWING AFTER NEW AR CALCULATION 
old_shape =ARs.shape[0]
#drop empty df
ARs.dropna(subset="-20",inplace=True)
ARs.dropna(subset="-1",inplace=True)
# need to drop SKYX bcs of extreme outliers
ARs = ARs.drop(ARs[ARs["Ticker"]=="SKYX"].index)


def draw_histo(CAR_m,CAR_f,ttype,tf):
    sample_size = 1500 
    subs_diff = []
    subs_avg_CAR_m = []
    subs_avg_CAR_f = []
    
    for i in range(10000):
        # pick subsample
        subsample_m = np.random.choice(CAR_m, sample_size, replace=True)
        subsample_f = np.random.choice(CAR_f, sample_size, replace=True)
        diff = subsample_m-subsample_f
        if (subsample_m.mean() < 1) & (subsample_m.mean()>-1):
            subs_avg_CAR_m.append(subsample_m.mean())
        else:
            print("ERROR: CAR_M outlier")
        subs_avg_CAR_f.append(subsample_f.mean())
        
        subs_diff.append(np.round(diff.mean(),6))

    fig = plt.figure(figsize=(10, 5))
    sns.histplot(subs_avg_CAR_m,bins = 100, alpha=0.6,color= "darkorange")
    sns.histplot(subs_avg_CAR_f,bins = 100, alpha=0.6,color="teal")
    plt.legend(["male", "female"])
    plt.xlabel("Mean of CAR")
    plt.ylabel("Count")

    plt.title(f"Histogram of means of samples of CARs for {ttype} in timeframe {tf}]")
    plt.savefig(path+f"/Vis/ttest_{ttype}_{tf}", dpi=600, bbox_inches='tight')

    clear_output(wait=True)
    plt.show()
    
    return subs_diff
    
if __name__ == "__main__":   
    ttest_results = []
    ttest_params = []   
    timeframes = [("-20","-1"),("0","5"),("0","10"),("0","20")]
    tradetype = ARs["Trade Type"].unique()

    for ttype in tradetype: 
        for tf in timeframes:
            #print(ttype)

            start = ARs.columns.get_loc(tf[0])
            end = ARs.columns.get_loc(tf[1])
            #print(start,end)
            ARs_subset = ARs[ARs["Trade Type"]==ttype]

            male = ARs_subset[ARs_subset["Gender"]=="Male"]
            CAR_m = male.iloc[:,start:end+1].sum(axis=1)

            female = ARs_subset[ARs_subset["Gender"]=="Female"]
            CAR_f = female.iloc[:,start:end+1].sum(axis=1)

            if ((CAR_m.mean() < 1) & (CAR_m.mean()>-1)):
                CAAR_diff = CAR_m.mean() -CAR_f.mean() 
            #print("CAAR:" +str(CAAR_diff))
            else: 
                print("ERROR: CAR mean"+str(CAR_m.mean()))

            subs_diff = draw_histo(CAR_m,CAR_f,ttype,tf)

            sign = int(2*(bool(CAAR_diff<0) -0.5)) 
            p_value = 2*np.mean(sign*np.asarray(subs_diff) > 0) 
            ttest_params.append((ttype, tf))
            ttest_results.append((CAAR_diff, p_value))

    
    with open(path+'ttest_params.pkl', 'wb') as f:
        pickle.dump(ttest_params, f)
    with open(path+'ttest_results.pkl', 'wb') as f:
        pickle.dump(ttest_results, f)

 