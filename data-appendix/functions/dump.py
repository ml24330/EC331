import json
import os

def dump(covariates, lower, upper, name):
    """
    Stores the output lower and upper bounds as a JSON file as "../dump/{name}"

    Parameters
    --------
    covariates : list of covariates
    lower : dictionary (or list of dictionaries) of computed lower bounds
    upper : dictionary (or list of dictionaries) of computed upper bounds
    name : string of file name to be saved as
    --------
    """

    obj = {
        "covaraites" : covariates,
        "lower" : lower,
        "upper": upper
    }

    url = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dumps", f"{name}.json")

    with open(url, "w+") as f:
        json.dump(obj, f)

    print(f"dumped one file at {url} successfully")
        

    