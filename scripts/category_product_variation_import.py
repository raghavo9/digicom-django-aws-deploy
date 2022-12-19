import os
from os import listdir
import pandas as pd
import numpy as np

from category.models import Category
from store.models import Product,Variation
from django.conf import settings


def run():

    excpetion_array = []

    # now since we are in context of django so we can use settings.py files variables
    media_path = str(settings.MEDIA_ROOT)
    folder_dir = media_path + "/photos/images"

    #for image in os.listdir(folder_dir):
    #    print(type(image),image)
    #    break
#
    #dir_items = os.listdir(folder_dir)
    #print(dir_items[2])


    #value = "xaa_55.jpeg"
    #value = "xaa_1.jpeg"
    #ind = 1
    #df = pd.read_csv("xaa.csv")
    ##res = df.iloc[55]["category"]
    ##print(res)

    #categoryObj,is_new = Category.objects.get_or_create(
    #    category_name = df.iloc[ind]["category"]
    #)
#
    #if is_new:
    #    categoryObj.description = df.iloc[ind]["category"]
    #    categoryObj.save()
#
    #
    #print(categoryObj.category_name,is_new)

    root = str(settings.BASE_DIR)
    csv_filepath = root+"/xaa.csv"
    df = pd.read_csv(csv_filepath)

    for image in os.listdir(folder_dir):
        try:
            #print(image)
            #print(str(image))
            #print(type(image))
            #image_filepath = root + "/media/photos/images/" + str(image)
            image_filepath = "/photos/images/" + str(image)
            #print(image_filepath)
            #break
            index = (image.split(".")[0]).split("_")[1]
            index = int(index)

            #creating CATEGORY
            sheet_cat_name = df.iloc[index]["category"]
            categoryObj,is_new = Category.objects.get_or_create(category_name = sheet_cat_name)
            if is_new:
                categoryObj.description = sheet_cat_name
                categoryObj.save()

            #creating PRODUCT
            productObj = Product(
                product_name = df.iloc[index]["title"],
                description = (str(df.iloc[index]["brand"]) + str(df.iloc[index]["category"]) + str(df.iloc[index]["title"])),
                brand = df.iloc[index]["brand"],
                price = df.iloc[index]["selling_price"],
                mrp_price = df.iloc[index]["mrp"],
                #images = (folder_dir+ "/" + str(image)),
                #images = (str(image)),
                url_height = 150,
                url_width = 75,
                images = (image_filepath),
                stock  = 999,
                is_available = True,
                category = categoryObj
            )
            productObj.save()

            #creating VARIATION
            if type(df.iloc[index]["size"]) == float:

                variationObj = Variation(
                        product = productObj,
                        variation_category = "size",
                        variation_value = "universal",
                        is_active = True,
                    )
                variationObj.save()

            else:
                for eachsize in str(df.iloc[index]["size"]).split(","):
                    variationObj = Variation(
                        product = productObj,
                        variation_category = "size",
                        variation_value = eachsize,
                        is_active = True,
                    )
                    variationObj.save()

            if type(df.iloc[index]["colour"]) == float:

                variationObj = Variation(
                        product = productObj,
                        variation_category = "color",
                        variation_value = "basic",
                        is_active = True,
                    )
                variationObj.save()

            else:
                for eachcolour in (df.iloc[index]["colour"]).split(","):
                    variationObj = Variation(
                        product = productObj,
                        variation_category = "color",
                        variation_value = eachcolour,
                        is_active = True,
                    )
                    variationObj.save()

        except:
            excpetion_array.append(image)
            continue


    if not excpetion_array:
        print("successfully imported all data")
    else:
        print("error occured in",excpetion_array)







    ##root = str(settings.BASE_DIR)
    ##csv_filepath = root+"/xaa.csv"
    ##df = pd.read_csv(csv_filepath)
##
    ##for image in os.listdir(folder_dir):
    ##    image = "xaa_0.jpeg"
    ##    #print(image)
    ##    #print(str(image))
    ##    #print(type(image))
    ##    #image_filepath = root + "/media/photos/images/" + str(image)
    ##    image_filepath = "/photos/images/" + str(image)
    ##    #print(image_filepath)
    ##    #break
    ##    index = (image.split(".")[0]).split("_")[1]
    ##    index = int(index)
    ##    #creating CATEGORY
    ##    sheet_cat_name = df.iloc[index]["category"]
##
    ##    categoryObj,is_new = Category.objects.get_or_create(category_name = sheet_cat_name)
    ##    if is_new:
    ##        categoryObj.description = sheet_cat_name
    ##        categoryObj.save()
    ##    #creating PRODUCT
    ##    productObj = Product(
    ##        product_name = df.iloc[index]["title"],
    ##        description = (str(df.iloc[index]["brand"]) + str(df.iloc[index]["category"]) + str(df.iloc[index]["title"])),
    ##        brand = df.iloc[index]["brand"],
    ##        price = df.iloc[index]["selling_price"],
    ##        mrp_price = df.iloc[index]["mrp"],
    ##        #images = (folder_dir+ "/" + str(image)),
    ##        #images = (str(image)),
    ##        url_height = 150,
    ##        url_width = 75,
    ##        images = (image_filepath),
    ##        stock  = 999,
    ##        is_available = True,
    ##        category = categoryObj
    ##    )
    ##    productObj.save()
    ##    #creating VARIATION
    ##    #if np.isnan(df.iloc[index]["size"]):
    ##    if type(df.iloc[index]["size"]) == float:
    ##        variationObj = Variation(
    ##                product = productObj,
    ##                variation_category = "size",
    ##                variation_value = "universal",
    ##                is_active = True,
    ##            )
    ##        variationObj.save()
    ##    else:
    ##        for eachsize in str(df.iloc[index]["size"]).split(","):
    ##            variationObj = Variation(
    ##                product = productObj,
    ##                variation_category = "size",
    ##                variation_value = eachsize,
    ##                is_active = True,
    ##            )
    ##            variationObj.save()
    ##    #if np.isnan(df.iloc[index]["colour"]):
    ##    if type(df.iloc[index]["colour"]) == float:
    ##        variationObj = Variation(
    ##                product = productObj,
    ##                variation_category = "color",
    ##                variation_value = "basic",
    ##                is_active = True,
    ##            )
    ##        variationObj.save()
    ##    else:
    ##        for eachcolour in (df.iloc[index]["colour"]).split(","):
    ##            variationObj = Variation(
    ##                product = productObj,
    ##                variation_category = "color",
    ##                variation_value = eachcolour,
    ##                is_active = True,
    ##            )
    ##            variationObj.save()
    ##    break
##