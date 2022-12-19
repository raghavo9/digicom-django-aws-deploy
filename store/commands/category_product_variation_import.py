import os
from os import listdir
import pandas as pd


from category.models import Category
from store.models import Product,Variation

#folder_dir = ""
#media_root_dir = settings.BASE_DIR
#
#print(media_root_dir)
#print(Path(""))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
folder_dir = BASE_DIR + "/media/photos/images"

for image in os.listdir(folder_dir):
    print(type(image),image)
    break
    
value = "xaa_55.jpeg"

df = pd.read_csv("xaa.csv")
res = df.iloc[55]["category"]
print(res)


categoryObj,_ = Category.objects.get_or_create(
    category_name = df.iloc[55]["category"],
    description = df.iloc[55]["category"]
)

print(categoryObj.category_name)