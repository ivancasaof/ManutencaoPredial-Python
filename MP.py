from textwrap import wrap
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
import time, pyodbc
from threading import Timer
from PIL import ImageTk, Image
from tkcalendar import *
from tkinter import scrolledtext
from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, AUTO_BIND_NO_TLS, SUBTREE
import babel.numbers
from pathlib import Path

fonte_titulo_principal = ('Segoe UI Bold',18,)
fonte_titulos = ('Segoe UI Bold', 12)
fonte_padrao = ('Segoe UI Semibold', 10)

#/////////////////////////////VARIAVEL GLOBAL/////////////////////////////
imgconvertida = None
notifica = None
compara = None
status_atendimento = None
data = time.strftime('%d/%m/%Y', time.localtime())
global titulo_todos
titulo_todos = 'MP GV - v1.6'
#/////////////////////////////FIM VARIAVEL GLOBAL/////////////////////////////

#/////////////////////////////PRINCIPAL/////////////////////////////
def contador():
    cont = cursor.execute(
        "SELECT COUNT(*) FROM chamados WHERE status NOT LIKE '%Encerrado%' AND status NOT LIKE '%Cancelado%'")
    for cont in cont.fetchall():
        global notifica
        notifica = cont[0]

def notificacao():
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
    toaster.show_toast("Manutenção Predial GV", "\nUm novo chamado foi aberto!", duration=10, icon_path="imagens\\ico.ico", threaded=True)

