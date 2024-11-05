from google.oauth2 import service_account
import pandas as pd
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
import base64
import re
import streamlit as st
import json
from google.auth import default
from google.cloud import aiplatform
from google.auth import default, credentials
from google.oauth2 import service_account
from google.cloud import storage
import io
import random
from datetime import datetime
import time
import os


project_id = "rntbci-digital-innovation-lab"
credentials_path = 'sa-gbs-data-extraction.json'
credentials = service_account.Credentials.from_service_account_file(credentials_path)
# credentials, project_id = default(scopes=["https://www.googleapis.com/auth/cloud-platform"],  credentials_path=credentials_path)
# aiplatform.init(project=project_id, credentials=credentials)
# service_account_credentials = service_account.Credentials.from_service_account_info(service_account_info)

# # Initialize Google Cloud Storage client
# storage_client = storage.Client(project = 'rntbci-digital-innovation-lab')
# # Define bucket and file names

bucket_name = "testing-bucket-hari-prasath"
file_name = "transaction_log_GBS.xlsx"

def authenticate_with_service_account(credentials_path):
    # Set the environment variable for the service account key
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

    # Instantiates a client
    storage_client = storage.Client(project = 'rntbci-digital-innovation-lab')

    return storage_client

storage_client = authenticate_with_service_account(credentials_path)


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


def update_excel_file(pdf_name_wo_extention):

    """Main function to update the Excel file."""
    # Read the existing Excel file from GCS
    df = read_excel_from_gcs(bucket_name, file_name)

    # Generate a random 16-bit transaction ID
    transaction_id = generate_transaction_id()

    # Example: Modify the DataFrame (add a new row)
    current_time= datetime.now()
    new_data = {"Date Of Execution" : current_time ,"transaction_id": pdf_name_wo_extention+"_"+str(transaction_id)}
    print(new_data)
    #df = df.append(new_data, ignore_index=True)
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    # Write the updated DataFrame back to the Excel file in GCS
    write_excel_to_gcs(df, bucket_name, file_name)
    
    print("Excel file updated successfully.")



def generate(text):
  vertexai.init(project="rntbci-digital-innovation-lab", location="us-central1", credentials=credentials)
#   vertexai.auth.set_credentials(credentials)
  aiplatform.init(project=project_id, credentials=credentials)
  model = GenerativeModel("gemini-1.5-pro-001")
  responses = model.generate_content(
      [document1, text],
      generation_config=generation_config,
      safety_settings=safety_settings,
      stream=True,
  )
#   for response in responses:
#     print(response.text, end="")
  return responses

def iterateResponse(response):
    output=""
    
    try:
        for res in response:
            #print(res)
            output= output + res.text
        output1=str(output)
        return output1
    
    except Exception as e:
        print(e)
        return None

# def generate_call(text):
#         try:
#             response = generate(text)  # Assuming 'generate' is defined elsewhere
#             #print("My response:\n",response)
#             return response
#         except Exception as e:
#             print(f"My Exception: ",str(e))
#     return None


