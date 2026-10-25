from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
import sqlite3, random, csv, os, webbrowser, urllib.parse
from datetime import datetime

DB_PATH = "ivo_colis.db"
TARIFS = {"Abidjan":1000,"Bingerville":1000,"Grand-Bassam":1500,"Dabou":1500,"Daloa":2500,"Bouake":2500,"Yamoussoukro":2500,"Korhogo":3000,"San Pedro":3000,"Autre":2000}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS commandes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, code TEXT, expediteur TEXT, tel_exp TEXT,
                  destinataire TEXT, tel_dest TEXT, adresse TEXT, ville TEXT,
                  description TEXT, montant TEXT, frais_liv TEXT, statut TEXT, livreur TEXT)""")
    conn.commit()
    conn.close()

init_db()
VILLES = list(TARIFS.keys())

class IVOVIPApp(App):
    def build(self):
        main = BoxLayout(orientation='vertical', padding=8, spacing=5)
        main.add_widget(Label(text="IVO COLIS EXPRESS VIP", size_hint_y=None, height=40, bold=True, font_size=16))
        menu = GridLayout(cols=3, size_hint_y=None, height=90, spacing=2)
        for txt, func in [("NOUVEAU", self.show_new), ("LISTE", self.show_list), ("LIVREUR", self.show_livreur), ("EXCEL", self.show_excel), ("CSV", self.show_csv), ("VIDER", self.clear_db_btn)]:
            b = Button(text=txt, font_size=11)
            b.bind(on_press=func)
            menu.add_widget(b)
        main.add_widget(menu)
        self.content = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.content.add_widget(self.grid)
        main.add_widget(self.content)
        self.last_code = ""; self.last_client = ""; self.last_tel = ""; self.last_ville = ""; self.last_montant = ""
        self.show_new(None)
        return main

    def clear_grid(self): self.grid.clear_widgets()

    def show_new(self, inst):
        self.clear_grid()
        self.grid.add_widget(Label(text="NOUVELLE COMMANDE", size_hint_y=None, height=30, bold=True))
        self.nom_exp = TextInput(hint_text="Nom vendeuse", size_hint_y=None, height=44)
        self.tel_exp = TextInput(hint_text="Tel vendeuse", size_hint_y=None, height=44)
        self.nom_dest = TextInput(hint_text="Nom client *", size_hint_y=None, height=44)
        self.tel_dest = TextInput(hint_text="Tel client *", size_hint_y=None, height=44)
        self.adresse = TextInput(hint_text="Adresse", size_hint_y=None, height=44)
        self.ville = Spinner(text="Abidjan", values=VILLES, size_hint_y=None, height=44)
        self.desc = TextInput(hint_text="Description colis", size_hint_y=None, height=44)
        self.montant = TextInput(hint_text="Montant a encaisser", input_filter='int', size_hint_y=None, height=44)
        self.lbl_prix = Label(text=f"Frais: {TARIFS['Abidjan']}F", size_hint_y=None, height=40, font_size=12)
        self.ville.bind(text=self.update_prix); self.montant.bind(text=self.update_prix)
        self.status = Label(text="Remplis et ENREGISTRER", size_hint_y=None, height=40)
        btn = Button(text="ENREGISTRER", size_hint_y=None, height=55, background_color=(0,0.7,0.3,1))
        btn.bind(on_press=self.save_cmd)
        btn_wa = Button(text="ENVOYER WHATSAPP", size_hint_y=None, height=55, background_color=(0.2,0.8,0.2,1))
        btn_wa.bind(on_press=self.send_whatsapp)
        for w in [self.nom_exp, self.tel_exp, self.nom_dest, self.tel_dest, self.adresse, self.ville, self.desc, self.montant, self.lbl_prix, btn, btn_wa, self.status]:
            self.grid.add_widget(w)

    def update_prix(self, inst, val):
        try:
            frais = TARIFS.get(self.ville.text, 2000)
            mont = int(self.montant.text) if self.montant.text and self.montant.text.isdigit() else 0
            self.lbl_prix.text = f"Frais {self.ville.text}: {frais}F | Montant: {mont}F | TOTAL: {frais+mont}F"
        except: pass

    def save_cmd(self, inst):
        if not self.nom_dest.text or not self.tel_dest.text:
            self.status.text = "Nom et tel client obligatoires!"; return
        code = f"IVO{random.randint(10000,99999)}"
        date = datetime.now().strftime("%d/%m/%Y %H:%M")
        frais = str(TARIFS.get(self.ville.text, 2000))
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("INSERT INTO commandes (date,code,expediteur,tel_exp,destinataire,tel_dest,adresse,ville,description,montant,frais_liv,statut,livreur) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (date, code, self.nom_exp.text, self.tel_exp.text, self.nom_dest.text, self.tel_dest.text, self.adresse.text, self.ville.text, self.desc.text, self.montant.text or "0", frais, "Enregistre", ""))
        conn.commit(); conn.close()
        self.last_code = code; self.last_client = self.nom_dest.text; self.last_tel = self.tel_dest.text; self.last_ville = self.ville.text; self.last_montant = self.montant.text or "0"
        self.status.text = f"OK Code {code} | Clique WHATSAPP"
        self.nom_dest.text = ""; self.tel_dest.text = ""; self.adresse.text = ""; self.desc.text = ""; self.montant.text = ""

    def send_whatsapp(self, inst):
        if not self.last_code: self.status.text = "Enregistre d'abord!"; return
        msg = f"Bonjour {self.last_client} ! Colis {self.last_code} arrive a {self.last_ville}. Montant: {self.last_montant}F + livraison. Le livreur vous appelle. Merci - IVO COLIS"
        try:
            tel = self.last_tel.strip().replace(" ","")
            if tel.startswith("0"): tel = "225" + tel[1:]
            if not tel.startswith("225"): tel = "225" + tel
            url = f"https://wa.me/{tel}?text={urllib.parse.quote(msg)}"
            webbrowser.open(url); self.status.text = f"WhatsApp ouvert pour {self.last_client}!"
        except: webbrowser.open(f"https://wa.me/?text={urllib.parse.quote(msg)}")

    def show_list(self, inst):
        self.clear_grid(); conn = sqlite3.connect(DB_PATH); rows = conn.execute("SELECT * FROM commandes ORDER BY id DESC LIMIT 100").fetchall(); conn.close()
        self.grid.add_widget(Label(text=f"LISTE {len(rows)} colis", size_hint_y=None, height=35, bold=True))
        for r in rows: self.grid.add_widget(Label(text=f"{r[2]} | {r[5]} {r[6]} | {r[8]} | {r[10]}F+f{r[11]} | {r[12]}", size_hint_y=None, height=38, font_size=11))

    def show_livreur(self, inst):
        self.clear_grid(); self.grid.add_widget(Label(text="MODE LIVREUR", size_hint_y=None, height=30, bold=True))
        self.nom_liv = TextInput(hint_text="Nom livreur", size_hint_y=None, height=44); self.code_liv = TextInput(hint_text="Code IVO", size_hint_y=None, height=44)
        self.info_liv = Label(text="Entre code et clique VOIR", size_hint_y=None, height=100)
        b1 = Button(text="VOIR INFOS", size_hint_y=None, height=50); b2 = Button(text="MARQUER LIVRE OK", size_hint_y=None, height=50, background_color=(0,0.7,0.3,1))
        b1.bind(on_press=self.voir_colis); b2.bind(on_press=self.marquer_livre); self.stat_liv = Label(text="Pret", size_hint_y=None, height=40)
        b_wa = Button(text="WHATSAPP CLIENT", size_hint_y=None, height=50, background_color=(0.2,0.8,0.2,1)); b_wa.bind(on_press=self.voir_colis_wa)
        for w in [self.nom_liv, self.code_liv, b1, self.info_liv, b2, b_wa, self.stat_liv]: self.grid.add_widget(w)

    def voir_colis(self, inst):
        code = self.code_liv.text.strip().upper(); conn = sqlite3.connect(DB_PATH); r = conn.execute("SELECT * FROM commandes WHERE code=?", (code,)).fetchone(); conn.close()
        if r: self.info_liv.text = f"{r[2]} {r[5]} {r[6]} {r[8]} {r[10]}F {r[12]}"; self.last_client=r[5]; self.last_tel=r[6]; self.last_code=r[2]; self.last_ville=r[8]; self.last_montant=r[10]
        else: self.info_liv.text = f"Code {code} introuvable"
    def voir_colis_wa(self, inst): self.voir_colis(inst); self.send_whatsapp(inst)
    def marquer_livre(self, inst):
        code=self.code_liv.text.strip().upper(); livreur=self.nom_liv.text
        if not code or not livreur: self.stat_liv.text="Entre code + nom"; return
        conn=sqlite3.connect(DB_PATH); conn.execute("UPDATE commandes SET statut='Livre', livreur=? WHERE code=?",(livreur,code)); conn.commit(); conn.close()
        self.stat_liv.text=f"{code} Livre par {livreur}"

    def show_excel(self, inst):
        self.clear_grid(); self.grid.add_widget(Label(text="EXPORT EXCEL", size_hint_y=None, height=30, bold=True))
        self.lbl_excel=Label(text="Clique", size_hint_y=None, height=60); b=Button(text="EXPORTER EXCEL", size_hint_y=None, height=60, background_color=(0,0.5,1,1)); b.bind(on_press=self.do_export_excel)
        self.grid.add_widget(b); self.grid.add_widget(self.lbl_excel)
    def do_export_excel(self, inst):
        try:
            import openpyxl; conn=sqlite3.connect(DB_PATH); rows=conn.execute("SELECT * FROM commandes ORDER BY id DESC").fetchall(); conn.close()
            if not rows: self.lbl_excel.text="Aucune"; return
            wb=openpyxl.Workbook(); ws=wb.active; ws.append(["Date","Code","Exp","TelExp","Dest","TelDest","Adr","Ville","Descr","Montant","Frais","Statut","Livreur"])
            for r in rows: ws.append(list(r[1:]))
            fname=f"IVO_{datetime.now().strftime('%d-%m_%H-%M')}.xlsx"
            for base in ["/storage/emulated/0/Download/","./"]:
                try: path=os.path.join(base,fname); wb.save(path); self.lbl_excel.text=f"OK {path} {len(rows)} lignes"; break
                except: continue
        except ImportError: self.lbl_excel.text="Pip install openpyxl"
        except Exception as e: self.lbl_excel.text=f"Erreur {e}"
    def show_csv(self, inst):
        self.clear_grid(); self.grid.add_widget(Label(text="EXPORT CSV", size_hint_y=None, height=30, bold=True))
        self.lbl_csv=Label(text="Clique", size_hint_y=None, height=60); b=Button(text="EXPORTER CSV", size_hint_y=None, height=60, background_color=(1,0.5,0,1)); b.bind(on_press=self.do_export_csv)
        self.grid.add_widget(b); self.grid.add_widget(self.lbl_csv)
    def do_export_csv(self, inst):
        conn=sqlite3.connect(DB_PATH); rows=conn.execute("SELECT * FROM commandes ORDER BY id DESC").fetchall(); conn.close()
        if not rows: self.lbl_csv.text="Aucune"; return
        fname=f"IVO_{datetime.now().strftime('%d-%m_%H-%M')}.csv"
        for base in ["/storage/emulated/0/Download/","./"]:
            try:
                path=os.path.join(base,fname)
                with open(path,'w',newline='',encoding='utf-8-sig') as f:
                    w=csv.writer(f); w.writerow(["Date","Code","Exp","TelExp","Dest","TelDest","Adr","Ville","Descr","Montant","Frais","Statut","Livreur"])
                    for r in rows: w.writerow(r[1:])
                self.lbl_csv.text=f"OK {path} {len(rows)} lignes"; break
            except: continue
    def clear_db_btn(self, inst):
        self.clear_grid(); self.grid.add_widget(Label(text="VIDER ?", size_hint_y=None, height=40, bold=True))
        b=Button(text="OUI VIDER", size_hint_y=None, height=60, background_color=(1,0,0,1)); b.bind(on_press=self.vider_base); self.grid.add_widget(b)
    def vider_base(self, inst):
        conn=sqlite3.connect(DB_PATH); conn.execute("DELETE FROM commandes"); conn.commit(); conn.close()
        self.clear_grid(); self.grid.add_widget(Label(text="Base videe!", size_hint_y=None, height=50))

if __name__ == '__main__':
    IVOVIPApp().run()
