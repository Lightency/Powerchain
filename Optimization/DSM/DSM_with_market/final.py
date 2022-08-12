from influxdb import *
from math import *
import sys
import time
import requests
from marketBack import *
from datetime import *
from tkinter import *
import sys
from tkinter import simpledialog
import tkinter
from web3 import Web3, HTTPProvider
from web3.gas_strategies.rpc import rpc_gas_price_strategy
w3 = Web3(Web3.HTTPProvider("https://eth-rinkeby.gateway.pokt.network/v1/lb/62e17c8bb37b8e00394baecb"))

sys.setrecursionlimit(100000)


#Calculate distance from coordinates
def distance(c1,c2):
    d = sqrt((c2[0] - c1[0])**2+(c2[1] - c1[1])**2)
    return(d)

#Return energy parameter (ep) depending on the user's preference for the type of energy (choice)
def EnergyFunction(choice1,choice2):
    if choice1 == choice2 and str(choice1) != "Grid":
        return(1)
    elif str(choice1) == "Grid" or str(choice2) == "Grid":
        return(0.5)
    else:
        return(0.75)

#Calculate the price preference for each buyer and seller
def price_pref(Eb,Es,pgb,pgs): 
    if Eb != 0:
        SDR = Es/Eb
        if SDR >= 0 and SDR <= 1:
            Ps = (pgb*pgs)/((pgb-pgs)*SDR + pgs)
            Pb = Ps*SDR + pgb*(1-SDR)
        else:
            Ps = pgs
            Pb = pgs
    else:
        Ps =pgb
        Pb = pgb
    return(Ps,Pb)

#Checks balance for each user
def check_balance(Wallet):
    endpoint = 'https://eth-rinkeby.gateway.pokt.network/v1/lb/62e17c8bb37b8e00394baecb'
    connection = Web3(HTTPProvider(endpoint))
    address = Wallet
    balance = connection.fromWei(connection.eth.getBalance(address, 'latest'), 'ether')
    return(balance)

#Calculate the score for each transaction between buyer i and seller j
def score_fn(d,Db,Ds,Eb,Es,Ep,Ps,Pb,balance):
    Cd=0.2
    if Ps > Pb:
        return(0)
    elif Pb > balance:
        return(0)
    else:
        sc =(Pb - d*Cd)
        if d<=Db and d<=Ds:
            sc = sc * Ep
        elif d<=Db and d>Ds:
            sc = 0.5*(Ds/d + Ep)
        elif d>Db and d<=Ds:
            sc = 0.5*(Db/d + Ep)
        else:
            sc = 1/3*(Db/d + Ds/d + Ep)
        
        if Eb == 0 or Es == 0:
            sc = 0
        else:
            sc = sc +  min(Eb,Es)
        return(sc)

#Calculate scores for all transactions between buyers from B and Sellers from S
def calculate_score(S,B,Ds,Db,Eb_dict,Es_dict,coor,pgb,pgs,Buyer_pref,Seller_pref,wallet):
    list = []
    api_url="https://rest.coinapi.io/v1/exchangerate/ETH/USD"
    headers = {'X-CoinAPI-Key' : '9144A509-00EE-439F-A021-FBFA712D8CA8'}
    response = requests.get(api_url, headers=headers)
    price = response.json()['rate']

    for i in range(0,5): #i parcours les vendeurs
        for j in range(0,5): # j parcours les acheteurs
            if i != j:
                d = distance(coor[i],coor[j])
                Ep = EnergyFunction(Buyer_pref[j],Seller_pref[i])
                (Ps,Pb) = price_pref(Eb_dict[B[j]],Es_dict[S[i]],pgb[j],pgs[i])
                balance = price * check_balance(wallet[j])
                score = score_fn(d,Db[j],Ds[i],Eb_dict[B[j]],Es_dict[S[i]],Ep,Ps,Pb,balance)
                list = list + [S[i],B[j],score]
    return(list)

def list_to_float(list):
    list1 = []
    for i in range(0,len(list)):
        if type(list[i]) == float or type(list[i]) == int:
            list1.append(list[i])
    return(list1)

def find_max(list,n):
    list1 = list_to_float(list)
    final_list = []
    for i in range(0,n):
        max1 = max(list1)
        for j in range(0,len(list1)):
            if float(list1[j]) == max1:
                ind=3*j+2
                final_list.append(ind)
                list1[j]=0
    return(final_list)

#transcats for the optimal path, returns Eb_dict and Es_dict after transcation
def transact(Es_dict,Eb_dict,Buyer,Seller):
    Es_dict1 = {}
    Eb_dict1 = {}
    Es_dict1.update(copy.deepcopy(Es_dict))
    Eb_dict1.update(copy.deepcopy(Eb_dict))
    if Es_dict[Seller] > Eb_dict[Buyer]:
            
        Es_dict1[Seller] = Es_dict[Seller] - Eb_dict[Buyer]
        Eb_dict1[Buyer] = 0
    else:
            
        Eb_dict1[Buyer] = Eb_dict[Buyer] - Es_dict[Seller]
        Es_dict1[Seller] = 0

    return(Es_dict1,Eb_dict1)

