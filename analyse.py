# import libraries
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest
import io
from openai import OpenAI
import openai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

openai_key = os.environ["OPENAI_KEY"]
key = os.environ['AZURE_KEY']
endpoint = os.environ['AZURE_ENDPOINT']


def get_categories():
    df = pd.read_excel("Customs Schedule.xlsx", sheet_name="Sheet1")
    return df['Item Description'].tolist()

def categorize_items(item):
    client = OpenAI(
    api_key= openai_key
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system",
             "content":f""" You are an intelligent categorization system. Your task is to categorize the items provided to you into one of the available categories based on the item's characteristics and description. The list of available categories is: {get_categories()}.

                            To help you understand the categories better, here are some example items and their corresponding categories:

                            Example 1: 
                            Item: A red, ripe apple
                            Category: Fruits

                            Example 2:
                            Item: A leather briefcase with multiple compartments
                            Category: Bags & Luggage

                            Example 3:
                            Item: A paperback novel in the mystery genre
                            Category: Books

                            Now, I will provide you with an item to categorize. Please examine the item's characteristics and description, and output the name of the most appropriate category from the list provided. If the item does not fit into any of the given categories, you can respond with "No category"."""
            },
            {
            "role": "user",
            "content": item
            }
        ],
        temperature=0.7,
        max_tokens=56,
        top_p=1,
        )
    return response.choices[0].message.content

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
            for idx, item in enumerate(invoice.fields.get("Items").get("valueArray")):
                print(f"...Item #{idx + 1}")
                item_description = item.get("valueObject").get("Description")
                if item_description:
                    details['description'].append(item_description.get('content'))
                    details['categories'].append(categorize_items(item_description.get('content')))
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