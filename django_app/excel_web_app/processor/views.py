import os
import shutil
import uuid
import json
from django.shortcuts import render
from django.http import HttpResponse, FileResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import pandas as pd


UPLOAD_DIRECTORY = os.path.join(settings.BASE_DIR, 'processor', 'temp')
CONFIG_PATH = os.path.join(settings.BASE_DIR, 'processor', 'config.json')

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)


def process_dental_data(df_dental, output_directory, branch_name):
    desired_columns = CONFIG['column_names']['desired']
    df_filtered = df_dental[desired_columns]
    net_amount_idx = df_filtered.columns.get_loc('Net Amount')
    df_modified = df_filtered.copy()
    df_modified.insert(net_amount_idx + 1, 'Blank Col 1', [''] * len(df_modified))
    df_modified.insert(net_amount_idx + 2, 'Blank Col 2', [''] * len(df_modified))
    new_column_names = CONFIG['column_names']['new']
    df_modified.columns = new_column_names

    consultation_df = df_modified[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
    consultation_tax = CONFIG['tax_rates']['consultation']
    consultation_df['Base Value'] = pd.to_numeric(consultation_df['Total inv'], errors='coerce') / consultation_tax
    consultation_df['Sgst'] = consultation_df['Base Value'] * (consultation_tax - 1) / 2
    consultation_df['Cgst'] = consultation_df['Base Value'] * (consultation_tax - 1) / 2
    consultation_df['Base Value'] = consultation_df['Base Value'].round(2)
    consultation_df['Sgst'] = consultation_df['Sgst'].round(2)
    consultation_df['Cgst'] = consultation_df['Cgst'].round(2)
    consultation_df['Total Amount'] = consultation_df['Base Value']
    consultation_df['Doctors  Name'] = 'Clinic'

    ortho_keywords = CONFIG['ortho_keywords']
    ortho_pattern = '|'.join(ortho_keywords)
    ortho_bonding_df = df_modified[df_modified['Treatment Name'].str.contains(ortho_pattern, case=False, na=False)].copy()
    ortho_tax = CONFIG['tax_rates']['ortho']
    ortho_bonding_df['Base Value'] = pd.to_numeric(ortho_bonding_df['Total inv'], errors='coerce') / ortho_tax
    ortho_bonding_df['Sgst'] = ortho_bonding_df['Base Value'] * (ortho_tax - 1) / 2
    ortho_bonding_df['Cgst'] = ortho_bonding_df['Base Value'] * (ortho_tax - 1) / 2
    ortho_bonding_df['Base Value'] = ortho_bonding_df['Base Value'].round(2)
    ortho_bonding_df['Sgst'] = ortho_bonding_df['Sgst'].round(2)
    ortho_bonding_df['Cgst'] = ortho_bonding_df['Cgst'].round(2)
    ortho_bonding_df['Total Amount'] = ortho_bonding_df['Base Value']

    consultation_mask = df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)
    ortho_mask = df_modified['Treatment Name'].str.contains(ortho_pattern, case=False, na=False)
    matched_rows_mask = consultation_mask | ortho_mask
    rest_df = df_modified[~matched_rows_mask].copy()
    rest_df = rest_df[~rest_df['Date'].astype(str).str.contains('Count:', case=False, na=False)]
    rest_df['Base Value'] = ''
    rest_df['Sgst'] = ''
    rest_df['Cgst'] = ''

    consultation_output_path = os.path.join(output_directory, f"{branch_name}_Dental_Consultation.xlsx")
    ortho_output_path = os.path.join(output_directory, f"{branch_name}_Dental_Ortho_Bonding.xlsx")
    rest_output_path = os.path.join(output_directory, f"{branch_name}_Dental_Rest.xlsx")
    consultation_df.to_excel(consultation_output_path, index=False)
    ortho_bonding_df.to_excel(ortho_output_path, index=False)
    rest_df.to_excel(rest_output_path, index=False)
    
    return {
        f"{branch_name}_Dental_Consultation": consultation_output_path,
        f"{branch_name}_Dental_Ortho_Bonding": ortho_output_path,
        f"{branch_name}_Dental_Rest": rest_output_path
    }


