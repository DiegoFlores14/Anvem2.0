import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import traceback
from flask import Flask, render_template, request, session, redirect, url_for, send_file, flash, jsonify
from datetime import timedelta
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Ajusta tu clave segura según lo necesites
DATA_FOLDER = os.path.join(app.root_path, "data")
GENERATED_FOLDER = os.path.join(app.root_path, "static", "generated")
os.makedirs(GENERATED_FOLDER, exist_ok=True)
app.permanent_session_lifetime = timedelta(minutes=30)

# Usuarios y sus artistas
USERS = {
    "GerardoTorres": {"password": "Gerardo444A", "artist": "Gerardo Torres"},
    "PabloOsorio": {"password": "Pablo159A", "artist": "Pablo Osorio"},
    "AlanMijes": {"password": "Alan247A", "artist": "Alan Mijes"},
    "JoseCaro": {"password": "Caro324A", "artist": "Jose Caro"},
    "ANVEMP": {"password": "ANVEM111A", "artist": "ANVEM PUBLISHING"},
    "ANVEML": {"password": "ANVEM222A", "artist": "ANVEM LYRICS"},
    "ANVEMT": {"password": "ANVEM333A", "artist": "ANVEM TUNES"},
    "AngelRodriguez": {"password": "Angel758A", "artist": "Angel Rodriguez"},
    "ChristianMorales": {"password": "Christian467A", "artist": "Christian Morales"},
    "ErickGutierrez": {"password": "Erick178A", "artist": "Erick Gutiérrez"},
    "IsauroMolinos": {"password": "Isauro999A", "artist": "Isauro Molinos"},
    "JoseOlivas": {"password": "Jose412A", "artist": "José Olivas"},
    "JoseRomero": {"password": "Jose223A", "artist": "José Romero"},
    "JuanLimon": {"password": "Juan111A", "artist": "Juan Limon"},
    "JulianMercado": {"password": "Julian657A", "artist": "Julián Mercado"},
    "MacarioCarvajal": {"password": "Macario963A", "artist": "Macario Carvajal"},
    "MichelCruz": {"password": "Michel582A", "artist": "Michel Cruz"},
    "OscarRegalado": {"password": "Oscar333A", "artist": "Oscar Regalado"},
    "RodrigoFlores": {"password": "Rodrigo741A", "artist": "Rodrigo Flores"},
    "AnvemT": {"password": "Anvem123A", "artist": "ANVEMTUNES"},
    "AnvemL": {"password": "Anvem321A", "artist": "ANVEM LYRICS"},
    "AnvemP": {"password": "Anvem213A", "artist": "ANVEM PUBLISHING"},
    "DanielNava": {"password": "Daniel874A", "artist": "Daniel Nava"},
    "DanielFuentes": {"password": "Daniel777A", "artist": "Daniel Fuentes"},
    "DenilsonJaramillo": {"password": "Denilson145A", "artist": "Denilson Jaramillo"},
    "FelipeManzanares": {"password": "Felipe654A", "artist": "Felipe Manzanares"},
    "FernandoRivas": {"password": "Fernando888A", "artist": "Fernando Rivas"},
    "FidelValenzuela": {"password": "Fidel547A", "artist": "Fidel Valenzuela"},
    "GaliaOrtiz": {"password": "Galia912A", "artist": "Galia Ortiz"},
    "JadielJaramillo": {"password": "Jadiel487A", "artist": "Jadiel Jaramillo"},
    "JoseCastro": {"password": "Castro479A", "artist": "Jose Castro"},
    "MarcoMendoza": {"password": "Marco845A", "artist": "Marco Mendoza"},
    "MisaelSanchez": {"password": "Misael845A", "artist": "Misael Sanchez"},
    "PaulinoSalazar": {"password": "Paulino663A", "artist": "Paulino Salazar"},
    "SergioEspinoza": {"password": "Sergio332A", "artist": "Sergio Espinoza"},
    "VictorGarcia": {"password": "Victor143A", "artist": "Victor Garcia"},
    "EmilianoMorales": {"password": "Emiliano917A", "artist": "Emiliano Morales"},
    "ErickPaez": {"password": "Erick555A", "artist": "Erick Paez"},
    "GustavoCastillo": {"password": "Gustavo872A", "artist": "Gustavo Castillo"},
    "PabloRodriguez": {"password": "Pablo657A", "artist": "Pablo Rodriguez"},
    "MarcoPadilla": {"password": "Padilla431A", "artist": "Marco Padilla"},
    "EduardoOveso": {"password": "Eduardo678A", "artist": "Eduardo Oveso"},
    "OmarAnaya": {"password": "Omar712A", "artist": "Omar Anaya"},
    "OscarFlores": {"password": "Oscar441A", "artist": "Oscar Flores"},
    "PaulinaServin": {"password": "Paulina478A", "artist": "Paulina Servin"},
    "RamonCumea": {"password": "Ramon614A", "artist": "Ramon Cuamea"},
    "VictorValdez": {"password": "Valdez455A", "artist": "Victor Valdez"},
    "DavidOrlando": {"password": "Orlando731A", "artist": "David Loya"},
    "EduardoGurrola": {"password": "Gurrola558A", "artist": "Eduardo Gurrola"},
    "PedroVilla": {"password": "Pedro111A", "artist": "Pedro Villa"},
    "SamanthaBarron": {"password": "Samantha123A", "artist": "Samantha Barrón"},
    "CarlosRamirez": {"password": "Carlos613A", "artist": "Carlos Ramirez"},
    "DavidLoya": {"password": "David676A", "artist": "David Loya"},
    "JuanLugo": {"password": "Juan442A", "artist": "Juan Lugo"},
    "MecsaSosa": {"password": "Mecsa212A", "artist": "Mecsa Sosa"},
    "MisaelHidalgo": {"password": "MisaelA999", "artist": "Misael Hidalgo"},
    "AdminUser": {"password": "Admin123", "is_admin": True}
}


