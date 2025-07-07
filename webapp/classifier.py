import pandas as pd
from ml_elements import get_model

def classifier(dataset):
    # Get prediction from the pipeline
    model_pipeline = get_model()
    result = model_pipeline.predict(dataset)

    # Reverse encoding to display the result
    if result == 0:
        result = "Pas annulé"
    elif result == 1:
        result = "Annulé"
    else:
        result = "Une erreur s'est produite"

    return result