#Returns the hypothetical paths for each transaction from the top N transactions
def matching(S,B,Ds,Db,coor,Eb_dict,Es_dict,N,pgb,pgs,Buyer_pref,Seller_pref,wallet): 
    
    list = calculate_score(S,B,Ds,Db,Eb_dict,Es_dict,coor,pgb,pgs,Buyer_pref,Seller_pref,wallet)
    Result = [{"N = ": N}]
    i = 1

    #find top N transactions
    maxN = find_max(list,N) #indexes (on list) of top N transactions

    while i < N+1:
        for j in range(0,N):

            #change the energy parameters
            Buyer = int(maxN[j]) - 1
            Seller = int(maxN[j]) - 2

            (Es_dict_new,Eb_dict_new) = transact(Es_dict,Eb_dict,list[Buyer],list[Seller])

            #Recaculate scores
            list1 = calculate_score(S,B,Ds,Db,Eb_dict_new,Es_dict_new,coor,pgb,pgs)
            #find next maximum
            k1_list = find_max(list1,2)
            k1 = k1_list[0]
            
            #add to result file
            Result.append({"iteration on top N transactions":i,
            "iteration for the couple of (S,B)": (list[Seller],list[Buyer]), 
            "next maximum transaction, buyer": list1[k1-1], 
            "next maximum transaction, seller": list1[k1-2], 
            "next highest score": list1[k1],
            "scores" : (list[maxN[j]],list1[k1]),
            "sum of scores": float(list[maxN[j]]) + float(list1[k1])})
            i = i+1

    return(Result)
#Returns the optimal path, i.e. the path with the highest cummulative score 
def path(Result,N):
    maxSc = 0
    somme = 0
    for i in range (1,N+1):
        somme = Result[i]["sum of scores"]
        if somme > maxSc:
            maxSc = somme
            TrNum = i
    return (TrNum)

#Calculates the sum of Eb and Es from dictionaries
def collective(Eb_dict,B):
    Eb_coll = 0
    for i in range(0,5):
        Eb_coll = Eb_coll + float(Eb_dict[B[i]])
    
    return(Eb_coll)

#Final function
def matching_Energy(S,B,Ds,Db,coor,Eb_dict,Es_dict,N,pgb,pgs,Buyer_pref,Seller_pref,wallet):
    i = 1
    Eb_coll =  collective(Eb_dict,B)
    Es_coll =  collective(Es_dict,S)
    Transactions = []
    while Eb_coll > 0 and Es_coll > 0:
        print("iteration number ",i)
        Result = matching(S,B,Ds,Db,coor,Eb_dict,Es_dict,N,pgb,pgs,Buyer_pref,Seller_pref,wallet)
        print(Result)
        TrNum = path(Result,N)
        print(Result[TrNum])
        #Transact for the highest path
            
        Seller1 = Result[TrNum]["iteration for the couple of (S,B)"][0]
        Buyer1  = Result[TrNum]["iteration for the couple of (S,B)"][1]
        Seller2 = Result[TrNum]["next maximum transaction, seller"]
        Buyer2 = Result[TrNum]["next maximum transaction, buyer"]


        #transact for transaction level-1
        (Es_dict1,Eb_dict1) = transact(Es_dict,Eb_dict,Buyer1,Seller1)
        print("Es 1 : ",Es_dict1,"Eb 1 : ",Eb_dict1)
        
        Eb_coll =  collective(Eb_dict1,B)
        Es_coll =  collective(Es_dict1,S)
        Transactions.append([Seller1,Buyer1])

        if Eb_coll == 0 or Es_coll == 0:
            print("Algorithm has reached its end")
        
        else:
            Transactions.append([Seller2,Buyer2])
            
            #transact for transaction level-2
            (Es_dict2,Eb_dict2) = transact(Es_dict1,Eb_dict1,Buyer2,Seller2)
            print("Es 2 : ",Es_dict2,"Eb 2 :",Eb_dict2)

            #change values:
            Es_dict.update(copy.deepcopy(Es_dict2)) 
            Eb_dict.update(copy.deepcopy(Eb_dict2))
            #condition to stop
            Eb_coll =  collective(Eb_dict2,B)
            Es_coll =  collective(Es_dict2,S)
            i = i+1
        
            print("Eb : ",Eb_coll,"Es : ",Es_coll)
    return(Transactions)

