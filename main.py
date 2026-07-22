import os
import pandas as pd
import warnings
from datetime import datetime
from app.db import get_overdue_mechanics, get_mechanic_details

warnings.filterwarnings('ignore')
from app.pdf_generator import generate_pdf
from app.drive_integration import get_drive_service, create_drive_folder, upload_file_to_drive
from app.utils import download_file

# TODO: REPLACE WITH YOUR ACTUAL GOOGLE DRIVE MAIN FOLDER ID
ROOT_DRIVE_FOLDER_ID = '0ACuChpZKhJIXUk9PVA'

def main():
    print("Iniciando processo de cobrança...")
    
    # Ensure images folder exists
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    print("Trazendo os dados do CSV")

    df_csv = pd.read_csv('/Users/francisconicasio/Desktop/Cobranza-Fisica/base_oficinas.csv')

    print(f"Linhas do CSV: {len(df_csv)}\n")

    print("Conectando ao Redshift para obter lista de mecânicas inadimplentes...")
    uid_list = df_csv['UID'].dropna().astype(str).tolist()
    
    try:
        df_mechanics = get_overdue_mechanics(uid_list)
    except Exception as e:
        print(f"Erro ao consultar Redshift: {e}")
        return

    total_clients = len(df_mechanics)
    print(f"Total a processar: {total_clients} clientes.")
    
    try:
        drive_service = get_drive_service()
    except Exception as e:
        print(f"Erro ao conectar com Google Drive: {e}")
        return
        
    tracking_data = []
    
    ten_percent = max(1, total_clients // 10)

    for index, row in df_mechanics.iterrows():
        uid = row['mechanic_office_uid']
        name = row['mechanic_office_name']
        invoices_count = row['invoices']
        overdue_amount = row['overdue_amount']
        cnpj = row['cnpj']
        address = row['address']
        zip_code = row['zip_code']
        email = row['contact_email']
        
        if (index + 1) % ten_percent == 0 or (index + 1) == total_clients:
            progress = ((index + 1) / total_clients) * 100
            print(f"Progresso: {progress:.0f}% ({index + 1}/{total_clients}) concluído...")
        
        try:
            df_details = get_mechanic_details(uid)
        except Exception as e:
            print(f"Erro ao consultar Postgres para UID {uid}: {e}")
            continue
            
        if df_details.empty:
            print(f"Sem detalhes no Postgres para {name}. Pulando.")
            continue
            
        # Create Document (PDF)
        pdf_filename = f"Notificacao_Extrajudicial_{str(name).replace(' ', '_').replace('/', '_')}.pdf"
        pdf_path = os.path.join(os.path.dirname(__file__), pdf_filename)
        generate_pdf(name, cnpj, address, zip_code, email, overdue_amount, invoices_count, df_details, pdf_path)
        
        # Create Drive Folder
        folder_name = f"{name} - {datetime.now().strftime('%Y-%m-%d')}"
        folder_id = create_drive_folder(drive_service, folder_name, ROOT_DRIVE_FOLDER_ID)
        
        # Upload Document
        upload_file_to_drive(drive_service, pdf_path, pdf_filename, folder_id)
        os.remove(pdf_path) # Clean up local document
                    
        # Add to tracking dataframe list
        tracking_data.append({
            'Nome_Cliente': name,
            'UID': uid,
            'Carpeta_Criada': folder_name,
            'Data_Criacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Link_Pasta_Drive': f"https://drive.google.com/drive/folders/{folder_id}"
        })
        
    # Save Tracking CSV
    if tracking_data:
        df_tracking = pd.DataFrame(tracking_data)
        csv_filename = f"Seguimento_Cobranza_Offline.csv"
        df_tracking.to_csv(csv_filename, index=False)
        print(f"Processo finalizado. Planilha gerada: {csv_filename}")
    else:
        print("Nenhum cliente processado com sucesso.")

if __name__ == '__main__':
    main()