def principal():
    root2.destroy()
    root = Tk()
    root.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())
    root.unbind_class("Button", "<Key-space>")
    root.focus_force()
    root.grab_set()
    def duploclique_tree_principal(event):
        if nivel_acesso == 0:
            visualizar_chamado()
        else:
            atendimento()

    def atualizar_lista_principal_encerrado():
        tree_principal.delete(*tree_principal.get_children())
        cursor.execute(
            "SELECT * FROM dbo.chamados WHERE status NOT LIKE '%Encerrado%' AND status NOT LIKE '%Cancelado%' ORDER BY id_chamado DESC")
        cont = 0
        for row in cursor:
            if cont % 2 == 0:
                if row[12] == None:
                    row[12] = ''
                tree_principal.insert('', 'end', text=" ",
                                      values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                      tags=('par',))
            else:
                if row[12] == None:
                    row[12] = ''
                tree_principal.insert('', 'end', text=" ",
                                      values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                      tags=('impar',))
            cont += 1
        contador()

    def atualizar_lista_principal():
        #label criada apenas para o contator ter uma referencia dentro dessa função
        lbl_loop = Label(frame4, text='', bg="#232729")
        lbl_loop.grid(row=0, column=2)

        if nivel_acesso == 0:
            btnatendimento.config(state='disabled')
            image_atendimento = Image.open('imagens\\atendimento_over.png')
            resize_atendimento = image_atendimento.resize((30, 35))
            nova_image_atendimento = ImageTk.PhotoImage(resize_atendimento)
            btnatendimento.photo = nova_image_atendimento
            btnatendimento.config(image=nova_image_atendimento, fg='#7c7c7c')
            btnatendimento.unbind("<Enter>")
            btnatendimento.unbind("<Leave>")

            btnferramentas.config(state='disabled')
            image_ferramentas = Image.open('imagens\\ferramentas_over.png')
            resize_ferramentas = image_ferramentas.resize((35, 35))
            nova_image_ferramentas = ImageTk.PhotoImage(resize_ferramentas)
            btnferramentas.photo = nova_image_ferramentas
            btnferramentas.config(image=nova_image_ferramentas, fg='#7c7c7c')
            btnferramentas.unbind("<Enter>")
            btnferramentas.unbind("<Leave>")

            clique_busca.set('Filtrar por...')
            ent_busca.delete(0, END)
            tree_principal.delete(*tree_principal.get_children())
            cursor.execute("SELECT * FROM dbo.chamados WHERE solicitante=? ORDER BY id_chamado DESC", (usuariologado,))
            cont = 0
            for row in cursor:
                if cont % 2 == 0:
                    if row[12] == None:
                        row[12] = ''
                    tree_principal.insert('', 'end', text=" ",
                                          values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                          tags=('par',))
                else:
                    if row[12] == None:
                        row[12] = ''
                    tree_principal.insert('', 'end', text=" ",
                                          values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                          tags=('impar',))
                cont += 1

        else:
            btnatendimento.config(state='normal')
            image_atendimento = Image.open('imagens\\atendimento.png')
            resize_atendimento = image_atendimento.resize((30, 35))
            nova_image_atendimento = ImageTk.PhotoImage(resize_atendimento)
            btnatendimento.photo = nova_image_atendimento
            btnatendimento.config(image=nova_image_atendimento, fg='#ffffff')
            btnatendimento.bind("<Enter>", muda_atendimento)
            btnatendimento.bind("<Leave>", volta_atendimento)

            btnferramentas.config(state='normal')
            image_ferramentas = Image.open('imagens\\ferramentas.png')
            resize_ferramentas = image_ferramentas.resize((35, 35))
            nova_image_ferramentas = ImageTk.PhotoImage(resize_ferramentas)
            btnferramentas.photo = nova_image_ferramentas
            btnferramentas.config(image=nova_image_ferramentas, fg='#ffffff')
            btnferramentas.bind("<Enter>", muda_ferramentas)
            btnferramentas.bind("<Leave>", volta_ferramentas)

            clique_busca.set('Filtrar por...')
            ent_busca.delete(0, END)
            tree_principal.delete(*tree_principal.get_children())
            cursor.execute("SELECT * FROM dbo.chamados WHERE status NOT LIKE '%Encerrado%' AND status NOT LIKE '%Cancelado%' ORDER BY id_chamado DESC")
            #cursor.execute("SELECT * FROM dbo.chamados WHERE status LIKE '%Aberto%' OR status LIKE '%Em andamento%' ORDER BY id_chamado DESC")
            #cursor.execute("SELECT * FROM dbo.chamados ORDER BY id_chamado DESC")
            cont = 0
            for row in cursor:
                if cont % 2 == 0:
                    if row[12] == None:
                        row[12] = ''
                    tree_principal.insert('', 'end', text=" ",
                                          values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                          tags=('par',))
                else:
                    if row[12] == None:
                        row[12] = ''
                    tree_principal.insert('', 'end', text=" ",
                                          values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                          tags=('impar',))
                cont += 1

            comp = cursor.execute(
                "SELECT COUNT(*) FROM chamados WHERE status NOT LIKE '%Encerrado%' AND status NOT LIKE '%Cancelado%'")
            for conti in comp.fetchall():
                global compara
                compara = conti[0]
            global notifica
            if compara < notifica:
                notifica = compara
            elif compara > notifica:
                notificacao()
                notifica = compara
        lbl_loop.after(300000, atualizar_lista_principal)
    # /////////////////////////////LOGIN INTERNO/////////////////////////////
    def login_interno():
        root2 = Toplevel()
        root2.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())
        root2.unbind_class("Button", "<Key-space>")
        root2.focus_force()
        root2.grab_set()

        def sair():
            root2.destroy()

        def entrar():
            user = euser.get()
            senha = esenha.get()
            if user == "" or senha == "":
                messagebox.showwarning('Login: Erro', 'Digite o Usuário ou Senha.', parent=root2)
            else:
                if clique.get() == "Usuário":
                    server_name = '192.168.1.19'
                    domain_name = 'gvdobrasil'
                    server = Server(server_name, get_info=ALL)
                    try:
                        Connection(server, user='{}\\{}'.format(domain_name, user), password=senha, authentication=NTLM,
                                   auto_bind=True)
                        global nivel_acesso
                        nivel_acesso = 0
                        global usuariologado
                        usuariologado = user
                        lbluserlogado.config(text=user, fg='#fff000')
                        atualizar_lista_principal()
                        root2.destroy()
                    except:
                        messagebox.showwarning('Login: Erro', 'Usuário ou senha inválidos.', parent=root2)
                else:
                    r = cursor.execute("SELECT * FROM dbo.analista WHERE login=?", (user,))
                    result = r.fetchone()
                    if result is None:
                        messagebox.showwarning('Login: Erro', 'Usuário ou Senha inválidos.', parent=root2)
                    else:
                        r = cursor.execute("SELECT * FROM dbo.analista WHERE login=?", (user,))
                        for login in r.fetchall():
                            filtro_user = login[1]
                            filtro_pwd = login[3]
                            if filtro_user == user and filtro_pwd == senha:
                                nivel_acesso = 1
                                usuariologado = login[2]
                                lbluserlogado.config(text=login[2], fg='#fff000')
                                atualizar_lista_principal()
                                root2.destroy()
                            else:
                                messagebox.showwarning('Login: Erro', 'Usuário ou Senha inválidos.', parent=root2)
        def entrar_bind(event):
            user = euser.get()
            senha = esenha.get()
            if user == "" or senha == "":
                messagebox.showwarning('Login: Erro', 'Digite o Usuário ou Senha.', parent=root2)
            else:
                if clique.get() == "Usuário":
                    server_name = '192.168.1.19'
                    domain_name = 'gvdobrasil'
                    server = Server(server_name, get_info=ALL)
                    try:
                        Connection(server, user='{}\\{}'.format(domain_name, user), password=senha, authentication=NTLM,
                                   auto_bind=True)
                        global nivel_acesso
                        nivel_acesso = 0
                        global usuariologado
                        usuariologado = user
                        lbluserlogado.config(text=user, fg='#fff000')
                        atualizar_lista_principal()
                        root2.destroy()
                    except:
                        messagebox.showwarning('Login: Erro', 'Usuário ou senha inválidos.', parent=root2)
                else:
                    r = cursor.execute("SELECT * FROM dbo.analista WHERE login=?", (user,))
                    result = r.fetchone()
                    if result is None:
                        messagebox.showwarning('Login: Erro', 'Usuário ou Senha inválidos.', parent=root2)
                    else:
                        r = cursor.execute("SELECT * FROM dbo.analista WHERE login=?", (user,))
                        for login in r.fetchall():
                            filtro_user = login[1]
                            filtro_pwd = login[3]
                            if filtro_user == user and filtro_pwd == senha:
                                nivel_acesso = 1
                                usuariologado = login[2]
                                lbluserlogado.config(text=login[2], fg='#fff000')
                                atualizar_lista_principal()
                                root2.destroy()
                            else:
                                messagebox.showwarning('Login: Erro', 'Usuário ou Senha inválidos.', parent=root2)
        frame0 = Frame(root2, bg='#ffffff')
        frame0.grid(row=0, column=0, stick='nsew')
        root2.grid_rowconfigure(0, weight=1)
        root2.grid_columnconfigure(0, weight=1)
        frame1 = Frame(frame0, bg="#232729")
        frame1.pack(side=TOP, fill=X, expand=False, anchor='center')
        frame2 = Frame(frame0, bg='#ffffff')
        frame2.pack(side=TOP, fill=X, expand=False, anchor='center', pady=10)
        frame3 = Frame(frame0, bg='#ffffff')
        frame3.pack(side=TOP, fill=X, expand=False, anchor='center')
        frame4 = Frame(frame0, bg='#ffffff')
        frame4.pack(side=TOP, fill=X, expand=False, anchor='center', pady=10)
        frame5 = Frame(frame0, bg='#232729')
        frame5.pack(side=TOP, fill=X, expand=False, anchor='center')

        image_login = Image.open('imagens\\login.png')
        resize_login = image_login.resize((35, 35))
        nova_image_login = ImageTk.PhotoImage(resize_login)

        lbllogin = Label(frame1, image=nova_image_login, text="Trocar Usuário", compound="left", bg='#232729',
                         fg='#FFFFFF', font=fonte_titulos)
        lbllogin.photo = nova_image_login
        lbllogin.grid(row=0, column=1)
        frame1.grid_columnconfigure(0, weight=1)
        frame1.grid_columnconfigure(2, weight=1)

        Label(frame2, text="Modo de Acesso:", bg='#ffffff', fg='#000000', font=fonte_padrao).grid(row=0, column=1,
                                                                                                  sticky="w")
        clique = StringVar()
        clique.set("Usuário")
        drop = OptionMenu(frame2, clique, "Usuário", "Responsável")
        drop.config(bg='#232729', fg='#FFFFFF', activebackground='#232729', activeforeground="#FFFFFF",
                    highlightthickness=0, relief=RIDGE, width=9, font=fonte_padrao)
        drop.grid(row=0, column=2, pady=10)
        frame2.grid_columnconfigure(0, weight=1)
        frame2.grid_columnconfigure(3, weight=1)

        Label(frame3, text="Usuário:", bg='#ffffff', fg='#000000', font=fonte_padrao).grid(row=1, column=1, sticky="w")
        euser = Entry(frame3, width=30, font=fonte_padrao)
        euser.grid(row=1, column=2, sticky="w", padx=5, pady=10)
        euser.focus_force()
        euser.bind("<Return>", entrar_bind)
        Label(frame3, text="Senha:", font=fonte_padrao, bg='#ffffff', fg='#000000').grid(row=2, column=1, sticky="w")
        esenha = Entry(frame3, show="*", width=30, font=fonte_padrao)
        esenha.grid(row=2, column=2, sticky="w", padx=5, pady=10)
        esenha.bind("<Return>", entrar_bind)
        frame3.grid_columnconfigure(0, weight=1)
        frame3.grid_columnconfigure(3, weight=1)

        bt1 = Button(frame4, text='Entrar', bg='#232729', fg='#FFFFFF', activebackground='#232729',
                     activeforeground="#FFFFFF", highlightthickness=0, width=10, relief=RIDGE, command=entrar,
                     font=fonte_padrao)
        bt1.grid(row=0, column=1, pady=5, padx=5)
        bt2 = Button(frame4, text='Sair', width=10, relief=RIDGE, command=sair, font=fonte_padrao)
        bt2.grid(row=0, column=2, pady=5, padx=5)
        frame4.grid_columnconfigure(0, weight=1)
        frame4.grid_columnconfigure(3, weight=1)

        Label(frame5, text="", bg='#232729', fg='#FFFFFF', font=fonte_padrao).grid(row=0, column=1, sticky="ew")
        frame5.grid_columnconfigure(0, weight=1)
        frame5.grid_columnconfigure(2, weight=1)
        '''root2.update()
        largura = frame0.winfo_width()
        altura = frame0.winfo_height()
        print(largura, altura)'''
        window_width = 300
        window_height = 275
        screen_width = root2.winfo_screenwidth()
        screen_height = root2.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        root2.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        root2.resizable(0, 0)
        root2.iconbitmap('imagens\\ico.ico')
        root2.title(titulo_todos)
    # /////////////////////////////FIM LOGIN INTERNO/////////////////////////////

    # /////////////////////////////ABRIR CHAMADO/////////////////////////////
    def abrirchamado():
        root2 = Toplevel(root)
        root2.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())
        root2.unbind_class("Button", "<Key-space>")
        root2.focus_force()
        root2.grab_set()
        hora = time.strftime('%H:%M:%S', time.localtime())

        def conversor(filename):
            # Convert digital data to binary format
            with open(filename, 'rb') as file:
                blobData = file.read()
            return blobData
        def anexo():
            anexo = filedialog.askopenfilename(initialdir="os.path.expanduser(default_dir)", title="Escolha um Arquivo",
                                               filetypes=([("JPG", "*.jpg"), ("JPEG", "*.jpeg"), ("Bitmap", "*.bmp")]), parent=root2)
            entryanexo.config(state=NORMAL)
            entryanexo.insert(0, anexo)
            entryanexo.config(state=DISABLED)
            global imgconvertida
            imgconvertida = conversor(anexo)
        def salvar():
            if clique_ocorr.get() == "" or cliquetipo.get() == "" or clique_setor.get() == "" or entrytitulo.get() == "" or txtdescr.get("1.0", 'end-1c') == "":
                messagebox.showwarning('+ Abrir Chamado: Erro', 'Todos os campos com ( * ) devem ser preenchidos.',
                                       parent=root2)
            elif entryramal.get() == "" and entrytelefone.get() == "":
                messagebox.showwarning('+ Abrir Chamado: Erro', 'Pelo menos um dos campos de contato (Telefone ou Ramal) devem ser preenchidos.', parent=root2)
            else:
                solicitante = entry_solicitante.get().upper()
                data_abertura = entrydataabertura.get()
                hora_abertura = entryhoraabertura.get()
                ocorr = clique_ocorr.get().upper()
                tipo = cliquetipo.get().upper()
                setor = clique_setor.get()
                titulo = entrytitulo.get().upper()
                anexo = imgconvertida
                descricao_problema = txtdescr.get("1.0", 'end-1c')
                telefone = entrytelefone.get().upper()
                ramal = entryramal.get().upper()
                status = "Aberto"
                tupla = (solicitante, data_abertura, hora_abertura, ocorr, tipo, setor, titulo, anexo, descricao_problema, telefone, ramal, status)
                ver = cursor.execute("SELECT * FROM dbo.chamados ORDER BY id_chamado DESC")
                result = ver.fetchone()
                if result == None:
                    cursor.execute(
                        "INSERT INTO dbo.chamados (solicitante, data_abertura, hora_abertura, ocorrencia, tipo, setor, titulo, anexo, descricao_problema, telefone, ramal, status) values(?,?,?,?,?,?,?,?,?,?,?,?)",
                        (tupla))
                    cursor.commit()
                    messagebox.showinfo('+ Abrir Chamado:', 'Chamado aberto com sucesso. Aguarde para ser atendido.',
                                        parent=root2)
                    atualizar_lista_principal()
                    root2.destroy()
                else:
                    cursor.execute("declare @newId int select @newId = max(id_chamado) from chamados DBCC CheckIdent('chamados', RESEED, @newId)")
                    cursor.execute(
                        "INSERT INTO dbo.chamados (solicitante, data_abertura, hora_abertura, ocorrencia, tipo, setor, titulo, anexo, descricao_problema, telefone, ramal, status) values(?,?,?,?,?,?,?,?,?,?,?,?)",
                        (tupla))
                    cursor.commit()
                    messagebox.showinfo('+ Abrir Chamado:', 'Chamado aberto com sucesso. Aguarde para ser atendido.',
                                        parent=root2)
                    atualizar_lista_principal()
                    root2.destroy()

        def cancelar():
            root2.destroy()

        frame0 = Frame(root2, bg='#ffffff')
        frame0.grid(row=0, column=0, stick='nsew')
        root2.grid_rowconfigure(0, weight=1)
        root2.grid_columnconfigure(0, weight=1)
        frame1 = Frame(frame0, bg="#232729")
        frame1.pack(side=TOP, fill=X, expand=False, anchor='center')
        frame2 = Frame(frame0, bg='#ffffff')
        frame2.pack(side=TOP, fill=X, expand=False, anchor='center', pady=8)
        frame3 = Frame(frame0, bg='#ffffff')
        frame3.pack(side=TOP, fill=X, expand=False, anchor='center', pady=8)
        frame4 = Frame(frame0, bg='#ffffff')
        frame4.pack(side=TOP, fill=X, expand=False, anchor='center', pady=8)
        frame5 = Frame(frame0, bg='#ffffff')
        frame5.pack(side=TOP, fill=X, expand=False, anchor='center', pady=8)
        frame6 = Frame(frame0, bg='#ffffff')
        frame6.pack(side=TOP, fill=X, expand=False, anchor='center', pady=8)
        frame7 = Frame(frame0, bg='#ffffff')
        frame7.pack(side=TOP, fill=X, expand=False, anchor='center', pady=8)
        frame8 = Frame(frame0, bg='#232729')
        frame8.pack(side=TOP, fill=X, expand=False, anchor='center')

        Label(frame1, image=nova_image_chamado, text=" + Abrir Chamado", compound="left", bg='#232729', fg='#FFFFFF',
              font=fonte_titulos).grid(row=0, column=1)
        frame1.grid_columnconfigure(0, weight=1)
        frame1.grid_columnconfigure(2, weight=1)

        Label(frame2, text="Solicitante:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=1, sticky="w")
        entry_solicitante = Entry(frame2, font=fonte_padrao, justify='center')
        entry_solicitante.grid(row=1, column=1, sticky="w")
        entry_solicitante.insert(0, usuariologado)
        entry_solicitante.config(state='disabled')

        Label(frame2, text="Data de Abertura:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=2, sticky="w", padx=12)
        entrydataabertura = Entry(frame2, font=fonte_padrao, justify='center')
        entrydataabertura.grid(row=1, column=2, sticky="w", padx=12)
        entrydataabertura.insert(0, data)
        entrydataabertura.config(state='disabled')

        Label(frame2, text="Hora de Abertura:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=3, sticky="w")
        entryhoraabertura = Entry(frame2, font=fonte_padrao, justify='center')
        entryhoraabertura.grid(row=1, column=3, sticky="w")
        entryhoraabertura.insert(0, hora)
        entryhoraabertura.config(state='disabled')

        frame2.grid_columnconfigure(0, weight=1)
        frame2.grid_columnconfigure(4, weight=1)

        Label(frame3, text="Ocorrência: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000').grid(row=0, column=1, sticky="w")
        clique_ocorr = StringVar()
        clique_ocorr.set('Manutenção Predial')
        drop_ocorr = OptionMenu(frame3, clique_ocorr, "Manutenção Predial")
        drop_ocorr.config(bg='#BDBDBD', fg='#FFFFFF', activebackground='#BDBDBD', activeforeground="#FFFFFF",
                        highlightthickness=0, relief=RIDGE, width=17)
        drop_ocorr.config(state='disabled')
        drop_ocorr.grid(row=1, column=1, sticky="w")


        Label(frame3, text="Tipo: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000').grid(row=0, column=2, sticky="w", padx=10)
        cliquetipo = StringVar()
        droptipo = OptionMenu(frame3, cliquetipo, "Civil", "Elétrica")
        droptipo.config(bg='#232729', fg='#FFFFFF', activebackground='#232729',
                       activeforeground="#FFFFFF", highlightthickness=0, relief=RIDGE, width=17)
        droptipo.grid(row=1, column=2, sticky="w", padx=10)

        Label(frame3, text="Setor: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000').grid(row=0, column=3, sticky="w")
        OptionList = [
            'Aciaria',
            'ADM',
            'Almoxarifado',
            'Ambulatório',
            'Balança',
            'EHS',
            'Inspeção de Tarugos',
            'Inspeção Laminação',
            'Laboratório Mecânico',
            'Laboratório Químico',
            'Laminação',
            'Logística',
            'Manutenção de Veículos',
            'Pátio de Sucatas',
            'Portaria',
            'Qualidade',
            'Refeitório',
            'Subestação',
            'Utilidades',
            'Vestiário'
            ]
        clique_setor = StringVar()
        drop_setor = OptionMenu(frame3, clique_setor, *OptionList)
        drop_setor.config(bg='#232729', fg='#FFFFFF', activebackground='#232729', activeforeground="#FFFFFF",
                        highlightthickness=0, relief=RIDGE, width=26)
        drop_setor.grid(row=1, column=3, sticky="w")

        frame3.grid_columnconfigure(0, weight=1)
        frame3.grid_columnconfigure(4, weight=1)

        lbltitulo = Label(frame4, text="Título: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000')
        lbltitulo.grid(row=0, column=1, sticky="w")
        entrytitulo = Entry(frame4, font=fonte_padrao, justify='center', width=44)
        entrytitulo.grid(row=1, column=1, sticky="ew", padx=(0,9))

        def muda_anexo(e):
            image_anexo = Image.open('imagens\\anexo_over.png')
            resize_anexo = image_anexo.resize((15, 20))
            nova_image_anexo = ImageTk.PhotoImage(resize_anexo)
            btnanexo.photo = nova_image_anexo
            btnanexo.config(image=nova_image_anexo, fg='#7c7c7c')
        def volta_anexo(e):
            image_anexo = Image.open('imagens\\anexo.png')
            resize_anexo = image_anexo.resize((15, 20))
            nova_image_anexo = ImageTk.PhotoImage(resize_anexo)
            btnanexo.photo = nova_image_anexo
            btnanexo.config(image=nova_image_anexo, fg='#232729')

        image_anexo = Image.open('imagens\\anexo.png')
        resize_anexo = image_anexo.resize((15, 20))
        nova_image_anexo = ImageTk.PhotoImage(resize_anexo)
        btnanexo = Button(frame4, image=nova_image_anexo, text=" Anexar arquivo.", compound="left",
                          font=fonte_padrao, bg='#ffffff', fg='#232729', command=anexo,
                          borderwidth=0, relief=RIDGE, activebackground="#ffffff", activeforeground="#7c7c7c")
        btnanexo.photo = nova_image_anexo
        btnanexo.grid(row=0, column=2, sticky="w", padx=(9,0))
        btnanexo.bind("<Enter>", muda_anexo)
        btnanexo.bind("<Leave>", volta_anexo)
        entryanexo = Entry(frame4, font=fonte_padrao, justify='center', width=24)
        entryanexo.grid(row=1, column=2, sticky="ew", padx=(9,0))
        entryanexo.config(state='disabled')
        frame4.grid_columnconfigure(0, weight=1)
        frame4.grid_columnconfigure(3, weight=1)

        Label(frame5, text="Descrição do Problema: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000').grid(row=0, column=1, sticky="w")
        txtdescr = scrolledtext.ScrolledText(frame5, width=69, height=10, font=fonte_padrao, wrap=WORD)
        txtdescr.grid(row=1, column=1)
        frame5.grid_columnconfigure(0, weight=1)
        frame5.grid_columnconfigure(2, weight=1)

        Label(frame6, text="Telefone: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000').grid(row=0, column=1, sticky="w")
        entrytelefone = Entry(frame6, font=fonte_padrao, justify='center')
        entrytelefone.grid(row=1, column=1, sticky="w")

        Label(frame6, text="Ramal: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000').grid(row=0, column=2, sticky="w", padx=14)
        entryramal = Entry(frame6, font=fonte_padrao, justify='center')
        entryramal.grid(row=1, column=2, sticky="w", padx=14)

        frame6.grid_columnconfigure(0, weight=1)
        frame6.grid_columnconfigure(3, weight=1)

        bt1 = Button(frame7, text='Salvar', bg='#232729', fg='#FFFFFF', activebackground='#232729',
                     activeforeground="#FFFFFF", highlightthickness=0, width=10, relief=RIDGE, command=salvar,
                     font=fonte_padrao)
        bt1.grid(row=0, column=1, padx=5)
        bt2 = Button(frame7, text='Cancelar', width=10, relief=RIDGE, command=cancelar, font=fonte_padrao)
        bt2.grid(row=0, column=2, padx=5)
        frame7.grid_columnconfigure(0, weight=1)
        frame7.grid_columnconfigure(3, weight=1)

        Label(frame8, text=" ", bg='#232729', fg='#FFFFFF', font=fonte_titulos).grid(row=0, column=1)
        frame8.grid_columnconfigure(0, weight=1)
        frame8.grid_columnconfigure(2, weight=1)

        '''root2.update()
        largura = frame0.winfo_width()
        altura = frame0.winfo_height()
        print(largura, altura)'''
        window_width = 550
        window_height = 571
        screen_width = root2.winfo_screenwidth()
        screen_height = root2.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        root2.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        #root2.resizable(0, 0)
        root2.configure(bg='#000000')
        root2.iconbitmap('imagens\\ico.ico')

    # /////////////////////////////FIM ABRIR CHAMADO/////////////////////////////

    # /////////////////////////////ATENDIMENTO/////////////////////////////
    def atendimento():
        def salvar():
            nome_analista = usuariologado
            prioridade = clique_prioridade.get()
            status = clique_status.get()
            data_atentimento = entrydataatendimento2.get()
            data_encerramento = entrydataencerramento.get()
            solucao = txtsolucao.get("1.0", 'end-1c')
            interacao = txtinteracao.get("1.0", 'end-1c')

            if status == "Aberto":
                messagebox.showwarning('Atenção !', 'Para concluir a alteração, o campo "STATUS" deve ser alterado.',
                                       parent=root2)
            elif status == "Em andamento" and data_atentimento == '':
                messagebox.showwarning('Atenção !',
                                       'Para concluir a alteração, o campo "DATA DO ATENDIMENTO" deve estar preenchido.',
                                       parent=root2)
            elif status == "Em andamento" and data_encerramento != '':
                messagebox.showwarning('Atenção !',
                                       'O campo "DATA DE ENCERRAMENTO" NÃO deve estar preenchido caso o status seja "EM ANDAMENTO".',
                                       parent=root2)
                entrydataencerramento.config(state='normal')
                entrydataencerramento.delete(0, END)
                entrydataencerramento.config(state='disabled')
            elif status == "Encerrado" and data_encerramento == '':
                messagebox.showwarning('Atenção !',
                                       'Para finalizar o chamado, o campo "DATA DE ENCERRAMENTO" deve estar preenchido.',
                                       parent=root2)
            elif status == "Encerrado" and solucao == '':
                messagebox.showwarning('Atenção !',
                                       'Para finalizar o chamado, o campo "SOLUÇÃO" deve estar preenchido.',
                                       parent=root2)
            elif prioridade == "":
                messagebox.showwarning('Atenção !', 'Defina uma prioridade para o chamado.',
                                       parent=root2)
            elif solucao != "" and data_encerramento == "":
                messagebox.showwarning('Atenção !',
                                       'O campo "Solução" só deve ser utilizado para finalizar o chamado. Utilize o campo de "Interação".',
                                       parent=root2)
            elif status == "Encerrado" and solucao != '' and data_encerramento != '':
                data_comparacao_atendimento = time.strptime(data_atentimento, "%d/%m/%Y")
                data_comparacao_encerramento = time.strptime(data_encerramento, "%d/%m/%Y")
                data_atual = time.strptime(data, "%d/%m/%Y")
                if data_comparacao_atendimento > data_comparacao_encerramento:
                    messagebox.showwarning('Atenção:', 'A "Data de Encerramento" não deve ser menor que a "Data de Atendimento"', parent=root2)
                elif data_comparacao_encerramento > data_atual:
                    messagebox.showwarning('Atenção:', 'A "Data de Encerramento" não deve ser superior a data de hoje.', parent=root2)
                else:
                    cursor.execute(
                        "UPDATE mp.dbo.chamados SET responsavel = ?, prioridade = ?, status = ?, data_atendimento = ?, data_encerramento = ?, interacao = ?, resolucao = ? WHERE id_chamado = ?",
                        (nome_analista, prioridade, status, data_atentimento, data_encerramento, interacao, solucao,
                         n_chamado))
                    cursor.commit()
                    messagebox.showinfo('Atendimento:', 'Alteração realizada com sucesso!', parent=root2)
                    atualizar_lista_principal_encerrado()
                    root2.destroy()
            elif status == "Cancelado" and solucao != '' and data_encerramento != '':
                data_comparacao_atendimento = time.strptime(data_atentimento, "%d/%m/%Y")
                data_comparacao_encerramento = time.strptime(data_encerramento, "%d/%m/%Y")
                data_atual = time.strptime(data, "%d/%m/%Y")
                if data_comparacao_atendimento > data_comparacao_encerramento:
                    messagebox.showwarning('Atenção:', 'A "Data de Encerramento" não deve ser menor que a "Data de Atendimento"', parent=root2)
                elif data_comparacao_encerramento > data_atual:
                    messagebox.showwarning('Atenção:', 'A "Data de Encerramento" não deve ser superior a data de hoje.', parent=root2)
                else:
                    cursor.execute(
                        "UPDATE mp.dbo.chamados SET responsavel = ?, prioridade = ?, status = ?, data_atendimento = ?, data_encerramento = ?, interacao = ?, resolucao = ? WHERE id_chamado = ?",
                        (nome_analista, prioridade, status, data_atentimento, data_encerramento, interacao, solucao,
                         n_chamado))
                    cursor.commit()
                    messagebox.showinfo('Atendimento:', 'Alteração realizada com sucesso!', parent=root2)
                    atualizar_lista_principal_encerrado()
                    root2.destroy()
            else:
                cursor.execute(
                    "UPDATE mp.dbo.chamados SET responsavel = ?, prioridade = ?, status = ?, data_atendimento = ?, data_encerramento = ?, interacao = ?, resolucao = ? WHERE id_chamado = ?",
                    (nome_analista, prioridade, status, data_atentimento, data_encerramento, interacao, solucao, n_chamado))
                cursor.commit()
                messagebox.showinfo('Atendimento:', 'Alteração realizada com sucesso!', parent=root2)
                atualizar_lista_principal()
                root2.destroy()

        def cancelar():
            root2.destroy()


        chamado_select = tree_principal.focus()
        if chamado_select == "":
            messagebox.showwarning('Atendimento:', 'Selecione um chamado na lista!', parent=root)
        else:
            n_chamado = tree_principal.item(chamado_select, "values")[0]
            r = cursor.execute("SELECT * FROM dbo.chamados WHERE id_chamado=?", (n_chamado,))
            result = r.fetchone()
            if result[14] == 'Encerrado' or result[14] == 'Cancelado':
                messagebox.showwarning('Atenção:',
                                       'Este chamado já foi finalizado. Acesse "Visualizar Atendimento" para eventuais consultas.', parent=root)
            elif result[12] != usuariologado and result[12] != None:
                messagebox.showwarning('Atendimento:', f'Este chamado já está sendo atendido pelo analista \n"{result[12]}".', parent=root)
            else:
                root2 = Toplevel(root)
                root2.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())
                root2.unbind_class("Button", "<Key-space>")
                root2.focus_force()
                root2.grab_set()

                def setup_entradas():
                    entrysolicitante.insert(0, result[1])
                    entrysolicitante.config(state='disabled')
                    entrydataabertura.insert(0, result[2])
                    entrydataabertura.config(state='disabled')
                    entryhoraabertura.insert(0, result[3])
                    entryhoraabertura.config(state='disabled')
                    entrytelefone.insert(0, result[10])
                    entrytelefone.config(state='disabled')
                    entryramal.insert(0, result[11])
                    entryramal.config(state='disabled')
                    entrysetor.insert(0, result[6])
                    entrysetor.config(state='disabled')
                    entryocorrencia.insert(0, result[4])
                    entryocorrencia.config(state='disabled')
                    entrytipo.insert(0, result[5])
                    entrytipo.config(state='disabled')
                    entrytitulo.insert(0, result[7])
                    entrytitulo.config(state='disabled')
                    txtdescr_atendimento.insert(END, result[9])
                    txtdescr_atendimento.config(fg='#696969')
                    txtdescr_atendimento.config(state='disabled')
                    if result[8] == None:
                        btabrir_anexo.config(state='disabled')
                    entryanalista2.insert(0, usuariologado)
                    entryanalista2.config(state='disabled')
                    if result[13] == None:
                        clique_prioridade.set('')
                    else:
                        clique_prioridade.set(result[13])
                    if result[14] == 'Aberto':
                        clique_status.set('Em andamento')
                        entrydataatendimento2.config(state='normal')
                        entrydataatendimento2.insert(0, data)
                        entrydataatendimento2.config(state='disabled')
                    else:
                        clique_status.set(result[14])

                    if result[15] != None:
                        entrydataatendimento2.config(state='normal')
                        entrydataatendimento2.insert(0, result[15])
                        entrydataatendimento2.config(state='disabled')

                    if result[17] != None:
                        txtinteracao.config(state='normal')
                        txtinteracao.insert(END, result[17])
                        txtinteracao.config(state='disabled')
                def abrir_anexo():
                    def conversorarquivo(data, filename):
                        with open(filename, 'wb') as file:
                            file.write(data)

                    nome_arquivo = result[8]
                    caminho = filedialog.asksaveasfilename(defaultextension=".*",
                                                           initialfile='Anexo_Chamado (' + str(result[0]) + ')',
                                                           initialdir='os.path.expanduser(default_dir)',
                                                           title='Salvar Anexo..',
                                                           filetypes=[("JPG", "*.jpg")])
                    conversorarquivo(nome_arquivo, caminho)

                def calendario_atendimento():
                    root3 = Toplevel(root2)
                    root3.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())
                    root3.unbind_class("Button", "<Key-space>")
                    root3.focus_force()
                    root3.grab_set()
                    window_width = 251
                    window_height = 212
                    screen_width = root3.winfo_screenwidth()
                    screen_height = root3.winfo_screenheight()
                    x_cordinate = int((screen_width / 2) - (window_width / 2))
                    y_cordinate = int((screen_height / 2) - (window_height / 2))
                    root3.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
                    root3.resizable(0, 0)
                    root3.title('Calendário:')

                    def salvar_calendario():
                        entrydataatendimento2.config(state='normal')
                        entrydataatendimento2.delete(0, END)
                        entrydataatendimento2.insert(0, cal.get_date())
                        entrydataatendimento2.config(state='disabled')
                        root3.destroy()

                    dia = time.strftime('%d', time.localtime())
                    mes = time.strftime('%m', time.localtime())
                    ano = time.strftime('%Y', time.localtime())
                    cal = Calendar(root3, selectmode='day', year=int(ano), month=int(mes), day=int(dia),
                                   date_pattern='dd/mm/y')
                    cal.grid(row=0, column=0)

                    btsalvarcalendario = Button(root3, text="Salvar", font=fonte_padrao, bg="#1d366c", fg="#ffffff",
                                                activebackground="#1d366c", activeforeground="#FFFFFF", relief=RIDGE,
                                                command=salvar_calendario)
                    btsalvarcalendario.grid(row=1, column=0, stick='we')
                    btsalvarcalendario.focus_force()
                    #root3.update()
                    #largura = root3.winfo_width()
                    #altura = root3.winfo_height()
                    #print(largura, altura)
                    root3.mainloop()

                def calendario_encerrado():
                    root3 = Toplevel(root2)
                    root3.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())
                    root3.unbind_class("Button", "<Key-space>")
                    root3.focus_force()
                    root3.grab_set()
                    window_width = 251
                    window_height = 212
                    screen_width = root3.winfo_screenwidth()
                    screen_height = root3.winfo_screenheight()
                    x_cordinate = int((screen_width / 2) - (window_width / 2))
                    y_cordinate = int((screen_height / 2) - (window_height / 2))
                    root3.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
                    root3.resizable(0, 0)
                    root3.title('Calendário:')

                    def salvar_encerrado():
                        entrydataencerramento.config(state='normal')
                        entrydataencerramento.delete(0, END)
                        entrydataencerramento.insert(0, cal.get_date())
                        entrydataencerramento.config(state='disabled')
                        root3.destroy()

                    dia = time.strftime('%d', time.localtime())
                    mes = time.strftime('%m', time.localtime())
                    ano = time.strftime('%Y', time.localtime())
                    cal = Calendar(root3, selectmode='day', year=int(ano), month=int(mes), day=int(dia),
                                   date_pattern='dd/mm/y')
                    cal.grid(row=0, column=0)
                    btsalvarcalendario = Button(root3, text="Salvar", font=fonte_padrao, bg="#1d366c", fg="#ffffff",
                                                activebackground="#1d366c", activeforeground="#FFFFFF", relief=RIDGE,
                                                command=salvar_encerrado)
                    btsalvarcalendario.grid(row=1, column=0, stick='we')
                    btsalvarcalendario.focus_force()
                    # root3.update()
                    # largura = frame0.winfo_width()
                    # altura = frame0.winfo_height()
                    # print(largura, altura)
                    root3.mainloop()

                def enviar_int():
                    txtinteracao.config(state='normal')
                    if txtinteracao.get("1.0", 'end-1c') == "":
                        interacao = entryinteracao.get()
                        if interacao == "":
                            messagebox.showwarning('Campo vazio:', 'Atenção! Campo de Interação vazio.', parent=root2)
                            txtinteracao.config(state='disabled')
                        else:
                            hora = time.strftime('%H:%M:%S', time.localtime())
                            txtinteracao.insert(END, f'{usuariologado}: ({data} - {hora})\n{interacao}\n-----------------------------------------------------------------------')
                            txtinteracao.config(state='disabled')
                            entryinteracao.delete(0, END)
                    else:
                        interacao = entryinteracao.get()
                        if interacao == "":
                            messagebox.showwarning('Campo vazio:', 'Atenção! Campo de Interação vazio.', parent=root2)
                            txtinteracao.config(state='disabled')
                        else:
                            hora = time.strftime('%H:%M:%S', time.localtime())
                            txtinteracao.insert(END, f'\n{usuariologado}: ({data} - {hora})\n{interacao}\n-----------------------------------------------------------------------')
                            txtinteracao.config(state='disabled')
                            entryinteracao.delete(0, END)
                def desfazer_int():
                    entryinteracao.delete(0, END)

                frame0 = Frame(root2, bg='#ffffff')
                frame0.grid(row=0, column=1, sticky=NSEW)
                frame_topo = Frame(frame0, bg='#232729')
                frame_topo.grid(row=0, column=1, sticky=NSEW, columnspan=2)
                frame_esquerda = LabelFrame(frame0, text="Informações do Chamado:", font=fonte_padrao, bg='#ffffff')
                frame_esquerda.grid(row=1, column=1, sticky=NSEW, padx=10)
                frame_direita = Frame(frame0, bg='#ffffff')
                frame_direita.grid(row=1, column=2, sticky=NSEW, padx=10)
                frame_baixo = Frame(frame0, bg='#232729')
                frame_baixo.grid(row=2, column=1, sticky=NSEW, columnspan=2)
                # //// TOPO ////
                Label(frame_topo, image=nova_image_atendimento, text=f" Atendimento: Chamado Nº {n_chamado}", compound="left", bg='#232729', fg='#FFFFFF', font=fonte_titulos).grid(row=0, column=1)
                frame_topo.grid_columnconfigure(0, weight=1)
                frame_topo.grid_columnconfigure(2, weight=1)
                # //// ESQUERDA ////
                frame1 = Frame(frame_esquerda, bg='#ffffff')
                frame1.grid(row=0, column=1, sticky=EW, pady=(6,0))
                frame2 = Frame(frame_esquerda, bg='#ffffff')
                frame2.grid(row=1, column=1, sticky=NSEW)
                frame3 = Frame(frame_esquerda, bg='#ffffff')
                frame3.grid(row=2, column=1, sticky=NSEW)

                Label(frame1, text="Solicitante:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=1, sticky="w")
                entrysolicitante = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
                entrysolicitante.grid(row=1, column=1, sticky="w")

                Label(frame1, text="Data de Abertura:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=2, sticky="w")
                entrydataabertura = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
                entrydataabertura.grid(row=1, column=2, sticky="w")

                Label(frame1, text="Hora de Abertura:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=3, sticky="w")
                entryhoraabertura = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
                entryhoraabertura.grid(row=1, column=3, sticky="w")

                Label(frame1, text="Telefone:", font=fonte_padrao, bg='#ffffff').grid(row=2, column=1, sticky="w")
                entrytelefone = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
                entrytelefone.grid(row=3, column=1, sticky="w")

                Label(frame1, text="Ramal:", font=fonte_padrao, bg='#ffffff').grid(row=2, column=2, sticky="w")
                entryramal = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
                entryramal.grid(row=3, column=2, sticky="w")

                Label(frame1, text="Setor:", font=fonte_padrao, bg='#ffffff').grid(row=2, column=3, sticky="w")
                entrysetor = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
                entrysetor.grid(row=3, column=3, sticky="w")

                Label(frame1, text="Ocorrência:", font=fonte_padrao, bg='#ffffff').grid(row=4, column=1, sticky="w")
                entryocorrencia = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
                entryocorrencia.grid(row=5, column=1, sticky="ew")

                Label(frame1, text="Tipo:*", font=fonte_padrao, bg='#ffffff').grid(row=4, column=2, sticky="w")
                entrytipo = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff', width=40)
                entrytipo.grid(row=5, column=2, columnspan=2)

                lbltitulo = Label(frame1, text="Título:*", font=fonte_padrao, bg='#ffffff')
                lbltitulo.grid(row=6, column=1, sticky="w")
                entrytitulo = Entry(frame1, font=fonte_padrao, justify='center', width=61)
                entrytitulo.grid(row=7, column=1, sticky="w", columnspan=3)

                frame1.grid_columnconfigure(0, weight=1)
                frame1.grid_columnconfigure(3, weight=1)

                Label(frame2, text="Descrição do Problema:*", font=fonte_padrao, bg='#ffffff').grid(row=0, column=1, sticky="w")
                txtdescr_atendimento = scrolledtext.ScrolledText(frame2, width=59, height=16, font=fonte_padrao, bg='#ffffff', wrap=WORD)
                txtdescr_atendimento.grid(row=1, column=1, sticky="ew", columnspan=2)
                frame2.grid_columnconfigure(0, weight=1)
                frame2.grid_columnconfigure(2, weight=1)

                def muda_anexo(e):
                    image_abriranexo = Image.open('imagens\\anexo_over.png')
                    resize_abriranexo = image_abriranexo.resize((15, 20))
                    nova_image_abriranexo = ImageTk.PhotoImage(resize_abriranexo)
                    btabrir_anexo.photo = nova_image_abriranexo
                    btabrir_anexo.config(image=nova_image_abriranexo, fg='#7c7c7c')
                def volta_anexo(e):
                    image_abriranexo = Image.open('imagens\\anexo.png')
                    resize_abriranexo = image_abriranexo.resize((15, 20))
                    nova_image_abriranexo = ImageTk.PhotoImage(resize_abriranexo)
                    btabrir_anexo.photo = nova_image_abriranexo
                    btabrir_anexo.config(image=nova_image_abriranexo, fg='#232729')

                image_abriranexo = Image.open('imagens\\anexo.png')
                resize_abriranexo = image_abriranexo.resize((15, 20))
                nova_image_abriranexo = ImageTk.PhotoImage(resize_abriranexo)
                btabrir_anexo = Button(frame3, image=nova_image_abriranexo, text=" Abrir Anexo.", compound="left",
                                  font=fonte_padrao, bg='#ffffff', fg='#232729', command=abrir_anexo,
                                  borderwidth=0, relief=RIDGE, activebackground="#ffffff", activeforeground="#7c7c7c")
                btabrir_anexo.photo = nova_image_abriranexo
                btabrir_anexo.grid(row=0, column=1, pady=6)
                btabrir_anexo.bind("<Enter>", muda_anexo)
                btabrir_anexo.bind("<Leave>", volta_anexo)
                frame3.grid_columnconfigure(0, weight=1)
                frame3.grid_columnconfigure(2, weight=1)
                # //// DIREITA ////
                frame1 = Frame(frame_direita, bg='#ffffff')
                frame1.grid(row=0, column=1, sticky=EW)
                frame2 = Frame(frame_direita, bg='#ffffff')
                frame2.grid(row=1, column=1, sticky=NSEW, pady=6)
                frame3 = LabelFrame(frame_direita, text="Interação do Chamado (Usuário\Analistas):", font=fonte_padrao,bg='#ffffff')
                frame3.grid(row=2, column=1, sticky=NSEW, pady=6)
                frame4 = Frame(frame_direita, bg='#ffffff')
                frame4.grid(row=3, column=1, sticky=NSEW)
                frame5 = Frame(frame_direita, bg='#ffffff')
                frame5.grid(row=4, column=1, sticky=NSEW)

                Label(frame1, text="Nome do Analista:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=1, sticky="w")
                entryanalista2 = Entry(frame1, font=fonte_padrao, justify='center', width=70, bg='#ffffff')
                entryanalista2.grid(row=1, column=1, sticky="ew")
                frame1.grid_columnconfigure(0, weight=1)
                frame1.grid_columnconfigure(2, weight=1)

                def cliquestatus(event):
                    if clique_status.get() == "Encerrado" or clique_status.get() == "Cancelado":
                        entrydataencerramento.config(state='normal')
                        entrydataencerramento.delete(0, END)
                        entrydataencerramento.insert(0, data)
                        entrydataencerramento.config(state='disabled')
                    elif clique_status.get() == "Em andamento" or clique_status.get() == "Aguardando Usuário" or clique_status.get() == "Chamado TOTVS":
                        entrydataencerramento.config(state='normal')
                        entrydataencerramento.delete(0, END)
                        entrydataencerramento.config(state='disabled')

                Label(frame2, text="Prioridade do Chamado:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=1, sticky="w", columnspan=5)
                options = ["Baixa", "Média", "Alta", "Urgente"]
                clique_prioridade = StringVar()

                drop_status = OptionMenu(frame2, clique_prioridade, *options)
                drop_status.config(bg='#232729', fg='#FFFFFF', activebackground='#232729', activeforeground="#FFFFFF",
                                   highlightthickness=0, relief=RIDGE, width=20)
                drop_status.grid(row=1, column=1, columnspan=5, sticky="w", pady=(0,10))


                Label(frame2, text="Status:", font=fonte_padrao, bg='#ffffff').grid(row=2, column=1, sticky="w")
                options = ["Em andamento", "Aguardando Usuário", "Chamado TOTVS", "Cancelado" ,"Encerrado"]
                clique_status = StringVar()

                drop_status = OptionMenu(frame2, clique_status, *options, command=cliquestatus)
                drop_status.config(bg='#232729', fg='#FFFFFF', activebackground='#232729', activeforeground="#FFFFFF",
                                   highlightthickness=0, relief=RIDGE, width=20)
                drop_status.grid(row=3, column=1, sticky="w")
                Label(frame2, text="Data do Atendimento:", font=fonte_padrao, bg='#ffffff').grid(row=2, column=2)
                entrydataatendimento2 = Entry(frame2, font=fonte_padrao, justify='center', width=22, bg='#ffffff')
                entrydataatendimento2.grid(row=3, column=2, columnspan=2, sticky="we", padx=8)
                entrydataatendimento2.config(state='disabled')

                Label(frame2, text="Data de Encerramento:", font=fonte_padrao, bg='#ffffff').grid(row=2, column=4, sticky="w")
                entrydataencerramento = Entry(frame2, font=fonte_padrao, justify='center', width=22, bg='#ffffff')
                entrydataencerramento.grid(row=3, column=4, columnspan=2, sticky="we")
                entrydataencerramento.config(state='disabled')

                frame2.grid_columnconfigure(0, weight=1)
                frame2.grid_columnconfigure(5, weight=1)

                entryinteracao = Entry(frame3, font=fonte_padrao, justify='center', width=46, bg='#ffffff')
                entryinteracao.grid(row=0, column=1, padx=(2,0))

                btn_envia_interacao = Button(frame3, text='Enviar', width=10, relief=RIDGE, font=fonte_padrao, command=enviar_int, bg="#232729", fg="#ffffff", activebackground="#232729", activeforeground="#FFFFFF", state=NORMAL)
                btn_envia_interacao.grid(row=0, column=2, padx=(5,0))
                btn_cancela_interacao = Button(frame3, text='Desfazer', width=10, font=fonte_padrao, command=desfazer_int)
                btn_cancela_interacao.grid(row=0, column=3, padx=(5,2))

                Label(frame3, text="Histórico:", font=fonte_padrao, bg='#ffffff').grid(row=1, column=1, sticky="w")
                txtinteracao = scrolledtext.ScrolledText(frame3, font=fonte_padrao, width=68, height=8, bg='#ffffff', wrap=WORD)
                txtinteracao.grid(row=2, column=1, columnspan=3, sticky="ew", padx=2, pady=(0,2))
                txtinteracao.config(state='disabled', fg='#696969')

                frame3.grid_columnconfigure(0, weight=1)
                frame3.grid_columnconfigure(4, weight=1)

                Label(frame4, text="Solução:*", font=fonte_padrao, bg='#ffffff').grid(row=0, column=1, sticky="w")
                txtsolucao = scrolledtext.ScrolledText(frame4, width=68, height=4, font=fonte_padrao, bg='#ffffff', wrap=WORD)
                txtsolucao.grid(row=1, column=1, sticky="ew", columnspan=2)
                txtsolucao.focus_force()
                frame4.grid_columnconfigure(0, weight=1)
                frame4.grid_columnconfigure(3, weight=1)

                btcancelar_atendimento = Button(frame5, text='Salvar', width=10, relief=RIDGE, command=salvar, font=fonte_padrao, bg="#232729", fg="#ffffff", activebackground="#232729", activeforeground="#FFFFFF", state=NORMAL)
                btcancelar_atendimento.grid(row=0, column=1, padx=5, pady=6)
                btconfirma_atencimento = Button(frame5, text='Cancelar', command=cancelar, width=10, font=fonte_padrao)
                btconfirma_atencimento.grid(row=0, column=2, padx=5, pady=6)

                frame5.grid_columnconfigure(0, weight=1)
                frame5.grid_columnconfigure(3, weight=1)

                # //// BAIXO ////
                Label(frame_baixo, text="", bg='#232729', fg='#FFFFFF', font=fonte_titulos).grid(row=0, column=1)
                frame_baixo.grid_columnconfigure(0, weight=1)
                frame_baixo.grid_columnconfigure(2, weight=1)
                setup_entradas()
                '''root2.update()
                largura = frame0.winfo_width()
                altura = frame0.winfo_height()
                print(largura, altura)'''
                window_width = 1002
                window_height = 603
                screen_width = root2.winfo_screenwidth()
                screen_height = root2.winfo_screenheight()
                x_cordinate = int((screen_width / 2) - (window_width / 2))
                y_cordinate = int((screen_height / 2) - (window_height / 2))
                root2.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
                #root2.resizable(0, 0)
                root2.configure(bg='#ffffff')
                root2.iconbitmap('imagens\\ico.ico')
                root2.grid_columnconfigure(0, weight=1)
                root2.grid_columnconfigure(2, weight=1)
    # /////////////////////////////FIM ATENDIMENTO/////////////////////////////

    # /////////////////////////////VISUALIZAR/////////////////////////////
    def visualizar_chamado():
        chamado_select = tree_principal.focus()
        if chamado_select == "":
            messagebox.showwarning('Atendimento:', 'Selecione um chamado na lista!', parent=root)
        else:
            n_chamado = tree_principal.item(chamado_select, "values")[0]
            r = cursor.execute("SELECT * FROM dbo.chamados WHERE id_chamado=?", (n_chamado,))
            result = r.fetchone()
            root2 = Toplevel(root)
            root2.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())
            root2.unbind_class("Button", "<Key-space>")
            root2.focus_force()
            root2.grab_set()
            def setup_entradas():
                if nivel_acesso == 1: #Analista
                    bt_editar_chamado.config(state='disabled')
                    bt_excluir_chamado.config(state='disabled')
                    entrysolicitante.insert(0, result[1])
                    entrysolicitante.config(state='disabled')
                    entrydataabertura.insert(0, result[2])
                    entrydataabertura.config(state='disabled')
                    entryhoraabertura.insert(0, result[3])
                    entryhoraabertura.config(state='disabled')
                    entrytelefone.insert(0, result[10])
                    entrytelefone.config(state='disabled')
                    entryramal.insert(0, result[11])
                    entryramal.config(state='disabled')
                    entrysetor.insert(0, result[6])
                    entrysetor.config(state='disabled')
                    entryocorrencia.insert(0, result[4])
                    entryocorrencia.config(state='disabled')
                    entrytitulo.insert(0, result[7])
                    entrytitulo.config(state='disabled')
                    entrytipo.insert(0, result[5])
                    entrytipo.config(state='disabled')
                    if result[12] != None:
                        entryanalista2.insert(0, result[12])
                        entryanalista2.config(state='disabled')
                    else:
                        entryanalista2.config(state='disabled')
                    txtdescr_atendimento.insert(END, result[9])
                    txtdescr_atendimento.config(state='disabled', fg='#696969')
                    if result[18] != None:
                        txtsolucao.config(state='normal')
                        txtsolucao.insert(END, result[18])
                        txtsolucao.config(state='disabled', fg='#696969')
                    if result[13] != None:
                        clique_prioridade.set(result[13])
                        drop_prioridade.config(state='disabled')
                    else:
                        drop_prioridade.config(state='disabled')

                    if result[8] == None:
                        btabrir_anexo.config(state='disabled')

                    if result[15] != None:
                        entrydataatendimento2.config(state='normal')
                        entrydataatendimento2.insert(0, result[15])
                        entrydataatendimento2.config(state='disabled')
                    clique_status.set(result[14])
                    drop_status.config(state='disabled')
                    if result[16] != None:
                        entrydataencerramento.config(state='normal')
                        entrydataencerramento.insert(0, result[16])
                        entrydataencerramento.config(state='disabled')
                    entryinteracao.config(state='disabled')
                    btn_envia_interacao.config(state='disabled')
                    btn_cancela_interacao.config(state='disabled')
                    btconfirma_atencimento.config(state='disabled')
                    btcancelar_atendimento.config(state='disabled')
                    if result[17] != None:
                        txtinteracao.config(state='normal')
                        txtinteracao.insert(END, result[17])
                        txtinteracao.config(state='disabled')
                    upper = usuariologado.upper()
                    if result[14] == "Aberto" and result[1] == upper:
                        bt_editar_chamado.config(state='normal')
                        bt_excluir_chamado.config(state='normal')
                else:
                    bt_editar_chamado.config(state='disabled')
                    bt_excluir_chamado.config(state='disabled')
                    entrysolicitante.insert(0, result[1])
                    entrysolicitante.config(state='disabled')
                    entrydataabertura.insert(0, result[2])
                    entrydataabertura.config(state='disabled')
                    entryhoraabertura.insert(0, result[3])
                    entryhoraabertura.config(state='disabled')
                    entrytelefone.insert(0, result[10])
                    entrytelefone.config(state='disabled')
                    entryramal.insert(0, result[11])
                    entryramal.config(state='disabled')
                    entrysetor.insert(0, result[6])
                    entrysetor.config(state='disabled')
                    entryocorrencia.insert(0, result[4])
                    entryocorrencia.config(state='disabled')
                    entrytitulo.insert(0, result[7])
                    entrytitulo.config(state='disabled')
                    entrytipo.insert(0, result[5])
                    entrytipo.config(state='disabled')
                    if result[12] != None:
                        entryanalista2.insert(0, result[12])
                        entryanalista2.config(state='disabled')
                    else:
                        entryanalista2.config(state='disabled')
                    txtdescr_atendimento.insert(END, result[9])
                    txtdescr_atendimento.config(state='disabled', fg='#696969')
                    if result[18] != None:
                        txtsolucao.config(state='normal')
                        txtsolucao.insert(END, result[18])
                        txtsolucao.config(state='disabled', fg='#696969')
                    if result[13] != None:
                        clique_prioridade.set(result[13])
                        drop_prioridade.config(state='disabled')
                    else:
                        drop_prioridade.config(state='disabled')

                    if result[8] == None:
                        btabrir_anexo.config(state='disabled')

                    if result[15] != None:
                        entrydataatendimento2.config(state='normal')
                        entrydataatendimento2.insert(0, result[15])
                        entrydataatendimento2.config(state='disabled')
                    clique_status.set(result[14])
                    drop_status.config(state='disabled')
                    if result[16] != None:
                        entrydataencerramento.config(state='normal')
                        entrydataencerramento.insert(0, result[16])
                        entrydataencerramento.config(state='disabled')
                    entryinteracao.config(state='normal')
                    btn_envia_interacao.config(state='normal')
                    btn_cancela_interacao.config(state='normal')
                    btconfirma_atencimento.config(state='normal')
                    btcancelar_atendimento.config(state='normal')
                    if result[17] != None:
                        txtinteracao.config(state='normal')
                        txtinteracao.insert(END, result[17])
                        txtinteracao.config(state='disabled')
                    upper = usuariologado.upper()
                    if result[14] == "Aberto" and result[1] == upper:
                        bt_editar_chamado.config(state='normal')
                        bt_excluir_chamado.config(state='normal')

            def abrir_anexo():
                def conversorarquivo(data, filename):
                    with open(filename, 'wb') as file:
                        file.write(data)

                nome_arquivo = result[8]
                caminho = filedialog.asksaveasfilename(defaultextension=".*",
                                                           initialfile='Anexo_Chamado (' + str(result[0]) + ')',
                                                           initialdir='os.path.expanduser(default_dir)',
                                                           title='Salvar Anexo..',
                                                           filetypes=[("JPG", "*.jpg")])
                conversorarquivo(nome_arquivo, caminho)
            def salvar():
                interacao = txtinteracao.get("1.0", 'end-1c')
                cursor.execute("UPDATE mp.dbo.chamados SET interacao = ? WHERE id_chamado = ?",(interacao, n_chamado))
                cursor.commit()
                messagebox.showinfo('Atendimento:', 'Alteração realizada com sucesso!', parent=root2)
                atualizar_lista_principal()
                root2.destroy()
            def cancelar():
                root2.destroy()
            def enviar_int():
                txtinteracao.config(state='normal')
                if txtinteracao.get("1.0", 'end-1c') == "":
                    interacao = entryinteracao.get()
                    if interacao == "":
                        messagebox.showwarning('Campo vazio:', 'Atenção! Campo de Interação vazio.', parent=root2)
                        txtinteracao.config(state='disabled')
                    else:
                        hora = time.strftime('%H:%M:%S', time.localtime())
                        txtinteracao.insert(END,
                                            f'{usuariologado}: ({data} - {hora})\n{interacao}\n-----------------------------------------------------------------------')
                        txtinteracao.config(state='disabled')
                        entryinteracao.delete(0, END)
                else:
                    interacao = entryinteracao.get()
                    if interacao == "":
                        messagebox.showwarning('Campo vazio:', 'Atenção! Campo de Interação vazio.', parent=root2)
                        txtinteracao.config(state='disabled')
                    else:
                        hora = time.strftime('%H:%M:%S', time.localtime())
                        txtinteracao.insert(END,
                                            f'\n{usuariologado}: ({data} - {hora})\n{interacao}\n-----------------------------------------------------------------------')
                        txtinteracao.config(state='disabled')
                        entryinteracao.delete(0, END)
            def desfazer_int():
                entryinteracao.delete(0, END)
                txtinteracao.config(state='normal')
                txtinteracao.delete('1.0', END)
                txtinteracao.insert(END, result[19])
                txtinteracao.config(state='disabled')
            def excluir_chamado():
                resposta = messagebox.askyesno('Atenção:', f'Tem certeza de que deseja excluir o chamado nº{result[0]}?', parent=root2)
                if resposta == True:
                    cursor.execute("DELETE FROM mp.dbo.chamados WHERE id_chamado = ?", (result[0]))
                    cursor.commit()
                    ver = cursor.execute("SELECT * FROM dbo.chamados ORDER BY id_chamado DESC")
                    resultado_busca = ver.fetchone()
                    if resultado_busca == None:
                        cursor.execute("DBCC CHECKIDENT('dbo.chamados', RESEED, 0)")
                    else:
                        cursor.execute("declare @newId int select @newId = max(id_chamado) from chamados DBCC CheckIdent('chamados', RESEED, @newId)")
                    messagebox.showinfo('Atenção:', f'Chamado nº{result[0]} excluído com sucesso!', parent=root2)
                    atualizar_lista_principal()
                    root2.destroy()
            def editar_chamado():
                root3 = Toplevel(root2)
                root3.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())
                root3.unbind_class("Button", "<Key-space>")
                root3.focus_force()
                root3.grab_set()
                hora = time.strftime('%H:%M:%S', time.localtime())

                def conversor(filename):
                    # Convert digital data to binary format
                    with open(filename, 'rb') as file:
                        blobData = file.read()
                    return blobData


                def anexo():
                    anexo = filedialog.askopenfilename(initialdir="os.path.expanduser(default_dir)",
                                                       title="Escolha um Arquivo",
                                                       filetypes=(
                                                       [("JPG", "*.jpg"), ("JPEG", "*.jpeg"), ("Bitmap", "*.bmp")]))
                    entryanexo.config(state=NORMAL)
                    entryanexo.insert(0, anexo)
                    entryanexo.config(state=DISABLED)
                    global imgconvertida
                    imgconvertida = conversor(anexo)

                def confirmar_edicao():
                    if cliquetipo.get() == "" or clique_setor.get() == "" or entrytitulo.get() == "" or txtdescr.get("1.0",'end-1c') == "":
                        messagebox.showwarning('+ Abrir Chamado: Erro',
                                               'Todos os campos com ( * ) devem ser preenchidos.',
                                               parent=root3)
                    elif entryramal.get() == "" and entrytelefone.get() == "":
                        messagebox.showwarning('+ Abrir Chamado: Erro', 'Pelo menos um dos campos de contato (Telefone ou Ramal) devem ser preenchidos.', parent=root3)
                    else:
                        data_abertura = entrydataabertura.get()
                        hora_abertura = entryhoraabertura.get()
                        tipo = cliquetipo.get().upper()
                        setor = clique_setor.get().upper()
                        titulo = entrytitulo.get().upper()
                        anexo = imgconvertida
                        descricao_problema = txtdescr.get("1.0", 'end-1c')
                        telefone = entrytelefone.get().upper()
                        ramal = entryramal.get().upper()
                        resposta = messagebox.askyesno('Atenção:',
                                                       f'Tem certeza de que deseja editar o chamado nº{result[0]}?',
                                                       parent=root3)
                        if resposta == True:
                            cursor.execute(
                                "UPDATE mp.dbo.chamados SET data_abertura = ? , hora_abertura = ?, tipo = ?,  setor = ?, titulo = ?, anexo = ?, descricao_problema = ?, telefone = ?, ramal = ?  WHERE id_chamado = ?",
                                (data_abertura, hora_abertura, tipo, setor, titulo, anexo, descricao_problema, telefone, ramal, n_chamado))
                            cursor.commit()
                            atualizar_lista_principal()
                            root3.destroy()
                            root2.destroy()

                def cancelar():
                    root2.destroy()

                def setup_entradas():
                    entrysolicitante.insert(0, result[1])
                    entrysolicitante.config(state='disabled')
                    cliquetipo.set(result[5])
                    clique_setor.set(result[6])
                    entrytitulo.config(state='normal')
                    entrytitulo.insert(0, result[7])
                    txtdescr.insert(END, result[9])

                    entrytelefone.insert(0, result[10])
                    entryramal.insert(0, result[11])

                frame0 = Frame(root3, bg='#ffffff')
                frame0.grid(row=0, column=0, stick='nsew')
                root3.grid_rowconfigure(0, weight=1)
                root3.grid_columnconfigure(0, weight=1)
                frame1 = Frame(frame0, bg="#232729")
                frame1.pack(side=TOP, fill=X, expand=False, anchor='center')
                frame2 = Frame(frame0, bg='#ffffff')
                frame2.pack(side=TOP, fill=X, expand=False, anchor='center', pady=8)
                frame3 = Frame(frame0, bg='#ffffff')
                frame3.pack(side=TOP, fill=X, expand=False, anchor='center', pady=8)
                frame4 = Frame(frame0, bg='#ffffff')
                frame4.pack(side=TOP, fill=X, expand=False, anchor='center', pady=8)
                frame5 = Frame(frame0, bg='#ffffff')
                frame5.pack(side=TOP, fill=X, expand=False, anchor='center', pady=8)
                frame6 = Frame(frame0, bg='#ffffff')
                frame6.pack(side=TOP, fill=X, expand=False, anchor='center', pady=8)
                frame7 = Frame(frame0, bg='#ffffff')
                frame7.pack(side=TOP, fill=X, expand=False, anchor='center', pady=8)
                frame8 = Frame(frame0, bg='#232729')
                frame8.pack(side=TOP, fill=X, expand=False, anchor='center')

                Label(frame1, image=nova_image_chamado, text=f" Editar Chamado: Nº {result[0]}", compound="left", bg='#232729',
                      fg='#FFFFFF',
                      font=fonte_titulos).grid(row=0, column=1)
                frame1.grid_columnconfigure(0, weight=1)
                frame1.grid_columnconfigure(2, weight=1)

                Label(frame2, text="Solicitante", font=fonte_padrao, bg='#ffffff').grid(row=0, column=1, sticky="w")
                entrysolicitante = Entry(frame2, font=fonte_padrao, justify='center')
                entrysolicitante.grid(row=1, column=1, sticky="w")

                Label(frame2, text="Data de Abertura:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=2,
                                                                                              sticky="w", padx=12)
                entrydataabertura = Entry(frame2, font=fonte_padrao, justify='center')
                entrydataabertura.grid(row=1, column=2, sticky="w", padx=12)
                entrydataabertura.insert(0, data)
                entrydataabertura.config(state='disabled')

                Label(frame2, text="Hora de Abertura:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=3,
                                                                                              sticky="w")
                entryhoraabertura = Entry(frame2, font=fonte_padrao, justify='center')
                entryhoraabertura.grid(row=1, column=3, sticky="w")
                entryhoraabertura.insert(0, hora)
                entryhoraabertura.config(state='disabled')

                frame2.grid_columnconfigure(0, weight=1)
                frame2.grid_columnconfigure(4, weight=1)

                Label(frame3, text="Ocorrência: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000').grid(row=0, column=1,
                                                                                                        sticky="w")
                clique_ocorr = StringVar()
                drop_ocorr = OptionMenu(frame3, clique_ocorr, "Manutenção Predial")
                drop_ocorr.config(bg='#BDBDBD', fg='#FFFFFF', activebackground='#232729', activeforeground="#FFFFFF",
                                  highlightthickness=0, relief=RIDGE, width=17)
                drop_ocorr.grid(row=1, column=1, sticky="w")
                clique_ocorr.set('Manutenção Predial')
                drop_ocorr.config(state='disabled')

                Label(frame3, text="Tipo: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000').grid(row=0, column=2,
                                                                                                  sticky="w", padx=10)
                cliquetipo = StringVar()
                droptipo = OptionMenu(frame3, cliquetipo, "Civil", "Elétrica")
                droptipo.config(bg='#232729', fg='#FFFFFF', activebackground='#232729', activeforeground="#FFFFFF",
                                highlightthickness=0, relief=RIDGE, width=17)
                droptipo.grid(row=1, column=2, sticky="w", padx=10)
                Label(frame3, text="Setor: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000').grid(row=0, column=3,sticky="w")

                OptionList = [
                    "Aciaria",
                    "ADM",
                    "Almoxarifado",
                    "Balança",
                    "EHS",
                    "Laminação",
                    "Manutenção de Veículos",
                    "Pátio de Sucatas",
                    "Portaria",
                    "Subestação",
                    "Utilidades",
                    "Vestiário"
                ]
                clique_setor = StringVar()
                drop_setor = OptionMenu(frame3, clique_setor, *OptionList)
                drop_setor.config(bg='#232729', fg='#FFFFFF', activebackground='#232729',
                               activeforeground="#FFFFFF", highlightthickness=0, relief=RIDGE, width=26)
                drop_setor.grid(row=1, column=3, sticky="w")
                frame3.grid_columnconfigure(0, weight=1)
                frame3.grid_columnconfigure(4, weight=1)

                lbltitulo = Label(frame4, text="Título: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000')
                lbltitulo.grid(row=0, column=1, sticky="w")

                def muda_anexo(e):
                    image_anexo = Image.open('imagens\\anexo_over.png')
                    resize_anexo = image_anexo.resize((15, 20))
                    nova_image_anexo = ImageTk.PhotoImage(resize_anexo)
                    btnanexo.photo = nova_image_anexo
                    btnanexo.config(image=nova_image_anexo, fg='#7c7c7c')

                def volta_anexo(e):
                    image_anexo = Image.open('imagens\\anexo.png')
                    resize_anexo = image_anexo.resize((15, 20))
                    nova_image_anexo = ImageTk.PhotoImage(resize_anexo)
                    btnanexo.photo = nova_image_anexo
                    btnanexo.config(image=nova_image_anexo, fg='#232729')

                image_anexo = Image.open('imagens\\anexo.png')
                resize_anexo = image_anexo.resize((15, 20))
                nova_image_anexo = ImageTk.PhotoImage(resize_anexo)
                btnanexo = Button(frame4, image=nova_image_anexo, text=" Anexar arquivo.", compound="left",
                                  font=fonte_padrao, bg='#ffffff', fg='#232729', command=anexo,
                                  borderwidth=0, relief=RIDGE, activebackground="#ffffff", activeforeground="#7c7c7c")
                btnanexo.photo = nova_image_anexo
                btnanexo.grid(row=0, column=2, sticky="w", padx=(9, 0))
                btnanexo.bind("<Enter>", muda_anexo)
                btnanexo.bind("<Leave>", volta_anexo)
                entrytitulo = Entry(frame4, font=fonte_padrao, justify='center', width=44)
                entrytitulo.grid(row=1, column=1, sticky="ew", padx=(0, 9))
                entrytitulo.config(state=DISABLED)
                entryanexo = Entry(frame4, font=fonte_padrao, justify='center', width=25)
                entryanexo.grid(row=1, column=2, sticky="ew", padx=(9, 0))
                entryanexo.config(state='disabled')
                frame4.grid_columnconfigure(0, weight=1)
                frame4.grid_columnconfigure(3, weight=1)
                
                Label(frame5, text="Descrição do Problema: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000').grid(
                    row=0, column=1, sticky="w")
                txtdescr = scrolledtext.ScrolledText(frame5, width=69, height=10, font=fonte_padrao, wrap=WORD)
                txtdescr.grid(row=1, column=1)
                frame5.grid_columnconfigure(0, weight=1)
                frame5.grid_columnconfigure(2, weight=1)

                Label(frame6, text="Telefone: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000').grid(row=0, column=1, sticky="w")
                entrytelefone = Entry(frame6, font=fonte_padrao, justify='center')
                entrytelefone.grid(row=1, column=1, sticky="w")

                Label(frame6, text="Ramal: *", font=fonte_padrao, bg='#ffffff', fg='#8B0000').grid(row=0, column=2, sticky="w", padx=14)
                entryramal = Entry(frame6, font=fonte_padrao, justify='center')
                entryramal.grid(row=1, column=2, sticky="w", padx=14)

                frame6.grid_columnconfigure(0, weight=1)
                frame6.grid_columnconfigure(3, weight=1)

                bt1 = Button(frame7, text='Confirmar', bg='#232729', fg='#FFFFFF', activebackground='#232729',
                             activeforeground="#FFFFFF", highlightthickness=0, width=10, relief=RIDGE, command=confirmar_edicao,
                             font=fonte_padrao)
                bt1.grid(row=0, column=1, padx=5)
                bt2 = Button(frame7, text='Cancelar', width=10, relief=RIDGE, command=cancelar, font=fonte_padrao)
                bt2.grid(row=0, column=2, padx=5)
                frame7.grid_columnconfigure(0, weight=1)
                frame7.grid_columnconfigure(3, weight=1)

                Label(frame8, text=" ", bg='#232729', fg='#FFFFFF', font=fonte_titulos).grid(row=0, column=1)
                frame8.grid_columnconfigure(0, weight=1)
                frame8.grid_columnconfigure(2, weight=1)
                #
                setup_entradas()
                

                # root2.update()
                # largura = frame0.winfo_width()
                # altura = frame0.winfo_height()
                # print(largura, altura)
                window_width = 550
                window_height = 571
                screen_width = root2.winfo_screenwidth()
                screen_height = root2.winfo_screenheight()
                x_cordinate = int((screen_width / 2) - (window_width / 2))
                y_cordinate = int((screen_height / 2) - (window_height / 2))
                root3.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
                root3.resizable(0, 0)
                root3.configure(bg='#000000')
                root3.iconbitmap('imagens\\ico.ico')

            frame0 = Frame(root2, bg='#ffffff')
            frame0.grid(row=0, column=1, sticky=NSEW)
            frame_topo = Frame(frame0, bg='#232729')
            frame_topo.grid(row=0, column=1, sticky=NSEW, columnspan=2)
            frame_esquerda = LabelFrame(frame0, text="Informações do Chamado:",
                                        font=fonte_padrao, bg='#ffffff')
            frame_esquerda.grid(row=1, column=1, sticky=NSEW, padx=10)
            frame_direita = Frame(frame0, bg='#ffffff')
            frame_direita.grid(row=1, column=2, sticky=NSEW, padx=10)
            frame_baixo = Frame(frame0, bg='#232729')
            frame_baixo.grid(row=2, column=1, sticky=NSEW, columnspan=2)
            # //// TOPO ////
            Label(frame_topo, image=nova_image_visualizarchamado, text=f" Visualizando Chamado: Nº {n_chamado}",
                  compound="left", bg='#232729', fg='#FFFFFF', font=fonte_titulos).grid(row=0, column=1)
            frame_topo.grid_columnconfigure(0, weight=1)
            frame_topo.grid_columnconfigure(2, weight=1)
            # //// ESQUERDA ////
            frame1 = Frame(frame_esquerda, bg='#ffffff')
            frame1.grid(row=0, column=1, sticky=EW, pady=(6, 0))
            frame2 = Frame(frame_esquerda, bg='#ffffff')
            frame2.grid(row=1, column=1, sticky=NSEW)
            frame3 = Frame(frame_esquerda, bg='#ffffff')
            frame3.grid(row=2, column=1, sticky=NSEW)

            Label(frame1, text="Solicitante:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=1, sticky="w")
            entrysolicitante = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
            entrysolicitante.grid(row=1, column=1, sticky="w")

            Label(frame1, text="Data de Abertura:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=2, sticky="w")
            entrydataabertura = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
            entrydataabertura.grid(row=1, column=2, sticky="w")

            Label(frame1, text="Hora de Abertura:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=3, sticky="w")
            entryhoraabertura = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
            entryhoraabertura.grid(row=1, column=3, sticky="w")

            Label(frame1, text="Telefone:", font=fonte_padrao, bg='#ffffff').grid(row=2, column=1, sticky="w")
            entrytelefone = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
            entrytelefone.grid(row=3, column=1, sticky="w")

            Label(frame1, text="Ramal:", font=fonte_padrao, bg='#ffffff').grid(row=2, column=2, sticky="w")
            entryramal = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
            entryramal.grid(row=3, column=2, sticky="w")

            Label(frame1, text="Setor:", font=fonte_padrao, bg='#ffffff').grid(row=2, column=3, sticky="w")
            entrysetor = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
            entrysetor.grid(row=3, column=3, sticky="w")

            Label(frame1, text="Ocorrência:", font=fonte_padrao, bg='#ffffff').grid(row=4, column=1, sticky="w")
            entryocorrencia = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff')
            entryocorrencia.grid(row=5, column=1, sticky="ew")

            Label(frame1, text="Tipo:", font=fonte_padrao, bg='#ffffff').grid(row=4, column=2, sticky="w")
            entrytipo = Entry(frame1, font=fonte_padrao, justify='center', bg='#ffffff', width=40)
            entrytipo.grid(row=5, column=2, columnspan=2)

            lbltitulo = Label(frame1, text="Título:", font=fonte_padrao, bg='#ffffff')
            lbltitulo.grid(row=6, column=1, sticky="w")
            entrytitulo = Entry(frame1, font=fonte_padrao, justify='center', width=61)
            entrytitulo.grid(row=7, column=1, sticky="w", columnspan=3)

            frame1.grid_columnconfigure(0, weight=1)
            frame1.grid_columnconfigure(3, weight=1)

            Label(frame2, text="Descrição do Problema:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=1,
                                                                                                sticky="w")
            txtdescr_atendimento = scrolledtext.ScrolledText(frame2, width=59, height=16, font=fonte_padrao,
                                                             bg='#ffffff', wrap=WORD)
            txtdescr_atendimento.grid(row=1, column=1, sticky="ew", columnspan=2)
            frame2.grid_columnconfigure(0, weight=1)
            frame2.grid_columnconfigure(2, weight=1)

            def muda_anexo(e):
                image_abriranexo = Image.open('imagens\\anexo_over.png')
                resize_abriranexo = image_abriranexo.resize((15, 20))
                nova_image_abriranexo = ImageTk.PhotoImage(resize_abriranexo)
                btabrir_anexo.photo = nova_image_abriranexo
                btabrir_anexo.config(image=nova_image_abriranexo, fg='#7c7c7c')

            def volta_anexo(e):
                image_abriranexo = Image.open('imagens\\anexo.png')
                resize_abriranexo = image_abriranexo.resize((15, 20))
                nova_image_abriranexo = ImageTk.PhotoImage(resize_abriranexo)
                btabrir_anexo.photo = nova_image_abriranexo
                btabrir_anexo.config(image=nova_image_abriranexo, fg='#232729')

            image_abriranexo = Image.open('imagens\\anexo.png')
            resize_abriranexo = image_abriranexo.resize((15, 20))
            nova_image_abriranexo = ImageTk.PhotoImage(resize_abriranexo)
            btabrir_anexo = Button(frame3, image=nova_image_abriranexo, text=" Abrir Anexo.", compound="left",
                                   font=fonte_padrao, bg='#ffffff', fg='#232729', command=abrir_anexo,
                                   borderwidth=0, relief=RIDGE, activebackground="#ffffff", activeforeground="#7c7c7c")
            btabrir_anexo.photo = nova_image_abriranexo
            btabrir_anexo.grid(row=0, column=0, pady=6, padx=(6,0))
            btabrir_anexo.bind("<Enter>", muda_anexo)
            btabrir_anexo.bind("<Leave>", volta_anexo)
            bt_editar_chamado = Button(frame3, text='Editar', width=10, relief=RIDGE, command=editar_chamado,
                                            font=fonte_padrao, bg="#232729", fg="#ffffff", activebackground="#232729",
                                            activeforeground="#FFFFFF", state=NORMAL)
            bt_editar_chamado.grid(row=0, column=3, padx=6)
            bt_excluir_chamado = Button(frame3, text='Excluir', command=excluir_chamado, width=10, font=fonte_padrao)
            bt_excluir_chamado.grid(row=0, column=4, padx=6)
            frame3.grid_columnconfigure(1, weight=1)
            frame3.grid_columnconfigure(2, weight=1)
            # //// DIREITA ////
            frame1 = Frame(frame_direita, bg='#ffffff')
            frame1.grid(row=0, column=1, sticky=EW)
            frame2 = Frame(frame_direita, bg='#ffffff')
            frame2.grid(row=1, column=1, sticky=NSEW, pady=6)
            frame3 = LabelFrame(frame_direita, text="Interação do Chamado (Usuário\Analistas):", font=fonte_padrao,
                                bg='#ffffff')
            frame3.grid(row=2, column=1, sticky=NSEW, pady=6)
            frame4 = Frame(frame_direita, bg='#ffffff')
            frame4.grid(row=3, column=1, sticky=NSEW)
            frame5 = Frame(frame_direita, bg='#ffffff')
            frame5.grid(row=4, column=1, sticky=NSEW)

            Label(frame1, text="Nome do Analista:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=1, sticky="w")
            entryanalista2 = Entry(frame1, font=fonte_padrao, justify='center', width=70, bg='#ffffff')
            entryanalista2.grid(row=1, column=1, sticky="ew")
            frame1.grid_columnconfigure(0, weight=1)
            frame1.grid_columnconfigure(2, weight=1)

            Label(frame2, text="Prioridade do Chamado:", font=fonte_padrao, bg='#ffffff').grid(row=0, column=1,
                                                                                               sticky="w", columnspan=5)
            options = ["Baixa", "Média", "Alta", "Urgente"]
            clique_prioridade = StringVar()

            drop_prioridade = OptionMenu(frame2, clique_prioridade, *options)
            drop_prioridade.config(bg='#232729', fg='#FFFFFF', activebackground='#232729', activeforeground="#FFFFFF",
                               highlightthickness=0, relief=RIDGE, width=20)
            drop_prioridade.grid(row=1, column=1, columnspan=5, sticky="w", pady=(0, 10))

            Label(frame2, text="Status:", font=fonte_padrao, bg='#ffffff').grid(row=2, column=1, sticky="w")
            options = ["Em andamento", "Encerrado"]
            clique_status = StringVar()

            drop_status = OptionMenu(frame2, clique_status, *options)
            drop_status.config(bg='#232729', fg='#FFFFFF', activebackground='#232729', activeforeground="#FFFFFF",
                               highlightthickness=0, relief=RIDGE, width=20)
            drop_status.grid(row=3, column=1, sticky="w")
            Label(frame2, text="Data do Atendimento:", font=fonte_padrao, bg='#ffffff').grid(row=2, column=2)
            entrydataatendimento2 = Entry(frame2, font=fonte_padrao, justify='center', width=22, bg='#ffffff')
            entrydataatendimento2.grid(row=3, column=2, columnspan=2, sticky="we", padx=8)
            entrydataatendimento2.config(state='disabled')
 
            Label(frame2, text="Data de Encerramento:", font=fonte_padrao, bg='#ffffff').grid(row=2, column=4, sticky="w")
            entrydataencerramento = Entry(frame2, font=fonte_padrao, justify='center', width=22, bg='#ffffff')
            entrydataencerramento.grid(row=3, column=4, columnspan=2, sticky="we")
            entrydataencerramento.config(state='disabled')
            frame2.grid_columnconfigure(0, weight=1)
            frame2.grid_columnconfigure(5, weight=1)

            entryinteracao = Entry(frame3, font=fonte_padrao, justify='center', width=46, bg='#ffffff')
            entryinteracao.grid(row=0, column=1, padx=(2, 0))
            entryinteracao.focus_force()

            btn_envia_interacao = Button(frame3, text='Enviar', width=10, relief=RIDGE, font=fonte_padrao,
                                            command=enviar_int, bg="#232729", fg="#ffffff", activebackground="#232729",
                                            activeforeground="#FFFFFF", state=NORMAL)
            btn_envia_interacao.grid(row=0, column=2, padx=(5, 0))
            btn_cancela_interacao = Button(frame3, text='Desfazer', width=10, font=fonte_padrao, command=desfazer_int)
            btn_cancela_interacao.grid(row=0, column=3, padx=(5, 2))

            Label(frame3, text="Histórico:", font=fonte_padrao, bg='#ffffff').grid(row=1, column=1, sticky="w")
            txtinteracao = scrolledtext.ScrolledText(frame3, font=fonte_padrao, width=68, height=8, bg='#ffffff', wrap=WORD)
            txtinteracao.grid(row=2, column=1, columnspan=3, sticky="ew", padx=2, pady=(0, 2))
            txtinteracao.config(state='disabled', fg='#696969')

            frame3.grid_columnconfigure(0, weight=1)
            frame3.grid_columnconfigure(4, weight=1)

            Label(frame4, text="Solução:*", font=fonte_padrao, bg='#ffffff').grid(row=0, column=1, sticky="w")
            txtsolucao = scrolledtext.ScrolledText(frame4, width=68, height=4, font=fonte_padrao, bg='#ffffff', wrap=WORD)
            txtsolucao.grid(row=1, column=1, sticky="ew", columnspan=2)
            txtsolucao.config(state='disabled', fg='#696969')
            frame4.grid_columnconfigure(0, weight=1)
            frame4.grid_columnconfigure(3, weight=1)

            btcancelar_atendimento = Button(frame5, text='Salvar', width=10, relief=RIDGE, command=salvar,
                                            font=fonte_padrao, bg="#232729", fg="#ffffff", activebackground="#232729",
                                            activeforeground="#FFFFFF", state=NORMAL)
            btcancelar_atendimento.grid(row=0, column=1, padx=5, pady=6)
            btconfirma_atencimento = Button(frame5, text='Cancelar', command=cancelar, width=10, font=fonte_padrao)
            btconfirma_atencimento.grid(row=0, column=2, padx=5, pady=6)

            frame5.grid_columnconfigure(0, weight=1)
            frame5.grid_columnconfigure(3, weight=1)

            # //// BAIXO ////
            Label(frame_baixo, text="", bg='#232729', fg='#FFFFFF', font=fonte_titulos).grid(row=0, column=1)
            frame_baixo.grid_columnconfigure(0, weight=1)
            frame_baixo.grid_columnconfigure(2, weight=1)
            setup_entradas()
            '''root2.update()
            largura = frame0.winfo_width()
            altura = frame0.winfo_height()
            print(largura, altura)'''
            window_width = 1002
            window_height = 593
            screen_width = root2.winfo_screenwidth()
            screen_height = root2.winfo_screenheight()
            x_cordinate = int((screen_width / 2) - (window_width / 2))
            y_cordinate = int((screen_height / 2) - (window_height / 2))
            root2.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
            root2.resizable(0, 0)
            root2.configure(bg='#ffffff')
            root2.iconbitmap('imagens\\ico.ico')
            root2.grid_columnconfigure(0, weight=1)
            root2.grid_columnconfigure(2, weight=1)
    # /////////////////////////////FIM VISUALIZAR/////////////////////////////

    def pesquisar_bind(event):
        pesquisar()
    def pesquisar():
        filtro = ent_busca.get()
        # ///////////////////BUSCA STATUS///////////////////
        if clique_busca.get() == "Status":
            if nivel_acesso == 0:
                cursor.execute("SELECT * FROM dbo.chamados WHERE status LIKE '%' + ? + '%' AND solicitante =? ORDER BY id_chamado DESC",
                               (filtro, usuariologado,))
                busca = cursor.fetchone()
                if busca is None:
                    messagebox.showwarning('Erro:', 'Nenhum registro encontrado', parent=root)
                else:
                    tree_principal.delete(*tree_principal.get_children())
                    cursor.execute("SELECT * FROM dbo.chamados WHERE status LIKE '%' + ? + '%' AND solicitante =? ORDER BY id_chamado DESC",
                        (filtro, usuariologado,))
                    for row in cursor:
                        if row[12] == None:
                            row[12] = ''
                        tree_principal.insert('', 'end', text=" ",
                                              values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                              tags=('par',))
            else:
                cursor.execute("SELECT * FROM dbo.chamados WHERE status LIKE '%' + ? + '%' ORDER BY id_chamado DESC",(filtro,))
                busca = cursor.fetchone()
                if busca is None:
                    messagebox.showwarning('Erro:', 'Nenhum registro encontrado', parent=root)
                else:
                    tree_principal.delete(*tree_principal.get_children())
                    cursor.execute("SELECT * FROM dbo.chamados WHERE status LIKE '%' + ? + '%' ORDER BY id_chamado DESC",(filtro,))
                    for row in cursor:
                        if row[12] == None:
                            row[12] = ''
                        tree_principal.insert('', 'end', text=" ",
                                              values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                              tags=('par',))
        # ///////////////////BUSCA Nº CHAMADO///////////////////
        elif clique_busca.get() == "Nº Chamado":
            if nivel_acesso == 0:
                cursor.execute("SELECT * FROM dbo.chamados WHERE id_chamado =? AND solicitante =?",
                               (filtro, usuariologado,))
                busca = cursor.fetchone()
                if busca is None:
                    messagebox.showwarning('Erro:', 'Nenhum registro encontrado', parent=root)
                else:
                    tree_principal.delete(*tree_principal.get_children())
                    cursor.execute("SELECT * FROM dbo.chamados WHERE id_chamado =? AND solicitante =?",
                                   (filtro, usuariologado,))
                    for row in cursor:
                        if row[12] == None:
                            row[12] = ''
                        tree_principal.insert('', 'end', text=" ",
                                              values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                              tags=('par',))
            else:
                cursor.execute("SELECT * FROM dbo.chamados WHERE id_chamado =?",(filtro,))
                busca = cursor.fetchone()
                if busca is None:
                    messagebox.showwarning('Erro:', 'Nenhum registro encontrado', parent=root)
                else:
                    tree_principal.delete(*tree_principal.get_children())
                    cursor.execute("SELECT * FROM dbo.chamados WHERE id_chamado =?",(filtro,))
                    for row in cursor:
                        if row[12] == None:
                            row[12] = ''
                        tree_principal.insert('', 'end', text=" ",
                                              values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                              tags=('par',))
        # ///////////////////BUSCA USUARIO///////////////////
        elif clique_busca.get() == "Solicitante":
            if nivel_acesso == 0:
                messagebox.showwarning('Erro:','Não é possível efetuar uma busca pelo próprio nome ou de outro usuário.', parent=root)
            else:
                cursor.execute("SELECT * FROM dbo.chamados WHERE solicitante LIKE '%' + ? + '%' ORDER BY id_chamado DESC",(filtro,))
                busca = cursor.fetchone()
                if busca is None:
                    messagebox.showwarning('Erro:', 'Nenhum registro encontrado', parent=root)
                else:
                    tree_principal.delete(*tree_principal.get_children())
                    cursor.execute("SELECT * FROM dbo.chamados WHERE solicitante LIKE '%' + ? + '%' ORDER BY id_chamado DESC",(filtro,))
                    for row in cursor:
                        if row[12] == None:
                            row[12] = ''
                        tree_principal.insert('', 'end', text=" ",
                                              values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                              tags=('par',))
        # ///////////////////BUSCA TIPO///////////////////
        elif clique_busca.get() == "Tipo":
            if nivel_acesso == 0:
                cursor.execute("SELECT * FROM dbo.chamados WHERE tipo LIKE '%' + ? + '%' AND solicitante =? ORDER BY id_chamado DESC",
                               (filtro, usuariologado,))
                busca = cursor.fetchone()
                if busca is None:
                    messagebox.showwarning('Erro:', 'Nenhum registro encontrado', parent=root)
                else:
                    tree_principal.delete(*tree_principal.get_children())
                    cursor.execute("SELECT * FROM dbo.chamados WHERE tipo LIKE '%' + ? + '%' AND solicitante =? ORDER BY id_chamado DESC",
                        (filtro, usuariologado,))
                    for row in cursor:
                        if row[12] == None:
                            row[12] = ''
                        tree_principal.insert('', 'end', text=" ",
                                              values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                              tags=('par',))
            else:
                cursor.execute("SELECT * FROM dbo.chamados WHERE tipo LIKE '%' + ? + '%' ORDER BY id_chamado DESC",(filtro,))
                busca = cursor.fetchone()
                if busca is None:
                    messagebox.showwarning('Erro:', 'Nenhum registro encontrado', parent=root)
                else:
                    tree_principal.delete(*tree_principal.get_children())
                    cursor.execute("SELECT * FROM dbo.chamados WHERE tipo LIKE '%' + ? + '%' ORDER BY id_chamado DESC",(filtro,))
                    for row in cursor:
                        if row[12] == None:
                            row[12] = ''
                        tree_principal.insert('', 'end', text=" ",
                                              values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                              tags=('par',))
        # ///////////////////BUSCA ANALISTA///////////////////
        elif clique_busca.get() == "Responsável":
            if nivel_acesso == 0:
                cursor.execute("SELECT * FROM dbo.chamados WHERE responsavel LIKE '%' + ? + '%' AND solicitante =? ORDER BY id_chamado DESC",
                               (filtro, usuariologado,))
                busca = cursor.fetchone()
                if busca is None:
                    messagebox.showwarning('Erro:', 'Nenhum registro encontrado', parent=root)
                else:
                    tree_principal.delete(*tree_principal.get_children())
                    cursor.execute("SELECT * FROM dbo.chamados WHERE responsavel LIKE '%' + ? + '%' AND solicitante =? ORDER BY id_chamado DESC",
                        (filtro, usuariologado,))
                    for row in cursor:
                        if row[12] == None:
                            row[12] = ''
                        tree_principal.insert('', 'end', text=" ",
                                              values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                              tags=('par',))
            else:
                cursor.execute("SELECT * FROM dbo.chamados WHERE responsavel LIKE '%' + ? + '%' ORDER BY id_chamado DESC",(filtro,))
                busca = cursor.fetchone()
                if busca is None:
                    messagebox.showwarning('Erro:', 'Nenhum registro encontrado', parent=root)
                else:
                    tree_principal.delete(*tree_principal.get_children())
                    cursor.execute("SELECT * FROM dbo.chamados WHERE responsavel LIKE '%' + ? + '%' ORDER BY id_chamado DESC",(filtro,))
                    for row in cursor:
                        if row[12] == None:
                            row[12] = ''
                        tree_principal.insert('', 'end', text=" ",
                                              values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                              tags=('par',))
        # ///////////////////BUSCA ANALISTA///////////////////
        elif clique_busca.get() == "Data Encerramento":
            if nivel_acesso == 0:
                cursor.execute("SELECT * FROM dbo.chamados WHERE data_encerramento LIKE '%' + ? + '%' AND solicitante =? ORDER BY id_chamado DESC",
                               (filtro, usuariologado,))
                busca = cursor.fetchone()
                if busca is None:
                    messagebox.showwarning('Erro:', 'Nenhum registro encontrado', parent=root)
                else:
                    tree_principal.delete(*tree_principal.get_children())
                    cursor.execute("SELECT * FROM dbo.chamados WHERE data_encerramento LIKE '%' + ? + '%' AND solicitante =? ORDER BY id_chamado DESC",
                        (filtro, usuariologado,))
                    for row in cursor:
                        if row[12] == None:
                            row[12] = ''
                        tree_principal.insert('', 'end', text=" ",
                                              values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                              tags=('par',))
            else:
                cursor.execute("SELECT * FROM dbo.chamados WHERE data_encerramento LIKE '%' + ? + '%' ORDER BY id_chamado DESC",(filtro,))
                busca = cursor.fetchone()
                if busca is None:
                    messagebox.showwarning('Erro:', 'Nenhum registro encontrado', parent=root)
                else:
                    tree_principal.delete(*tree_principal.get_children())
                    cursor.execute("SELECT * FROM dbo.chamados WHERE data_encerramento LIKE '%' + ? + '%' ORDER BY id_chamado DESC",(filtro,))
                    for row in cursor:
                        if row[12] == None:
                            row[12] = ''
                        tree_principal.insert('', 'end', text=" ",
                                              values=(row[0], row[2], row[1], row[4], row[5], row[6], row[7], row[14], row[12]),
                                              tags=('par',))

    def drop_selecao_busca(event):
        # ///////////////////REMOVE BUSCA///////////////////
        if clique_busca.get() == "Remover Filtro":
            atualizar_lista_principal()
    def ferramentas():
        def trocasenha():
            root3 = Toplevel()
            root3.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())
            root3.unbind_class("Button", "<Key-space>")
            root3.focus_force()
            root3.grab_set()
            def confirmar():
                senha_atual = esenha_antiga.get()
                senha_nova = esenha_nova.get()
                senha_confirma = esenha_confirma.get()
                user = usuariologado
                if senha_atual == "" or senha_nova == "" or senha_confirma == "":
                    messagebox.showwarning('Erro:','Preencha todos os campos!', parent=root3)
                else:
                    r = cursor.execute("SELECT * FROM mp.dbo.analista WHERE nome_analista=?", (user,))
                    for login in r.fetchall():
                            filtro_pwd = login[3]
                            if filtro_pwd == senha_nova and senha_nova == senha_confirma:
                                messagebox.showwarning('Erro', 'A nova senha deve ser diferente da atual.', parent=root3)
                            elif filtro_pwd != senha_atual:
                                messagebox.showwarning('Erro:', 'Senha atual inválida.', parent=root3)
                            elif senha_nova != senha_confirma:
                                messagebox.showwarning('Erro:', 'Erro ao confirmar a nova senha.', parent=root3)
                            elif filtro_pwd == senha_atual and senha_nova == senha_confirma:
                                cursor.execute("UPDATE mp.dbo.analista SET senha=? WHERE nome_analista=?", (senha_confirma, user,))
                                conectar.commit()
                                messagebox.showwarning('Sucesso:', 'Senha alterada com sucesso!', parent=root3)
                                root3.destroy()
                                root2.destroy()
            def sair():
                root3.destroy()

            def confirmar_bind(event):
                confirmar()

            frame0 = Frame(root3, bg='#ffffff')
            frame0.grid(row=0, column=0, stick='nsew')
            root3.grid_rowconfigure(0, weight=1)
            root3.grid_columnconfigure(0, weight=1)
            frame1 = Frame(frame0, bg="#232729")
            frame1.pack(side=TOP, fill=X, expand=False, anchor='center')
            frame2 = Frame(frame0, bg='#ffffff')
            frame2.pack(side=TOP, fill=X, expand=False, anchor='center', pady=10)
            frame3 = Frame(frame0, bg='#ffffff')
            frame3.pack(side=TOP, fill=X, expand=False, anchor='center')
            frame4 = Frame(frame0, bg='#232729')
            frame4.pack(side=TOP, fill=X, expand=True, anchor='center')

            image_trocasenha2 = Image.open('imagens\\trocasenha2.png')
            resize_trocasenha2 = image_trocasenha2.resize((35, 35))
            nova_image_trocasenha2 = ImageTk.PhotoImage(resize_trocasenha2)

            lbllogin = Label(frame1, image=nova_image_trocasenha2, text=" Alterar Senha", compound="left",
                             bg='#232729',
                             fg='#FFFFFF', font=fonte_titulos)
            lbllogin.photo = nova_image_trocasenha2
            lbllogin.grid(row=0, column=1)
            frame1.grid_columnconfigure(0, weight=1)
            frame1.grid_columnconfigure(2, weight=1)

            Label(frame2, text="Senha Atual:", font=fonte_padrao, bg='#ffffff', fg='#000000').grid(row=0, column=1,
                                                                                             sticky="ew")

            esenha_antiga = Entry(frame2, show="*", width=20, font=fonte_padrao)
            esenha_antiga.grid(row=0, column=2, sticky="w", padx=5, pady=10)
            esenha_antiga.focus_force()
            esenha_antiga.bind("<Return>", confirmar_bind)

            Label(frame2, text="Nova Senha:", font=fonte_padrao, bg='#ffffff', fg='#000000').grid(row=1, column=1,
                                                                                             sticky="ew")
            esenha_nova = Entry(frame2, show="*", width=20, font=fonte_padrao)
            esenha_nova.grid(row=1, column=2, sticky="w", padx=5, pady=10)
            esenha_nova.bind("<Return>", confirmar_bind)

            Label(frame2, text="Confirmar Nova Senha:", font=fonte_padrao, bg='#ffffff', fg='#000000').grid(row=2, column=1,
                                                                                             sticky="ew")
            esenha_confirma = Entry(frame2, show="*", width=20, font=fonte_padrao)
            esenha_confirma.grid(row=2, column=2, sticky="w", padx=5, pady=10)
            esenha_confirma.bind("<Return>", confirmar_bind)

            frame2.grid_columnconfigure(0, weight=1)
            frame2.grid_columnconfigure(3, weight=1)

            bt1 = Button(frame3, text='Confirmar', bg='#232729', fg='#FFFFFF', activebackground='#232729',
                         activeforeground="#FFFFFF", highlightthickness=0, width=10, relief=RIDGE, command=confirmar,
                         font=fonte_padrao)
            bt1.grid(row=0, column=1, pady=5, padx=5)
            bt2 = Button(frame3, text='Sair', width=10, relief=RIDGE, command=sair, font=fonte_padrao)
            bt2.grid(row=0, column=2, pady=5, padx=5)
            frame3.grid_columnconfigure(0, weight=1)
            frame3.grid_columnconfigure(3, weight=1)

            Label(frame4, text="", bg='#232729', fg='#FFFFFF', font=fonte_padrao).grid(row=0, column=1, sticky="ew")
            frame4.grid_columnconfigure(0, weight=1)
            frame4.grid_columnconfigure(2, weight=1)
            '''root3.update()
            largura = frame0.winfo_width()
            altura = frame0.winfo_height()
            print(largura, altura)'''
            window_width = 340
            window_height = 247
            screen_width = root2.winfo_screenwidth()
            screen_height = root2.winfo_screenheight()
            x_cordinate = int((screen_width / 2) - (window_width / 2))
            y_cordinate = int((screen_height / 2) - (window_height / 2))
            root3.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
            root3.resizable(0, 0)
            root3.iconbitmap('imagens\\ico.ico')
            root3.title(titulo_todos)

        root2 = Toplevel()
        root2.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())
        root2.unbind_class("Button", "<Key-space>")
        root2.focus_force()
        root2.grab_set()

        frame0 = Frame(root2, bg='#ffffff')
        frame0.grid(row=0, column=0, stick='nsew')
        root2.grid_rowconfigure(0, weight=1)
        root2.grid_columnconfigure(0, weight=1)
        frame1 = Frame(frame0, bg="#232729")
        frame1.pack(side=TOP, fill=X, expand=False, anchor='center', pady=(0,20))
        frame2 = Frame(frame0, bg='#ffffff')
        frame2.pack(side=TOP, fill=X, expand=False, anchor='center', pady=6)
        frame3 = Frame(frame0, bg='#232729')
        frame3.pack(side=TOP, fill=X, expand=False, anchor='center', pady=(20,0))

        lblferr = Label(frame1, image=nova_image_ferramentas, text=" Ferramentas", compound="left", bg='#232729',
                         fg='#FFFFFF', font=fonte_titulos)
        lblferr.grid(row=0, column=1)
        frame1.grid_columnconfigure(0, weight=1)
        frame1.grid_columnconfigure(2, weight=1)

        def muda_trocasenha(e):
            image_trocasenha = Image.open('imagens\\trocasenha_over.png')
            resize_trocasenha = image_trocasenha.resize((55, 55))
            nova_image_trocasenha = ImageTk.PhotoImage(resize_trocasenha)
            btntrocasenha.photo = nova_image_trocasenha
            btntrocasenha.config(image=nova_image_trocasenha, fg='#7c7c7c')
        def volta_trocasenha(e):
            image_trocasenha = Image.open('imagens\\trocasenha.png')
            resize_trocasenha = image_trocasenha.resize((55, 55))
            nova_image_trocasenha = ImageTk.PhotoImage(resize_trocasenha)
            btntrocasenha.photo = nova_image_trocasenha
            btntrocasenha.config(image=nova_image_trocasenha, fg='#232729')
        image_trocasenha = Image.open('imagens\\trocasenha.png')
        resize_trocasenha = image_trocasenha.resize((55, 55))
        nova_image_trocasenha = ImageTk.PhotoImage(resize_trocasenha)
        btntrocasenha = Button(frame2, image=nova_image_trocasenha, text="Alterar Senha", compound="top",
                          font=fonte_titulos, bg="#fff3ff", fg='#232729', command=trocasenha, borderwidth=0,
                          relief=RIDGE,
                          activebackground="#ffffff", activeforeground="#7c7c7c")
        btntrocasenha.photo = nova_image_trocasenha
        btntrocasenha.grid(row=0, column=1, padx=15)
        btntrocasenha.bind("<Enter>", muda_trocasenha)
        btntrocasenha.bind("<Leave>", volta_trocasenha)

        def muda_relatorio(e):
            image_relatorio = Image.open('imagens\\relatorio_over.png')
            resize_relatorio = image_relatorio.resize((55, 55))
            nova_image_relatorio = ImageTk.PhotoImage(resize_relatorio)
            btnrelatorio.photo = nova_image_relatorio
            btnrelatorio.config(image=nova_image_relatorio, fg='#7c7c7c')
        def volta_relatorio(e):
            image_relatorio = Image.open('imagens\\relatorio.png')
            resize_relatorio = image_relatorio.resize((55, 55))
            nova_image_relatorio = ImageTk.PhotoImage(resize_relatorio)
            btnrelatorio.photo = nova_image_relatorio
            btnrelatorio.config(image=nova_image_relatorio, fg='#232729')
        image_relatorio = Image.open('imagens\\relatorio.png')
        resize_relatorio = image_relatorio.resize((55, 55))
        nova_image_relatorio = ImageTk.PhotoImage(resize_relatorio)
        btnrelatorio = Button(frame2, image=nova_image_relatorio, text="Relatórios", compound="top",
                          font=fonte_titulos, bg="#fff3ff", fg='#232729', command="trocasenha", borderwidth=0,
                          relief=RIDGE,
                          activebackground="#ffffff", activeforeground="#7c7c7c")
        btnrelatorio.photo = nova_image_relatorio
        btnrelatorio.grid(row=0, column=2, padx=15)
        btnrelatorio.bind("<Enter>", muda_relatorio)
        btnrelatorio.bind("<Leave>", volta_relatorio)
        frame2.grid_columnconfigure(0, weight=1)
        frame2.grid_columnconfigure(3, weight=1)

        Label(frame3, text="", bg='#232729', fg='#FFFFFF', font=fonte_padrao).grid(row=0, column=1, sticky="ew")
        frame3.grid_columnconfigure(0, weight=1)
        frame3.grid_columnconfigure(2, weight=1)
        '''root2.update()
        largura = frame0.winfo_width()
        altura = frame0.winfo_height()
        print(largura, altura)'''
        window_width = 400
        window_height = 198
        screen_width = root2.winfo_screenwidth()
        screen_height = root2.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        root2.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        root2.resizable(0, 0)
        root2.iconbitmap('imagens\\ico.ico')
        root2.title(titulo_todos)
    # /////////////////////////////FIM FERRAMENTAS/////////////////////////////


    # -------------------FRAME PRINCIPAL-------------------#
    frame0 = Frame(root, bg="#3f464a")
    frame0.grid(row=0, column=0, stick='nsew')
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    frame1 = Frame(frame0, bg="#ffffff")
    frame1.pack(side=TOP, fill=X, expand=False, anchor='center')
    frame2 = Frame(frame0, bg="#232729")
    frame2.pack(side=TOP, fill=X, expand=False, anchor='n')
    frame3 = Frame(frame0, highlightbackground="#2c2c2c", highlightcolor="#2c2c2c", highlightthickness=1, borderwidth=2)
    frame3.pack(side=TOP, fill=BOTH, expand=True, anchor='n')
    frame4 = Frame(frame0, bg="#232729")
    frame4.pack(side=TOP, fill=X, expand=False, anchor='n')

    # -------------------FRAME1-------------------#
    image_logo = Image.open('imagens\\logo.png')
    resize_logo = image_logo.resize((800, 137))
    nova_image_logo = ImageTk.PhotoImage(resize_logo)
    lbl1 = Label(frame1, image=nova_image_logo, bg="#ffffff")
    lbl1.photo = nova_image_logo
    lbl1.grid(row=0, column=1)
    frame1.grid_columnconfigure(0, weight=1)
    frame1.grid_columnconfigure(2, weight=1)

    # -------------------FRAME2-------------------#
    def muda_login(e):
        image_login = Image.open('imagens\\login_over.png')
        resize_login = image_login.resize((35, 35))
        nova_image_login = ImageTk.PhotoImage(resize_login)
        btnlogin.photo = nova_image_login
        btnlogin.config(image=nova_image_login, fg='#7c7c7c')
    def volta_login(e):
        image_login = Image.open('imagens\\login.png')
        resize_login = image_login.resize((35, 35))
        nova_image_login = ImageTk.PhotoImage(resize_login)
        btnlogin.photo = nova_image_login
        btnlogin.config(image=nova_image_login, fg='#ffffff')
    image_login = Image.open('imagens\\login.png')
    resize_login = image_login.resize((35, 35))
    nova_image_login = ImageTk.PhotoImage(resize_login)
    btnlogin = Button(frame2, image=nova_image_login, text="Trocar Usuário", compound="left",
                      font=fonte_padrao, bg="#232729", fg='#FFFFFF', command=login_interno, borderwidth=0, relief=RIDGE,
                      activebackground="#232729", activeforeground="#232729")
    btnlogin.photo = nova_image_login
    btnlogin.grid(row=0, column=1, pady=2, padx=10)
    btnlogin.bind("<Enter>", muda_login)
    btnlogin.bind("<Leave>", volta_login)

    def muda_chamado(e):
        image_chamado = Image.open('imagens\\chamado_over.png')
        resize_chamado = image_chamado.resize((30, 35))
        nova_image_chamado = ImageTk.PhotoImage(resize_chamado)
        btnchamado.photo = nova_image_chamado
        btnchamado.config(image=nova_image_chamado, fg='#7c7c7c')
    def volta_chamado(e):
        image_chamado = Image.open('imagens\\chamado.png')
        resize_chamado = image_chamado.resize((30, 35))
        nova_image_chamado = ImageTk.PhotoImage(resize_chamado)
        btnchamado.photo = nova_image_chamado
        btnchamado.config(image=nova_image_chamado, fg='#ffffff')

    image_chamado = Image.open('imagens\\chamado.png')
    resize_chamado = image_chamado.resize((30, 35))
    nova_image_chamado = ImageTk.PhotoImage(resize_chamado)
    btnchamado = Button(frame2, image=nova_image_chamado, text=" + Abrir Chamado", compound="left", font=fonte_padrao,
                        bg="#232729", fg='#FFFFFF', command=abrirchamado, borderwidth=0, relief=RIDGE,
                        activebackground="#232729", activeforeground="#232729")
    btnchamado.photo = nova_image_chamado
    btnchamado.grid(row=0, column=2, pady=2, padx=10)
    btnchamado.bind("<Enter>", muda_chamado)
    btnchamado.bind("<Leave>", volta_chamado)

    def muda_atendimento(e):
        image_atendimento = Image.open('imagens\\atendimento_over.png')
        resize_atendimento = image_atendimento.resize((30, 35))
        nova_image_atendimento = ImageTk.PhotoImage(resize_atendimento)
        btnatendimento.photo = nova_image_atendimento
        btnatendimento.config(image=nova_image_atendimento, fg='#7c7c7c')
    def volta_atendimento(e):
        image_atendimento = Image.open('imagens\\atendimento.png')
        resize_atendimento = image_atendimento.resize((30, 35))
        nova_image_atendimento = ImageTk.PhotoImage(resize_atendimento)
        btnatendimento.photo = nova_image_atendimento
        btnatendimento.config(image=nova_image_atendimento, fg='#ffffff')

    image_atendimento = Image.open('imagens\\atendimento.png')
    resize_atendimento = image_atendimento.resize((30, 35))
    nova_image_atendimento = ImageTk.PhotoImage(resize_atendimento)
    btnatendimento = Button(frame2, image=nova_image_atendimento, text=" Atendimento", compound="left",
                            font=fonte_padrao, bg="#232729", fg='#FFFFFF', command=atendimento, borderwidth=0,
                            relief=RIDGE, activebackground="#232729", activeforeground="#232729")
    btnatendimento.photo = nova_image_atendimento
    btnatendimento.grid(row=0, column=3, pady=2, padx=10)
    btnatendimento.bind("<Enter>", muda_atendimento)
    btnatendimento.bind("<Leave>", volta_atendimento)

    def muda_visualizarchamado(e):
        image_visualizarchamado = Image.open('imagens\\visualizar_over.png')
        resize_visualizarchamado = image_visualizarchamado.resize((30, 25))
        nova_image_visualizarchamado = ImageTk.PhotoImage(resize_visualizarchamado)
        btnvisualizarchamado.photo = nova_image_visualizarchamado
        btnvisualizarchamado.config(image=nova_image_visualizarchamado, fg='#7c7c7c')
    def volta_visualizarchamado(e):
        image_visualizarchamado = Image.open('imagens\\visualizar.png')
        resize_visualizarchamado = image_visualizarchamado.resize((30, 25))
        nova_image_visualizarchamado = ImageTk.PhotoImage(resize_visualizarchamado)
        btnvisualizarchamado.photo = nova_image_visualizarchamado
        btnvisualizarchamado.config(image=nova_image_visualizarchamado, fg='#ffffff')

    image_visualizarchamado = Image.open('imagens\\visualizar.png')
    resize_visualizarchamado = image_visualizarchamado.resize((30, 25))
    nova_image_visualizarchamado = ImageTk.PhotoImage(resize_visualizarchamado)
    btnvisualizarchamado = Button(frame2, image=nova_image_visualizarchamado, text=" Visualizar\Editar Chamado",
                                  compound="left", font=fonte_padrao, bg="#232729", fg='#FFFFFF', command=visualizar_chamado,
                                  borderwidth=0, relief=RIDGE, activebackground="#232729", activeforeground="#232729")
    btnvisualizarchamado.photo = nova_image_visualizarchamado
    btnvisualizarchamado.grid(row=0, column=4, pady=2, padx=10)
    btnvisualizarchamado.bind("<Enter>", muda_visualizarchamado)
    btnvisualizarchamado.bind("<Leave>", volta_visualizarchamado)

    def muda_ferramentas(e):
        image_ferramentas = Image.open('imagens\\ferramentas_over.png')
        resize_ferramentas = image_ferramentas.resize((35, 35))
        nova_image_ferramentas = ImageTk.PhotoImage(resize_ferramentas)
        btnferramentas.photo = nova_image_ferramentas
        btnferramentas.config(image=nova_image_ferramentas, fg='#7c7c7c')
    def volta_ferramentas(e):
        image_ferramentas = Image.open('imagens\\ferramentas.png')
        resize_ferramentas = image_ferramentas.resize((35, 35))
        nova_image_ferramentas = ImageTk.PhotoImage(resize_ferramentas)
        btnferramentas.photo = nova_image_ferramentas
        btnferramentas.config(image=nova_image_ferramentas, fg='#ffffff')

    image_ferramentas = Image.open('imagens\\ferramentas.png')
    resize_ferramentas = image_ferramentas.resize((35, 35))
    nova_image_ferramentas = ImageTk.PhotoImage(resize_ferramentas)
    btnferramentas = Button(frame2, image=nova_image_ferramentas, text=" Ferramentas", compound="left",
                            font=fonte_padrao, bg="#232729", fg='#FFFFFF', command=ferramentas,
                            borderwidth=0, relief=RIDGE, activebackground="#232729", activeforeground="#7c7c7c")
    btnferramentas.photo = nova_image_ferramentas
    btnferramentas.grid(row=0, column=5, pady=2, padx=10)
    btnferramentas.bind("<Enter>", muda_ferramentas)
    btnferramentas.bind("<Leave>", volta_ferramentas)

    clique_busca = StringVar()
    drop_busca = OptionMenu(frame2, clique_busca, 'Status', 'Nº Chamado', 'Solicitante', 'Tipo', 'Responsável','Data Encerramento', 'Remover Filtro', command=drop_selecao_busca)
    drop_busca.config(font=fonte_padrao, bg='#232729', fg='#FFFFFF', activebackground='#232729', activeforeground="#FFFFFF", highlightthickness=0, relief=RIDGE, width=15)
    drop_busca['menu'].insert_separator(6)
    drop_busca.grid(row=0, column=7, padx=(0,2))
    clique_busca.set('Filtrar por...')
    ent_busca = Entry(frame2, width=30, font=fonte_padrao, justify='center')
    ent_busca.grid(row=0, column=8, ipady=4)
    ent_busca.bind('<Return>', pesquisar_bind)

    def muda_busca(e):
        image_busca = Image.open('imagens\\lupa_over.png')
        resize_busca = image_busca.resize((25, 25))
        nova_image_busca = ImageTk.PhotoImage(resize_busca)
        btn_busca.photo = nova_image_busca
        btn_busca.config(image=nova_image_busca, fg='#7c7c7c')
    def volta_busca(e):
        image_busca = Image.open('imagens\\lupa.png')
        resize_busca = image_busca.resize((25, 25))
        nova_image_busca = ImageTk.PhotoImage(resize_busca)
        btn_busca.photo = nova_image_busca
        btn_busca.config(image=nova_image_busca, fg='#ffffff')
    image_busca = Image.open('imagens\\lupa.png')
    resize_busca = image_busca.resize((25, 25))
    nova_image_busca = ImageTk.PhotoImage(resize_busca)
    btn_busca = Button(frame2, image=nova_image_busca, bg="#232729", fg='#FFFFFF', command=pesquisar,
                            borderwidth=0, relief=RIDGE, activebackground="#232729", activeforeground="#7c7c7c")
    btn_busca.photo = nova_image_busca
    btn_busca.grid(row=0, column=9, padx=(4,30))
    btn_busca.bind("<Enter>", muda_busca)
    btn_busca.bind("<Leave>", volta_busca)


    image_usuario = Image.open('imagens\\usuario.png')
    resize_usuario = image_usuario.resize((30, 30))
    nova_image_usuario = ImageTk.PhotoImage(resize_usuario)
    lbluserlogado = Label(frame2, image=nova_image_usuario, text=usuariologado, compound="left", font=fonte_padrao, bg="#232729", fg='#fff000')
    lbluserlogado.photo = nova_image_ferramentas
    lbluserlogado.grid(row=0, column=10)


    frame2.grid_columnconfigure(6, weight=1)
    frame2.grid_columnconfigure(6, weight=1)

    # -------------------FRAME3-------------------#
    style = ttk.Style()
    # style.theme_use('default')
    style.configure('Treeview',
                    background='#ffffff',
                    rowheight=24,
                    fieldbackground='#ffffff',
                    font=fonte_padrao)
    style.configure("Treeview.Heading",
                    foreground='#000000',
                    background="#ffffff",
                    font=fonte_padrao)
    style.map('Treeview', background=[('selected', '#6f7477')])

    tree_principal = ttk.Treeview(frame3, selectmode='browse')
    vsb = ttk.Scrollbar(frame3, orient="vertical", command=tree_principal.yview)
    vsb.pack(side=RIGHT, fill='y')
    tree_principal.configure(yscrollcommand=vsb.set)
    vsbx = ttk.Scrollbar(frame3, orient="horizontal", command=tree_principal.xview)
    vsbx.pack(side=BOTTOM, fill='x')
    tree_principal.configure(xscrollcommand=vsbx.set)
    tree_principal.pack(side=LEFT, fill=BOTH, expand=True, anchor='n')
    tree_principal["columns"] = ("1", "2", "3", "4", "5", "6", "7", "8", "9")
    tree_principal['show'] = 'headings'
    tree_principal.column("1", width=20, anchor='c')
    tree_principal.column("2", width=50, anchor='c')
    tree_principal.column("3", width=50, anchor='c')
    tree_principal.column("4", width=50, anchor='c')
    tree_principal.column("5", width=50, anchor='c')
    tree_principal.column("6", width=50, anchor='c')
    tree_principal.column("7", width=250, anchor='c')
    tree_principal.column("8", width=50, anchor='c')
    tree_principal.column("9", width=50, anchor='c')
    tree_principal.heading("1", text="Nº Chamado")
    tree_principal.heading("2", text="Data de Abertura")
    tree_principal.heading("3", text="Solicitante")
    tree_principal.heading("4", text="Ocorrência")
    tree_principal.heading("5", text="Tipo")
    tree_principal.heading("6", text="Setor")
    tree_principal.heading("7", text="Título")
    tree_principal.heading("8", text="Status")
    tree_principal.heading("9", text="Responsável")
    tree_principal.tag_configure('par', background='#e9e9e9')
    tree_principal.tag_configure('impar', background='#ffffff')
    tree_principal.bind("<Double-1>", duploclique_tree_principal)
    frame3.grid_columnconfigure(0, weight=1)
    frame3.grid_columnconfigure(3, weight=1)

    # -------------------FRAME4-------------------#
    lbllacuna = Label(frame4, text='', bg="#232729")
    lbllacuna.grid(row=0, column=1)
    frame4.grid_columnconfigure(0, weight=1)
    frame4.grid_columnconfigure(3, weight=1)
    contador()
    atualizar_lista_principal()
    root.title(titulo_todos)
    root.state('zoomed')
    root.iconbitmap('imagens\\ico.ico')
    root.mainloop()

#/////////////////////////////FIM PRINCIPAL/////////////////////////////

# /////////////////////////////INICIO LOGIN/////////////////////////////
def login():
    splash_root.destroy()
    global root2
    root2 = Tk()
    root2.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())
    root2.unbind_class("Button", "<Key-space>")
    root2.focus_force()
    root2.grab_set()

    def sair():
        root2.destroy()

    def entrar():
        user = euser.get()
        senha = esenha.get()
        if user == "" or senha == "":
            messagebox.showwarning('Login: Erro', 'Digite o Usuário ou Senha.', parent=root2)
        else:
            if clique.get() == "Usuário":
                server_name = '192.168.1.19'
                domain_name = 'gvdobrasil'
                server = Server(server_name, get_info=ALL)
                try:
                    Connection(server, user='{}\\{}'.format(domain_name, user), password=senha, authentication=NTLM,
                               auto_bind=True)
                    global nivel_acesso
                    nivel_acesso = 0
                    global usuariologado
                    usuariologado = user
                    principal()
                except:
                    messagebox.showwarning('Login: Erro', 'Usuário ou senha inválidos.', parent=root2)
            else:
                r = cursor.execute("SELECT * FROM dbo.analista WHERE login=?", (user,))
                result = r.fetchone()
                if result is None:
                    messagebox.showwarning('Login: Erro', 'Usuário ou Senha inválidos.', parent=root2)
                else:
                    r = cursor.execute("SELECT * FROM dbo.analista WHERE login=?", (user,))
                    for login in r.fetchall():
                        filtro_user = login[1]
                        filtro_pwd = login[3]
                        if filtro_user == user and filtro_pwd == senha:
                            nivel_acesso = 1
                            usuariologado = login[2]
                            contador()
                            principal()
                        else:
                            messagebox.showwarning('Login: Erro', 'Usuário ou Senha inválidos.', parent=root2)

    def entrar_bind(event):
        user = euser.get()
        senha = esenha.get()
        r = cursor.execute("SELECT * FROM dbo.analista WHERE login=?", (user,))
        result = r.fetchone()
        if result != None:
            clique.set("Analista")
        if user == "" or senha == "":
            messagebox.showwarning('Login: Erro', 'Digite o Usuário ou Senha.', parent=root2)
        else:
            if clique.get() == "Usuário":
                server_name = '192.168.1.19'
                domain_name = 'gvdobrasil'
                server = Server(server_name, get_info=ALL)
                try:
                    Connection(server, user='{}\\{}'.format(domain_name, user), password=senha, authentication=NTLM,
                               auto_bind=True)
                    global nivel_acesso
                    nivel_acesso = 0
                    global usuariologado
                    usuariologado = user
                    principal()
                except:
                    messagebox.showwarning('Login: Erro', 'Usuário ou senha inválidos.', parent=root2)
            else:
                r = cursor.execute("SELECT * FROM dbo.analista WHERE login=?", (user,))
                result = r.fetchone()
                if result is None:
                    messagebox.showwarning('Login: Erro', 'Usuário ou Senha inválidos.', parent=root2)
                else:
                    r = cursor.execute("SELECT * FROM dbo.analista WHERE login=?", (user,))
                    for login in r.fetchall():
                        filtro_user = login[1]
                        filtro_pwd = login[3]
                        if filtro_user == user and filtro_pwd == senha:
                            nivel_acesso = 1
                            usuariologado = login[2]
                            principal()
                        else:
                            messagebox.showwarning('Login: Erro', 'Usuário ou Senha inválidos.', parent=root2)
    frame0 = Frame(root2, bg='#ffffff')
    frame0.grid(row=0, column=0, stick='nsew')
    root2.grid_rowconfigure(0, weight=1)
    root2.grid_columnconfigure(0, weight=1)
    frame1 = Frame(frame0, bg="#232729")
    frame1.pack(side=TOP, fill=X, expand=False, anchor='center')
    frame2 = Frame(frame0, bg='#ffffff')
    frame2.pack(side=TOP, fill=X, expand=False, anchor='center', pady=10)
    frame3 = Frame(frame0, bg='#ffffff')
    frame3.pack(side=TOP, fill=X, expand=False, anchor='center')
    frame4 = Frame(frame0, bg='#ffffff')
    frame4.pack(side=TOP, fill=X, expand=False, anchor='center', pady=10)
    frame5 = Frame(frame0, bg='#232729')
    frame5.pack(side=TOP, fill=X, expand=False, anchor='center')

    image_login = Image.open('imagens\\login.png')
    resize_login = image_login.resize((35, 35))
    nova_image_login = ImageTk.PhotoImage(resize_login)

    lbllogin = Label(frame1, image=nova_image_login, text=" Login", compound="left", bg='#232729',
          fg='#FFFFFF', font=fonte_titulos)
    lbllogin.photo = nova_image_login
    lbllogin.grid(row=0, column=1)
    frame1.grid_columnconfigure(0, weight=1)
    frame1.grid_columnconfigure(2, weight=1)

    Label(frame2, text="Modo de Acesso:", bg='#ffffff', fg='#000000', font=fonte_padrao).grid(row=0, column=1,
                                                                                              sticky="w")
    clique = StringVar()
    clique.set("Usuário")
    drop = OptionMenu(frame2, clique, "Usuário", "Responsável")
    drop.config(bg='#232729', fg='#FFFFFF', activebackground='#232729', activeforeground="#FFFFFF",
                highlightthickness=0, relief=RIDGE, width=9, font=fonte_padrao)
    drop.grid(row=0, column=2, pady=10)
    frame2.grid_columnconfigure(0, weight=1)
    frame2.grid_columnconfigure(3, weight=1)

    Label(frame3, text="Usuário:", bg='#ffffff', fg='#000000', font=fonte_padrao).grid(row=1, column=1, sticky="w")
    euser = Entry(frame3, width=30, font=fonte_padrao)
    euser.grid(row=1, column=2, sticky="w", padx=5, pady=10)
    euser.focus_force()
    euser.bind("<Return>", entrar_bind)
    Label(frame3, text="Senha:", font=fonte_padrao, bg='#ffffff', fg='#000000').grid(row=2, column=1, sticky="w")
    esenha = Entry(frame3, show="*", width=30, font=fonte_padrao)
    esenha.grid(row=2, column=2, sticky="w", padx=5, pady=10)
    esenha.bind("<Return>", entrar_bind)
    frame3.grid_columnconfigure(0, weight=1)
    frame3.grid_columnconfigure(3, weight=1)

    bt1 = Button(frame4, text='Entrar', bg='#232729', fg='#FFFFFF', activebackground='#3f464a',
                 activeforeground="#FFFFFF", highlightthickness=0, width=10, relief=RIDGE, command=entrar,
                 font=fonte_padrao)
    bt1.grid(row=0, column=1, pady=5, padx=5)

    bt2 = Button(frame4, text='Sair', width=10, relief=RIDGE, command=sair, font=fonte_padrao)
    bt2.grid(row=0, column=2, pady=5, padx=5)
    frame4.grid_columnconfigure(0, weight=1)
    frame4.grid_columnconfigure(3, weight=1)

    Label(frame5, text="", bg='#232729', fg='#FFFFFF', font=fonte_padrao).grid(row=0, column=1, sticky="ew")
    frame5.grid_columnconfigure(0, weight=1)
    frame5.grid_columnconfigure(2, weight=1)
    '''root2.update()
    largura = frame0.winfo_width()
    altura = frame0.winfo_height()
    print(largura, altura)'''
    window_width = 300
    window_height = 275
    screen_width = root2.winfo_screenwidth()
    screen_height = root2.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    root2.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
    root2.resizable(0, 0)
    root2.iconbitmap('imagens\\ico.ico')
    root2.title(titulo_todos)
# /////////////////////////////FIM LOGIN/////////////////////////////


#/////////////////////////////ROOT SPLASH/////////////////////////////
splash_root =Tk()
frame0 = Frame(splash_root, bg="#000000")
frame0.grid(row=0, column=0, stick='nsew')
splash_root.grid_rowconfigure(0, weight=1)
splash_root.grid_columnconfigure(0, weight=1)

image_splash = Image.open('imagens\\splash.png')
resize_splash = image_splash.resize((490, 430))
nova_image_splash = ImageTk.PhotoImage(resize_splash)
lbl_splash = Label(frame0, image=nova_image_splash)
lbl_splash.pack()
lbl_splash.photo = nova_image_splash

#splash_root.update()
#largura = splash_root.winfo_width()
#altura = splash_root.winfo_height()
#print(largura, altura)
window_width = 490
window_height = 430
screen_width = splash_root.winfo_screenwidth()
screen_height = splash_root.winfo_screenheight()
x_cordinate = int((screen_width / 2) - (window_width / 2))
y_cordinate = int((screen_height / 2) - (window_height / 2))
splash_root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
splash_root.resizable(0, 0)
splash_root.overrideredirect(True)
splash_root.after(4000, login)
#/////////////////////////////FIM ROOT SPLASH/////////////////////////////

#/////////////////////////////BANCO DE DADOS/////////////////////////////

# Banco de Dados
'''
server = 'tcp:GVBRSRV01,1433'
database = 'helpdesk'
username = 'sa'
password = 'gv2K20ADM'
conectar = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = conectar.cursor()
'''
'''
server = 'GVBRSRV01\SQLEXPRESS2014'
database = 'helpdesk'
conectar = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + '; Trusted_Connection=yes')
cursor = conectar.cursor()
'''
server = '192.168.1.19\SQLEXPRESS2014'
database = 'mp'
username = 'acesso_rede'
password = '61765561ic'
conectar = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = conectar.cursor()
#/////////////////////////////FIM BANCO DE DADOS/////////////////////////////
mainloop()