#Extract data from openems edges:
#   Extract Eb and Es
def Extract_es_eb(Eb_dict,Es_dict,time_min,time_max,edge_id):
    #Extract data
    client = InfluxDBClient(host='54.226.203.148', port=8086, database='Backend')
    result=client.query('SELECT mean("_sum/GridSellActiveEnergy"),mean("_sum/GridBuyActiveEnergy") FROM "autogen"."data" WHERE "edge"=',str(edge_id),' GROUP BY time(1h) fill(null)')
    jon=result.raw #dict
    ser=jon['series'] #dict
    data=[] #list of all inputs
    ind_min=0
    ind_max=0
    length=len(ser[0]['values'])-1
    for i in range(0,length):
        data=data+ser[0]['values'][i]
    
    for k in range(0,len(data)):
        if str(data[k]) == str(time_min):
            ind_min=k
        elif str(data[k]) == str(time_max):
            ind_max=k+3
    data_limit=data[ind_min:ind_max]

    #Extract eb,es
    length = len(data_limit)
    i = 1
    j = 2
    es_sum= 0
    eb_sum = 0
    while j<length:
        es_sum = es_sum + data_limit[i]
        eb_sum = eb_sum + data_limit[j]
        i = i+3
        j = j+3
    
    divide = length/3
    es = es_sum/divide
    eb = eb_sum/divide
    Eb_dict[str(edge_id)] = eb
    Es_dict[str(edge_id)] = es
    return(Es_dict,Eb_dict)
#   Extract consumption, to calculate pgs
def Extract_con(time_min,time_max,edge_id):
    #Extract data
    client = InfluxDBClient(host='54.226.203.148', port=8086, database='Backend')
    result=client.query('SELECT mean("_sum/ConsumptionActiveEnergy") FROM "autogen"."data" WHERE "edge"=',str(edge_id),' GROUP BY time(7d) fill(null)')
    jon=result.raw #dict
    ser=jon['series'] #dict
    data=[] #list of all inputs
    ind_min=0
    ind_max=0
    length=len(ser[0]['values'])-1
    for i in range(0,length):
        data=data+ser[0]['values'][i]
    
    for j in range(0,len(data)):
        if str(data[j]) == str(time_min):
            ind_min=j
            print("yes")
        elif str(data[j]) == str(time_max):
            ind_max=j+3
    data_limit=data[ind_min:ind_max]

    #Calculate consumption
    length = len(data_limit)
    i = 1
    k = 2
    con_sum= 0
    while k<length:
        con_sum = con_sum + data_limit[i]
        i = i+2
    
    divide = length/2
    con = con_sum/divide
    return(con)
# Calculate pgs and pgb, according to the tunisian company (STEG) tarrifs
def tarrif_pgs(con):
    if 1 <= con <= 50:
        return(62)
    elif 51 <= con <= 100:
        return(96)
    elif 101 <= con <= 200:
        return(182)
    elif 201 <= con <= 300:
        return(224)
    elif 301 <= con <= 500:
        return(347)
    else:
        return(420)

def tarrif_pgb():

    month = int(date.today().strftime("%m"))
    hour = int(datetime.now().strftime("%H"))

    if month in range(6,9):
        if 6 <= hour < 9 or 14 <= hour < 19:
            return(86.87)
        elif 9 <= hour < 14:
            return(103.53)
        elif 19 <= hour < 22:
            return(91.63)
        else:
            return(82.11)
    else:
        if 7 <= hour < 18:
            return(86.87)
        elif 18 <= hour < 21:
            return(91.63)
        else:
            return(82.11)

def index(Buyer,Seller,S):
    ind1 = 0
    ind2 = 0
    for i in range(0,5):
        if Buyer == S[i]:
            ind1 = i
        if Seller == S[i]:
            ind2 = i
    return(ind1,ind2)
#modify the time inside the function
def auction(time_min,time_max):
    Es_dict = {'C':0,'D1':0,'D2':0,'D3':0,'D4':0}
    Eb_dict = {'C':0,'D1':0,'D2':0,'D3':0,'D4':0}
    edge_id = ['C','D1','D2','D3','D4'] 
    for i in edge_id:
        (Es_dict,Eb_dict) = Extract_es_eb(Eb_dict,Es_dict,time_min,time_max,i)
    
    pgs = []
    pgb = []
    for j in edge_id:
        con = Extract_con('2022-08-01T00:00:00Z','2022-09-01T00:00:00Z',j)
        pgs.append(tarrif_pgs(con))
        pgb.append(tarrif_pgb())
    
    return(Es_dict,Eb_dict,pgs,pgb)

