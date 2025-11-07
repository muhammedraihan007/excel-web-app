import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd

# Import the blueprint
from sales_blueprint import sales_blueprint

app_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(app_dir, 'uploads')
CLEANED_FOLDER = os.path.join(app_dir, 'cleaned_files')
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CLEANED_FOLDER'] = CLEANED_FOLDER


# Register the blueprint
app.register_blueprint(sales_blueprint, url_prefix='/sales')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_receipt_dataframe(df, bank_name, original_filename):
    df = df.copy() # Explicitly work on a copy to avoid SettingWithCopyWarning
    columns_to_keep = ['Date', 'Pt Id', 'Patient', 'Amount', 'Paid By']
    existing_columns = [col for col in columns_to_keep if col in df.columns]
    df = df[existing_columns]
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        df['Date'] = df['Date'].dt.strftime('%d-%m-%Y')
    df.dropna(subset=existing_columns, inplace=True)

    card_df = None
    if 'Paid By' in df.columns and 'Card' in df['Paid By'].unique():
        card_df = df[df['Paid By'] == 'Card'].copy()
        df = df[df['Paid By'] != 'Card']
        card_df['Paid By'] = card_df['Paid By'].replace({'Card': bank_name})

    if 'Paid By' in df.columns:
        df['Paid By'] = df['Paid By'].replace({'Cash': 'Cash Collection', 'Wallet': bank_name})

    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'Receipt Template - dental - g pay..xlsx')
    template_df = pd.read_excel(template_path)
    new_headers = template_df.columns.tolist()

    df.columns = new_headers[:len(df.columns)]

    cleaned_filename = f"cleaned_{original_filename}"
    cleaned_file_path = os.path.join(app.config['CLEANED_FOLDER'], cleaned_filename)
    df.to_excel(cleaned_file_path, index=False)

    card_cleaned_filename = None
    if card_df is not None:
        card_df.columns = new_headers[:len(card_df.columns)]
        card_cleaned_filename = f"card_cleaned_{original_filename}"
        card_cleaned_file_path = os.path.join(app.config['CLEANED_FOLDER'], card_cleaned_filename)
        card_df.to_excel(card_cleaned_file_path, index=False)

    return cleaned_filename, card_cleaned_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/payments')
def payments():
    return render_template('payments.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        df = pd.read_excel(file_path)
        bank_name = request.form.get('bank')
        branch = request.form.get('branch')

        if branch == 'Kalamassery':
            if 'Notes' not in df.columns:
                return render_template('payments.html', error='The uploaded file for Kalamassery branch is missing the \'Notes\' column.')
            
            dental_df = df[df['Notes'].str.contains('dental', case=False, na=False)].copy()
            skin_df = df[df['Notes'].str.contains('skin', case=False, na=False)].copy()
            hair_df = df[df['Notes'].str.contains('hair', case=False, na=False)].copy()

            download_links = {}

            if not dental_df.empty:
                cleaned_filename, card_cleaned_filename = process_receipt_dataframe(dental_df, bank_name, f"Kalamassery_Dental_{filename}")
                download_links['Kalamassery_Dental'] = url_for('download_file', filename=cleaned_filename)
                if card_cleaned_filename:
                    download_links['Kalamassery_Dental_Card'] = url_for('download_file', filename=card_cleaned_filename)
            
            if not skin_df.empty:
                cleaned_filename, card_cleaned_filename = process_receipt_dataframe(skin_df, bank_name, f"Kalamassery_Skin_{filename}")
                download_links['Kalamassery_Skin'] = url_for('download_file', filename=cleaned_filename)
                if card_cleaned_filename:
                    download_links['Kalamassery_Skin_Card'] = url_for('download_file', filename=card_cleaned_filename)

            if not hair_df.empty:
                cleaned_filename, card_cleaned_filename = process_receipt_dataframe(hair_df, bank_name, f"Kalamassery_Hair_{filename}")
                download_links['Kalamassery_Hair'] = url_for('download_file', filename=cleaned_filename)
                if card_cleaned_filename:
                    download_links['Kalamassery_Hair_Card'] = url_for('download_file', filename=card_cleaned_filename)

            return render_template('download.html', download_links=download_links, message='File processed successfully!')

        elif branch == 'Vedimara':
            if 'Notes' not in df.columns:
                return render_template('payments.html', error='The uploaded file for Vedimara branch is missing the \'Notes\' column.')
            
            dental_df = df[df['Notes'].str.contains('dental', case=False, na=False)].copy()
            skin_df = df[df['Notes'].str.contains('skin', case=False, na=False)].copy()
            economy_df = df[df['Notes'].str.contains('economy', case=False, na=False)].copy()

            download_links = {}

            if not dental_df.empty:
                cleaned_filename, card_cleaned_filename = process_receipt_dataframe(dental_df, bank_name, f"Vedimara_Dental_{filename}")
                download_links['Vedimara_Dental'] = url_for('download_file', filename=cleaned_filename)
                if card_cleaned_filename:
                    download_links['Vedimara_Dental_Card'] = url_for('download_file', filename=card_cleaned_filename)
            
            if not skin_df.empty:
                cleaned_filename, card_cleaned_filename = process_receipt_dataframe(skin_df, bank_name, f"Vedimara_Skin_{filename}")
                download_links['Vedimara_Skin'] = url_for('download_file', filename=cleaned_filename)
                if card_cleaned_filename:
                    download_links['Vedimara_Skin_Card'] = url_for('download_file', filename=card_cleaned_filename)

            if not economy_df.empty:
                cleaned_filename, card_cleaned_filename = process_receipt_dataframe(economy_df, bank_name, f"Vedimara_Economy_{filename}")
                download_links['Vedimara_Economy'] = url_for('download_file', filename=cleaned_filename)
                if card_cleaned_filename:
                    download_links['Vedimara_Economy_Card'] = url_for('download_file', filename=card_cleaned_filename)

            return render_template('download.html', download_links=download_links, message='File processed successfully!')

        elif branch == 'Choondy':
            if 'Notes' not in df.columns:
                return render_template('payments.html', error='The uploaded file for Choondy branch is missing the \'Notes\' column.')
            
            dental_df = df[df['Notes'].str.contains('dental', case=False, na=False)].copy()
            skin_hair_df = df[df['Notes'].str.contains('skin|hair', case=False, na=False)].copy()

            download_links = {}

            if not dental_df.empty:
                cleaned_filename, card_cleaned_filename = process_receipt_dataframe(dental_df, bank_name, f"Choondy_Dental_{filename}")
                download_links['Choondy_Dental'] = url_for('download_file', filename=cleaned_filename)
                if card_cleaned_filename:
                    download_links['Choondy_Dental_Card'] = url_for('download_file', filename=card_cleaned_filename)
            
            if not skin_hair_df.empty:
                cleaned_filename, card_cleaned_filename = process_receipt_dataframe(skin_hair_df, bank_name, f"Choondy_Skin_Hair_{filename}")
                download_links['Choondy_Skin_Hair'] = url_for('download_file', filename=cleaned_filename)
                if card_cleaned_filename:
                    download_links['Choondy_Skin_Hair_Card'] = url_for('download_file', filename=card_cleaned_filename)

            return render_template('download.html', download_links=download_links, message='File processed successfully!')

        else: # Default Aluva logic
            cleaned_filename, card_cleaned_filename = process_receipt_dataframe(df, bank_name, filename)
            return render_template('download.html', cleaned_filename=cleaned_filename, card_cleaned_filename=card_cleaned_filename)


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['CLEANED_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)