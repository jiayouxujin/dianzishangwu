from django.forms import model_to_dict


def calcount(invertory, param):
    invertorydict = model_to_dict(invertory)
    tempvalue = param - invertorydict['materialInventory'] - invertorydict['processInventory']
    return tempvalue