POSSIBLE_TITLE_KEYWORDS = ["song", "titulo", "title", "nombre", "cancion", "track"]
POSSIBLE_ROYALTIES_KEYWORDS = ["royalt", "ganancia", "amount", "importe", "revenue"]
POSSIBLE_SOURCE_KEYWORDS = ["source", "fuente", "plataforma"]


QUARTER_RANGES = {
    "1": "01 JAN - 31 MAR",
    "2": "01 APR - 30 JUN",
    "3": "01 JUL - 30 SEP",
    "4": "01 OCT - 31 DEC"
}

def find_column(df, keywords, fallback_to_first=True):
    for col in df.columns:
        if any(kw in col.lower() for kw in keywords):
            return col
    return df.columns[0] if fallback_to_first else None

def clean_by_song(df):
    df.drop(columns=[c for c in df.columns if "unit" in c.lower()], inplace=True, errors="ignore")
    title_col = find_column(df, POSSIBLE_TITLE_KEYWORDS)
    royalties_col = find_column(df, POSSIBLE_ROYALTIES_KEYWORDS)
    df = df[[title_col, royalties_col]].copy()
    df.columns = ["Song", "Royalties"]
    df.dropna(subset=["Song"], inplace=True)
    df = df[~df["Song"].str.contains("TOTAL", case=False, na=False)]
    df["Royalties"] = pd.to_numeric(df["Royalties"], errors="coerce").fillna(0)
    return df.nlargest(10, "Royalties")

def clean_by_source(df):
    df.drop(columns=[c for c in df.columns if "unit" in c.lower()], inplace=True, errors="ignore")
    source_col = find_column(df, POSSIBLE_SOURCE_KEYWORDS)
    royalties_col = find_column(df, POSSIBLE_ROYALTIES_KEYWORDS)
    df = df[[source_col, royalties_col]].copy()
    df.columns = ["Source", "Royalties"]
    df.dropna(subset=["Source"], inplace=True)
    df = df[~df["Source"].str.contains("TOTAL", case=False, na=False)]
    df["Royalties"] = pd.to_numeric(df["Royalties"], errors="coerce").fillna(0)
    return df

