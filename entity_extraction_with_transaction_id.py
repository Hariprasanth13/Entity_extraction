import pandas as pd
from google.cloud import storage
import io
import random

# Initialize Google Cloud Storage client
storage_client = storage.Client(project = 'rntbci-digital-innovation-lab')

# Define bucket and file names
bucket_name = "testing-bucket-hari-prasath"
file_name = "transaction_log_GBS.xlsx"

def read_excel_from_gcs(bucket_name, file_name):
    """Reads an Excel file from GCS and loads it into a pandas DataFrame."""
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Download the file content as bytes
    file_data = blob.download_as_bytes()

    # Load the Excel file into a pandas DataFrame
    df = pd.read_excel(io.BytesIO(file_data), engine='openpyxl')
    return df

def write_excel_to_gcs(df, bucket_name, file_name):
    """Writes a pandas DataFrame to an Excel file in GCS."""
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Save the pandas DataFrame to a BytesIO stream as an Excel file
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    # Upload the Excel file to GCS
    blob.upload_from_string(excel_buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def generate_transaction_id():
    """Generates a random 16-bit transaction ID."""
    return random.randint(0, 2**16 - 1)


def update_excel_file():

    """Main function to update the Excel file."""
    # Read the existing Excel file from GCS
    df = read_excel_from_gcs(bucket_name, file_name)

    # Generate a random 16-bit transaction ID
    transaction_id = generate_transaction_id()

    # Example: Modify the DataFrame (add a new row)
    new_data = {"transaction_id": "fileName+str(transaction_id)"}
    print(new_data)
    df = df.append(new_data, ignore_index=True)

    # Write the updated DataFrame back to the Excel file in GCS
    write_excel_to_gcs(df, bucket_name, file_name)
    
    print("Excel file updated successfully.")

filePath = "C:\\Users\\z031415\\OneDrive - Alliance\\My projects\\Projects\\GBS_project\\GBS_EE\\common\\18310343.pdf"
fileName = filePath.split("\\")[-1].split('.')[0]
print(fileName)

# Call the function to update the Excel file
update_excel_file()
