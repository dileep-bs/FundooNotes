list=[1,2,3,4,5,6,5,4,7,8,9,10,6,4,34,54,7,8,9,0,200,100,100,100]
for i in range(len(list)):
    if i!=0 and i%4==0:
        print("")
    print(list[i],end=' ')