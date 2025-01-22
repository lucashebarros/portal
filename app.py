import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
TENANT_ID = os.getenv('TENANT_ID')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# Função para obter o Access Token
def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        'client_id': CLIENT_ID,
        'scope': 'https://analysis.windows.net/powerbi/api/.default',
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=data)
    try:
        response.raise_for_status()
        token = response.json()['access_token']
        st.write("Access Token Obtido: ", token)  # Log do Access Token
        return token
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
        st.write(response.text)  # Log da resposta do erro
    except Exception as err:
        st.error(f"Other error occurred: {err}")
        st.write(response.text)  # Log da resposta do erro

# Função para obter os Workspaces
def get_workspaces(access_token):
    url = "https://api.powerbi.com/v1.0/myorg/groups"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        st.write("Resposta da API de Workspaces: ", response.json())  # Log da Resposta da API
        return response.json()['value']
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
        st.write(response.text)  # Log da resposta do erro
    except Exception as err:
        st.error(f"Other error occurred: {err}")
        st.write(response.text)  # Log da resposta do erro

# Função para obter os Relatórios
def get_reports(access_token, workspace_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()['value']
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
        st.write(response.text)  # Log da resposta do erro
    except Exception as err:
        st.error(f"Other error occurred: {err}")
        st.write(response.text)  # Log da resposta do erro

# Função para gerar o Embed Token
def generate_embed_token(access_token, group_id, report_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}/GenerateToken"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'accessLevel': 'View'
    }
    response = requests.post(url, headers=headers, json=data)
    try:
        response.raise_for_status()
        return response.json()['token']
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
        st.write(response.text)  # Log da resposta do erro
    except Exception as err:
        st.error(f"Other error occurred: {err}")
        st.write(response.text)  # Log da resposta do erro

# Interface do Streamlit
def main():
    st.title("Portal de Dashboards")
    
    # Login Simples
    st.sidebar.header("Login")
    usuario = st.sidebar.text_input("Usuário")
    senha = st.sidebar.text_input("Senha", type='password')
    
    if st.sidebar.button("Entrar"):
        if usuario == 'admin' and senha == '1234':
            st.sidebar.success("Login realizado com sucesso!")
            
            access_token = get_access_token()
            
            if access_token:
                # Seleção de Workspace
                workspaces = get_workspaces(access_token)
                if workspaces:
                    workspace_names = [ws['name'] for ws in workspaces]
                    workspace_choice = st.selectbox("Selecione o Workspace", workspace_names)
                    workspace_id = workspaces[workspace_names.index(workspace_choice)]['id']
                    
                    # Seleção de Relatório
                    reports = get_reports(access_token, workspace_id)
                    if reports:
                        report_names = [report['name'] for report in reports]
                        report_choice = st.selectbox("Selecione o Relatório", report_names)
                        report_id = reports[report_names.index(report_choice)]['id']
                        
                        if st.button("Embutir Relatório"):
                            embed_token = generate_embed_token(access_token, workspace_id, report_id)
                            embed_url = f"https://app.powerbi.com/reportEmbed?reportId={report_id}&groupId={workspace_id}"
                            
                            # Exibir Relatório Embutido
                            st.markdown(f"""
                            <iframe width="100%" height="800" src="{embed_url}&access_token={embed_token}" frameborder="0" allowfullscreen></iframe>
                            """, unsafe_allow_html=True)
        else:
            st.sidebar.error("Usuário ou senha incorretos.")

if __name__ == "__main__":
    main()
