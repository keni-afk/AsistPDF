import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import calendar
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors

# ─────────────────────────────────────────────
# PALETA
# ─────────────────────────────────────────────
C_BG       = "#0F1117"
C_SURFACE  = "#1A1D27"
C_CARD     = "#22263A"
C_BORDER   = "#2E3350"
C_ACCENT   = "#4F8EF7"
C_ERROR    = "#F75F5F"
C_TEXT     = "#E8EAF2"
C_MUTED    = "#8890B0"
C_WHITE    = "#FFFFFF"
C_INPUT_BG = "#181B2A"

FONT_ENTRY = ("Consolas", 10)
FONT_BTN   = ("Segoe UI", 10, "bold")
FONT_PREV  = ("Georgia", 11)

# ─────────────────────────────────────────────
# TIPOS DE DOCUMENTO
# ─────────────────────────────────────────────
DOCUMENT_TYPES = {
    "SOLICITUD DE VACACIONES": "vacaciones",
    "CARTA DE RENUNCIA":       "renuncia",
    "CARTA DE RECOMENDACION":  "recomendacion",
    "SOLICITUD DE EMPLEO":     "empleo",
    "SOLICITUD DE PERMISO":    "permiso",
}

# Campos: (label, key, tipo)  tipo: "entry" | "date" | "textarea"
SPECIFIC_FIELDS = {
    "vacaciones":    [
        ("Periodo solicitado (inicio)", "periodo_ini", "date"),
        ("Periodo solicitado (fin)",    "periodo_fin", "date"),
        ("Cantidad de dias",            "dias",        "entry"),
    ],
    "renuncia":      [
        ("Motivo de renuncia",   "motivo_renuncia",   "textarea"),
        ("Fecha de efectividad", "fecha_efectividad", "date"),
        ("Ultimo dia laboral",   "ultimo_dia",        "date"),
    ],
    "recomendacion": [
        ("Nombre recomendado",    "recomendado", "entry"),
        ("Relacion laboral",      "relacion",    "entry"),
        ("Cualidades destacadas", "cualidades",  "textarea"),
    ],
    "empleo":        [
        ("Puesto solicitado",    "puesto",      "entry"),
        ("Experiencia destacada","experiencia", "textarea"),
    ],
    "permiso":       [
        ("Motivo del permiso", "motivo",   "textarea"),
        ("Duracion / Fechas",  "duracion", "entry"),
    ],
}

COMMON_FIELDS = [
    ("Nombre completo",    "nombre",             "entry"),
    ("DNI / Cedula",       "cedula",             "entry"),
    ("Cargo",              "cargo",              "entry"),
    ("Telefono",           "telefono",           "entry"),
    ("Correo electronico", "email",              "entry"),
    ("Destinatario",       "destinatario",       "entry"),
    ("Cargo destinatario", "cargo_destinatario", "entry"),
    ("Empresa",            "empresa",            "entry"),
    ("Fecha del documento","fecha",              "date"),
]

REQUIRED_COMMON = {"nombre", "cedula", "cargo", "destinatario", "cargo_destinatario", "empresa", "fecha"}
REQUIRED_SPECIFIC = {
    "vacaciones":    {"periodo_ini", "periodo_fin", "dias"},
    "renuncia":      {"motivo_renuncia", "fecha_efectividad", "ultimo_dia"},
    "recomendacion": {"recomendado", "relacion", "cualidades"},
    "empleo":        {"puesto", "experiencia"},
    "permiso":       {"motivo", "duracion"},
}


