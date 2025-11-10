import os
import shutil
import uuid
from django.shortcuts import render
from django.http import HttpResponse, FileResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import pandas as pd

# Define the UPLOAD_DIRECTORY within the app's directory
UPLOAD_DIRECTORY = os.path.join(settings.BASE_DIR, 'processor', 'temp')

def process_excel_file_logic(sales_file_path: str, receipt_file_path: str, output_directory: str, branch: str):
    # 1. Read the Excel file
    df = pd.read_excel(sales_file_path)

    if branch == "Kalamassery":
        # Kalamassery branch logic
        if 'Notes' not in df.columns:
            raise ValueError("The uploaded file for the Kalamassery branch is missing the 'Notes' column.")
        
        # 1. Split by 'Notes' column
        df['Notes'] = df['Notes'].str.lower().str.strip()
        dental_df = df[df['Notes'] == 'dental'].copy()
        skin_df = df[df['Notes'] == 'skin'].copy()
        hair_df = df[df['Notes'] == 'hair'].copy()

        processed_files = {}

        # Process Dental
        if not dental_df.empty:
            # (Same as original logic)
            desired_columns = ['Date', 'Pt ID', 'Patient', 'Treatment Name', 'Doctor', 'Net Amount', 'Tax', 'Total', 'Invoice']
            df_filtered = dental_df[desired_columns]
            net_amount_idx = df_filtered.columns.get_loc('Net Amount')
            df_modified = df_filtered.copy()
            df_modified.insert(net_amount_idx + 1, 'Blank Col 1', [''] * len(df_modified))
            df_modified.insert(net_amount_idx + 2, 'Blank Col 2', [''] * len(df_modified))
            new_column_names = ['Date', 'ID', 'Name', 'Treatment Name', 'Doctors  Name', 'Total Amount', 'Base Value', 'Sgst', 'Cgst', 'Total inv', 'Invoice No']
            df_modified.columns = new_column_names

            consultation_df = df_modified[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
            consultation_df['Base Value'] = pd.to_numeric(consultation_df['Total inv'], errors='coerce') / 1.18
            consultation_df['Sgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Cgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Base Value'] = consultation_df['Base Value'].round(2)
            consultation_df['Sgst'] = consultation_df['Sgst'].round(2)
            consultation_df['Cgst'] = consultation_df['Cgst'].round(2)
            consultation_df['Total Amount'] = consultation_df['Base Value']
            consultation_df['Doctors  Name'] = 'Clinic'

            ortho_keywords = ['dental ortho bonding', 'ortho bonding new', 'debonding']
            ortho_pattern = '|'.join(ortho_keywords)
            ortho_bonding_df = df_modified[df_modified['Treatment Name'].str.contains(ortho_pattern, case=False, na=False)].copy()
            ortho_bonding_df['Base Value'] = pd.to_numeric(ortho_bonding_df['Total inv'], errors='coerce') / 1.05
            ortho_bonding_df['Sgst'] = ortho_bonding_df['Base Value'] * 0.025
            ortho_bonding_df['Cgst'] = ortho_bonding_df['Base Value'] * 0.025
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

            consultation_output_path = os.path.join(output_directory, "Kalamassery_Dental_Consultation.xlsx")
            ortho_output_path = os.path.join(output_directory, "Kalamassery_Dental_Ortho_Bonding.xlsx")
            rest_output_path = os.path.join(output_directory, "Kalamassery_Dental_Rest.xlsx")
            consultation_df.to_excel(consultation_output_path, index=False)
            ortho_bonding_df.to_excel(ortho_output_path, index=False)
            rest_df.to_excel(rest_output_path, index=False)
            processed_files.update({
                "Kalamassery_Dental_Consultation": consultation_output_path,
                "Kalamassery_Dental_Ortho_Bonding": ortho_output_path,
                "Kalamassery_Dental_Rest": rest_output_path
            })

        # Process Skin
        if not skin_df.empty:
            desired_columns = ['Date', 'Pt ID', 'Patient', 'Treatment Name', 'Doctor', 'Net Amount', 'Tax', 'Total', 'Invoice']
            df_filtered = skin_df[desired_columns]
            net_amount_idx = df_filtered.columns.get_loc('Net Amount')
            df_modified = df_filtered.copy()
            df_modified.insert(net_amount_idx + 1, 'Blank Col 1', [''] * len(df_modified))
            df_modified.insert(net_amount_idx + 2, 'Blank Col 2', [''] * len(df_modified))
            new_column_names = ['Date', 'ID', 'Name', 'Treatment Name', 'Doctors  Name', 'Total Amount', 'Base Value', 'Sgst', 'Cgst', 'Total inv', 'Invoice No']
            df_modified.columns = new_column_names

            consultation_df = df_modified[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
            consultation_df['Base Value'] = pd.to_numeric(consultation_df['Total inv'], errors='coerce') / 1.18
            consultation_df['Sgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Cgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Base Value'] = consultation_df['Base Value'].round(2)
            consultation_df['Sgst'] = consultation_df['Sgst'].round(2)
            consultation_df['Cgst'] = consultation_df['Cgst'].round(2)
            consultation_df['Total Amount'] = consultation_df['Base Value']
            consultation_df['Doctors  Name'] = 'Clinic'

            other_treatments_df = df_modified[~df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
            other_treatments_df['Base Value'] = pd.to_numeric(other_treatments_df['Total inv'], errors='coerce') / 1.05
            other_treatments_df['Sgst'] = other_treatments_df['Base Value'] * 0.025
            other_treatments_df['Cgst'] = other_treatments_df['Base Value'] * 0.025
            other_treatments_df['Base Value'] = other_treatments_df['Base Value'].round(2)
            other_treatments_df['Sgst'] = other_treatments_df['Sgst'].round(2)
            other_treatments_df['Cgst'] = other_treatments_df['Cgst'].round(2)
            other_treatments_df['Total Amount'] = other_treatments_df['Base Value']
            
            consultation_output_path = os.path.join(output_directory, "Kalamassery_Skin_Consultation.xlsx")
            other_output_path = os.path.join(output_directory, "Kalamassery_Skin_Other.xlsx")
            consultation_df.to_excel(consultation_output_path, index=False)
            other_treatments_df.to_excel(other_output_path, index=False)
            processed_files.update({
                "Kalamassery_Skin_Consultation": consultation_output_path,
                "Kalamassery_Skin_Other": other_output_path
            })

        # Process Hair
        if not hair_df.empty:
            desired_columns = ['Date', 'Pt ID', 'Patient', 'Treatment Name', 'Doctor', 'Net Amount', 'Tax', 'Total', 'Invoice']
            df_filtered = hair_df[desired_columns]
            net_amount_idx = df_filtered.columns.get_loc('Net Amount')
            df_modified = df_filtered.copy()
            df_modified.insert(net_amount_idx + 1, 'Blank Col 1', [''] * len(df_modified))
            df_modified.insert(net_amount_idx + 2, 'Blank Col 2', [''] * len(df_modified))
            new_column_names = ['Date', 'ID', 'Name', 'Treatment Name', 'Doctors  Name', 'Total Amount', 'Base Value', 'Sgst', 'Cgst', 'Total inv', 'Invoice No']
            df_modified.columns = new_column_names

            df_modified['Base Value'] = pd.to_numeric(df_modified['Total inv'], errors='coerce') / 1.18
            df_modified['Sgst'] = df_modified['Base Value'] * 0.09
            df_modified['Cgst'] = df_modified['Base Value'] * 0.09
            df_modified['Base Value'] = df_modified['Base Value'].round(2)
            df_modified['Sgst'] = df_modified['Sgst'].round(2)
            df_modified['Cgst'] = df_modified['Cgst'].round(2)
            df_modified['Total Amount'] = df_modified['Base Value']
            
            # Change Doctors Name to Clinic only for consultation
            df_modified.loc[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False), 'Doctors  Name'] = 'Clinic'

            hair_output_path = os.path.join(output_directory, "Kalamassery_Hair.xlsx")
            df_modified.to_excel(hair_output_path, index=False)
            processed_files["Kalamassery_Hair"] = hair_output_path

        return processed_files

    elif branch == "Vedimara":
        receipt_df = pd.read_excel(receipt_file_path)
        receipt_df.rename(columns={'Pt Id': 'Pt ID'}, inplace=True)
        merged_df = pd.merge(df, receipt_df[['Pt ID', 'Notes']], on='Pt ID', how='left')
        
        merged_df['Notes_y'] = merged_df['Notes_y'].str.lower().str.strip()
        dental_df = merged_df[merged_df['Notes_y'] == 'dental'].copy()
        economy_df = merged_df[merged_df['Notes_y'] == 'economy'].copy()
        skin_df = merged_df[merged_df['Notes_y'] == 'skin'].copy()

        processed_files = {}

        # Process Dental
        if not dental_df.empty:
            # (Same as original logic)
            desired_columns = ['Date', 'Pt ID', 'Patient', 'Treatment Name', 'Doctor', 'Net Amount', 'Tax', 'Total', 'Invoice']
            df_filtered = dental_df[desired_columns]
            net_amount_idx = df_filtered.columns.get_loc('Net Amount')
            df_modified = df_filtered.copy()
            df_modified.insert(net_amount_idx + 1, 'Blank Col 1', [''] * len(df_modified))
            df_modified.insert(net_amount_idx + 2, 'Blank Col 2', [''] * len(df_modified))
            new_column_names = ['Date', 'ID', 'Name', 'Treatment Name', 'Doctors  Name', 'Total Amount', 'Base Value', 'Sgst', 'Cgst', 'Total inv', 'Invoice No']
            df_modified.columns = new_column_names

            consultation_df = df_modified[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
            consultation_df['Base Value'] = pd.to_numeric(consultation_df['Total inv'], errors='coerce') / 1.18
            consultation_df['Sgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Cgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Base Value'] = consultation_df['Base Value'].round(2)
            consultation_df['Sgst'] = consultation_df['Sgst'].round(2)
            consultation_df['Cgst'] = consultation_df['Cgst'].round(2)
            consultation_df['Total Amount'] = consultation_df['Base Value']
            consultation_df['Doctors  Name'] = 'Clinic'

            ortho_keywords = ['dental ortho bonding', 'ortho bonding new', 'debonding']
            ortho_pattern = '|'.join(ortho_keywords)
            ortho_bonding_df = df_modified[df_modified['Treatment Name'].str.contains(ortho_pattern, case=False, na=False)].copy()
            ortho_bonding_df['Base Value'] = pd.to_numeric(ortho_bonding_df['Total inv'], errors='coerce') / 1.05
            ortho_bonding_df['Sgst'] = ortho_bonding_df['Base Value'] * 0.025
            ortho_bonding_df['Cgst'] = ortho_bonding_df['Base Value'] * 0.025
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

            consultation_output_path = os.path.join(output_directory, "Vedimara_Dental_Consultation.xlsx")
            ortho_output_path = os.path.join(output_directory, "Vedimara_Dental_Ortho_Bonding.xlsx")
            rest_output_path = os.path.join(output_directory, "Vedimara_Dental_Rest.xlsx")
            consultation_df.to_excel(consultation_output_path, index=False)
            ortho_bonding_df.to_excel(ortho_output_path, index=False)
            rest_df.to_excel(rest_output_path, index=False)
            processed_files.update({
                "Vedimara_Dental_Consultation": consultation_output_path,
                "Vedimara_Dental_Ortho_Bonding": ortho_output_path,
                "Vedimara_Dental_Rest": rest_output_path
            })

        # Process Economy
        if not economy_df.empty:
            # (Same as original logic)
            desired_columns = ['Date', 'Pt ID', 'Patient', 'Treatment Name', 'Doctor', 'Net Amount', 'Tax', 'Total', 'Invoice']
            df_filtered = economy_df[desired_columns]
            net_amount_idx = df_filtered.columns.get_loc('Net Amount')
            df_modified = df_filtered.copy()
            df_modified.insert(net_amount_idx + 1, 'Blank Col 1', [''] * len(df_modified))
            df_modified.insert(net_amount_idx + 2, 'Blank Col 2', [''] * len(df_modified))
            new_column_names = ['Date', 'ID', 'Name', 'Treatment Name', 'Doctors  Name', 'Total Amount', 'Base Value', 'Sgst', 'Cgst', 'Total inv', 'Invoice No']
            df_modified.columns = new_column_names

            consultation_df = df_modified[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
            consultation_df['Base Value'] = pd.to_numeric(consultation_df['Total inv'], errors='coerce') / 1.18
            consultation_df['Sgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Cgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Base Value'] = consultation_df['Base Value'].round(2)
            consultation_df['Sgst'] = consultation_df['Sgst'].round(2)
            consultation_df['Cgst'] = consultation_df['Cgst'].round(2)
            consultation_df['Total Amount'] = consultation_df['Base Value']
            consultation_df['Doctors  Name'] = 'Clinic'

            ortho_keywords = ['dental ortho bonding', 'ortho bonding new', 'debonding']
            ortho_pattern = '|'.join(ortho_keywords)
            ortho_bonding_df = df_modified[df_modified['Treatment Name'].str.contains(ortho_pattern, case=False, na=False)].copy()
            ortho_bonding_df['Base Value'] = pd.to_numeric(ortho_bonding_df['Total inv'], errors='coerce') / 1.05
            ortho_bonding_df['Sgst'] = ortho_bonding_df['Base Value'] * 0.025
            ortho_bonding_df['Cgst'] = ortho_bonding_df['Base Value'] * 0.025
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

            consultation_output_path = os.path.join(output_directory, "Vedimara_Economy_Consultation.xlsx")
            ortho_output_path = os.path.join(output_directory, "Vedimara_Economy_Ortho_Bonding.xlsx")
            rest_output_path = os.path.join(output_directory, "Vedimara_Economy_Rest.xlsx")
            consultation_df.to_excel(consultation_output_path, index=False)
            ortho_bonding_df.to_excel(ortho_output_path, index=False)
            rest_df.to_excel(rest_output_path, index=False)
            processed_files.update({
                "Vedimara_Economy_Consultation": consultation_output_path,
                "Vedimara_Economy_Ortho_Bonding": ortho_output_path,
                "Vedimara_Economy_Rest": rest_output_path
            })

        # Process Skin
        if not skin_df.empty:
            desired_columns = ['Date', 'Pt ID', 'Patient', 'Treatment Name', 'Doctor', 'Net Amount', 'Tax', 'Total', 'Invoice']
            df_filtered = skin_df[desired_columns]
            net_amount_idx = df_filtered.columns.get_loc('Net Amount')
            df_modified = df_filtered.copy()
            df_modified.insert(net_amount_idx + 1, 'Blank Col 1', [''] * len(df_modified))
            df_modified.insert(net_amount_idx + 2, 'Blank Col 2', [''] * len(df_modified))
            new_column_names = ['Date', 'ID', 'Name', 'Treatment Name', 'Doctors  Name', 'Total Amount', 'Base Value', 'Sgst', 'Cgst', 'Total inv', 'Invoice No']
            df_modified.columns = new_column_names

            consultation_df = df_modified[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
            consultation_df['Base Value'] = pd.to_numeric(consultation_df['Total inv'], errors='coerce') / 1.18
            consultation_df['Sgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Cgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Base Value'] = consultation_df['Base Value'].round(2)
            consultation_df['Sgst'] = consultation_df['Sgst'].round(2)
            consultation_df['Cgst'] = consultation_df['Cgst'].round(2)
            consultation_df['Total Amount'] = consultation_df['Base Value']
            consultation_df['Doctors  Name'] = 'Clinic'

            other_treatments_df = df_modified[~df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
            other_treatments_df['Base Value'] = pd.to_numeric(other_treatments_df['Total inv'], errors='coerce') / 1.05
            other_treatments_df['Sgst'] = other_treatments_df['Base Value'] * 0.025
            other_treatments_df['Cgst'] = other_treatments_df['Base Value'] * 0.025
            other_treatments_df['Base Value'] = other_treatments_df['Base Value'].round(2)
            other_treatments_df['Sgst'] = other_treatments_df['Sgst'].round(2)
            other_treatments_df['Cgst'] = other_treatments_df['Cgst'].round(2)
            other_treatments_df['Total Amount'] = other_treatments_df['Base Value']
            
            consultation_output_path = os.path.join(output_directory, "Vedimara_Skin_Consultation.xlsx")
            other_output_path = os.path.join(output_directory, "Vedimara_Skin_Other.xlsx")
            consultation_df.to_excel(consultation_output_path, index=False)
            other_treatments_df.to_excel(other_output_path, index=False)
            processed_files.update({
                "Vedimara_Skin_Consultation": consultation_output_path,
                "Vedimara_Skin_Other": other_output_path
            })

        return processed_files

    elif branch == "Choondy":
        # Choondy branch logic
        # Split by 'Doctor' column
        skin_df = df[df['Doctor'] == 'Redhina Raj'].copy()
        dental_df = df[df['Doctor'] != 'Redhina Raj'].copy()

        processed_files = {}

        # Process Dental
        if not dental_df.empty:
            desired_columns = ['Date', 'Pt ID', 'Patient', 'Treatment Name', 'Doctor', 'Net Amount', 'Tax', 'Total', 'Invoice']
            df_filtered = dental_df[desired_columns]
            net_amount_idx = df_filtered.columns.get_loc('Net Amount')
            df_modified = df_filtered.copy()
            df_modified.insert(net_amount_idx + 1, 'Blank Col 1', [''] * len(df_modified))
            df_modified.insert(net_amount_idx + 2, 'Blank Col 2', [''] * len(df_modified))
            new_column_names = ['Date', 'ID', 'Name', 'Treatment Name', 'Doctors  Name', 'Total Amount', 'Base Value', 'Sgst', 'Cgst', 'Total inv', 'Invoice No']
            df_modified.columns = new_column_names

            consultation_df = df_modified[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
            consultation_df['Base Value'] = pd.to_numeric(consultation_df['Total inv'], errors='coerce') / 1.18
            consultation_df['Sgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Cgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Base Value'] = consultation_df['Base Value'].round(2)
            consultation_df['Sgst'] = consultation_df['Sgst'].round(2)
            consultation_df['Cgst'] = consultation_df['Cgst'].round(2)
            consultation_df['Total Amount'] = consultation_df['Base Value']
            consultation_df['Doctors  Name'] = 'Clinic'

            ortho_keywords = ['dental ortho bonding', 'ortho bonding new', 'debonding']
            ortho_pattern = '|'.join(ortho_keywords)
            ortho_bonding_df = df_modified[df_modified['Treatment Name'].str.contains(ortho_pattern, case=False, na=False)].copy()
            ortho_bonding_df['Base Value'] = pd.to_numeric(ortho_bonding_df['Total inv'], errors='coerce') / 1.05
            ortho_bonding_df['Sgst'] = ortho_bonding_df['Base Value'] * 0.025
            ortho_bonding_df['Cgst'] = ortho_bonding_df['Base Value'] * 0.025
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

            consultation_output_path = os.path.join(output_directory, "Choondy_Dental_Consultation.xlsx")
            ortho_output_path = os.path.join(output_directory, "Choondy_Dental_Ortho_Bonding.xlsx")
            rest_output_path = os.path.join(output_directory, "Choondy_Dental_Rest.xlsx")
            consultation_df.to_excel(consultation_output_path, index=False)
            ortho_bonding_df.to_excel(ortho_output_path, index=False)
            rest_df.to_excel(rest_output_path, index=False)
            processed_files.update({
                "Choondy_Dental_Consultation": consultation_output_path,
                "Choondy_Dental_Ortho_Bonding": ortho_output_path,
                "Choondy_Dental_Rest": rest_output_path
            })

        # Process Skin
        if not skin_df.empty:
            desired_columns = ['Date', 'Pt ID', 'Patient', 'Treatment Name', 'Doctor', 'Net Amount', 'Tax', 'Total', 'Invoice']
            df_filtered = skin_df[desired_columns]
            net_amount_idx = df_filtered.columns.get_loc('Net Amount')
            df_modified = df_filtered.copy()
            df_modified.insert(net_amount_idx + 1, 'Blank Col 1', [''] * len(df_modified))
            df_modified.insert(net_amount_idx + 2, 'Blank Col 2', [''] * len(df_modified))
            new_column_names = ['Date', 'ID', 'Name', 'Treatment Name', 'Doctors  Name', 'Total Amount', 'Base Value', 'Sgst', 'Cgst', 'Total inv', 'Invoice No']
            df_modified.columns = new_column_names

            consultation_df = df_modified[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
            consultation_df['Base Value'] = pd.to_numeric(consultation_df['Total inv'], errors='coerce') / 1.18
            consultation_df['Sgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Cgst'] = consultation_df['Base Value'] * 0.09
            consultation_df['Base Value'] = consultation_df['Base Value'].round(2)
            consultation_df['Sgst'] = consultation_df['Sgst'].round(2)
            consultation_df['Cgst'] = consultation_df['Cgst'].round(2)
            consultation_df['Total Amount'] = consultation_df['Base Value']
            consultation_df['Doctors  Name'] = 'Clinic'

            other_treatments_df = df_modified[~df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
            other_treatments_df['Base Value'] = pd.to_numeric(other_treatments_df['Total inv'], errors='coerce') / 1.05
            other_treatments_df['Sgst'] = other_treatments_df['Base Value'] * 0.025
            other_treatments_df['Cgst'] = other_treatments_df['Base Value'] * 0.025
            other_treatments_df['Base Value'] = other_treatments_df['Base Value'].round(2)
            other_treatments_df['Sgst'] = other_treatments_df['Sgst'].round(2)
            other_treatments_df['Cgst'] = other_treatments_df['Cgst'].round(2)
            other_treatments_df['Total Amount'] = other_treatments_df['Base Value']
            
            consultation_output_path = os.path.join(output_directory, "Choondy_Skin_Consultation.xlsx")
            other_output_path = os.path.join(output_directory, "Choondy_Skin_Other.xlsx")
            consultation_df.to_excel(consultation_output_path, index=False)
            other_treatments_df.to_excel(other_output_path, index=False)
            processed_files.update({
                "Choondy_Skin_Consultation": consultation_output_path,
                "Choondy_Skin_Other": other_output_path
            })

        return processed_files

    else: # Original logic for Aluva and other branches
        # 2. Keep only the specified columns
        desired_columns = ['Date', 'Pt ID', 'Patient', 'Treatment Name', 'Doctor', 'Net Amount', 'Tax', 'Total', 'Invoice']
        df_filtered = df[desired_columns]

        # 3. Insert two blank columns between 'Net Amount' and 'Tax'
        net_amount_idx = df_filtered.columns.get_loc('Net Amount')
        df_modified = df_filtered.copy()
        df_modified.insert(net_amount_idx + 1, 'Blank Col 1', [''] * len(df_modified))
        df_modified.insert(net_amount_idx + 2, 'Blank Col 2', [''] * len(df_modified))

        # Rename columns
        new_column_names = ['Date', 'ID', 'Name', 'Treatment Name', 'Doctors  Name', 'Total Amount', 'Base Value', 'Sgst', 'Cgst', 'Total inv', 'Invoice No']
        df_modified.columns = new_column_names

        # 4. Split the data into three new Excel files based on 'Treatment Name'
        consultation_df = df_modified[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()
        consultation_df['Base Value'] = pd.to_numeric(consultation_df['Total inv'], errors='coerce') / 1.18
        consultation_df['Sgst'] = consultation_df['Base Value'] * 0.09
        consultation_df['Cgst'] = consultation_df['Base Value'] * 0.09
        consultation_df['Base Value'] = consultation_df['Base Value'].round(2)
        consultation_df['Sgst'] = consultation_df['Sgst'].round(2)
        consultation_df['Cgst'] = consultation_df['Cgst'].round(2)
        consultation_df['Total Amount'] = consultation_df['Base Value']
        consultation_df['Doctors  Name'] = 'Clinic'

        ortho_keywords = ['dental ortho bonding', 'ortho bonding new', 'debonding']
        ortho_pattern = '|'.join(ortho_keywords)
        ortho_bonding_df = df_modified[df_modified['Treatment Name'].str.contains(ortho_pattern, case=False, na=False)].copy()
        ortho_bonding_df['Base Value'] = pd.to_numeric(ortho_bonding_df['Total inv'], errors='coerce') / 1.05
        ortho_bonding_df['Sgst'] = ortho_bonding_df['Base Value'] * 0.025
        ortho_bonding_df['Cgst'] = ortho_bonding_df['Base Value'] * 0.025
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

        consultation_output_path = os.path.join(output_directory, "Treatments_Done_Consultation.xlsx")
        ortho_output_path = os.path.join(output_directory, "Treatments_Done_Ortho_Bonding.xlsx")
        rest_output_path = os.path.join(output_directory, "Treatments_Done_Rest.xlsx")
        consultation_df.to_excel(consultation_output_path, index=False)
        ortho_bonding_df.to_excel(ortho_output_path, index=False)
        rest_df.to_excel(rest_output_path, index=False)

        return {
            "consultation_path": consultation_output_path,
            "ortho_path": ortho_output_path,
            "rest_path": rest_output_path
        }

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
