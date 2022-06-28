from datetime import *

#returns peak period
def peak_period():
    now = datetime.now()
    mon = date.today()
    month = mon.strftime("%m")
    current_hour = now.strftime("%H")
    hour = int(current_hour)
    
    peak = False
    mid_peak = False
    off_peak = False
    Summer = ['06','07','08'] 
    if month in Summer:
        if hour in range (15,20):
            peak = True
            print("peak")
        elif (hour in range(6,15)) or (hour in range(20,22)):
            mid_peak = True
            print("mid_peak")
        else:
            off_peak = True
            print("off_peak")
    else:
        if hour in range (6,10) or hour in range(17,20):
            peak = True
            print("peak")
        elif hour in range(10,17) or hour in range(20,22):
            mid_peak = True
            print("mid_peak")
        else:
            off_peak = True
            print("off_peak")
    return(peak, mid_peak, off_peak)

#returns decision
def stability(frequency,voltage,peak,mid_peak,off_peak):
    increase = False
    inc_val = 0
    decrease = False
    dec_val = 0
    minimize = False
    min_val = 0
    i = min(len(frequency),len(voltage))
    for j in range (0,i):
        f_st=False
        v_st=False
        f=frequency[j]
        v=voltage[j]
        if f>=50:
            if f <= 52.5:
                f_st=True
                print("50<=",f,"<=52.2\n")
            else:
                increase = True
                if off_peak:
                    inc_val = 150
                    print("increase load to 150%\n")
                else:
                    inc_val = 100
                    print("increase load to 100%\n")
        elif f >= 47.5:
            f_st=True
            print("47.5<=",f,"<=50\n")
        else:
            decrease = True
            dec_val = 50
            print ("decrease load to 50%\n")
        
        if f_st == True:

            if v >= 230:
                if v <= 253:
                    print("230<=",v,"<=253\n")
                    v_st=True
                    minimize = True
                    if peak:
                        min_val = 80
                        print("the usage should be up to 80% of the load")
                    elif mid_peak:
                        min_val = 100
                        print("the usage should be up to 100% of the load")
                    else:
                        min_val = 150
                        print("the usage should be up to 150% of the load")
                else:
                    increase = True
                    if peak:
                        inc_val = 80
                        print("increase load to 80%\n")
                    elif mid_peak:
                        inc_val = 100
                        print("increase load to 100%\n")
                    else:
                        inc_val = 150
                        print("increase load to 150%\n")
            elif v >= 195.5:
                print("195.5<=",v,"<=230\n")
                v_st=True
                minimize = True
                if peak:
                    min_val = 70
                    print("the usage should be up to 70% of the load")
                elif mid_peak:
                    min_val = 80
                    print("the usage should be up to 80% of the load")
                else:
                    min_val = 150
                    print("the usage should be up to 150% of the load")
            else:
                decrease = True
                if peak:
                    dec_val = 60
                    print("decrease load up to 60%")
                elif mid_peak:
                    dec_val = 80
                    print("decrease load up to 80%")
                else:
                    dec_val = 100
                    print("decrease load up to 100%")
    return(increase,inc_val,decrease,dec_val,minimize,min_val)