import streamlit as st # type: ignore
from google.oauth2 import service_account
import pandas as pd
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
import base64
import json
import re


uploaded_file = None

def extraction(secondPrompt):
    global uploaded_file
    if uploaded_file is not None:
        pdf_data = uploaded_file.read()
        bytecode = base64.b64encode(pdf_data)
        document1 = Part.from_data(
                    mime_type="application/pdf",  
                    data=base64.b64decode(bytecode)
                )
    else:
        st.write("Uploaded file is Null")
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
    text1 = """you are an expert in invoice entity extraction. Extract all the required fields mentioned below from the pdf. The field names may not be the same as given, you have to intelligently identify those fields. 
.Return the response in JSON beautify format.

Required Fields:
Billing Name (FACTURE ENVOYÉE À,Platnik/Payer) - extract only the billing name
Buyer NIF (NUM INTRA,N° TVA intracommunautaire CLIENT,Renault Espana S.A VAT No,VAT-nr)
Billing Company name - extract the company name from buyer details
Delivery address (ship to party,Livré à,Odbiorca/Recipient,Récept. de marchandises)- Do not include 'API', 'CSP', 'ACH' . Also do not include new line character
Supplier Name - Extract full name
Supplier NIF (TVA,N° IDENTIFICATION) - extract complete data
Supplier code (Supplier Number,Customer Reference,FOURNISSEUR,Fournisseur,numéro de compte chez le destinataire,Code client,CLIENT CODE,SUPPLIER ACCOUNT NO) - don't extract the data after '-'
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
BL / Delivery note numbers (Delivery No,N° BL,BORDEREAU LIVRAISON,Doc. réception,BL)
Purchase order number (Votre commande,COMMANDE,REFERENCE COMMANDE CLIENT,Commande,Vos références,N° de Bon de commande,Votre N° de commande,Votre reference,Votre Cde - N* Lig,Reference client) - don't extract the data after '-'

If the Buyer NIF is not found then extract the data from code TVA or Votre T.V.A
If the Delivery note number is not found please extract the data from Nr.DDT or B.LIVRAIS
If the Net Amount is not found then extract the data from Total or Hors Taxe.
If the supplier code is not found extract the data from Compte Fournisseur
If Net amount is not found extract the data from invoice amount or Final amount
If the purchase order number is not found extract the data from commande client or Order N°
If Exoneration detail is not found extract the data from TVA exigible d’après les débits
If BL / Delivery note number is not found extract the data from N° d'expedition or BSR
If Delivery address is not found extract the data from 'Consignee'
If the Tax amount is 'null' then return as '0'

Purchase order number sometimes starts with 'BDC '
BL / Delivery note number sometimes starts with 'BSR ' or 'BSR'
Supplier code sometimes starts with 'CF' or 'CF '. Do not include 'CF' in the extraction
For supplier code extract the data from entity that starts with 'CF' or 'CF ' even though if it is explicitly mentioned
Article/part number sometimes ends with 'R'
Billing company name should be same as the billing name
Replace Votre Commande entity name with Purchase order number
Sometimes Article/part number can be found after 'KN' but do not include 'KN'
If Article/part number ends with 'R' extract the entity along with 'R'
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
 "BL / Delivery note numbers": "",
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
 "BL / Delivery note numbers": "",
 "Purchase order number": ""
 }]
 }
"""
    text2=''' you are an expert in invoice entity extraction. Extract all the required fields mentioned below from the pdf. The field names may not be the same as given, you have to intelligently identify those fields. 
.Return the response in JSON beautify format.

Required Fields:
Supplier Code (Compte Fournisseur,account number at recipient,Cta.en client,Customer Reference,Code client)

If the Supplier code is not found extract the data from 'FOURNISSEUR' or 'code client'
For supplier code extract the data from entity that starts with 'CF' or 'CF ' 
'''

    #extracted_entities=generate(document1,text1,generation_config,safety_settings)
    vertexai.init(project="rntbci-digital-innovation-lab", location="us-central1")
    model = GenerativeModel("gemini-1.5-pro-001")
    if secondPrompt==False:
        responses = model.generate_content(
            [document1, text1],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True,
        )
        #Collecting responses
        extracted_entities = []
        
        for response in responses:
            extracted_entities.append(response.text)
    
    
        return extracted_entities
    else:
        responses = model.generate_content(
            [document1, text1],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True,
        )
        st.write("Inside text2")
        #Collecting responses
        extracted_entities = []
        
        for response in responses:
            st.write(response)
            extracted_entities.append(response.text)
        
        
        return extracted_entities
    
    # #Collecting responses
    # extracted_entities = []
    
    # for response in responses:
    #     extracted_entities.append(response.text)
    
    
    # return extracted_entities

# def generate(document1,text1,generation_config,safety_settings):
#     vertexai.init(project="rntbci-digital-innovation-lab", location="us-central1")
#     model = GenerativeModel("gemini-1.5-pro-001")
#     responses = model.generate_content(
#         [document1, text1],
#         generation_config=generation_config,
#         safety_settings=safety_settings,
#         stream=True,
#     )
#     extracted_entities = []
#     for response in responses:
#         extracted_entities.append(response.text)
    
#     return extracted_entities

# Function to check for null values in a dictionary
def check_null_values(dictionary):
    for key, value in dictionary.items():
        if value is None:
            return True, key
    return False, None

def main():
    global uploaded_file
    # st.title("GBS Invoice Entity Extraction")
    # uploaded_file = st.file_uploader('Upload your file', type ='pdf')
    output = ''''''
    if st.button("Submit"):
        if uploaded_file is not None:
            st.write("File uploaded Successfully")
            #with open(uploaded_file,'rb') as file:

            entities = extraction(secondPrompt=False)
            # Display extracted entities
            st.header("Extracted Entities")
            for idx, entity in enumerate(entities, start=1):
                output+=str(entity).strip()
            st.write(output)
            
            pattern = r'"([^"]+)": "([^"]+)"'

            # Find all matches in the cleaned string
            matches = re.findall(pattern, output)
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

            if "Supplier Code" not in data_dict.keys():
                st.write("Supplier code not present")
                response = extraction(secondPrompt=True)
                for res in response:
                    output= output + res.text
                output1=str(output)
    
                st.write("Second prompt executed")
                
            
            # has_null, key_with_null = check_null_values(data_dict)
            # st.write(key_with_null)
            # Create a dictionary from the matches
            # data_dict = dict(matches)
            # st.write("First Output \n",output)
            # st.write("********Entities extracted successfully**********")
            
            

if __name__ == "__main__":
    st.title("GBS Invoice Entity Extraction")
    uploaded_file = st.file_uploader('Upload your file', type ='pdf')
    main()

    