# ─────────────────────────────────────────────
# CALENDARIO
# ─────────────────────────────────────────────
class CalendarPicker(tk.Toplevel):
    def __init__(self, anchor_widget, var, on_pick=None):
        super().__init__(anchor_widget.winfo_toplevel())
        self.var       = var
        self.on_pick   = on_pick
        self.overrideredirect(True)
        self.configure(bg=C_CARD, highlightthickness=1, highlightbackground=C_BORDER)
        self.resizable(False, False)

        try:
            d = datetime.strptime(var.get(), "%d/%m/%Y")
            self._year, self._month = d.year, d.month
        except ValueError:
            n = datetime.now()
            self._year, self._month = n.year, n.month

        self._build()
        self._place(anchor_widget)
        self.grab_set()
        self.focus_set()
        self.bind("<FocusOut>", lambda e: self._safe_destroy())

    def _safe_destroy(self):
        try:
            self.destroy()
        except Exception:
            pass

    def _place(self, w):
        w.update_idletasks()
        x = w.winfo_rootx()
        y = w.winfo_rooty() + w.winfo_height() + 2
        sw = self.winfo_screenwidth()
        self.update_idletasks()
        pw = self.winfo_reqwidth()
        if x + pw > sw:
            x = sw - pw - 4
        self.geometry(f"+{x}+{y}")

    def _build(self):
        for w in self.winfo_children():
            w.destroy()

        hdr = tk.Frame(self, bg=C_CARD, pady=6)
        hdr.pack(fill="x", padx=8)

        tk.Button(hdr, text="<", bg=C_CARD, fg=C_ACCENT, font=("Segoe UI",9,"bold"),
                  relief="flat", bd=0, cursor="hand2",
                  command=self._prev).pack(side="left")

        month_names = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                       "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        tk.Label(hdr, text=f"{month_names[self._month-1]} {self._year}",
                 font=("Segoe UI",10,"bold"), fg=C_WHITE, bg=C_CARD).pack(side="left", expand=True)

        tk.Button(hdr, text=">", bg=C_CARD, fg=C_ACCENT, font=("Segoe UI",9,"bold"),
                  relief="flat", bd=0, cursor="hand2",
                  command=self._next).pack(side="right")

        days_fr = tk.Frame(self, bg=C_CARD, pady=2)
        days_fr.pack(padx=8)
        for i, d in enumerate(["Lu","Ma","Mi","Ju","Vi","Sa","Do"]):
            tk.Label(days_fr, text=d, width=3, font=("Segoe UI",8,"bold"),
                     fg=C_MUTED, bg=C_CARD).grid(row=0, column=i, padx=1)

        grid_fr = tk.Frame(self, bg=C_CARD)
        grid_fr.pack(padx=8, pady=(0,8))

        today = datetime.now()
        for r, week in enumerate(calendar.monthcalendar(self._year, self._month)):
            for c, day in enumerate(week):
                if day == 0:
                    tk.Label(grid_fr, text="", width=3, bg=C_CARD).grid(row=r, column=c, padx=1, pady=1)
                else:
                    is_today = (day == today.day and self._month == today.month and self._year == today.year)
                    bg_  = C_ACCENT if is_today else C_SURFACE
                    fg_  = C_WHITE  if is_today else C_TEXT
                    fn_  = ("Segoe UI",9,"bold") if is_today else ("Segoe UI",9)
                    tk.Button(grid_fr, text=str(day), width=3, bg=bg_, fg=fg_, font=fn_,
                              relief="flat", bd=0, cursor="hand2",
                              activebackground=C_ACCENT, activeforeground=C_WHITE,
                              command=lambda d=day: self._pick(d)
                    ).grid(row=r, column=c, padx=1, pady=1)

    def _prev(self):
        self._month -= 1
        if self._month < 1:
            self._month = 12; self._year -= 1
        self._build()

    def _next(self):
        self._month += 1
        if self._month > 12:
            self._month = 1; self._year += 1
        self._build()

    def _pick(self, day):
        self.var.set(f"{day:02d}/{self._month:02d}/{self._year}")
        if self.on_pick:
            self.on_pick()
        self._safe_destroy()


# ─────────────────────────────────────────────
# HELPERS UI
# ─────────────────────────────────────────────
def _darken(h, f=0.75):
    h = h.lstrip("#")
    r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    return "#{:02x}{:02x}{:02x}".format(int(r*f),int(g*f),int(b*f))


