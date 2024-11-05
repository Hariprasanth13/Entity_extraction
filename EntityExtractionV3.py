import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models

def generate():
  vertexai.init(project="rntbci-digital-innovation-lab", location="us-central1")
  model = GenerativeModel(
    "gemini-1.5-pro-001",
  )
  responses = model.generate_content(
      [text1, image1],
      generation_config=generation_config,
      safety_settings=safety_settings,
      stream=True,
  )

  for response in responses:
    print(response.text, end="")

text1 = """Extract the below mentioned entities from the image given.
Billing Name
Buyer NIF
Billing Company name
Delivery address
Supplier Name 
Supplier NIF
Supplier code
Transaction Type - identify the type of invoice from the pdf
Invoice number
Invoice date
Net Amount
Tax percentage
Tax Amount
Gross Amount
Currency
IBAN Code
Contract number
EXONERATION details
Invoice description (Description)
Article/part numbers (Ref)
QTY details of part
Unit measurement details
Unit price of Part
total price of part
BL / Delivery note numbers
Purchase order number (V/REF,Votre n° commande)
sample format:
{{
"Billing Name": "RENAULT S.A.S",
 "Buyer NIF": "FR66780129987",
 "Billing Company name": "RENAULT S.A.S",
 "Delivery address detail / Plant code": "13, AVENUE PAUL LANGEVIN",  
 "Supplier Name": "Samaya Electronics Egypted.",
 "Supplier NIF": "413-042-480",
 "Supplier code": "",256854,
 "Transaction Type": "Invoice",
 "Invoice number": "43631",
 "Invoice date": "19/10/2023",
 "Net Amount": "27074.16",
 "Tax percentage": "0%",
 "Tax Amount": ".00",
 "Gross Amount": "27074.16",
 "Currency": "EUR",
 "Supplier Bank A/c details": "HSBC Bank Egypt S.A.E",
"items": [
  {{
   "Invoice description": "BETASEALTM 1527EPG REPAIR KIT",
   "Article/part numbers":"00099090112",
   "QTY details of part": "1.080,000",
   "Unit price of Part": "78,21,
   "total price of part":"8.446,68",
   "BL / Delivery note numbers": "863697686",
   "Contract number": "683513"
  }}]
  }}"""

with open("C:\\Projects\\GBS_project\\GBS_EE\\images\\page0.jpg",'rb') as file:
  image_data = file.read()

bytecode = base64.b64encode(image_data)

image1 = Part.from_data(
    mime_type="image/jpeg",
    data=base64.b64decode(bytecode))



generation_config = {
    "max_output_tokens": 8192,
    "top_p": 0.95,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

generate()

