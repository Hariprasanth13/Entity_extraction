text = '''
Invoice Number: 63501112513877
Invoice Date: 16-04-2024
Due Date: 31-05-2024
Total Amount: 10 080,00 EUR
Tax Amount: 1 680,00 EUR
Vendor Name: CAPGEMINI TECHNOLOGY SERVICES
Vendor Address: 145-151 quai du Président Roosevelt CS 30186 92445, Issy les Moulineaux Cedex France
Vendor VAT Number: FR85 479 766 842
Client Name: RENAULT S.A.S.
Client Address: CSP ACHATS FOURN PROTOS/INGENIER CSP ACH 4 44 78084 YVELINES CEDEX 9 France
Client VAT Number: FR66780129987
Line Items:
Description: Recipient: CAROLE LEGRAND POSTE 00010: R LS 240106 50613 EXPLOIT CAPG Acceptance Document: 5112621915 Sheet Number: 1001213401 MARS 2024
Quantity: 8 400,00
Unit Price: 1.00
Total: 8 400,00
'''

# Split the text into lines
lines = text.strip().split('\n')

# Remove spaces from each line
cleaned_lines = [line.replace(' ', '') for line in lines]

# Join the cleaned lines back into a single string
cleaned_text = '\n'.join(cleaned_lines)

print(cleaned_text)