def generate_source_pie_chart(df):
    df_sorted = df.sort_values(by="Royalties", ascending=False)

    top5 = df_sorted.head(5)
    others = df_sorted.iloc[5:]
    total_others = others["Royalties"].sum()
    total_val = df_sorted["Royalties"].sum()


    if total_others / total_val >= 0.1:
        df_final = pd.concat(
            [top5, pd.DataFrame([["Others", total_others]], columns=["Source", "Royalties"])],
            ignore_index=True
        )
    else:
        df_final = top5


    df_final = df_final.sort_values(by="Royalties", ascending=False).reset_index(drop=True)

    legend_labels = [
        f"{src} - {royalty / df_final['Royalties'].sum() * 100:.1f}%"
        for src, royalty in zip(df_final["Source"], df_final["Royalties"])
    ]

    fig, ax = plt.subplots(figsize=(10, 8), facecolor='none')
    wedges, _ = ax.pie(
        df_final["Royalties"],
        startangle=90,
        labels=None,
        wedgeprops=dict(edgecolor='white')
    )
    ax.axis('equal')

    plt.legend(
        wedges,
        legend_labels,
        title="Plataformas",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        labelspacing=1.3,
        prop={'size': 14},
        frameon=False
    )
    plt.tight_layout()
    plt.savefig(os.path.join(GENERATED_FOLDER, "source_pie_chart.png"), transparent=True)
    plt.close()

def load_admin_summary(quarter, year):
    filename = f"resumen_por_artista_T{quarter}-{year}.xlsx"
    file_path = os.path.join(DATA_FOLDER, filename)
    summary_data = {}


    if not os.path.exists(file_path):

        summary_data["Resumen"] = "<p style='color:red;'>Archivo no encontrado.</p>"
        summary_data["total"] = 0.0
        return summary_data

    try:
        df = pd.read_excel(file_path, dtype={"Artista Normalizado": str, "Your Earnings": float})

        df.columns = [str(col).strip().lower() for col in df.columns]

        df.rename(columns={"artista normalizado": "artist", "your earnings": "royalties"}, inplace=True)

        df["royalties"] = pd.to_numeric(df["royalties"], errors="coerce").fillna(0)

        df = df.sort_values(by="royalties", ascending=False)


        summary_data["Resumen"] = df.to_html(
            index=False,
            border=0,
            float_format="%.2f",
            classes="table table-transparent text-center align-middle",
            formatters={
                "artist": lambda x: f'<td style="text-align: left;">{x.title()}</td>',
                "royalties": lambda x: f'<td style="text-align: right;">{x:.2f}</td>'
            },
            escape=False
        )

        summary_data["total"] = round(df["royalties"].sum(), 2)

    except Exception as e:

        summary_data["Resumen"] = f"<p style='color:red;'>Error al procesar resumen: {e}</p>"
        summary_data["total"] = 0.0

    return summary_data

def generate_song_bar_chart(df):
    df_sorted = df.sort_values(by="Royalties", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='none')
    ax.bar(df_sorted["Song"], df_sorted["Royalties"], color="steelblue")
    ax.set_ylabel("Royalties")
    ax.set_title("Top 10 Songs")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(GENERATED_FOLDER, "song_bar_chart.png"), transparent=True)
    plt.close()



def extract_net_payment_from_by_song(file_path):
    try:

        df = pd.read_excel(file_path, sheet_name="By Song", skiprows=8, dtype=str)
        df = df.fillna('')
        for i in range(len(df)):
            for j in range(len(df.columns)):
                cell_value = str(df.iloc[i, j]).strip().lower()
                if "net payment" in cell_value:


                    if j + 1 < len(df.columns):
                        value = df.iloc[i, j + 1]

                    elif j > 0:
                        value = df.iloc[i, j - 1]

                    else:
                        value = ""


                    value = str(value).replace(",", "").replace("$", "").strip()


                    try:
                        return round(float(value), 2)
                    except:

                        return 0.0


        return 0.0

    except Exception as e:

        return 0.0