def mk_btn(parent, text, cmd, accent=C_ACCENT, width=150, height=34):
    cvs = tk.Canvas(parent, width=width, height=height,
                    bg=C_SURFACE, highlightthickness=0, cursor="hand2")
    r = 7; x1,y1,x2,y2 = 1,1,width-1,height-1

    def draw(fill):
        cvs.delete("b")
        for kw in [
            dict(coords=(x1,y1,x1+2*r,y1+2*r), start=90,  extent=90),
            dict(coords=(x2-2*r,y1,x2,y1+2*r), start=0,   extent=90),
            dict(coords=(x1,y2-2*r,x1+2*r,y2), start=180, extent=90),
            dict(coords=(x2-2*r,y2-2*r,x2,y2), start=270, extent=90),
        ]:
            cvs.create_arc(*kw["coords"], start=kw["start"], extent=kw["extent"],
                           fill=fill, outline="", tags="b")
        cvs.create_rectangle(x1+r,y1,x2-r,y2, fill=fill, outline="", tags="b")
        cvs.create_rectangle(x1,y1+r,x2,y2-r, fill=fill, outline="", tags="b")
        cvs.create_text(width//2,height//2, text=text, fill=C_WHITE, font=FONT_BTN, tags="b")

    draw(accent)
    cvs.bind("<Enter>",    lambda e: draw(_darken(accent)))
    cvs.bind("<Leave>",    lambda e: draw(accent))
    cvs.bind("<Button-1>", lambda e: cmd())
    return cvs


def lbl(parent, text, size=9, bold=False, color=C_TEXT, bg=C_SURFACE):
    f = ("Segoe UI", size, "bold") if bold else ("Segoe UI", size)
    return tk.Label(parent, text=text, font=f, fg=color, bg=bg)


def make_entry(parent, var, width=34):
    return tk.Entry(parent, textvariable=var, font=FONT_ENTRY,
                    bg=C_INPUT_BG, fg=C_TEXT, insertbackground=C_ACCENT,
                    relief="flat", highlightthickness=1,
                    highlightbackground=C_BORDER, highlightcolor=C_ACCENT,
                    width=width)


def make_textarea(parent, height=4, width=30):
    outer = tk.Frame(parent, bg=C_BORDER, padx=1, pady=1)
    txt = tk.Text(outer, font=FONT_ENTRY, bg=C_INPUT_BG, fg=C_TEXT,
                  insertbackground=C_ACCENT, relief="flat",
                  height=height, width=width, wrap=tk.WORD,
                  highlightthickness=0, padx=6, pady=4)
    txt.pack(fill="both", expand=True)
    txt.bind("<FocusIn>",  lambda e: outer.configure(bg=C_ACCENT))
    txt.bind("<FocusOut>", lambda e: outer.configure(bg=C_BORDER))
    return outer, txt


def make_date_row(parent, var, callback=None):
    row = tk.Frame(parent, bg=C_SURFACE)
    e = tk.Entry(row, textvariable=var, font=FONT_ENTRY,
                 bg=C_INPUT_BG, fg=C_TEXT, insertbackground=C_ACCENT,
                 relief="flat", highlightthickness=1,
                 highlightbackground=C_BORDER, highlightcolor=C_ACCENT,
                 width=14)
    e.pack(side="left")

    def open_cal():
        CalendarPicker(e, var, on_pick=callback)

    cal_lbl = tk.Label(row, text=" 📅 ", font=("Segoe UI",12),
                       bg=C_INPUT_BG, fg=C_ACCENT, cursor="hand2")
    cal_lbl.pack(side="left")
    cal_lbl.bind("<Button-1>", lambda ev: open_cal())
    e.bind("<Return>", lambda ev: open_cal())

    hint = tk.Label(row, text="DD/MM/AAAA", font=("Segoe UI",8),
                    fg=C_MUTED, bg=C_SURFACE)
    hint.pack(side="left", padx=4)

    if callback:
        var.trace_add("write", lambda *a: callback())
    return row


# ─────────────────────────────────────────────
# TEXTO DEL DOCUMENTO
# ─────────────────────────────────────────────
def gv(d, k):
    v = d.get(k, "")
    return v.strip() if isinstance(v, str) else ""


def build_text(doc_type, cd, sd):
    nombre = gv(cd,"nombre"); cedula = gv(cd,"cedula"); cargo = gv(cd,"cargo")
    tel    = gv(cd,"telefono"); email = gv(cd,"email")
    dest   = gv(cd,"destinatario"); cdest = gv(cd,"cargo_destinatario")
    emp    = gv(cd,"empresa"); fecha = gv(cd,"fecha")

    header = f"{fecha}\n\nSenor(a):\n{dest}\n{cdest}\n{emp}\nPresente.-\n"
    footer = (f"\n\nAtentamente,\n\n\n{nombre}\n"
              f"DNI/C.I.: {cedula}\nCargo: {cargo}\n"
              + (f"Telefono: {tel}\n" if tel else "")
              + (f"Correo: {email}\n" if email else ""))

    bodies = {
        "vacaciones": (
            f"\nREF: SOLICITUD DE VACACIONES\n\n"
            f"De mi mayor consideracion:\n\n"
            f"Mediante la presente le hago llegar mis mas cordiales saludos y le deseo el mayor de los exitos en las funciones que desempena por esta prestigiosa empresa.\n\n"
            f"El motivo de la presente carta es interpuesta por mi persona, {nombre}, con C.I. {cedula}, en calidad de {cargo}, para su conocimiento y solicitar formalmente lo siguiente:\n\n"
            f"Solicito formalmente el goce de mis vacaciones correspondientes al periodo del {gv(sd,'periodo_ini')} al {gv(sd,'periodo_fin')}, por un total de {gv(sd,'dias')} dias, de acuerdo a la normativa vigente, quedando a la espera de su aprobacion.\n\n"
            f"Sin otro en particular, me despido de su persona, agradeciendole la atencion a lo mencionado anteriormente y quedando a la espera de su respuesta."
        ),
        "renuncia": (
            f"\nREF: RENUNCIA VOLUNTARIA\n\n"
            f"De mi mayor consideracion:\n\n"
            f"Por medio de la presente, yo {nombre}, identificado con DNI/C.I. {cedula}, presento mi renuncia voluntaria al cargo de {cargo} dentro de {emp}.\n\n"
            f"Motivo: {gv(sd,'motivo_renuncia')}\n\n"
            f"Fecha de efectividad: {gv(sd,'fecha_efectividad')}\nUltimo dia laboral: {gv(sd,'ultimo_dia')}\n\n"
            f"Agradezco la oportunidad brindada y el aprendizaje obtenido durante mi permanencia en la institucion."
        ),
        "recomendacion": (
            f"\nREF: CARTA DE RECOMENDACION\n\n"
            f"De mi mayor consideracion:\n\n"
            f"Por medio de la presente tengo el agrado de recomendar a {gv(sd,'recomendado')}, con quien tuve el gusto de trabajar en calidad de {gv(sd,'relacion')}.\n\n"
            f"Cualidades destacadas: {gv(sd,'cualidades')}\n\n"
            f"Considero que posee excelentes capacidades profesionales y humanas, por lo que recomiendo ampliamente su incorporacion."
        ),
        "empleo": (
            f"\nREF: SOLICITUD DE EMPLEO\n\n"
            f"De mi mayor consideracion:\n\n"
            f"Me dirijo a usted con el fin de postular al puesto de {gv(sd,'puesto')} en {emp}.\n\n"
            f"Experiencia destacada:\n{gv(sd,'experiencia')}\n\n"
            f"Quedo atento(a) a cualquier entrevista o evaluacion que consideren pertinente."
        ),
        "permiso": (
            f"\nREF: SOLICITUD DE PERMISO\n\n"
            f"De mi mayor consideracion:\n\n"
            f"Yo, {nombre}, identificado(a) con DNI/C.I. {cedula}, en calidad de {cargo}, solicito permiso por el siguiente motivo:\n\n"
            f"{gv(sd,'motivo')}\n\nDuracion: {gv(sd,'duracion')}\n\n"
            f"Agradezco su comprension y quedo en espera de su respuesta favorable."
        ),
    }
    return header + bodies.get(doc_type, "") + footer


# ─────────────────────────────────────────────
# PDF
# ─────────────────────────────────────────────
def generar_pdf(doc_type, cd, sd, archivo):
    try:
        doc = SimpleDocTemplate(archivo, pagesize=letter,
                                leftMargin=2.5*cm, rightMargin=2.5*cm,
                                topMargin=2.5*cm, bottomMargin=2.5*cm)
        marron = colors.HexColor("#1A1A1A")
        gris   = colors.HexColor("#444444")

        sn = ParagraphStyle("N", fontName="Times-Roman", fontSize=11, leading=18,
                            alignment=TA_JUSTIFY, textColor=marron)
        sr = ParagraphStyle("R", fontName="Times-Bold",  fontSize=11, leading=18,
                            alignment=TA_CENTER, spaceAfter=4, textColor=marron)
        sf = ParagraphStyle("F", fontName="Times-Roman", fontSize=11, leading=18,
                            alignment=TA_LEFT, textColor=marron)
        sd_ = ParagraphStyle("D", fontName="Times-Roman",fontSize=11, leading=18,
                             alignment=TA_LEFT, textColor=gris)

        nombre = gv(cd,"nombre"); cedula = gv(cd,"cedula"); cargo = gv(cd,"cargo")
        tel    = gv(cd,"telefono"); email = gv(cd,"email")
        dest   = gv(cd,"destinatario"); cdest = gv(cd,"cargo_destinatario")
        emp    = gv(cd,"empresa"); fecha = gv(cd,"fecha")

        elems = []
        def p(t, s=None): elems.append(Paragraph(t, s or sn))
        def sp(): elems.append(Spacer(1, 0.3*cm))

        p(fecha, sd_)
        elems.append(Spacer(1, 0.4*cm))
        p("Senor(a):")
        p(f"<b>{dest}</b>")
        p(f"<b>{cdest}</b>")
        if emp: p(emp)
        p("Presente.-")
        elems.append(Spacer(1, 0.5*cm))

        ref_names = {
            "vacaciones":"SOLICITUD DE VACACIONES",
            "renuncia":"RENUNCIA VOLUNTARIA",
            "recomendacion":"CARTA DE RECOMENDACION",
            "empleo":"SOLICITUD DE EMPLEO",
            "permiso":"SOLICITUD DE PERMISO",
        }
        p(f'<u><b>REF: {ref_names.get(doc_type,"")}</b></u>', sr)
        elems.append(Spacer(1, 0.3*cm))
        p("De mi mayor consideracion:")
        sp()

        if doc_type == "vacaciones":
            p("Mediante la presente le hago llegar mis mas cordiales saludos y le deseo el mayor de los exitos en las funciones que desempena por esta prestigiosa empresa.")
            sp()
            p(f'El motivo de la presente carta es interpuesta por mi persona, <b>{nombre}</b>, con C.I. <b>{cedula}</b>, en calidad de <b>{cargo}</b>, para su conocimiento y solicitar formalmente lo siguiente:')
            sp()
            p(f'Solicito formalmente el goce de mis vacaciones correspondientes al periodo del <b>{gv(sd,"periodo_ini")}</b> al <b>{gv(sd,"periodo_fin")}</b>, por un total de <b>{gv(sd,"dias")} dias</b>, de acuerdo a la normativa vigente, quedando a la espera de su aprobacion.')
            sp()
            p("Sin otro en particular, me despido de su persona, agradeciendole la atencion a lo mencionado anteriormente y quedando a la espera de su respuesta.")

        elif doc_type == "renuncia":
            p(f'Por medio de la presente, yo <b>{nombre}</b>, identificado con DNI/C.I. <b>{cedula}</b>, presento mi <b>renuncia voluntaria</b> al cargo de <b>{cargo}</b> dentro de <b>{emp}</b>.')
            sp()
            p(f'<b>Motivo:</b> {gv(sd,"motivo_renuncia")}')
            p(f'<b>Fecha de efectividad:</b> {gv(sd,"fecha_efectividad")}')
            p(f'<b>Ultimo dia laboral:</b> {gv(sd,"ultimo_dia")}')
            sp()
            p("Agradezco la oportunidad brindada y el aprendizaje obtenido durante mi permanencia en la institucion.")

        elif doc_type == "recomendacion":
            p(f'Por medio de la presente tengo el agrado de recomendar a <b>{gv(sd,"recomendado")}</b>, con quien tuve el gusto de trabajar en calidad de <b>{gv(sd,"relacion")}</b>.')
            sp()
            p(f'<b>Cualidades destacadas:</b> {gv(sd,"cualidades")}')
            sp()
            p("Considero que posee excelentes capacidades profesionales y humanas, por lo que recomiendo ampliamente su incorporacion.")

        elif doc_type == "empleo":
            p(f'Me dirijo a usted con el fin de postular al puesto de <b>{gv(sd,"puesto")}</b> en <b>{emp}</b>.')
            sp()
            p("<b>Experiencia destacada:</b>")
            for linea in gv(sd,"experiencia").split("\n"):
                if linea.strip():
                    p(linea.strip())
            sp()
            p("Quedo atento(a) a cualquier entrevista o evaluacion que consideren pertinente.")

        elif doc_type == "permiso":
            p(f'Yo, <b>{nombre}</b>, identificado(a) con DNI/C.I. <b>{cedula}</b>, en calidad de <b>{cargo}</b>, solicito permiso por el siguiente motivo:')
            sp()
            for linea in gv(sd,"motivo").split("\n"):
                if linea.strip():
                    p(linea.strip())
            sp()
            p(f'<b>Duracion:</b> {gv(sd,"duracion")}')
            sp()
            p("Agradezco su comprension y quedo en espera de su respuesta favorable.")

        elems.append(Spacer(1, 0.6*cm))
        p("Atentamente,")
        elems.append(Spacer(1, 1.0*cm))
        p(f"<b>{nombre}</b>", sf)
        p(f"DNI/C.I.: {cedula}", sf)
        p(f"Cargo: {cargo}", sf)
        if tel:   p(f"Telefono: {tel}", sf)
        if email: p(f"Correo: {email}", sf)

        doc.build(elems)
        return True
    except Exception as e:
        messagebox.showerror("Error PDF", str(e))
        return False


# ─────────────────────────────────────────────
# VALIDACION
# ─────────────────────────────────────────────
def validate_date(s):
    try:
        datetime.strptime(s.strip(), "%d/%m/%Y")
        return True
    except ValueError:
        return False


# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────
class AsistPDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AsistPDF Pro")
        self.root.configure(bg=C_BG)
        self.root.geometry("1300x840")
        self.root.minsize(960, 640)
        try:
            self.root.state("zoomed")
        except Exception:
            pass

        self.doc_type_var     = tk.StringVar(value="SOLICITUD DE VACACIONES")
        self.common_vars      = {}
        self.specific_entries = {}
        self.specific_texts   = {}
        self._err_labels      = {}

        self._build_ui()
        self._refresh_specific_fields()
        self._update_preview()

    # ─── layout ───────────────────────────────
    def _build_ui(self):
        self.sidebar = tk.Frame(self.root, bg=C_SURFACE, width=400)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        right = tk.Frame(self.root, bg=C_BG)
        right.pack(side="left", fill="both", expand=True)
        self._build_sidebar()
        self._build_right(right)

    # ─── sidebar ──────────────────────────────
    def _build_sidebar(self):
        sb = self.sidebar

        hdr = tk.Frame(sb, bg=C_SURFACE, pady=18)
        hdr.pack(fill="x", padx=22)
        tk.Label(hdr, text="⬡",      font=("Segoe UI",20),        fg=C_ACCENT, bg=C_SURFACE).pack(side="left")
        tk.Label(hdr, text=" AsistPDF", font=("Segoe UI",17,"bold"), fg=C_WHITE,  bg=C_SURFACE).pack(side="left")
        tk.Label(hdr, text=" Pro",    font=("Segoe UI",17,"bold"), fg=C_ACCENT, bg=C_SURFACE).pack(side="left")

        tk.Frame(sb, height=1, bg=C_BORDER).pack(fill="x")

        # selector tipo
        sf = tk.Frame(sb, bg=C_SURFACE, pady=12)
        sf.pack(fill="x", padx=20)
        lbl(sf, "TIPO DE DOCUMENTO", 8, bold=True, color=C_MUTED).pack(anchor="w")
        tk.Frame(sf, height=5, bg=C_SURFACE).pack()
        dm = tk.OptionMenu(sf, self.doc_type_var, *DOCUMENT_TYPES.keys(),
                           command=lambda _: self._on_doc_change())
        dm.configure(bg=C_INPUT_BG, fg=C_TEXT, activebackground=C_CARD,
                     activeforeground=C_WHITE, font=("Segoe UI",10,"bold"),
                     relief="flat", bd=0, highlightthickness=1,
                     highlightbackground=C_BORDER, highlightcolor=C_ACCENT, width=30)
        dm["menu"].configure(bg=C_CARD, fg=C_TEXT, font=("Segoe UI",10),
                             activebackground=C_ACCENT, activeforeground=C_WHITE)
        dm.pack(fill="x")

        tk.Frame(sb, height=1, bg=C_BORDER).pack(fill="x", pady=(6,0))
        lbl(sb, "DATOS DEL REMITENTE", 8, bold=True, color=C_MUTED).pack(anchor="w", padx=20, pady=(12,4))

        wrap = tk.Frame(sb, bg=C_SURFACE)
        wrap.pack(fill="both", expand=True)

        cvs = tk.Canvas(wrap, bg=C_SURFACE, highlightthickness=0)
        vsb = tk.Scrollbar(wrap, orient="vertical", command=cvs.yview,
                           bg=C_SURFACE, troughcolor=C_BG, activebackground=C_ACCENT)
        cvs.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        cvs.pack(fill="both", expand=True)

        self.fields_frame = tk.Frame(cvs, bg=C_SURFACE)
        wid = cvs.create_window((0,0), window=self.fields_frame, anchor="nw")
        cvs.bind("<Configure>", lambda e: cvs.itemconfig(wid, width=e.width))
        self.fields_frame.bind("<Configure>",
            lambda e: cvs.configure(scrollregion=cvs.bbox("all")))
        cvs.bind_all("<MouseWheel>",
            lambda e: cvs.yview_scroll(-1*(e.delta//120), "units"))

        self._build_common_fields()

        # botones
        tk.Frame(sb, height=1, bg=C_BORDER).pack(fill="x", side="bottom")
        bb = tk.Frame(sb, bg=C_SURFACE, pady=10)
        bb.pack(fill="x", side="bottom")
        row = tk.Frame(bb, bg=C_SURFACE)
        row.pack(fill="x", padx=10)
        mk_btn(row, "Ejemplo",     self._load_example, accent=C_CARD,   width=108, height=34).pack(side="left",  padx=3)
        mk_btn(row, "Limpiar",     self._clear_all,    accent=C_CARD,   width=108, height=34).pack(side="left",  padx=3)
        mk_btn(row, "Generar PDF", self._save_pdf,     accent=C_ACCENT, width=150, height=34).pack(side="right", padx=3)

    # ─── campos comunes ────────────────────────
    def _build_common_fields(self):
        ff = self.fields_frame
        for lbl_text, key, ftype in COMMON_FIELDS:
            grp = tk.Frame(ff, bg=C_SURFACE)
            grp.pack(fill="x", padx=16, pady=3)

            rl = tk.Frame(grp, bg=C_SURFACE)
            rl.pack(fill="x")
            lbl(rl, lbl_text, 9, bold=True, color=C_MUTED).pack(side="left")
            el = tk.Label(rl, text="", font=("Segoe UI",8), fg=C_ERROR, bg=C_SURFACE)
            el.pack(side="left", padx=4)
            self._err_labels[key] = el

            var = tk.StringVar()
            if key == "fecha":
                var.set(datetime.now().strftime("%d/%m/%Y"))
            self.common_vars[key] = var

            if ftype == "date":
                w = make_date_row(grp, var, callback=self._update_preview)
                w.pack(fill="x", pady=(2,0))
            else:
                e = make_entry(grp, var, width=36)
                e.pack(fill="x", pady=(2,0))
                var.trace_add("write", lambda *a: self._update_preview())

    # ─── área derecha ──────────────────────────
    def _build_right(self, parent):
        top = tk.Frame(parent, bg=C_BG, pady=16)
        top.pack(fill="x", padx=26)
        self.doc_title_label = tk.Label(top, text="SOLICITUD DE VACACIONES",
                                        font=("Segoe UI",15,"bold"), fg=C_WHITE, bg=C_BG)
        self.doc_title_label.pack(side="left")
        tk.Label(top, text="  Vista previa  ", font=("Segoe UI",8,"bold"),
                 fg=C_ACCENT, bg=C_CARD, padx=6, pady=3).pack(side="left", padx=10)

        cols = tk.Frame(parent, bg=C_BG)
        cols.pack(fill="both", expand=True, padx=26, pady=(0,18))

        # campos específicos
        left_col = tk.Frame(cols, bg=C_SURFACE, width=300)
        left_col.pack(side="left", fill="y", padx=(0,12))
        left_col.pack_propagate(False)

        lbl(left_col, "DATOS DEL DOCUMENTO", 8, bold=True, color=C_MUTED, bg=C_SURFACE).pack(
            anchor="w", padx=14, pady=(14,4))

        sp_cvs = tk.Canvas(left_col, bg=C_SURFACE, highlightthickness=0)
        sp_vsb = tk.Scrollbar(left_col, orient="vertical", command=sp_cvs.yview,
                              bg=C_SURFACE, troughcolor=C_BG, activebackground=C_ACCENT)
        sp_cvs.configure(yscrollcommand=sp_vsb.set)
        sp_vsb.pack(side="right", fill="y")
        sp_cvs.pack(fill="both", expand=True)

        self.specific_frame = tk.Frame(sp_cvs, bg=C_SURFACE)
        sw = sp_cvs.create_window((0,0), window=self.specific_frame, anchor="nw")
        sp_cvs.bind("<Configure>", lambda e: sp_cvs.itemconfig(sw, width=e.width))
        self.specific_frame.bind("<Configure>",
            lambda e: sp_cvs.configure(scrollregion=sp_cvs.bbox("all")))

        # preview
        right_col = tk.Frame(cols, bg=C_CARD)
        right_col.pack(side="left", fill="both", expand=True)

        ph = tk.Frame(right_col, bg=C_CARD, pady=8)
        ph.pack(fill="x", padx=18)
        lbl(ph, "PREVISUALIZACION DEL DOCUMENTO", 8, bold=True, color=C_MUTED, bg=C_CARD).pack(side="left")

        tk.Frame(right_col, height=1, bg=C_BORDER).pack(fill="x")

        self.preview_text = tk.Text(right_col, wrap=tk.WORD, font=FONT_PREV,
                                    bg=C_CARD, fg=C_TEXT, insertbackground=C_ACCENT,
                                    padx=28, pady=22, relief="flat",
                                    state="disabled", cursor="arrow")
        pvsb = tk.Scrollbar(right_col, orient="vertical", command=self.preview_text.yview,
                            bg=C_CARD, troughcolor=C_BG)
        self.preview_text.configure(yscrollcommand=pvsb.set)
        pvsb.pack(side="right", fill="y")
        self.preview_text.pack(fill="both", expand=True)

        self.preview_text.tag_configure("ref",    font=("Georgia",12,"bold"), justify="center", foreground=C_WHITE)
        self.preview_text.tag_configure("normal", font=FONT_PREV, foreground=C_TEXT)
        self.preview_text.tag_configure("muted",  font=("Segoe UI",10), foreground=C_MUTED)

    # ─── campos específicos ────────────────────
    def _refresh_specific_fields(self):
        for w in self.specific_frame.winfo_children():
            w.destroy()
        self.specific_entries.clear()
        self.specific_texts.clear()

        common_keys = {k for _, k, _ in COMMON_FIELDS}
        for k in list(self._err_labels.keys()):
            if k not in common_keys:
                del self._err_labels[k]

        doc_key = DOCUMENT_TYPES[self.doc_type_var.get()]

        for lbl_text, key, ftype in SPECIFIC_FIELDS[doc_key]:
            grp = tk.Frame(self.specific_frame, bg=C_SURFACE)
            grp.pack(fill="x", padx=12, pady=5)

            rl = tk.Frame(grp, bg=C_SURFACE)
            rl.pack(fill="x")
            lbl(rl, lbl_text, 9, bold=True, color=C_MUTED).pack(side="left")
            el = tk.Label(rl, text="", font=("Segoe UI",8), fg=C_ERROR, bg=C_SURFACE)
            el.pack(side="left", padx=4)
            self._err_labels[key] = el

            if ftype == "textarea":
                outer, txt = make_textarea(grp, height=4, width=26)
                outer.pack(fill="x", pady=(2,0))
                txt.bind("<KeyRelease>", lambda e: self._update_preview())
                self.specific_texts[key] = txt

            elif ftype == "date":
                var = tk.StringVar()
                w = make_date_row(grp, var, callback=self._update_preview)
                w.pack(fill="x", pady=(2,0))
                self.specific_entries[key] = var

            else:
                var = tk.StringVar()
                e = make_entry(grp, var, width=26)
                e.pack(fill="x", pady=(2,0))
                var.trace_add("write", lambda *a: self._update_preview())
                self.specific_entries[key] = var

        self._update_preview()

    def _on_doc_change(self):
        self.doc_title_label.configure(text=self.doc_type_var.get())
        self._refresh_specific_fields()

    # ─── datos ────────────────────────────────
    def _get_specific_data(self):
        d = {k: v.get() for k, v in self.specific_entries.items()}
        for k, txt in self.specific_texts.items():
            d[k] = txt.get("1.0", tk.END).strip()
        return d

    # ─── preview ──────────────────────────────
    def _update_preview(self):
        cd = {k: v.get() for k, v in self.common_vars.items()}
        sd = self._get_specific_data()

        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", tk.END)

        if not cd.get("nombre","").strip():
            self.preview_text.insert(tk.END,
                "\n\nComplete los datos del remitente para visualizar el documento.", "muted")
            self.preview_text.configure(state="disabled")
            return

        doc_key = DOCUMENT_TYPES[self.doc_type_var.get()]
        texto   = build_text(doc_key, cd, sd)

        for linea in texto.split("\n"):
            tag = "ref" if linea.startswith("REF:") else "normal"
            self.preview_text.insert(tk.END,
                ("\n"+linea+"\n" if tag=="ref" else linea+"\n"), tag)

        self.preview_text.configure(state="disabled")

    # ─── guardar PDF ──────────────────────────
    def _save_pdf(self):
        cd      = {k: v.get() for k, v in self.common_vars.items()}
        sd      = self._get_specific_data()
        doc_key = DOCUMENT_TYPES[self.doc_type_var.get()]

        # limpiar errores
        for el in self._err_labels.values():
            el.configure(text="")

        # validar requeridos
        missing = []
        label_map = {k: l for l,k,_ in COMMON_FIELDS}
        for l,k,_ in SPECIFIC_FIELDS[doc_key]:
            label_map[k] = l

        for key in REQUIRED_COMMON:
            if not cd.get(key,"").strip():
                missing.append(f"• {label_map.get(key, key)}")
                if key in self._err_labels:
                    self._err_labels[key].configure(text="requerido")

        for key in REQUIRED_SPECIFIC.get(doc_key, set()):
            if key in self.specific_entries:
                val = self.specific_entries[key].get().strip()
            elif key in self.specific_texts:
                val = self.specific_texts[key].get("1.0", tk.END).strip()
            else:
                val = ""
            if not val:
                missing.append(f"• {label_map.get(key, key)}")
                if key in self._err_labels:
                    self._err_labels[key].configure(text="requerido")

        if missing:
            messagebox.showwarning("Campos requeridos",
                "Por favor completa los siguientes campos:\n\n" + "\n".join(missing))
            return

        # validar formato de fechas
        date_keys_c = [k for _,k,t in COMMON_FIELDS if t=="date"]
        date_keys_s = [k for _,k,t in SPECIFIC_FIELDS[doc_key] if t=="date"]
        bad_dates = []
        for k in date_keys_c:
            v = cd.get(k,"")
            if v and not validate_date(v):
                bad_dates.append(f"• {label_map.get(k,k)}: '{v}'")
                if k in self._err_labels:
                    self._err_labels[k].configure(text="formato invalido")
        for k in date_keys_s:
            v = sd.get(k,"")
            if v and not validate_date(v):
                bad_dates.append(f"• {label_map.get(k,k)}: '{v}'")
                if k in self._err_labels:
                    self._err_labels[k].configure(text="formato invalido")
        if bad_dates:
            messagebox.showwarning("Fecha invalida",
                "Usa el formato DD/MM/AAAA en:\n\n" + "\n".join(bad_dates))
            return

        # nombre archivo: NombreApellido_tipodoc_DD-MM-AAAA.pdf
        nombre_limpio = cd.get("nombre","documento").strip().replace(" ","_")
        fecha_hoy     = datetime.now().strftime("%d-%m-%Y")
        sugerido      = f"{nombre_limpio}_{doc_key}_{fecha_hoy}.pdf"

        archivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF","*.pdf")],
            initialfile=sugerido,
            title="Guardar PDF"
        )
        if not archivo:
            return

        ok = generar_pdf(doc_key, cd, sd, archivo)
        if ok:
            messagebox.showinfo("PDF generado", f"Guardado correctamente:\n{archivo}")

    # ─── ejemplo ──────────────────────────────
    def _load_example(self):
        ej = {"nombre":"Tanjiro Kamado","cedula":"54789231","cargo":"CAZADOR DE DEMONIOS RANGO HASHIRA",
              "telefono":"555 666 888","email":"tkamado@demonslayer.com",
              "destinatario":"Kagaya Ubuyashiki","cargo_destinatario":"MASTER DEL ORDEN DEMON SLAYER",
              "empresa":"Demon Slayer Corp","fecha":datetime.now().strftime("%d/%m/%Y")}
        for k,v in ej.items():
            if k in self.common_vars:
                self.common_vars[k].set(v)

        doc_key = DOCUMENT_TYPES[self.doc_type_var.get()]
        ej_sp = {
            "vacaciones":    {"periodo_ini":"01/07/2025","periodo_fin":"20/07/2025","dias":"20"},
            "renuncia":      {"motivo_renuncia":"Buscar a mi hermana Nezuko y encontrar la cura definitiva.","fecha_efectividad":"15/08/2025","ultimo_dia":"14/08/2025"},
            "recomendacion": {"recomendado":"Nezuko Kamado","relacion":"hermana - Demon Blood Art User","cualidades":"Resistencia extraordinaria, control del fuego del demonio y corazon puro."},
            "empleo":        {"puesto":"Genio del Manga","experiencia":"10 anos de experiencia creando historias épicas de acción y sobrenatural.\nDirigí equipos de animadores en proyectos de impacto mundial."},
            "permiso":       {"motivo":"Entrenamiento especial en la Montaña del Rengoku para dominar nuevas Respiraciones.","duracion":"3 dias (18/07/2025 - 20/07/2025)"},
        }
        for k,v in ej_sp.get(doc_key,{}).items():
            if k in self.specific_entries:
                self.specific_entries[k].set(v)
            elif k in self.specific_texts:
                self.specific_texts[k].delete("1.0", tk.END)
                self.specific_texts[k].insert("1.0", v)

        for el in self._err_labels.values():
            el.configure(text="")
        self._update_preview()

    # ─── limpiar ──────────────────────────────
    def _clear_all(self):
        for var in self.common_vars.values(): var.set("")
        for var in self.specific_entries.values(): var.set("")
        for txt in self.specific_texts.values(): txt.delete("1.0", tk.END)
        if "fecha" in self.common_vars:
            self.common_vars["fecha"].set(datetime.now().strftime("%d/%m/%Y"))
        for el in self._err_labels.values(): el.configure(text="")
        self._update_preview()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    AsistPDFApp(root)
    root.mainloop()