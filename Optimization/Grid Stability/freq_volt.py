#verifies that the frequency is stable: 47.5 <= f <= 52.2 Hz
def f_stable(frequency):
    for f in frequency:
        f_st=False
        if f>=50:
            if f <= 52.5:
                f_st=True
                print("50<=",f,"<=52.2")
            else:
                print("increase load in the of peak period by 50%")
        elif f >= 47.5:
            f_st=True
            print("47.5<=",f,"<=50")
        else:
            print ("decrease load by 50% at any cost")
    print(f_st)
    return f_st

#verifies that the voltage is stable: 195.5 <= V <= 253
def v_stable(voltage):
    for v in voltage:
        v_st=False
        print(v)
        if v >= 230:
            if v <= 253:
                print("230<=",v,"<=253")
                v_st=True
            else:
                print("increase load")
        elif v >= 195.5:
            print("195.5<=",v,"<=230")
            v_st=True
        else:
            print ("decrease load")
    return v_st