import pandas as pd
import urllib.request as url_lib
from django.conf import settings

def run():

    #now we are inside django's context so we can use settings varaibles

    root = str(settings.BASE_DIR)
    filepath = root + "/xaa.csv"
    #df = pd.read_csv("xaa.csv")
    df = pd.read_csv(filepath , nrows=10 , skiprows=[1])
    df = pd.read_csv(filepath)
    #print(df.iloc[1]["title"])
    #exit()
    #print(df)
    
    for index,row in df.iterrows() :
        #print(index , row["brand"], " ---> " ,row["title"], "----> " , row["category"])
        if ("https://assets.ajio.com" in row["images"]) or  ("https://udaan.azureedge.net" in row["images"]) :
            images = row["images"]
            images = images.replace("~^",",")
            images = images.strip(",")
            firstImage = images.split(",")[0]
            print(firstImage)
    
            # dowload the image locally
    
            url = firstImage
            filename = "xaa_"+str(index)+".jpeg"
            fullpath = "images/"+filename
            url_lib.urlretrieve(url, fullpath)
    
    
        else:
            continue

