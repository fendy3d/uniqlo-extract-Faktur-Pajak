import re
from re import sub
from decimal import Decimal
import pdfplumber
import pandas as pd
from collections import namedtuple
import datetime
import os
import csv
from enum import Enum

pathToPdfs = os.getcwd()+"/dropPdfHere/"

#These are for non-line-items.csv
header_row = ['Nomor Seri Faktur Pajak', 'Nama Pengusaha Kena Pajak', 'Nama Pembeli Barang Kena Pajak', 'DPP', 'PPN', 'Tanggal Faktur Pajak', 'Reference Text']
list_of_rows = []

#These are for lineitems.csv
header_line_items_row = ['Nomor Seri Faktur Pajak', 'Number', 'Line Item', 'Line Amount']
list_of_line_items_rows = []

# VARIABLES FOR YUNIKE
# entity_code: other PT = 0, PT VIVO MOBILE INDONESIA = 1, PT PINTAR BELANJA INDONESIA = 2

# entity_code = int(input("0: Others\n1: PT ECart\nPlease input entity code: ")) # <---- CHANGE THIS!
entity_code = 0

def reformatDate(date_string):
    #assuming date is written like 03 Januari 2022
    date_list = date_string.split(" ")
    _, day, month, year = date_list
    if (month == "Januari"):
        month = "01"
    elif (month == "Februari"):
        month = "02"
    elif (month == "Maret"):
        month = "03"
    elif (month == "April"):
        month = "04"
    elif (month == "Mei"):
        month = "05"
    elif (month == "Juni"):
        month = "06"
    elif (month == "Juli"):
        month = "07"
    elif (month == "Agustus"):
        month = "08"
    elif (month == "September"):
        month = "09"
    elif (month == "Oktober"):
        month = "10"
    elif (month == "November"):
        month = "11"
    elif (month == "Desember"):
        month = "12"
    return day + "/" + month + "/" + year

def getInformation(ListOfText):
    if entity_code == 0:
        nomorSeriFakturPajak = ListOfText[1].split(":")[-1].strip()
        namaPengusahaKenaPajak = ListOfText[3].split(":")[-1]
        namaPembeliBarangKenaPajak = ListOfText[8].split(":")[-1]
        dpp = ""
        ppn = ""
        tanggalFakturPajak = reformatDate(ListOfText[-7].split(",")[-1]) #reformat to dd/mm/yyyy
        referenceText = ListOfText[-5]

    for text in ListOfText:
        if "Total PPN" in text:
            ppn = text.split(" ")[-1]
            ppn = float(ppn.replace('.','').replace(',','.'))
        elif "Dasar Pengenaan Pajak" in text:
            dpp = text.split(" ")[-1]
            dpp = float(dpp.replace('.','').replace(',','.'))
    return [nomorSeriFakturPajak, namaPengusahaKenaPajak, namaPembeliBarangKenaPajak, dpp, ppn, tanggalFakturPajak, referenceText]


for _, _, files in os.walk(pathToPdfs):
    for filename in files:
        if '.pdf' in filename:
            print ("Extracting " + filename + "....")
            pdf = pdfplumber.open(pathToPdfs + filename)
            number_of_pages = len(pdf.pages)
            
            
            if number_of_pages == 1:
                #Extracting 'non-line-items' information
                texts = pdf.pages[0].extract_text() # get all texts. Using this to get other information
                counter = 0
                
                list_of_texts = list(texts.split("\n"))

                # UNCOMMENT THESE TO PRINT THE INDEX OF THE TEXTS
                # for text in list_of_texts:
                #     print(str(counter) + " : " + text)
                #     counter += 1

                list_of_rows.append(getInformation(list_of_texts))

                nsfp = getInformation(list_of_texts)[0]

                #Extracting 'line items' information
                table = pdf.pages[0].extract_table() # get the table from that page. Using this to get line items information
                for row in table:
                    if row[0].isdigit():
                        row.insert(0,nsfp)
                        row[2] = row[2].replace('.','').replace(',','.')
                        row[3] = row[3].replace('.','').replace(',','.')
                        list_of_line_items_rows.append(row)
                print ("Success: " + filename)
                print ("\n")
                
            elif number_of_pages > 1:
                print("Warning! "+ filename + "has been skipped because it has more than 1 page.")

            print("=========================")

            
    #Exporting csv of non-line items
    df = pd.DataFrame(list_of_rows, columns=header_row)
    df.to_csv('non-line-items.csv',index=False)
    print("non-line-items.csv has been successfully exported.")
    
    #Exporting csv of line items
    df2 = pd.DataFrame(list_of_line_items_rows, columns=header_line_items_row)
    df2.to_csv('line-items.csv',index=False)
    print("line-items.csv has been successfully exported.")

    print("All hail Lord Fendy!")
