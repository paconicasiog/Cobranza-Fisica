import os
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright

def format_document(doc):
    if not doc: return ""
    doc_clean = ''.join(filter(str.isdigit, str(doc)))
    if len(doc_clean) == 11:
        return f"{doc_clean[:3]}.{doc_clean[3:6]}.{doc_clean[6:9]}-{doc_clean[9:]}"
    elif len(doc_clean) == 14:
        return f"{doc_clean[:2]}.{doc_clean[2:5]}.{doc_clean[5:8]}/{doc_clean[8:12]}-{doc_clean[12:]}"
    return doc

def generate_pdf(client_name, cnpj, address, zip_code, email, total_amount, invoice_count, df_details, output_path):
    # Generates an HTML document that matches the extrajudicial notification design
    
    # Generate table rows
    table_rows = ""
    today = pd.to_datetime('today').normalize()
    nfs_list = []
    
    for index, row in df_details.iterrows():
        uid = str(row['expected_payment_id'])
        uid_short = uid[:15] + "..." if len(uid) > 15 else uid
        
        due_date = pd.to_datetime(row['due_date'])
        
        delay_days = (today - due_date).days
        if delay_days < 0: delay_days = 0
        
        valor = float(row['amount'])
        table_rows += f"""
        <tr>
            <td>{uid_short}</td>
            <td>{due_date.strftime('%d/%m/%Y')}</td>
            <td>{delay_days}</td>
            <td>R$ {valor:.2f}</td>
        </tr>"""
        
    formatted_cnpj = format_document(cnpj)
        
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            margin: 20mm;
        }}
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #ffffff;
            color: #000000;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            background-color: #ffffff;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #4A63E6;
            margin: 0;
            font-size: 48px;
            letter-spacing: 10px;
            font-weight: bold;
        }}
        .date-section {{
            text-align: right;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        .title {{
            text-align: center;
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 40px;
        }}
        .content {{
            font-size: 14px;
            line-height: 1.5;
            text-align: justify;
        }}
        .content p {{
            margin-bottom: 20px;
        }}
        .content strong {{
            font-weight: bold;
        }}
        .subject {{
            margin-top: 30px;
            margin-bottom: 20px;
            font-weight: bold;
        }}
        .salutation {{
            margin-bottom: 20px;
        }}
        .indent {{
            text-indent: 40px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            font-size: 13px;
        }}
        th, td {{
            border: 1px solid #000000;
            padding: 8px;
            text-align: center;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        .signature-section {{
            text-align: center;
            margin-top: 50px;
            margin-bottom: 50px;
            page-break-inside: avoid;
        }}
        .signature-name {{
            font-weight: bold;
        }}
        .footer-page-break {{
            page-break-before: always;
            padding-top: 20px;
        }}
        .qr-section {{
            margin-top: 30px;
            text-align: center;
            padding: 30px;
            border-top: 2px dashed #cccccc;
            page-break-inside: avoid;
        }}
        .qr-container {{
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }}
        .qr-box {{
            width: 45%;
        }}
        .qr-box h2 {{
            color: #4A63E6;
            font-size: 16px;
            margin-bottom: 10px;
        }}
        .qr-box p {{
            font-size: 12px;
            margin-bottom: 15px;
            height: 40px;
        }}
        .qr-image {{
            width: 130px;
            height: 130px;
            margin: 0 auto;
        }}
        .contact-info {{
            margin-top: 15px;
            font-size: 14px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>M E C A N I Z O U</h1>
        </div>
        
        <div class="date-section">
            São Paulo, {datetime.now().strftime('%d/%m/%Y')}.
        </div>
        
        <div class="title">
            NOTIFICAÇÃO EXTRAJUDICIAL
        </div>
        
        <div class="content">
            <p>
                <strong>Notificada: {client_name}</strong>, pessoa jurídica de direito privado, inscrita no CNPJ sob o n. {formatted_cnpj}, com sede na {address}, {zip_code}.<br>
                Endereço eletrônico: {email}.
            </p>
            
            <p>
                <strong>Notificante: MECANIZOU INTERMEDIAÇÃO DE NEGÓCIOS LTDA.</strong>, pessoa jurídica de direito privado, inscrita no CNPJ sob o nº 37.199.406/0001-55, com sede na Rua Ezequiel Freire, nº 55, Térreo, Santana, São Paulo/SP, CEP: 02034-000 (“<strong>Mecanizou</strong>”).
            </p>
            
            <div class="subject">
                Assunto: REGULARIZAÇÃO DE DÉBITO
            </div>
            
            <div class="salutation">
                Prezados senhores,
            </div>
            
            <p class="indent">
                Enquanto advogado e bastante procurador da Notificante, <strong>Mecanizou</strong>, sirvo-me da presente para <strong>NOTIFICÁ-LOS</strong> formalmente acerca da <strong>existência de débito pendente</strong>, decorrente da aquisição de produtos fornecidos pela notificante.
            </p>
            
            <p class="indent">
                Após levantamento e conferência dos títulos relacionados às operações comerciais realizadas entre as partes, foi apurado débito no valor total de <strong>R$ {float(total_amount):.2f}</strong>.
            </p>
            
            <p class="indent">
                Portanto, a Notificada é responsável pelo pagamento de <strong>{invoice_count} boleto(s) vencido(s)</strong>, correspondentes às prestações descritas nos respectivos títulos de cobrança, no valor total informado acima.
            </p>
            
            <p class="indent">
                Cumpre destacar que, na tentativa de solução amigável da pendência, o time da notificante têm atuado no contato com diversas áreas e pessoas da notificada sobre o tema, enviando todos os documentos quando solicitados, contudo, ainda seguimos sem avanços concretos ou uma data definida para o pagamento.
            </p>
            
            <p class="indent">
                Diante disso, ficam V.Sas. <strong>NOTIFICADOS</strong> para que, no prazo improrrogável de 24 (vinte e quatro) horas, contadas do recebimento desta notificação, procedam ao cumprimento com as obrigações de pagamento.
            </p>
            
            <p class="indent">
                Fica desde já consignado que, caso não haja o pagamento ou retorno válido dentro do prazo acima estipulado, considerar-se-á definitivamente frustrada a tentativa de composição amigável, ficando a notificante autorizada a adotar imediatamente as medidas extrajudiciais e judiciais cabíveis para satisfação do crédito, inclusive com protesto, negativação ou ingresso da competente ação judicial para cobrança, acrescido de correção monetária, juros, multa contratual e honorários advocatícios.
            </p>
            
            <p class="indent">
                A presente notificação tem por finalidade constituir formalmente os devedores em mora e oportunizar a última tentativa de solução extrajudicial, antes da adoção das medidas judiciais cabíveis.
            </p>
            
            <p>Listagem dos boletos</p>
            
            <table>
                <thead>
                    <tr>
                        <th>ID Boleto</th>
                        <th>Vencimento</th>
                        <th>Dias Atraso</th>
                        <th>Valor (R$)</th>
                    </tr>
                </thead>
                <tbody>{table_rows}
                </tbody>
            </table>
            
            <p style="text-align: center; margin-top: 40px;">Sem mais para o momento.</p>
            <p style="text-align: center;">Atenciosamente.</p>
            
            <div class="signature-section">
                <div class="signature-name">Caio Paixão</div>
                <div>OAB/SP n° 419.742</div>
                <div class="signature-name">CAIO PAIXAO SOCIEDADE INDIVIDUAL DE ADVOCACIA</div>
            </div>
            
            <!-- Page break for the QR Code and contact section -->
            <div class="footer-page-break"></div>
            
            <div class="qr-section">
                <div class="qr-container">
                    <div class="qr-box">
                        <h2>Área do Mecânico</h2>
                        <p>Escaneie o QR Code abaixo para acessar a Área do Mecânico e regularizar sua situação.</p>
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&color=0050B3&data=https://app.mecanizou.com/vencimentos" alt="QR Code Site" class="qr-image">
                    </div>
                    
                    <div class="qr-box">
                        <h2>Fale Conosco</h2>
                        <p>Precisa de ajuda ou quer negociar? Contate nossa equipe pelo WhatsApp.</p>
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&color=0050B3&data=https://wa.me/551150398151" alt="QR Code WhatsApp" class="qr-image">
                        <div class="contact-info">
                            <span style="color: #0050B3; font-size: 16px;">+55 11 5039-8151</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content)
        page.pdf(path=output_path, format="A4", print_background=True)
        browser.close()
