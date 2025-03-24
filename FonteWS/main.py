import customtkinter as ctk
from tkinter import ttk
import asyncpg
import asyncio
import threading
# Configuração da janela principal

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.title("WareSearch")
root.iconbitmap(r"Ware.click.ico")
root.geometry("1000x500")

loop = asyncio.new_event_loop()
def iniciar_loop_asyncio():
    """Inicia o loop asyncio em uma thread separada"""
    asyncio.set_event_loop(loop)
    loop.run_forever()

thread_asyncio = threading.Thread(target=iniciar_loop_asyncio, daemon=True)
thread_asyncio.start()

# Variáveis globais para armazenar todas as integrações carregadas
todas_integracoes = []

async def conectar_banco():
    """Conecta ao banco de dados PostgreSQL"""
    return await asyncpg.connect(
        user="wareline_integracoes", password="War&lin$2025@", database="teste;", host="44.207.38.121"
    )

async def carregar_dados():
    """Carrega todos os clientes e todas as integrações"""
    global todas_integracoes

    try:
        conn = await conectar_banco()

        # Carrega clientes
        query_clientes = "SELECT codigo, nome FROM clientes ORDER BY nome"
        rows_clientes = await conn.fetch(query_clientes)
        tree_clientes.delete(*tree_clientes.get_children())

        for row in rows_clientes:
            tree_clientes.insert("", "end", values=(row["codigo"], row["nome"]))

        # Carrega integrações (e armazena em todas_integracoes)
        query_integracoes = "SELECT cliente_id, nome_integracao FROM integracoes"
        todas_integracoes = await conn.fetch(query_integracoes)

        await conn.close()
    except Exception as e:
        print("Erro ao carregar dados:", e)

def selecionar_cliente(event):
    """Filtra e exibe apenas as integrações do cliente selecionado"""
    item_selecionado = tree_clientes.selection()
    if item_selecionado:
        cliente_id = tree_clientes.item(item_selecionado, "values")[0]

        # Filtra as integrações desse cliente
        integracoes_cliente = [row["nome_integracao"] for row in todas_integracoes if str(row["cliente_id"]) == cliente_id]

        # Limpa e insere as novas integrações filtradas
        tree_integracoes.delete(*tree_integracoes.get_children())
        for integracao in integracoes_cliente:
            tree_integracoes.insert("", "end", values=(integracao,))

def atualizar_dados():
    """Chama a atualização assíncrona de forma segura"""
    loop.call_soon_threadsafe(lambda: asyncio.create_task(carregar_dados()))

# Criando a interface
frame_principal = ctk.CTkFrame(root)
frame_principal.pack(fill="both", expand=True, padx=10, pady=5)

# Frame esquerdo (Clientes)
frame_clientes = ctk.CTkFrame(frame_principal)
frame_clientes.pack(side="left", fill="both", expand=True, padx=10, pady=5)

label_clientes = ctk.CTkLabel(frame_clientes, text="📃 Clientes", font=("Arial", 15, "bold"),
fg_color='#B22222', text_color='white', corner_radius=10)
label_clientes.pack()

tree_clientes = ttk.Treeview(frame_clientes, columns=("codigo", "nome"), show="headings")
tree_clientes.heading("codigo", text="Código")
tree_clientes.heading("nome", text="Nome do Cliente")

scroll_clientes = ttk.Scrollbar(frame_clientes, orient="vertical", command=tree_clientes.yview)
tree_clientes.configure(yscrollcommand=scroll_clientes.set)

scroll_clientes.pack(side="right", fill="y")
tree_clientes.pack(fill="both", expand=True)

#botao de refresh
btn_atualizar = ctk.CTkButton(root, text="🔄 Atualizar", command=atualizar_dados,
fg_color='#B22222', text_color='white', font=('Arial', 15, 'bold'))
btn_atualizar.pack(pady=10)

# Frame direito (Integrações do cliente selecionado)
frame_integracoes = ctk.CTkFrame(frame_principal)
frame_integracoes.pack(side="right", fill="both", expand=True, padx=10, pady=5)

label_integracoes = ctk.CTkLabel(frame_integracoes, text="💻 Integração",
font=("Arial", 15, "bold"), fg_color='#B22222',text_color='white', corner_radius=10)
label_integracoes.pack()

tree_integracoes = ttk.Treeview(frame_integracoes, columns=("integracao",), show="headings")
tree_integracoes.heading("integracao", text="Integrações")

scroll_integracoes = ttk.Scrollbar(frame_integracoes, orient="vertical", command=tree_integracoes.yview)
tree_integracoes.configure(yscrollcommand=scroll_integracoes.set)

scroll_integracoes.pack(side="right", fill="y")
tree_integracoes.pack(fill="both", expand=True)

# Associa a função ao clique no cliente
tree_clientes.bind("<<TreeviewSelect>>", selecionar_cliente)

# Carrega os dados ao iniciar o programa
asyncio.run(carregar_dados())

root.mainloop()
