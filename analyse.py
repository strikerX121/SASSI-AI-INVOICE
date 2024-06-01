# import libraries
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest
import io
from openai import OpenAI
from openai.types.chat.completion_create_params import ResponseFormat
import openai
import json
import pandas as pd
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

openai_key = os.environ["OPENAI_KEY"]
key = os.environ['AZURE_KEY']
endpoint = os.environ['AZURE_ENDPOINT']


def get_categories():
    df = pd.read_excel("Customs Schedule.xlsx", sheet_name="Sheet1")
    return df['Item Description'].tolist()

# def fix_name(item):
#     client = OpenAI(
#     api_key= openai_key
#     )
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role":"system",
#              "content":f""" """
#             },
#             {
#             "role": "user",
#             "content": item
#             }
#         ],
#         temperature=0.7,
#         max_tokens=56,
#         top_p=1,
#         )
#     return response.choices[0].message.content


def categorize_items(item):
    client = OpenAI(
    api_key= openai_key
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system",
             "content":f""" You are an intelligent categorization system with the ability to correct and optimize item names. Your task is threefold:

1. Fix any errors in the item name provided, such as typos, grammatical mistakes, or incorrect words. If the item name is already correct, leave it unchanged.

2. Shorten the corrected item name to only include the essential title or product name. Remove any unnecessary descriptors, adjectives, or specifications that don't significantly alter the product's identity.

3. Add the quantity of the item in parentheses at the end of the shortened title. If no quantity is explicitly mentioned, assume it to be (1). If multiple quantities are mentioned (e.g., "pack of 6"), use that value.

4. Categorize the fixed and optimized item into one of the available categories based on its characteristics and description. The list of available categories is: {get_categories()}.

To help you understand the task better, here are some example items, their corrected and optimized names, and their corresponding categories:

Example 1: 
Original Item: A reed, ripe appel with a slightly bruised skin
Corrected & Optimized Item: Apple (1)
Category: Fruits

Example 2:
Original Item: A lether breifcase with multiple compartments, expandable, for office use
Corrected & Optimized Item: Leather Briefcase (1)
Category: Bags & Luggage

Example 3:
Original Item: A paperback novel in the mystery genre, 500 pages long
Corrected & Optimized Item: Mystery Novel (1)
Category: Books

Example 4:
Original Item: Pack of 6 ballpoint pens, blue ink, medium point
Corrected & Optimized Item: Ballpoint Pens (6)
Category: Office Supplies

Now, I will provide you with an item to correct, optimize, and categorize. Please:
1. Fix any errors in its name.
2. Shorten it to only the essential title or product name.
3. Add the quantity in parentheses at the end.
4. Assign it to the most appropriate category from the list provided.

If the item does not fit into any of the given categories, you can use "No Category".

Please provide your response in JSON format with the following structure:
{{
  "originalItem": "The original item name as provided",
  "correctedItem": "The shortened item name with quantity",
  "category": "The most appropriate category from the list"
}}

The "correctedItem" field should now contain only the essential product title followed by the quantity in parentheses. If no correction or optimization is needed, the core title in "originalItem" and "correctedItem" should be identical, but "correctedItem" should still have the quantity added."""
            },
            {
            "role": "user",
            "content": item
            }
        ],
        temperature=0.7,
        top_p=1,
        )

    return json.loads(response.choices[0].message.content)

def analyze_invoice(file):
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    invoice_doc = AnalyzeDocumentRequest(bytes_source=file.read())

    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-invoice", invoice_doc
    )
    invoices = poller.result()

    if invoices.documents:
        details = {'description':[],
                   'unit_price': [],
                   'categories': [],
                   'amount': [],
                   'subtotal': 0}
        for idx, invoice in enumerate(invoices.documents):
            print(f"--------Analyzing invoice #{idx + 1}--------")
            print("Invoice items:")
            if invoice.fields.get("Items"):
                for idx, item in enumerate(invoice.fields.get("Items").get("valueArray")):
                    print(f"...Item #{idx + 1}")
                    item_description = item.get("valueObject").get("Description")
                    if item_description:
                        fixed_data = categorize_items(item_description.get('content'))
                        details['description'].append(fixed_data['correctedItem'])
                        details['categories'].append(fixed_data['category'])
                        print("---------------------------------------------------------------------------")
                    unit_price = item.get("valueObject").get("UnitPrice")
                    if unit_price:
                        details['unit_price'].append(f"{unit_price.get('content')}")
                    amount = item.get("valueObject").get("Amount")
                    if amount:
                        details['amount'].append(amount.get('content'))

                subtotal = invoice.fields.get("SubTotal")
                if subtotal:
                    details['subtotal'] = subtotal.get('content')

                else:
                    total = invoice.fields.get("Total")
                    if total:
                        details['total'] = total.get('content')
    return details


# if __name__ == "__main__":
    #  analyze_invoice()
    # print(get_categories())
    # print(categorize_items())