def load_excel_data(artist, quarter, year):

    filename = f"{artist}T{quarter}-{year}.xlsx"
    file_path = os.path.join(DATA_FOLDER, filename)
    sheets_data = {}

    if not os.path.exists(file_path):
        sheets_data["By Song"] = "<p style='color:red;'>Archivo no encontrado.</p>"
        sheets_data["By Source"] = "<p style='color:red;'>Archivo no encontrado.</p>"
        sheets_data["total_royalties"] = 0.0
        return sheets_data

    try:
        df_song = pd.read_excel(file_path, sheet_name="By Song", skiprows=8, nrows=11)
        df_song_clean = clean_by_song(df_song)
        generate_song_bar_chart(df_song_clean)
        sheets_data["By Song"] = df_song_clean.to_html(
            header=False, index=False, border=0, float_format="%.2f",
            classes="table table-transparent text-center align-middle",
            formatters={
                "Song": lambda x: f'<td style="text-align: left;">{x}</td>',
                "Royalties": lambda x: f'<td style="text-align: right;">{x:.2f}</td>'
            }, escape=False
        )
    except Exception as e:
        sheets_data["By Song"] = f"<p style='color:red;'>Error 'By Song': {e}</p>"

    try:
        df_source = pd.read_excel(file_path, sheet_name="By Source", skiprows=8)
        df_source_clean = clean_by_source(df_source)
        generate_source_pie_chart(df_source_clean)
        top3 = df_source_clean.nlargest(5, "Royalties")
        sheets_data["By Source"] = top3.to_html(
            header=False, index=False, border=0, float_format="%.2f",
            classes="table table-transparent text-center align-middle",
            formatters={
                "Source": lambda x: f'<td style="text-align: left;">{x}</td>',
                "Royalties": lambda x: f'<td style="text-align: right;">{x:.2f}</td>'
            }, escape=False
        )
    except Exception as e:
        sheets_data["By Source"] = f"<p style='color:red;'>Error 'By Source': {e}</p>"

    sheets_data["total_royalties"] = extract_net_payment_from_by_song(file_path)


    return sheets_data



def calculate_future_total(artist, selected_quarter, selected_year):
    all_files = os.listdir(DATA_FOLDER)
    pattern = re.compile(re.escape(artist) + r"T(\d)-(\d{4})\.xlsx")
    matched = [m for m in (pattern.match(f) for f in all_files) if m]
    total = 0.0

    for m in matched:
        q, y = int(m.group(1)), int(m.group(2))
        if y == int(selected_year) and q <= int(selected_quarter):
            file_path = os.path.join(DATA_FOLDER, f"{artist}T{q}-{selected_year}.xlsx")
            try:
                total += float(extract_net_payment_from_by_song(file_path) or 0)
            except: continue
    return round(total, 2)