#for inpputs
def init():
    ROOT = tkinter.Tk()
    ROOT.withdraw()
    N = simpledialog.askstring(title="N",
                                  prompt="Type the number of potential paths you want")

    Db = simpledialog.askstring(title="Buyer Distance Preference",
                                  prompt="Type the list of distance preference for the Buyers")

    Ds = simpledialog.askstring(title="Seller Distance Preference",
                                  prompt="Type the list of distance preference for the Sellers")

    Buyer_pref = simpledialog.askstring(title="Energy type Preference",
                                  prompt="Type the list of energy type preferences for the Buyers")

    Seller_pref = simpledialog.askstring(title="Energy type Preference",
                                  prompt="Type the list of energy type preferences for the Sellers")
    
    change = simpledialog.askstring(title="Change Wallet address",
                                  prompt="Do you like to change the wallet address of a prosumer, type 1 for yes and 0 for no")
    return(N,Db,Ds,Buyer_pref,Seller_pref,change)

def change_wallet(change,wallet):
    if change:
        id = int(input("Type the id of prosumer to change its wallet address, starting from C as 0"))
        wallet[id] = str(input("Type the new wallet address"))
    return(wallet)

#phase 1 extracts the data (Eb and Es) and calculates pgs and pgb
def phase1():
    now = datetime.now()
    start = now - timedelta(days = 1) + timedelta(minutes= 10)
    end = start + timedelta(minutes=30)
    (Es_dict,Eb_dict,pgs,pgb) = auction(start,end)
    return(Es_dict,Eb_dict,pgs,pgb)

#phase 2 returns the list of transactions to be executed
def phase2():
    (Es_dict,Eb_dict,pgs,pgb) = phase1()
    Transactions = matching_Energy(S,B,Ds,Db,coor,Eb_dict,Es_dict,N,pgb,pgs,Buyer_pref,Seller_pref,wallet)
    return(Transactions)


#transfer money from the buyer's wallet to the sender, and sign and record transaction
def transfer_money(Seller,Buyer,amount,private_keys,wallets,S,En):
    (ind_b,ind_s)=index(Buyer,Seller,S)
    account_from = {
        "private_key": private_keys[ind_b],
        "address": wallets[ind_b],
    }
    address_to = wallets[ind_s]
    w3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
    tx_create = w3.eth.account.sign_transaction(
        {
            "nonce": w3.eth.get_transaction_count(account_from["address"]),
            "gasPrice": w3.eth.generate_gas_price(),
            "gas": 21000,
            "to": address_to,
            "value": w3.toWei(amount, "ether"),
            "energy":En,
        },
        account_from["private_key"],
    )
    tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transaction successful with hash: { tx_receipt.transactionHash.hex() }")

# run transactions and payment
def phase3():
    for element in Transactions:
        for i in element:
            (ind1,ind2) = index(i[1],i[0],S)
            (Ps,Pb) = price_pref(Eb_dict[i[1]],Es_dict[i[0]],pgb[ind1],pgs[ind2])
            price = max(Ps,Pb)
            price_to_pay = min(Eb_dict[i[1]],Es_dict[i[0]]) * price
            En = min(Eb_dict(i[1]),Es_dict(i[0]))
            transfer_money(i[0],i[1],price_to_pay,private_keys,wallets,S,En)



######################################### Algo ##################################################################################

S = ['C','D1','D2','D3','D4'] 
B = ['C','D1','D2','D3','D4']
coor = [[36.8787562, 10.3181637],[36.8790899, 10.3189784],[36.8789689, 10.3187105],[36.8788638, 10.3184386],[36.8788211, 10.3183575]]

wallets = ['0xfe12C299191C98Ea8b670b7ff0f923c9ea4f3006','0x388983b8aBEA15A2fd2b00D7E52aa3b78FB7D57c','0x2352A0738C375072EfBeA3a27Ea8d378f5a45De4','0x25DeE17B893Cc9b44b40582644F3157d9296ec5f','0xbA0F7425DEC220e2EFfF90B32B5E34967eA28739']
private_keys=['ac4fc7c5aefee20841cecc606c7c4302be96447c2aa4653161d093a6c83833b6','455a43365992956a0b9b7e0ed971ebe32d31a936c703eb422675f29bc753aee3','b29da889e48232315704df86814a36045a4b13a2625f494b1f1573d02715091e','30c60973cdf47c4a76368721ed6a5023041cb3d29b92342e1469fb672137f614','29e7de64d4dd21a72c7041bf597aa1af96817184aff5027bb74bdd493219f81e']
#market structure:
#   phase 1 runs for 15 min (15*60 = 900 seconds)
#   phase 2 runs for 30 min
#   phase 3 runs for 15 min
start = 1
while start:
    start = int(input("initializing program, type 0 to stop\n"))
    if start == 0:
        break
    else:
        (N,Db,Ds,Buyer_pref,Seller_pref,change) = init()
        wallet = change_wallet(change,wallets)
        (Es_dict,Eb_dict,pgs,pgb) = phase1()
        time.sleep(900)
        Transactions = phase2()
        time.sleep(1800)
        phase3()
        time.sleep(900)