def process_skin_data(df_skin, output_directory, branch_name):
    desired_columns = CONFIG['column_names']['desired']
    df_filtered = df_skin[desired_columns]
    net_amount_idx = df_filtered.columns.get_loc('Net Amount')
    df_modified = df_filtered.copy()
    df_modified.insert(net_amount_idx + 1, 'Blank Col 1', [''] * len(df_modified))
    df_modified.insert(net_amount_idx + 2, 'Blank Col 2', [''] * len(df_modified))
    new_column_names = CONFIG['column_names']['new']
    df_modified.columns = new_column_names

    consultation_df = df_modified[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
    consultation_tax = CONFIG['tax_rates']['consultation']
    consultation_df['Base Value'] = pd.to_numeric(consultation_df['Total inv'], errors='coerce') / consultation_tax
    consultation_df['Sgst'] = consultation_df['Base Value'] * (consultation_tax - 1) / 2
    consultation_df['Cgst'] = consultation_df['Base Value'] * (consultation_tax - 1) / 2
    consultation_df['Base Value'] = consultation_df['Base Value'].round(2)
    consultation_df['Sgst'] = consultation_df['Sgst'].round(2)
    consultation_df['Cgst'] = consultation_df['Cgst'].round(2)
    consultation_df['Total Amount'] = consultation_df['Base Value']
    consultation_df['Doctors  Name'] = 'Clinic'

    other_treatments_df = df_modified[~df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
    ortho_tax = CONFIG['tax_rates']['ortho']
    other_treatments_df['Base Value'] = pd.to_numeric(other_treatments_df['Total inv'], errors='coerce') / ortho_tax
    other_treatments_df['Sgst'] = other_treatments_df['Base Value'] * (ortho_tax - 1) / 2
    other_treatments_df['Cgst'] = other_treatments_df['Base Value'] * (ortho_tax - 1) / 2
    other_treatments_df['Base Value'] = other_treatments_df['Base Value'].round(2)
    other_treatments_df['Sgst'] = other_treatments_df['Sgst'].round(2)
    other_treatments_df['Cgst'] = other_treatments_df['Cgst'].round(2)
    other_treatments_df['Total Amount'] = other_treatments_df['Base Value']
    
    consultation_output_path = os.path.join(output_directory, f"{branch_name}_Skin_Consultation.xlsx")
    other_output_path = os.path.join(output_directory, f"{branch_name}_Skin_Other.xlsx")
    consultation_df.to_excel(consultation_output_path, index=False)
    other_treatments_df.to_excel(other_output_path, index=False)
    
    return {
        f"{branch_name}_Skin_Consultation": consultation_output_path,
        f"{branch_name}_Skin_Other": other_output_path
    }


def process_hair_data(df_hair, output_directory, branch_name):
    desired_columns = CONFIG['column_names']['desired']
    df_filtered = df_hair[desired_columns]
    net_amount_idx = df_filtered.columns.get_loc('Net Amount')
    df_modified = df_filtered.copy()
    df_modified.insert(net_amount_idx + 1, 'Blank Col 1', [''] * len(df_modified))
    df_modified.insert(net_amount_idx + 2, 'Blank Col 2', [''] * len(df_modified))
    new_column_names = CONFIG['column_names']['new']
    df_modified.columns = new_column_names

    hair_tax = CONFIG['tax_rates']['hair']
    df_modified['Base Value'] = pd.to_numeric(df_modified['Total inv'], errors='coerce') / hair_tax
    df_modified['Sgst'] = df_modified['Base Value'] * (hair_tax - 1) / 2
    df_modified['Cgst'] = df_modified['Base Value'] * (hair_tax - 1) / 2
    df_modified['Base Value'] = df_modified['Base Value'].round(2)
    df_modified['Sgst'] = df_modified['Sgst'].round(2)
    df_modified['Cgst'] = df_modified['Cgst'].round(2)
    df_modified['Total Amount'] = df_modified['Base Value']
    
    df_modified.loc[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False), 'Doctors  Name'] = 'Clinic'

    hair_output_path = os.path.join(output_directory, f"{branch_name}_Hair.xlsx")
    df_modified.to_excel(hair_output_path, index=False)
    
    return {f"{branch_name}_Hair": hair_output_path}


def process_economy_data(df_economy, output_directory, branch_name):
    return process_dental_data(df_economy, output_directory, f"{branch_name}_Economy")


def process_excel_file_logic(sales_file_path: str, receipt_file_path: str, output_directory: str, branch: str):
    
    df = pd.read_excel(sales_file_path)
    processed_files = {}

    if branch == "Kalamassery":
        if 'Notes' not in df.columns:
            raise ValueError("The uploaded file for the Kalamassery branch is missing the 'Notes' column.")
        
        df['Notes'] = df['Notes'].str.lower().str.strip()
        dental_df = df[df['Notes'] == 'dental'].copy()
        skin_df = df[df['Notes'] == 'skin'].copy()
        hair_df = df[df['Notes'] == 'hair'].copy()

        if not dental_df.empty:
            processed_files.update(process_dental_data(dental_df, output_directory, "Kalamassery"))
        if not skin_df.empty:
            processed_files.update(process_skin_data(skin_df, output_directory, "Kalamassery"))
        if not hair_df.empty:
            processed_files.update(process_hair_data(hair_df, output_directory, "Kalamassery"))

    elif branch == "Vedimara":
        receipt_df = pd.read_excel(receipt_file_path)
        receipt_df.rename(columns={'Pt Id': 'Pt ID'}, inplace=True)
        merged_df = pd.merge(df, receipt_df[['Pt ID', 'Notes']], on='Pt ID', how='left')
        
        merged_df['Notes_y'] = merged_df['Notes_y'].str.lower().str.strip()
        dental_df = merged_df[merged_df['Notes_y'] == 'dental'].copy()
        economy_df = merged_df[merged_df['Notes_y'] == 'economy'].copy()
        skin_df = merged_df[merged_df['Notes_y'] == 'skin'].copy()

        if not dental_df.empty:
            processed_files.update(process_dental_data(dental_df, output_directory, "Vedimara"))
        if not economy_df.empty:
            processed_files.update(process_economy_data(economy_df, output_directory, "Vedimara"))
        if not skin_df.empty:
            processed_files.update(process_skin_data(skin_df, output_directory, "Vedimara"))

    elif branch == "Choondy":
        skin_df = df[df['Doctor'] == 'Redhina Raj'].copy()
        dental_df = df[df['Doctor'] != 'Redhina Raj'].copy()

        if not dental_df.empty:
            processed_files.update(process_dental_data(dental_df, output_directory, "Choondy"))
        if not skin_df.empty:
            processed_files.update(process_skin_data(skin_df, output_directory, "Choondy"))
        
    elif branch == "Aluva":
        skin_df = df[df['Doctor'] == 'New Doctor'].copy()
        dental_df = df[df['Doctor'] != 'New Doctor'].copy()

        if not dental_df.empty:
            processed_files.update(process_dental_data(dental_df, output_directory, "Aluva"))
        if not skin_df.empty:
            processed_files.update(process_skin_data(skin_df, output_directory, "Aluva"))
    
    elif branch == "استلام":
        processed_files.update(process_dental_data(df, output_directory, "استلام"))
    elif branch == "paravoor":
        processed_files.update(process_dental_data(df, output_directory, "paravoor"))
        
    else: # Original logic 
        processed_files.update(process_dental_data(df, output_directory, "Treatments_Done"))

    return processed_files


def home(request):
    return render(request, 'processor/home.html')

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            sales_file = request.FILES['excel_file']
            branch = request.POST.get('branch')
            receipt_file = request.FILES.get('receipt_file')

            if not sales_file.name.endswith(('.xlsx', '.xls')):
                return render(request, 'processor/upload.html', {'error': 'Invalid file type for sales file. Only .xlsx and .xls are allowed.'})

            if branch == 'Vedimara' and not receipt_file:
                return render(request, 'processor/upload.html', {'error': 'Receipt file is required for Vedimara branch.'})

            if receipt_file and not receipt_file.name.endswith(('.xlsx', '.xls')):
                return render(request, 'processor/upload.html', {'error': 'Invalid file type for receipt file. Only .xlsx and .xls are allowed.'})

            sales_file_extension = os.path.splitext(sales_file.name)[1]
            unique_sales_filename = f"{uuid.uuid4()}{sales_file_extension}"
            sales_upload_path = os.path.join(UPLOAD_DIRECTORY, unique_sales_filename)

            os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

            with open(sales_upload_path, "wb+") as destination:
                for chunk in sales_file.chunks():
                    destination.write(chunk)

            receipt_upload_path = ""
            if receipt_file:
                receipt_file_extension = os.path.splitext(receipt_file.name)[1]
                unique_receipt_filename = f"{uuid.uuid4()}{receipt_file_extension}"
                receipt_upload_path = os.path.join(UPLOAD_DIRECTORY, unique_receipt_filename)
                with open(receipt_upload_path, "wb+") as destination:
                    for chunk in receipt_file.chunks():
                        destination.write(chunk)

            try:
                processed_files = process_excel_file_logic(sales_upload_path, receipt_upload_path, UPLOAD_DIRECTORY, branch)
                
                os.remove(sales_upload_path)
                if receipt_upload_path:
                    os.remove(receipt_upload_path)

                download_links = {}
                for key, path in processed_files.items():
                    filename = os.path.basename(path)
                    download_links[key] = filename

                return render(request, 'processor/upload.html', {'download_links': download_links, 'message': 'File processed successfully!'})
            except Exception as e:
                if os.path.exists(sales_upload_path):
                    os.remove(sales_upload_path)
                if receipt_upload_path and os.path.exists(receipt_upload_path):
                    os.remove(receipt_upload_path)
                return render(request, 'processor/upload.html', {'error': f"Error processing Excel file: {e}"})
        else:
            return render(request, 'processor/upload.html', {'error': 'Please upload a sales file.'})
    return render(request, 'processor/upload.html')


def download_file(request, filename):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    raise Http404("File not found")
