# Importing modules
import io
import os
import boto3
import joblib

def get_model():
    # AWS S3 config
    aws_access_key_id = os.getenv('aws_access_key_id')
    aws_secret_access_key = os.getenv('aws_secret_access_key')

    s3 = boto3.client(
        service_name = "s3",
        region_name = "eu-west-3",
        aws_access_key_id = aws_access_key_id,
        aws_secret_access_key = aws_secret_access_key,
    )

    # Bucket informations
    bucket_name = "hotel-resa-prediction"
    prefix_model = "models/"
    filename_model = "finetuned_hotel_bookings_churn_model.pkl" 

    # Getting the model
    result_model = s3.list_objects(Bucket=bucket_name)
    for obj in result_model.get('Contents'):
        if (obj["Key"].startswith(prefix_model)) and (obj["Key"].endswith(filename_model)):
            model = s3.get_object(Bucket=bucket_name, Key=obj.get('Key'))
            model_content = model['Body'].read()
            model_pipeline = joblib.load(io.BytesIO(model_content))
            return model_pipeline