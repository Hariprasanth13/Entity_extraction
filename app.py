from google.oauth2 import service_account
import pandas as pd
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
import base64


def generate():
  vertexai.init(project="rntbci-digital-innovation-lab", location="us-central1")
  model = GenerativeModel("gemini-1.5-pro-001")
  responses = model.generate_content(
      [document1, text1],
      generation_config=generation_config,
      safety_settings=safety_settings,
      stream=True,
  )

  for response in responses:
    print(response.text, end="")

with open("C:\\Projects\\GBS_project\\GBS_EE\\FRANCE_POE\\18734145.pdf",'rb') as file:
  pdf_data = file.read()

bytecode = base64.b64encode(pdf_data)

document1 = Part.from_data(
    mime_type="application/pdf",  
    data=base64.b64decode(bytecode)
)


text1 = """you are an expert in invoice entity extraction. Extract all the required fields mentioned below from the pdf. The field names may not be the same as given, you have to intelligently identify those fields. 
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
BL / Delivery note numbers (Delivery No,N° BL)
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
      "BL / Delivery note numbers": "01/0/14070",
      "Purchase order number": "5000008971"
    }]
    }"""

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

generate()

