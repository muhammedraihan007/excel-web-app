import os
import uuid
from flask import Blueprint, render_template, request, send_from_directory, current_app, redirect, url_for
import pandas as pd

sales_blueprint = Blueprint('sales', __name__)

UPLOAD_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

def process_excel_file_logic(input_file_path: str, output_directory: str):
    # 1. Read the Excel file
    df = pd.read_excel(input_file_path)

    # 2. Keep only the specified columns
    desired_columns = ['Date', 'Pt ID', 'Patient', 'Treatment Name', 'Doctor', 'Net Amount', 'Tax', 'Total', 'Invoice']
    df_filtered = df[desired_columns]

    # 3. Insert two blank columns between 'Net Amount' and 'Tax'
    # Find the index of 'Net Amount'
    net_amount_idx = df_filtered.columns.get_loc('Net Amount')

    # Create two empty columns
    blank_col_1 = [''] * len(df_filtered)
    blank_col_2 = [''] * len(df_filtered)

    # Insert the blank columns
    df_modified = df_filtered.copy() # Work on a copy to avoid SettingWithCopyWarning
    df_modified.insert(net_amount_idx + 1, 'Blank Col 1', blank_col_1)
    df_modified.insert(net_amount_idx + 2, 'Blank Col 2', blank_col_2)

    # Rename columns
    new_column_names = ['Date', 'ID', 'Name', 'Treatment Name', 'Doctors  Name', 'Total Amount', 'Base Value', 'Sgst', 'Cgst', 'Total inv', 'Invoice No']
    df_modified.columns = new_column_names

    # 4. Split the data into three new Excel files based on 'Treatment Name'
    # For 'consultation'
    consultation_df = df_modified[df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)].copy()

    # Calculations for consultation_df
    consultation_df['Base Value'] = pd.to_numeric(consultation_df['Total inv'], errors='coerce') / 1.18
    consultation_df['Sgst'] = consultation_df['Base Value'] * 0.09
    consultation_df['Cgst'] = consultation_df['Base Value'] * 0.09

    consultation_df['Base Value'] = consultation_df['Base Value'].round(2)
    consultation_df['Sgst'] = consultation_df['Sgst'].round(2)
    consultation_df['Cgst'] = consultation_df['Cgst'].round(2)

    consultation_df['Total Amount'] = consultation_df['Base Value']
    consultation_df['Doctors  Name'] = 'Clinic'


    # For 'Ortho Bonding' related treatments
    ortho_keywords = ['dental ortho bonding', 'ortho bonding new', 'debonding']
    ortho_pattern = '|'.join(ortho_keywords)
    ortho_bonding_df = df_modified[df_modified['Treatment Name'].str.contains(ortho_pattern, case=False, na=False)].copy()

    # Calculations for ortho_bonding_df
    ortho_bonding_df['Base Value'] = pd.to_numeric(ortho_bonding_df['Total inv'], errors='coerce') / 1.05
    ortho_bonding_df['Sgst'] = ortho_bonding_df['Base Value'] * 0.025
    ortho_bonding_df['Cgst'] = ortho_bonding_df['Base Value'] * 0.025

    ortho_bonding_df['Base Value'] = ortho_bonding_df['Base Value'].round(2)
    ortho_bonding_df['Sgst'] = ortho_bonding_df['Sgst'].round(2)
    ortho_bonding_df['Cgst'] = ortho_bonding_df['Cgst'].round(2)

    ortho_bonding_df['Total Amount'] = ortho_bonding_df['Base Value']

    # For the rest
    # Create boolean masks for each condition
    consultation_mask = df_modified['Treatment Name'].str.contains('consultation', case=False, na=False)
    ortho_mask = df_modified['Treatment Name'].str.contains(ortho_pattern, case=False, na=False)

    # Combine the masks to find all rows that match either condition
    matched_rows_mask = consultation_mask | ortho_mask

    # Select rows that do NOT match either condition
    rest_df = df_modified[~matched_rows_mask].copy()

    # Remove the summary row (e.g., "Count: 7 6090 6090")
    rest_df = rest_df[~rest_df['Date'].astype(str).str.contains('Count:', case=False, na=False)]

    # Clear columns for rest_df
    rest_df['Base Value'] = ''
    rest_df['Sgst'] = ''
    rest_df['Cgst'] = ''


    # 5. Save these separate DataFrames into new Excel files
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

@sales_blueprint.route('/sales', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'excel_file' not in request.files:
            return render_template('sales_upload.html', error='No file part')
        file = request.files['excel_file']
        if file.filename == '':
            return render_template('sales_upload.html', error='No selected file')
        if file and file.filename.endswith(('.xlsx', '.xls')):
            filename = f"{uuid.uuid4()}.xlsx"
            upload_file_path = os.path.join(UPLOAD_DIRECTORY, filename)
            os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
            file.save(upload_file_path)
            
            try:
                processed_files = process_excel_file_logic(upload_file_path, UPLOAD_DIRECTORY)
                os.remove(upload_file_path)

                download_links = {}
                for key, path in processed_files.items():
                    filename = os.path.basename(path)
                    download_links[key] = url_for('sales.download_file', filename=filename)

                return render_template('sales_upload.html', download_links=download_links, message='File processed successfully!')
            except Exception as e:
                if os.path.exists(upload_file_path):
                    os.remove(upload_file_path)
                return render_template('sales_upload.html', error=f"Error processing Excel file: {e}")
    return render_template('sales_upload.html')

@sales_blueprint.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_DIRECTORY, filename, as_attachment=True)