def get_investment_amount(quarter, year):
    investment_file = os.path.join(DATA_FOLDER, "inversion.xlsx")
    if not os.path.exists(investment_file): return "No se han realizado inversiones"
    try:
        df = pd.read_excel(investment_file)
        df.columns = [str(col).strip().lower() for col in df.columns]


        possible_year_cols = [c for c in df.columns if 'año' in c or 'ano' in c or 'year' in c]
        possible_quarter_cols = [c for c in df.columns if 'trimestre' in c or 'quarter' in c or 'trim' in c]
        possible_amount_cols = [c for c in df.columns if 'invers' in c or 'inversión' in c or 'amount' in c or 'inversion' in c]
        if not possible_year_cols or not possible_quarter_cols or not possible_amount_cols: return "No se han realizado inversiones"
        year_col, quarter_col, amount_col = possible_year_cols[0], possible_quarter_cols[0], possible_amount_cols[0]
        match = df[(pd.to_numeric(df[year_col], errors='coerce') == int(year)) & (pd.to_numeric(df[quarter_col], errors='coerce') == int(quarter))]
        if not match.empty:
            return round(float(match.iloc[0][amount_col]), 2)
        return "No se han realizado inversiones"
    except: return "No se han realizado inversiones"

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.permanent = True

    if request.method == 'POST':
        username, password = request.form.get('username'), request.form.get('password')
        user = USERS.get(username)
        if user and user['password'] == password:
            session.update({'user': username, 'username': username, 'is_admin': user.get('is_admin', False)})
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect(url_for("login"))
    username = session["user"]
    user_info = USERS.get(username)
    artist = user_info.get("artist", username)

    is_admin = session.get("is_admin", False)






    all_files = os.listdir(DATA_FOLDER)

    if is_admin:
        selected_artist_key = request.args.get("artist") or "all"
        if selected_artist_key == "all":
            pattern = re.compile(r"resumen_por_artista_T(\d)-(\d{4})\.xlsx")
            artist_name, image_filename = "Resumen General", "resumen_general.png"
        else:
            artist_file_key = USERS.get(selected_artist_key, {}).get("artist", selected_artist_key)
            artist_name, image_filename = artist_file_key, f"{artist_file_key}.jpg"
        available_artists = ["all"] + [k for k in USERS if k != "AdminUser"]

    else:
        selected_artist_key = username
        artist_file_key = user_info.get("artist", selected_artist_key)
        artist_name, image_filename = artist_file_key, f"{artist_file_key}.jpg"
        pattern = re.compile(re.escape(artist_file_key) + r"T(\d)-(\d{4})\.xlsx")
        available_artists = []


    session['selected_artist_key'] = selected_artist_key







    matched = [m for m in (pattern.match(f) for f in all_files) if m]

    available_years = sorted(set(m.group(2) for m in matched))
    selected_year = request.args.get("year") or (available_years[-1] if available_years else "2024")
    available_quarters = sorted(set(m.group(1) for m in matched if m.group(2) == selected_year), reverse=True)
    selected_quarter = request.args.get("quarter") or (available_quarters[0] if available_quarters else "1")

    image_path = os.path.join("static", "images", image_filename)
    artist_image = f"images/{image_filename}" if os.path.exists(image_path) else "images/default.jpg"

    return render_template("dashboard.html", artist_name=artist_name, artist_image=artist_image,
        selected_year=selected_year, selected_quarter=selected_quarter, available_years=available_years,
        available_quarters=available_quarters, available_artists=available_artists,
        selected_artist_key=selected_artist_key, is_admin=is_admin, USERS=USERS)

@app.route("/load_dashboard_data")
def load_dashboard_data():
    if "user" not in session: return jsonify({"error": "Unauthorized"}), 401
    try:
        selected_artist_key, selected_year, selected_quarter = request.args.get("artist"), request.args.get("year"), request.args.get("quarter")
        is_admin = session.get("is_admin", False)

        if is_admin and (not selected_artist_key or selected_artist_key == "all"):
            quarter_range = QUARTER_RANGES.get(selected_quarter.replace("T", ""), "Desconocido")
            return jsonify({"sheets": None, "future_total": 0.0, "investment": 0.0, "balance": 0.0, "quarter_dates": f"{quarter_range} {selected_year}"})

        artist = USERS.get(selected_artist_key if is_admin else session["user"], {}).get("artist")
        sheets_data = load_excel_data(artist, selected_quarter, selected_year)
        future_total = calculate_future_total(artist, selected_quarter, selected_year)
        investment = get_investment_amount(selected_quarter, selected_year)
        balance = round(future_total - investment, 2) if isinstance(investment, (int, float)) else None
        quarter_range = QUARTER_RANGES.get(selected_quarter.replace("T", ""), "Desconocido")







        return jsonify({
            "sheets": {"by_song": sheets_data["By Song"], "by_source": sheets_data["By Source"], "total_royalties": sheets_data["total_royalties"]},
            "future_total": future_total, "investment": investment, "balance": balance, "quarter_dates": f"{quarter_range} {selected_year}"

        })


    except Exception as e:
        return jsonify({"error": "Error interno"}), 500

@app.route("/download_statement")
def download_statement():
    if "user" not in session: return redirect(url_for("login"))
    artist = USERS[session["user"]]["artist"]
    quarter, year = request.args.get("quarter"), request.args.get("year")
    file_path = os.path.join(DATA_FOLDER, f"{artist}A{quarter}-{year}.xlsx")
    if os.path.exists(file_path): return send_file(file_path, as_attachment=True)
    return "Archivo no encontrado", 404

if __name__ == "__main__":
    app.run(debug=True)
    