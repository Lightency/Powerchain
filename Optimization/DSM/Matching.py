from math import *
from random import *
from random import randint
import sys
sys.setrecursionlimit(100000)

################################################################# Context ####################################################################
#The parameters to score a transaction between a buyer and a seller are:
    #Eb, Es: energy to be bought and sold respectively
    #Pb: price preferance for the buyer
    #Pgs: price of the grid for sale
    #Pgb: price of purchase from the grid
    # { Ps < Pb
    #   Pgs < Ps
    #   Pb < Pgb }
    # -> Pgs < Ps < Pb < Pgb
    #d: distance between two agents (calculated from coordiantes, in Km) 
    #Cd: distance charge
    #Ds and Db distance preferance for the buyer and seller
    #EP: energy function, the types of energy are "solar", "wind", and "fossil"= Grid, EP is between 0.5 and 1

#DER_state -> status of each DER : deficit or excess and other use cases
#functionalities and priorities of the central

##################################################################   functions   #############################################################

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

#Calculate the score for each transaction between buyer i and seller j
def score_fn(d,Db,Ds,Eb,Es,Pb,Ep):
    Cd=0.2
    sc =(Pb - d*Cd)
    if d<=Db and d<=Ds:
        sc = sc * Ep
    elif d<=Db and d>Ds:
        sc = 0.5*(Ds/d + Ep)
    elif d>Db and d<=Ds:
        sc = 0.5*(Db/d + Ep)
    else:
        sc = 1/3*(Db/d + Ds/d + Ep)
    sc = sc +  min(Eb,Es)
    return(sc)

#Calculate scores for all transactions between buyers from B and Sellers from S
def calculate_score(S,B,Ds,Db,Eb_dict,Es_dict,Pb,coor):
    list = []
    for i in range(0,5): #i parcours les vendeurs
        for j in range(0,5): # j parcours les acheteurs
            if i != j:
                d = distance(coor[i],coor[j])
                choices = ["wind","solar","Grid"]
                rand1 = randint(0,2)
                rand2 = randint(0,2)
                choice1 = choices[rand1]
                choice2 = choices[rand2]
                Ep = EnergyFunction(choice1,choice2)
                score = score_fn(d,Db[j],Ds[i],Eb_dict[B[j]],Es_dict[S[i]],Pb[j],Ep)
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

#Returns the hypothetical paths for each transaction from the top N transactions
def matching(S,B,Ds,Db,Pb,coor,Eb_dict,Es_dict,N):
    list = calculate_score(S,B,Ds,Db,Eb_dict,Es_dict,Pb,coor)
    Result = [{"N = ": N}]
    i = 1

    #find top N transactions
    maxN = find_max(list,N) #indexes (on list) of top N transactions
    while i < N+1:
        for j in range(0,N):
            Eb_dict1 = Eb_dict
            Es_dict1= Es_dict
            #change the energy parameters
            Buyer = int(maxN[j]) - 1
            Seller = int(maxN[j]) - 2
            if  Eb_dict[list[Buyer]] > Es_dict[list[Seller]]:
                Eb_dict1[list[Buyer]] = Eb_dict[list[Buyer]] - Es_dict[list[Seller]]
                Es_dict1[list[Seller]] = 0
            else:
                Es_dict1[list[Seller]] = Es_dict[list[Seller]] - Eb_dict[list[Buyer]]
                Eb_dict1[list[Buyer]] = 0
            #Recaculate scores
            list1 = calculate_score(S,B,Ds,Db,Eb_dict1,Es_dict1,Pb,coor)
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
    return (maxSc, TrNum)

#transcats for the optimal path, returns Eb_dict and Es_dict after transcation
def transact(Es_dict,Eb_dict,Buyer,Seller):
    Es_dict1 = Es_dict
    Eb_dict1 = Eb_dict
    if Es_dict[Seller] > Eb_dict[Buyer]:
            
        Es_dict1[Seller] = Es_dict[Seller] - Eb_dict[Buyer]
        Eb_dict1[Buyer] = 0
    else:
            
        Eb_dict1[Buyer] = Eb_dict[Buyer] - Es_dict[Seller]
        Es_dict1[Seller] = 0

    return(Es_dict1,Eb_dict1)

#Calculates the sum of Eb and Es from dictionaries
def collective(Eb_dict,B):
    Eb_coll = 0
    for i in range(0,5):
        Eb_coll = Eb_coll + float(Eb_dict[B[i]])
    
    return(Eb_coll)

#Final function
def matching_Energy(S,B,Ds,Db,Pb,coor,Eb_dict,Es_dict,N):
    i = 1
    Eb_coll =  collective(Eb_dict,B)
    Es_coll =  collective(Es_dict,S)
    while Eb_coll > 0 and Es_coll > 0:
        print("iteration number ",i)
        Result = matching(S,B,Ds,Db,Pb,coor,Eb_dict,Es_dict,N)
        print(Result)
        [maxSc,TrNum] = path(Result,N)
        print(Result[TrNum])
        #Transact for the highest path
            
        Seller1 = Result[TrNum]["iteration for the couple of (S,B)"][0]
        Buyer1  = Result[TrNum]["iteration for the couple of (S,B)"][1]
        Seller2 = Result[TrNum]["next maximum transaction, seller"]
        Buyer2 = Result[TrNum]["next maximum transaction, buyer"]

        #transact for transaction level-1
        (Es_dict1,Eb_dict1) = transact(Es_dict,Eb_dict,Buyer1,Seller1)
        print("Es 1 : ",Es_dict1,"Eb 1 : ",Eb_dict1)
        #transact for transaction level-2
        (Es_dict2,Eb_dict2) = transact(Es_dict1,Eb_dict1,Buyer2,Seller2)
        print("Es 2 : ",Es_dict2,"Eb 2 :",Eb_dict2)

        #change values:
        Es_dict = Es_dict2
        Eb_dict = Eb_dict2
        #condition to stop
        Eb_coll =  collective(Eb_dict2,B)
        Es_coll =  collective(Es_dict2,S)
        i = i+1
        print("Eb : ",Eb_coll,"Es : ",Es_coll)

####################################################       inputs and algo      ###############################################################

#inputs from the user
Pb = [1,0.5,0.8,0.35,0.2]
Ps = [0.2,1,0.3,0.8,0.5]
Db=[0.2,0.1,0.3,0.1,0.2]
Ds=[0.2,0.2,0.1,0.3,0.1]

#constants
S = ['C','D1','D2','D3','D4'] 
B = ['C','D1','D2','D3','D4']
coor = [[36.8787562, 10.3181637],[36.8790899, 10.3189784],[36.8789689, 10.3187105],[36.8788638, 10.3184386],[36.8788211, 10.3183575]]

#data extracted from DERs In Real Time
Eb=[5,1,2,3,4]
Es=[10,2,5,3,4]
Eb_dict = {'C':5.0,'D1':1.0,'D2':2,'D3':3,'D4':12}
Es_dict = {'C':10,'D1':2.0,'D2':5,'D3':0,'D4':10}

#Algo

N = int(input("Type N\n"))
matching_Energy(S,B,Ds,Db,Pb,coor,Eb_dict,Es_dict,N)