if __name__ == "__main__":
    st.title("GBS Invoice Entity Extraction")
    pdf_file = st.file_uploader('Upload your file', type ='pdf')
    if st.button("Submit"):
        pdf_name = pdf_file.name
        pdf_name_wo_extention = pdf_name.split('.')[0]
        pdf_data = pdf_file.read()
        bytecode = base64.b64encode(pdf_data)

        document1 = Part.from_data(
            mime_type="application/pdf",  
            data=base64.b64decode(bytecode)
        )


        text1 = """you are an expert in invoice entity extraction. Extract all the required fields mentioned below from the pdf. The field names may not be the same as given, you have to intelligently identify those fields. 
.Return the response in JSON beautify format.

Required Fields:
Billing Name (FACTURE ENVOYÉE À,Platnik/Payer) - extract only the billing name
Buyer NIF (NUM INTRA,N° TVA intracommunautaire CLIENT,Renault Espana S.A VAT No,VAT-nr)
Billing Company name - extract the company name from buyer details
Delivery address (ship to party,Livré à,Odbiorca/Recipient)- Do not include 'API', 'CSP', 'ACH' . Also do not include new line character
Supplier Name - Extract full name
Supplier NIF (TVA,N° IDENTIFICATION) - extract complete data
Supplier code (Supplier Number,Customer Reference,FOURNISSEUR,Fournisseur) - don't extract the data after '-'
Transaction Type - should be identified from the type of doc provided
Invoice number
Invoice date
Net Amount (Total H.T,Amount Positions)
Tax percentage
Tax Amount
Gross Amount
Currency
IBAN Code
EXONERATION details
Invoice description - extract only the description entity and don't include other entities - Do not include new line character while extracting data instead leave a space
Article/part number (selling code,Ref,cust Mat number,Articles et Prestations,Customer Material,MABEC) - Do not include new line character while extracting data instead leave a space
QTY details of part (volume,Quantité)
Unit measurement details
Unit price of Part
total price of part (Montant HT)
BL/Delivery note numbers (Delivery No,N° BL,BORDEREAU LIVRAISON,Doc. réception,BL,Nºalbarán Issue) - extract the 10 digit number which starts with '5'
Purchase order number (Votre commande,COMMANDE,REFERENCE COMMANDE CLIENT,Commande,Vos références,N° de Bon de commande,Votre N° de commande,Votre reference,Votre Cde - N* Lig,Reference client) - don't extract the data after '-'

If the Buyer NIF is not found then extract the data from code TVA or Votre T.V.A
If the Delivery note number is not found please extract the data from Nr.DDT or B.LIVRAIS
If the Net Amount is not found then extract the data from Total or Hors Taxe.
If the supplier code is not found extract the data from Compte Fournisseur
If Net amount is not found extract the data from invoice amount or Final amount
If the purchase order number is not found extract the data from commande client or Order N°
If Exoneration detail is not found extract the data from TVA exigible d’après les débits
If BL/Delivery note numbers is not found extract the data from N° d'expedition or BSR
If Delivery address is not found extract the data from 'Consignee'
If the Tax amount is 'null' then return as '0'

Purchase order number sometimes starts with 'BDC '
BL/Delivery note numbers sometimes starts with 'BSR ' or 'BSR'
For supplier code extract the data from entity that starts with 'CF' or 'CF ' even though if it is explicitly mentioned
Billing company name should be same as the billing name
Replace Votre Commande entity name with Purchase order number
Sometimes Article/part number can be found after 'KN' but do not include 'KN'
Article/part number sometimes ends with 'R'.If Article/part number ends with 'R' extract the entity along with 'R'
Article/part number - Do not take the value after space while extracting the data

Sample response:
{
 "Billing Name": "",
 "Buyer NIF": "FR 66780129987",
 "Billing Company name": "sample company",
 "Delivery address": "13 AV PAUL LANGEVIN, France",
 "Supplier Name": "Cebi Italy S.p.A.",
 "Supplier NIF": "03019880040",
 "Supplier code": "210483",
 "Transaction Type": "INVOICE",
 "Invoice number": "134884",
 "Invoice date": "31/08/2023",
 "Net Amount": "27.210,92",
 "Tax percentage": "0",
 "Tax Amount": "0",
 "Gross Amount": "27.210,92",
 "Currency": "EUR",
 "IBAN Code": "IT82Z0103037490000001036493",
 "BL/Delivery note numbers": "",
 "EXONERATION details": "Nlart41DL331/93",
 "Purchase order number": ""
 "items": [
 {
 "Invoice description": "BLOC BSC NPS RENAULT BCB 2POL INRAL",
 "Article/part numbers": "D7077R.04",
 "QTY details of part": "96,00",
 "Unit measurement details": "PCE",
 "Unit price of Part": "8,45700",
 "total price of part": "811,87",
 "BL/Delivery note numbers": "",
 "Purchase order number": ""
 }]
 }
"""
        spanish_text = '''you are an expert in invoice entity extraction. Extract all the required fields mentioned below from the pdf. The field names may not be the same as given, you have to intelligently identify those fields. 
.Return the response in JSON beautify format.

Required Fields:
Billing Name (FACTURE ENVOYÉE À)
Buyer NIF (NUM INTRA)
Billing Company name 
Delivery address (ship to party,Livré à)
Supplier Name 
Supplier NIF (TVA)
Supplier code (Supplier Number,Customer Reference,FOURNISSEUR)
Transaction Type - should be identified from the type of doc provided
Invoice number
Invoice date
Net Amount
Tax percentage
Tax Amount
Gross Amount
Currency
IBAN Code
Contract number (Reference No)
EXONERATION details
Invoice description
Article/part number (selling code,Ref)
QTY details of part (volume)
Unit measurement details
Unit price of Part
total price of part (Montant HT)
BL/Delivery note numbers (Delivery No,N° BL)
Purchase order number (COMMANDE,REFERENCE COMMANDE CLIENT,Commande,Vos références,N° de Bon de commande)

If the Buyer NIF is not found then extract the data from code TVA
If the Delivery note number is not found please extract the data from Nr.DDT or B.LIVRAIS
If the Net Amount is not found then extract the data from Total or Hors Taxe.
If the contract number is not found extract the data from Reference cde Client or your order reference
If the supplier code is not found extract the data from Compte Fournisseur
If Net amount is not found extract the data from invoice amount
If the purchase order number is not found extract the data from commande client
If Exoneration detail is not found extract the data from TVA exigible d’après les débits


Sample response:
{
  "Billing Name": "RENAULT SAS",
  "Buyer NIF": "FR 66780129987",
  "Billing Company name": "RENAULT SAS",
  "Delivery address": "13 AV PAUL LANGEVIN, France",
  "Supplier Name": "Cebi Italy S.p.A.",
  "Supplier NIF": "03019880040",
  "Supplier code": "210483",
  "Transaction Type": "INVOICE",
  "Invoice number": "134884",
  "Invoice date": "31/08/2023",
  "Net Amount": "27.210,92",
  "Tax percentage": "0",
  "Tax Amount": "0",
  "Gross Amount": "27.210,92",
  "Currency": "EUR",
  "IBAN Code": "IT82Z0103037490000001036493",
  "Contract number": "62818",
  "EXONERATION details": "Nlart41DL331/93",
  "items": [
    {
      "Invoice description": "BLOC BSC NPS RENAULT BCB 2POL INRAL",
      "Article/part numbers": "D7077R.04",
      "QTY details of part": "96,00",
      "Unit measurement details": "PCE",
      "Unit price of Part": "8,45700",
      "total price of part": "811,87",
      "BL/Delivery note numbers": "01/0/14070",
      "Purchase order number": "5000008971"
    }]
    }'''
        generation_config = {
            "max_output_tokens": 8192,
            "temperature": 0,
            "top_p": 0.95,
        }

        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        output =""

        #writing the transaction details in excel file
        update_excel_file(pdf_name_wo_extention)

        response = generate(text1)
        

        output1 = iterateResponse(response)

        if output1 is None:
            response = generate(spanish_text)
            output1 = iterateResponse(response)

        if output1 is None:
            st.write("Cannot generate Response for this document")
        #print(output1)
        else:
            pattern = r'"([^"]+)": "([^"]+)"'

            # Find all matches in the cleaned string
            matches = re.findall(pattern, output1)
            #st.write(matches)
            data_dict = {}
            count = 0
            for key,value in matches:
                
                if key.strip() not in data_dict.keys():
                    data_dict[key.strip()] = value
                    count+=1
                else:
                    data_dict[f"{key.strip()}_{count}"]=value
                    count+=1
            
            output1 = output1.replace('\\n',' ')
            output1 = output1.replace('CF','')
            st.write(output1)

            text2 ="""
            you are an expert in invoice entity extraction. Extract all the required fields mentioned below from the pdf. The field names may not be the same as given, you have to intelligently identify those fields. 
    .Return the response in JSON beautify format.

    Required Fields:
    Buyer NIF (IDENTIFICATION TVA,Your VAT-No,Renault Espana S.A VAT No,VAT-nr)
    Delivery address (Nom du projet,Odbiorca/Recipient,Récept. de marchandises) - Do not include 'API CSP ACH' . Also do not include new line character
    Currency
    Transaction Type
    Invoice Number
    Supplier NIF (Mersis No)
    Supplier Code (Compte Fournisseur,account number at recipient,Cta.en client,Customer Reference,Code client,numéro de compte chez le destinataire,Code client,CLIENT CODE,SUPPLIER ACCOUNT NO)
    BL/Delivery note numbers (Nºalbarán Issue) - extract the 10 digit number which starts with '5'
    Purchase Order Number (SAER NO,Vos références,Our ref. No.,Votre N° de commande,Votre reference,Votre Cde - N* Lig,Reference client)

    If the Supplier code is not found extract the data from 'FOURNISSEUR' or 'code client'
    For supplier code extract the data from entity that starts with 'CF' or 'CF '
            """
            second_output=""
            keys = [key.lower() for key in data_dict.keys()]
            #st.write(keys)
            if "supplier code" not in keys or "bl/delivery note numbers" not in keys or "purchase order number" not in keys or "buyer nif" not in keys or "supplier nif" not in keys or "transaction type" not in keys or "delivery address" not in keys or "currency" not in keys or "invoice number" not in keys:
                #st.write("Supplier code not present")
                response = generate(text2)

                for res in response:
                    second_output= second_output + res.text
                print("Second response : \n", second_output)
                second_output=second_output.replace('\\n',' ')
                second_output = second_output.replace('CF','')
                
                pattern = r'"([^"]+)": "([^"]+)"'

                # Find all matches in the cleaned string
                matches1 = re.findall(pattern, second_output)
                #st.write(matches)
                data_dict_secon_prompt = {}

                for key,value in matches1:
                    new_key = re.sub(r'\s*\(.*\)', '', key).strip()
                    #print("New key: ",new_key)
                    data_dict_secon_prompt[new_key.strip().lower()] = value
                print(data_dict_secon_prompt)

                fields = ["supplier code","bl/delivery note numbers","purchase order number","buyer nif","supplier nif","transaction type","currency","delivery address","invoice number"]
                for k in fields:
                    if k not in keys and k in data_dict_secon_prompt.keys():
                        temp_value = data_dict_secon_prompt[k]
                        st.write(k+" : "+temp_value)
                # second_output=str(second_output)
                # second_output=second_output.replace('\\n',' ')
                # second_output = second_output.replace('CF','')
                # st.write(second_output)


