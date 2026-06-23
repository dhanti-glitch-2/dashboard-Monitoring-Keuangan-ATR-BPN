import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import base64, io, os, json

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Proyeksi Anggaran ATR/BPN",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── LOGIN & MANAJEMEN USER ──────────────────────────────────────────────────
ROLE_LABEL = {
    'keuangan':     'Admin Keuangan',
    'kepala_kantor':'Kepala Kantor',
    'kasubbag_tu':  'Kasubbag Tata Usaha',
    'seksi':        'Admin Seksi',
}
FULL_ACCESS_ROLES = ['keuangan', 'kepala_kantor', 'kasubbag_tu']

USERS_FILE = os.path.join(os.path.dirname(__file__), 'users_data.json')

DEFAULT_USERS = {
    "admin":         {"password": "atrbpn2025",  "role": "keuangan",     "nama": "Admin Keuangan"},
    "kepala.kantor": {"password": "kepala2025",  "role": "kepala_kantor","nama": "Kepala Kantor"},
    "kasubbag.tu":   {"password": "kasubbag2025","role": "kasubbag_tu",  "nama": "Kasubbag Tata Usaha"},
    "andi.s1":   {"password": "andi2025",   "role": "seksi", "seksi": "S1", "nama": "Andi Wijaya"},
    "siti.s1":   {"password": "siti2025",   "role": "seksi", "seksi": "S1", "nama": "Siti Rahma"},
    "budi.s2":   {"password": "budi2025",   "role": "seksi", "seksi": "S2", "nama": "Budi Santoso"},
    "rina.s2":   {"password": "rina2025",   "role": "seksi", "seksi": "S2", "nama": "Rina Putri"},
    "doni.s3":   {"password": "doni2025",   "role": "seksi", "seksi": "S3", "nama": "Doni Saputra"},
    "wati.s3":   {"password": "wati2025",   "role": "seksi", "seksi": "S3", "nama": "Wati Susanti"},
    "eko.s4":    {"password": "eko2025",    "role": "seksi", "seksi": "S4", "nama": "Eko Prasetyo"},
    "lina.s4":   {"password": "lina2025",   "role": "seksi", "seksi": "S4", "nama": "Lina Marlina"},
    "fajar.s5":  {"password": "fajar2025",  "role": "seksi", "seksi": "S5", "nama": "Fajar Hidayat"},
    "dewi.s5":   {"password": "dewi2025",   "role": "seksi", "seksi": "S5", "nama": "Dewi Lestari"},
    "gilang.s6": {"password": "gilang2025", "role": "seksi", "seksi": "S6", "nama": "Gilang Ramadhan"},
    "yuni.s6":   {"password": "yuni2025",   "role": "seksi", "seksi": "S6", "nama": "Yuni Astuti"},
}

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and len(data) > 0:
                return data
        except Exception:
            pass
    save_users(DEFAULT_USERS)
    return dict(DEFAULT_USERS)

def save_users(users_dict):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_dict, f, indent=2, ensure_ascii=False)

USERS = load_users()

def show_login():
    st.markdown("""
    <style>
    .login-wrap {
        max-width: 420px; margin: 80px auto 0; background: white;
        border-radius: 20px; padding: 40px 36px;
        box-shadow: 0 8px 40px rgba(26,58,107,0.13);
    }
    .login-logo { text-align:center; margin-bottom:24px; }
    .login-title { font-size:22px; font-weight:800; color:#1a3a6b; text-align:center; margin-bottom:4px; }
    .login-sub { font-size:12px; color:#636e72; text-align:center; margin-bottom:28px; }
    </style>
    <div class="login-wrap">
      <div class="login-logo"><span style="font-size:56px">🏛️</span></div>
      <div class="login-title">ATR/BPN Surabaya I</div>
      <div class="login-sub">Sistem Proyeksi & Monitoring Anggaran</div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1,2,1])
    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)
        username = st.text_input("👤 Username", placeholder="Masukkan username")
        password = st.text_input("🔒 Password", type="password", placeholder="Masukkan password")
        login_btn = st.button("🔑 Masuk", use_container_width=True, type="primary")

        if login_btn:
            if username in USERS and USERS[username]["password"] == password:
                user_info = USERS[username]
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['role'] = user_info["role"]
                st.session_state['seksi_akses'] = user_info.get("seksi", None)
                st.session_state['nama_user'] = user_info.get("nama", username)
                st.rerun()
            else:
                st.error("❌ Username atau password salah. Silakan coba lagi.")
                st.info("⚠️ Akses hanya untuk Admin Keuangan, Kepala Kantor, Kasubbag TU, dan pegawai Seksi yang terdaftar.")

        st.markdown("""
        <div style='text-align:center;font-size:11px;color:#b2bec3;margin-top:20px'>
        © 2026 Kantor ATR/BPN Surabaya I
        </div>
        """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'seksi_akses' not in st.session_state:
    st.session_state['seksi_akses'] = None
if 'nama_user' not in st.session_state:
    st.session_state['nama_user'] = None

if not st.session_state['logged_in']:
    show_login()
    st.stop()

ROLE = st.session_state['role']
SEKSI_AKSES = st.session_state['seksi_akses']
NAMA_USER = st.session_state.get('nama_user') or st.session_state.get('username','')

# ─── KONSTANTA ───────────────────────────────────────────────────────────────
BULAN = ['Februari','Maret','April','Mei','Juni','Juli',
         'Agustus','September','Oktober','November','Desember']
SEKSI_LIST = ['S1','S2','S3','S4','S5','S6']
SEKSI_NAMA = {
    'S1': 'Survei & Pemetaan',
    'S2': 'Penetapan Hak & Pendaftaran',
    'S3': 'Penataan & Pemberdayaan',
    'S4': 'Pengadaan Tanah & Pengembangan',
    'S5': 'Pengendalian & Sengketa',
    'S6': 'Sub Bag Tata Usaha'
}
COLORS = ['#1a3a6b','#00b894','#e17055','#c8a84b','#9b59b6','#2e86de']
SEKSI_COLORS = dict(zip(SEKSI_LIST, COLORS))

# ─── REGRESI ─────────────────────────────────────────────────────────────────
# Koefisien dari laporan SPSS. Risiko diklasifikasikan berdasarkan MAE:
#   Rendah  → MAE ≤ 1%   (prediksi sangat akurat)
#   Sedang  → 1% < MAE ≤ 3%  (prediksi cukup baik)
#   Tinggi  → MAE > 3%   (prediksi kurang akurat, perlu perhatian)
REGRESI = {
    'S1': {'a': 10.201, 'b': -0.331, 'mae': 2.53,  'risiko': 'Sedang'},   # 1% < 2.53% ≤ 3%
    'S2': {'a': 10.390, 'b': -0.350, 'mae': 0.44,  'risiko': 'Rendah'},   # 0.44% ≤ 1%
    'S3': {'a':  8.371, 'b': -0.279, 'mae': 4.99,  'risiko': 'Tinggi'},   # 4.99% > 3%
    'S4': {'a': 10.974, 'b': -0.422, 'mae': 0.01,  'risiko': 'Rendah'},   # 0.01% ≤ 1%
    'S5': {'a': 10.312, 'b': -0.324, 'mae': 0.03,  'risiko': 'Rendah'},   # 0.03% ≤ 1%
    'S6': {'a': 11.724, 'b': -0.446, 'mae': 0.01,  'risiko': 'Rendah'},   # 0.01% ≤ 1%
}

# Tren historis (% realisasi tahunan dari pagu)
TREN = {
    'S1': {2018:81.79,2019:81.07,2020:84.58,2021:96.08,2022:93.88,2023:93.88,2024:66.75,2025:98.25},
    'S2': {2018:85.00,2019:88.00,2020:86.41,2021:78.99,2022:88.88,2023:98.82,2024:99.94,2025:99.99},
    'S3': {2018:71.53,2019:71.09,2020:55.48,2021:24.34,2022:68.63,2023:95.49,2024:100.00,2025:98.74},
    'S4': {2018:98.00,2019:37.26,2020:100.00,2021:100.00,2022:99.95,2023:100.00,2024:100.00,2025:100.00},
    'S5': {2018:78.61,2019:75.71,2020:89.78,2021:99.81,2022:99.98,2023:99.94,2024:93.44,2025:99.25},
    'S6': {2018:96.60,2019:98.22,2020:98.29,2021:98.95,2022:98.90,2023:99.73,2024:99.39,2025:99.98},
}

# ─── LOAD DATA EXCEL ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    b64_path = os.path.join(os.path.dirname(__file__), 'data_b64.txt')
    with open(b64_path, 'r') as f:
        b64 = f.read().strip()
    xls_bytes = base64.b64decode(b64)
    df = pd.read_excel(io.BytesIO(xls_bytes), sheet_name='DATA GABUNGAN LENGKAP', header=2)
    df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
    df = df[df['Seksi'].isin(SEKSI_LIST)]
    df = df[df['Bulan'].isin(BULAN)]
    df['Tahun'] = df['Tahun'].astype(int)
    int_cols = ['Pagu PNBP (Rp)','Pagu RM PTSL (Rp)','Pagu RM Non-PTSL (Rp)',
                'Realisasi PNBP (Rp)','Realisasi RM PTSL (Rp)','Realisasi RM Non-PTSL (Rp)']
    for c in int_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
    df['TotalPagu'] = df['Pagu PNBP (Rp)'] + df['Pagu RM PTSL (Rp)'] + df['Pagu RM Non-PTSL (Rp)']
    df['TotalReal'] = df['Realisasi PNBP (Rp)'] + df['Realisasi RM PTSL (Rp)'] + df['Realisasi RM Non-PTSL (Rp)']
    return df

# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────
def get_pagu(df, seksi, tahun, bulan_idx=None):
    sub = df[(df['Seksi']==seksi) & (df['Tahun']==tahun)].copy()
    if sub.empty:
        return 0
    sub['_idx'] = sub['Bulan'].apply(lambda b: BULAN.index(b) if b in BULAN else -1)
    sub = sub[sub['_idx'] >= 0].sort_values('_idx')
    if bulan_idx is not None:
        sub = sub[sub['_idx'] <= bulan_idx]
        if sub.empty:
            return 0
    row = sub.iloc[-1]
    return int(row['Pagu PNBP (Rp)'] + row['Pagu RM PTSL (Rp)'] + row['Pagu RM Non-PTSL (Rp)'])

def get_pct_bulanan(df, seksi, tahun):
    pagu = get_pagu(df, seksi, tahun)
    if pagu == 0:
        return [0.0] * 11
    kum_rp = []
    for bln in BULAN:
        sub = df[(df['Seksi']==seksi) & (df['Tahun']==tahun) & (df['Bulan']==bln)]
        kum_rp.append(int(sub.iloc[0]['TotalReal']) if not sub.empty else None)
    for i in range(len(kum_rp)):
        if kum_rp[i] is None:
            kum_rp[i] = kum_rp[i-1] if i > 0 else 0
    hasil = []
    prev = 0
    for val in kum_rp:
        delta_rp = val - prev
        pct = round(delta_rp / pagu * 100, 4)
        pct = max(0.0, pct)
        pct = min(pct, 100.0)
        hasil.append(pct)
        prev = val
    return hasil

def get_kumulatif(pct):
    kum, total = [], 0
    for p in pct:
        total += p
        kum.append(round(total, 4))
    return kum

def get_delta(pct):
    delta = [pct[0]]
    for i in range(1, len(pct)):
        delta.append(round(pct[i] - pct[i-1], 4))
    return delta

def get_sisa(df, seksi, tahun, sampai_idx):
    pagu = get_pagu(df, seksi, tahun, bulan_idx=sampai_idx)
    total_real = 0
    for i in range(sampai_idx, -1, -1):
        bln = BULAN[i]
        sub = df[(df['Seksi']==seksi) & (df['Tahun']==tahun) & (df['Bulan']==bln)]
        if not sub.empty:
            total_real = int(sub.iloc[0]['TotalReal'])
            break
    total_real = min(total_real, pagu) if pagu > 0 else total_real
    sisa = max(0, pagu - total_real)
    pct_real = round(total_real / pagu * 100, 2) if pagu > 0 else 0.0
    pct_real = min(pct_real, 100.0)
    sisa_pct = round(100.0 - pct_real, 2)
    return {
        'total_pagu': pagu,
        'realisasi_rp': total_real,
        'sisa_rp': sisa,
        'realisasi_pct': pct_real,
        'sisa_pct': sisa_pct,
    }

def get_dashboard_summary(df, tahun):
    per_seksi = {}
    total_pagu = 0
    total_real = 0
    for s in SEKSI_LIST:
        pagu = get_pagu(df, s, tahun)
        sub = df[(df['Seksi']==s) & (df['Tahun']==tahun)].copy()
        sub['_bulan_idx'] = sub['Bulan'].apply(lambda b: BULAN.index(b) if b in BULAN else -1)
        sub = sub[sub['_bulan_idx'] >= 0].sort_values('_bulan_idx')
        real_rp = int(sub.iloc[-1]['TotalReal']) if not sub.empty else 0
        real_rp = min(real_rp, pagu) if pagu > 0 else real_rp
        pct = round(real_rp / pagu * 100, 2) if pagu > 0 else 0
        pct = min(pct, 100.0)
        per_seksi[s] = {
            'nama': SEKSI_NAMA[s],
            'pagu': pagu,
            'realisasi_rp': real_rp,
            'realisasi_pct': pct,
        }
        total_pagu += pagu
        total_real += real_rp
    pct_total = round(total_real / total_pagu * 100, 2) if total_pagu > 0 else 0
    return {
        'total_pagu': total_pagu,
        'total_realisasi': total_real,
        'pct_realisasi': pct_total,
        'sisa_pagu': total_pagu - total_real,
        'sisa_pct': round((total_pagu - total_real) / total_pagu * 100, 2) if total_pagu > 0 else 0,
        'per_seksi': per_seksi,
        'tahun': tahun,
    }

def badge_color(pct):
    if pct >= 80: return "🟢"
    elif pct >= 50: return "🟡"
    return "🔴"

def risiko_color(risiko):
    return {'Rendah':'#00b894','Sedang':'#fdcb6e','Tinggi':'#d63031'}.get(risiko,'#636e72')

# ─── HITUNG REGRESI ───────────────────────────────────────────────────────────
@st.cache_data
def compute_all_regresi(_df):
    """
    Tahap 1: Koefisien a, b dari laporan SPSS (hardcode).
             Proyeksi 2026 = substitusi X=1..11 ke persamaan Tahap 1.
    Tahap 2: Pool data aktual 2018-2025 + proyeksi 2026 → fit ulang otomatis.
             Proyeksi 2027 = substitusi X=1..11 ke persamaan Tahap 2.
    """
    tahun_aktual = list(range(2018, 2026))

    def regresi_ols(x_vals, y_vals):
        x = np.array(x_vals, dtype=float)
        y = np.array(y_vals, dtype=float)
        n = len(x)
        if n < 2:
            return 0.0, 0.0, 0.0, 0.0, []
        b = (n*np.sum(x*y) - np.sum(x)*np.sum(y)) / (n*np.sum(x**2) - np.sum(x)**2)
        a = (np.sum(y) - b*np.sum(x)) / n
        y_pred = a + b * x
        ss_res = np.sum((y - y_pred)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r2 = float(1 - ss_res/ss_tot) if ss_tot != 0 else 0.0
        mae = float(np.mean(np.abs(y - y_pred)))
        return round(a,4), round(b,4), round(r2,4), round(mae,4), y_pred.tolist()

    hasil = {}
    for s in SEKSI_LIST:
        x_gabung, y_gabung = [], []
        for tahun in tahun_aktual:
            pct_list = get_pct_bulanan(_df, s, tahun)
            for bi, pct in enumerate(pct_list):
                x_gabung.append(bi + 1)
                y_gabung.append(pct)

        a1 = REGRESI[s]['a']
        b1 = REGRESI[s]['b']
        mae1 = REGRESI[s]['mae']
        y_pred_gabung = [round(a1 + b1*x, 4) for x in x_gabung]
        ss_res1 = sum((y - yp)**2 for y, yp in zip(y_gabung, y_pred_gabung))
        ss_tot1 = sum((y - float(np.mean(y_gabung)))**2 for y in y_gabung)
        r2_1 = round(1 - ss_res1/ss_tot1, 4) if ss_tot1 != 0 else 0.0

        proj2026 = [max(0.0, round(a1 + b1*x, 4)) for x in range(1, 12)]

        x_gabung2 = x_gabung.copy()
        y_gabung2 = y_gabung.copy()
        for bi, pct in enumerate(proj2026):
            x_gabung2.append(bi + 1)
            y_gabung2.append(pct)

        a2, b2, r2_2, mae2, y_pred_gabung2 = regresi_ols(x_gabung2, y_gabung2)
        proj2027 = [max(0.0, round(a2 + b2*x, 4)) for x in range(1, 12)]

        hasil[s] = {
            'a1': a1, 'b1': b1, 'r2_1': r2_1, 'mae1': mae1,
            'x_gabung': x_gabung, 'y_gabung': y_gabung, 'y_pred_gabung': y_pred_gabung,
            'proj2026': proj2026,
            'a2': a2, 'b2': b2, 'r2_2': r2_2, 'mae2': mae2,
            'x_gabung2': x_gabung2, 'y_gabung2': y_gabung2, 'y_pred_gabung2': y_pred_gabung2,
            'proj2027': proj2027,
        }
    return hasil

# ─── LOAD ────────────────────────────────────────────────────────────────────
df = load_data()
regresi_data = compute_all_regresi(df)
PROYEKSI_2026 = {s: regresi_data[s]['proj2026'] for s in SEKSI_LIST}
PROYEKSI_2027 = {s: regresi_data[s]['proj2027'] for s in SEKSI_LIST}

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
  --primary: #1a3a6b; --secondary: #c8a84b; --accent: #2e86de;
  --bg: #f0f4f8; --success: #00b894; --danger: #d63031;
  --warning: #fdcb6e; --muted: #636e72;
}
[data-testid="stSidebar"] { background: var(--primary) !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] .stSelectbox label { color: rgba(255,255,255,0.6) !important; font-size:11px !important; }
[data-testid="stSidebar"] .stButton button {
    background-color: rgba(255,255,255,0.15) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background-color: rgba(255,255,255,0.28) !important;
    border-color: rgba(255,255,255,0.6) !important;
}
.stat-card {
  border-radius: 16px; padding: 22px 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  color: white; position: relative; overflow: hidden; transition: transform .2s;
}
.stat-card:hover { transform: translateY(-3px); }
.stat-icon { font-size: 28px; margin-bottom: 10px; }
.stat-value { font-size: 22px; font-weight: 800; }
.stat-label { font-size: 12px; opacity: 0.8; margin-top: 2px; }
.stat-sub { font-size: 11px; opacity: 0.7; margin-top: 6px; }
.chart-card {
  background: white; border-radius: 16px; padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06); margin-bottom: 16px;
}
.chart-title {
  font-weight: 700; color: var(--primary); font-size: 14px;
  margin-bottom: 16px; display: flex; align-items: center; gap: 8px;
}
.badge-success { background:#d4edda; color:#155724; padding:3px 10px; border-radius:50px; font-size:11px; font-weight:700; }
.badge-warning { background:#fff3cd; color:#856404; padding:3px 10px; border-radius:50px; font-size:11px; font-weight:700; }
.badge-danger  { background:#f8d7da; color:#721c24; padding:3px 10px; border-radius:50px; font-size:11px; font-weight:700; }
.stMetric { background:white; border-radius:12px; padding:16px !important; box-shadow:0 2px 12px rgba(0,0,0,0.06); }
.info-box {
  background:#e8f4fd; border-radius:10px; padding:14px 18px;
  margin-bottom:16px; border-left:4px solid #1a3a6b;
  font-size:13px; line-height:1.7;
}
.info-box-green {
  background:#e8fdf5; border-radius:10px; padding:14px 18px;
  margin-bottom:16px; border-left:4px solid #00b894;
  font-size:13px; line-height:1.7;
}
.info-box-yellow {
  background:#fffbea; border-radius:10px; padding:14px 18px;
  margin-bottom:16px; border-left:4px solid #c8a84b;
  font-size:13px; line-height:1.7;
}
.keterangan-box {
  background:#f8f9fa; border-radius:10px; padding:16px 20px;
  margin-top:8px; font-size:13px; line-height:1.8;
}
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:16px 0 12px; border-bottom:1px solid rgba(255,255,255,0.15); margin-bottom:8px'>
      <div style='font-size:42px'>🏛️</div>
      <div style='font-weight:700; font-size:13px; color:#c8a84b; margin-top:6px'>ATR/BPN SURABAYA I</div>
      <div style='font-size:11px; opacity:0.6'>Sistem Proyeksi Anggaran</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='font-size:11px;color:rgba(255,255,255,0.5);text-align:center;margin-bottom:6px'>
    👤 Login sebagai: <strong style='color:#c8a84b'>{NAMA_USER}</strong><br>
    <span style='font-size:10px;opacity:0.7'>{ROLE_LABEL.get(ROLE, ROLE)}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:10px;text-transform:uppercase;letter-spacing:1.5px;opacity:0.45;padding:12px 0 4px;font-weight:600'>Menu Utama</div>", unsafe_allow_html=True)

    if ROLE in FULL_ACCESS_ROLES:
        menu_options = ["🏠 Dashboard", "📊 Monitoring Bulanan", "📈 Analisis & Proyeksi", "📐 Regresi Linear", "👥 Manajemen User"]
    else:
        menu_options = ["🏠 Dashboard", "📊 Monitoring Bulanan"]

    halaman = st.radio("", menu_options, label_visibility="collapsed")

    if ROLE == 'seksi':
        st.markdown(f"""
        <div style='background:rgba(200,168,75,0.15);border-radius:8px;padding:8px 12px;
                    margin-top:8px;font-size:11px;color:#c8a84b;text-align:center'>
        🔒 Akses: <b>{SEKSI_AKSES} — {SEKSI_NAMA[SEKSI_AKSES]}</b>
        </div>
        """, unsafe_allow_html=True)
    elif ROLE in FULL_ACCESS_ROLES:
        st.markdown(f"""
        <div style='background:rgba(0,184,148,0.15);border-radius:8px;padding:8px 12px;
                    margin-top:8px;font-size:11px;color:#00b894;text-align:center'>
        🔓 Akses: <b>Seluruh Seksi (S1–S6)</b>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for key in ['logged_in','username','role','seksi_akses','nama_user']:
            st.session_state[key] = False if key == 'logged_in' else None
        st.rerun()
    st.markdown("<div style='font-size:11px;opacity:0.5;text-align:center;margin-top:8px'>© 2026 ATR/BPN Surabaya I</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if halaman == "🏠 Dashboard":
    st.markdown("<h4 style='color:#1a3a6b;font-weight:800;margin-bottom:4px'>🏠 Dashboard — Ringkasan Anggaran</h4>", unsafe_allow_html=True)
    st.markdown("""
    <div class='info-box'>
    📌 <b>Tentang halaman ini:</b> Dashboard menampilkan ringkasan realisasi anggaran seluruh seksi
    untuk tahun yang dipilih. <b>Pagu</b> adalah jumlah anggaran yang dialokasikan,
    <b>Realisasi</b> adalah anggaran yang sudah terserap/digunakan, dan
    <b>Sisa Pagu</b> adalah selisih anggaran yang belum digunakan hingga akhir data.
    </div>
    """, unsafe_allow_html=True)

    tahun_list_db = sorted(df['Tahun'].unique().tolist(), reverse=True)
    tahun_ref = st.selectbox("📅 Pilih Tahun", tahun_list_db, index=0, key='db_tahun')
    summary = get_dashboard_summary(df, tahun_ref)

    if ROLE == 'seksi':
        st.markdown(f"""
        <div style='background:#fff3cd;border-radius:10px;padding:12px 18px;margin-bottom:16px;
                    border-left:4px solid #c8a84b;font-size:13px'>
        🔒 Anda login sebagai <b>{NAMA_USER} — {SEKSI_AKSES} ({SEKSI_NAMA[SEKSI_AKSES]})</b>.
        Dashboard hanya menampilkan data seksi Anda.
        </div>
        """, unsafe_allow_html=True)

    tampil_seksi = SEKSI_LIST if ROLE in FULL_ACCESS_ROLES else [SEKSI_AKSES]

    if ROLE in FULL_ACCESS_ROLES:
        c1,c2,c3,c4 = st.columns(4)
        cards = [
            (c1,"💼",f"Rp {summary['total_pagu']:,.0f}",f"Total Pagu {tahun_ref}","Jumlah anggaran dialokasikan","linear-gradient(135deg,#1a3a6b,#2e6da4)"),
            (c2,"✅",f"Rp {summary['total_realisasi']:,.0f}","Total Realisasi",f"{summary['pct_realisasi']}% terserap","linear-gradient(135deg,#00b894,#00cec9)"),
            (c3,"⏳",f"Rp {summary['sisa_pagu']:,.0f}","Sisa Pagu",f"{summary['sisa_pct']}% belum terserap","linear-gradient(135deg,#e17055,#d63031)"),
            (c4,"📊",f"{summary['pct_realisasi']}%","% Realisasi Keseluruhan",f"Tahun {tahun_ref}","linear-gradient(135deg,#c8a84b,#f9ca24)"),
        ]
        for col, icon, val, lbl, sub, grad in cards:
            col.markdown(f"""
            <div class="stat-card" style="background:{grad}">
              <div class="stat-icon">{icon}</div>
              <div class="stat-value">{val}</div>
              <div class="stat-label">{lbl}</div>
              <div class="stat-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        d = summary['per_seksi'][SEKSI_AKSES]
        c1,c2,c3 = st.columns(3)
        cards_s = [
            (c1,"💼",f"Rp {d['pagu']:,.0f}",f"Pagu {SEKSI_AKSES}",f"Tahun {tahun_ref}","linear-gradient(135deg,#1a3a6b,#2e6da4)"),
            (c2,"✅",f"Rp {d['realisasi_rp']:,.0f}","Realisasi",f"{d['realisasi_pct']}% terserap","linear-gradient(135deg,#00b894,#00cec9)"),
            (c3,"⏳",f"Rp {d['pagu']-d['realisasi_rp']:,.0f}","Sisa Pagu",f"{round(100-d['realisasi_pct'],2)}% belum terserap","linear-gradient(135deg,#e17055,#d63031)"),
        ]
        for col, icon, val, lbl, sub, grad in cards_s:
            col.markdown(f"""
            <div class="stat-card" style="background:{grad}">
              <div class="stat-icon">{icon}</div>
              <div class="stat-value">{val}</div>
              <div class="stat-label">{lbl}</div>
              <div class="stat-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([4,6])
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🎯 Capaian Realisasi</div>', unsafe_allow_html=True)
        st.caption("Gauge (indikator jarum) menunjukkan persentase anggaran yang sudah terserap. Garis kuning = target 85%.")
        pct_gauge = summary['pct_realisasi'] if ROLE in FULL_ACCESS_ROLES else summary['per_seksi'][SEKSI_AKSES]['realisasi_pct']
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct_gauge,
            number={'suffix':'%','font':{'size':40,'color':'#1a3a6b'}},
            gauge={
                'axis':{'range':[0,100],'tickcolor':'#636e72'},
                'bar':{'color':'#1a3a6b','thickness':0.25},
                'steps':[
                    {'range':[0,50],'color':'#ffeaea'},
                    {'range':[50,75],'color':'#fff3cd'},
                    {'range':[75,100],'color':'#d4edda'},
                ],
                'threshold':{'line':{'color':'#c8a84b','width':4},'thickness':0.75,'value':85}
            }
        ))
        fig_gauge.update_layout(margin=dict(t=20,b=20,l=20,r=20),
                                paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',height=280)
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar':False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Realisasi per Seksi</div>', unsafe_allow_html=True)
        st.caption("Batang hijau = realisasi ≥ 80% (baik), kuning = 50–79% (perlu perhatian), merah = < 50% (kritis). Garis putus-putus kuning = target 85%.")
        seksi_names = [summary['per_seksi'][s]['nama'] for s in tampil_seksi]
        seksi_pcts  = [summary['per_seksi'][s]['realisasi_pct'] for s in tampil_seksi]
        bar_colors  = ['#00b894' if v>=80 else '#fdcb6e' if v>=50 else '#d63031' for v in seksi_pcts]
        fig_bar = go.Figure(go.Bar(
            x=seksi_names, y=seksi_pcts,
            marker=dict(color=bar_colors),
            text=[f"{v}%" for v in seksi_pcts], textposition='outside',
        ))
        fig_bar.add_shape(type='line',x0=-0.5,x1=len(tampil_seksi)-0.5,y0=85,y1=85,
                          line=dict(color='#c8a84b',width=2,dash='dot'))
        fig_bar.update_layout(
            margin=dict(t=20,b=60,l=40,r=20),
            paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[0,115],title='%',gridcolor='#f0f0f0'),
            xaxis=dict(tickangle=-15,tickfont=dict(size=10)),
            height=280,font=dict(family='Segoe UI',color='#2d3436')
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar':False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-title">📋 Ringkasan Anggaran per Seksi — {tahun_ref}</div>', unsafe_allow_html=True)
    rows = []
    for s in tampil_seksi:
        d = summary['per_seksi'][s]
        pct_v = d['realisasi_pct']
        badge = "🟢 " if pct_v>=80 else "🟡 " if pct_v>=50 else "🔴 "
        rows.append({
            'Seksi': f"{s} — {d['nama']}",
            'Total Pagu (Rp)': f"Rp {d['pagu']:,.0f}",
            'Realisasi (Rp)': f"Rp {d['realisasi_rp']:,.0f}",
            '% Realisasi': f"{badge}{pct_v}%",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption("🟢 ≥ 80% (baik)  |  🟡 50–79% (perlu perhatian)  |  🔴 < 50% (kritis)")
    st.markdown('</div>', unsafe_allow_html=True)

    if ROLE in FULL_ACCESS_ROLES:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🚀 Akses Cepat</div>', unsafe_allow_html=True)
        qa1, qa2 = st.columns(2)
        with qa1:
            st.info("📊 **Monitoring Bulanan** — Pantau sisa pagu & pertumbuhan realisasi per bulan untuk setiap seksi.")
        with qa2:
            st.info("📈 **Analisis & Proyeksi** — Lihat proyeksi realisasi 2026–2027 dan analisis risiko penyerapan anggaran.")
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN 2 — MONITORING BULANAN
# ═══════════════════════════════════════════════════════════════════════════════
elif halaman == "📊 Monitoring Bulanan":
    st.markdown("<h4 style='color:#1a3a6b;font-weight:800;margin-bottom:8px'>📊 Monitoring Realisasi Bulanan</h4>", unsafe_allow_html=True)
    st.markdown("""
    <div class='info-box'>
    📌 <b>Tentang halaman ini:</b> Halaman ini memantau penyerapan anggaran setiap seksi
    per bulan pada tahun yang dipilih. Pilih tahun dan bulan batas akhir untuk melihat
    kondisi realisasi sampai bulan tersebut.<br><br>
    <b>Pagu</b> = total anggaran yang dialokasikan &nbsp;|&nbsp;
    <b>Realisasi</b> = anggaran yang sudah terserap &nbsp;|&nbsp;
    <b>Sisa Pagu</b> = anggaran yang belum digunakan
    </div>
    """, unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([1,1,4])
    with fc1:
        tahun_sel = st.selectbox("Tahun", list(range(2018,2026)), index=7)
    with fc2:
        bulan_sel = st.selectbox("s/d Bulan", BULAN, index=10)
    bulan_idx = BULAN.index(bulan_sel)

    st.markdown("<br>", unsafe_allow_html=True)

    tampil_seksi_mon = SEKSI_LIST if ROLE in FULL_ACCESS_ROLES else [SEKSI_AKSES]

    cols = st.columns(min(3, len(tampil_seksi_mon)))
    card_colors = ['#2196F3','#4CAF50','#FF9800','#E91E63','#9C27B0','#00BCD4']
    hasil_monitoring = {}

    for s in SEKSI_LIST:
        sisa = get_sisa(df, s, tahun_sel, bulan_idx)
        pct  = get_pct_bulanan(df, s, tahun_sel)
        hasil_monitoring[s] = {
            'nama': SEKSI_NAMA[s],
            'sisa': sisa,
            'pct_bulanan': pct,
            'kumulatif': get_kumulatif(pct),
            'delta': get_delta(pct),
        }

    for i, s in enumerate(tampil_seksi_mon):
        d = hasil_monitoring[s]
        c = card_colors[SEKSI_LIST.index(s)]
        sisa = d['sisa']
        pct_v = sisa['realisasi_pct']
        badge_cls = "badge-success" if pct_v>=80 else "badge-warning" if pct_v>=50 else "badge-danger"
        pct_bar = min(pct_v, 100)
        col_idx = i % len(cols)
        with cols[col_idx]:
            st.markdown(f"""
            <div style='background:white;border-radius:14px;padding:18px 20px;
                        box-shadow:0 4px 14px rgba(0,0,0,0.06);
                        border-top:4px solid {c};margin-bottom:16px'>
              <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                <div>
                  <div style='font-weight:800;font-size:14px;color:#1a3a6b'>{s} — {d['nama']}</div>
                  <div style='font-size:11px;color:#636e72;margin-top:2px'>
                    Pagu: <strong>Rp {sisa['total_pagu']:,.0f}</strong>
                  </div>
                </div>
                <span class="{badge_cls}">{pct_v}% terserap</span>
              </div>
              <div style='background:#f0f4f8;border-radius:50px;height:8px;overflow:hidden;margin:12px 0 8px'>
                <div style='width:{pct_bar}%;height:100%;background:{c};border-radius:50px'></div>
              </div>
              <div style='display:flex;justify-content:space-between'>
                <div>
                  <div style='font-size:11px;color:#636e72'>Realisasi s/d {bulan_sel}</div>
                  <div style='font-size:13px;font-weight:700;color:#00b894'>Rp {sisa['realisasi_rp']:,.0f}</div>
                </div>
                <div style='text-align:right'>
                  <div style='font-size:11px;color:#636e72'>Sisa Pagu</div>
                  <div style='font-size:13px;font-weight:700;color:#d63031'>Rp {sisa['sisa_rp']:,.0f}</div>
                  <div style='font-size:11px;color:#d63031'>{sisa['sisa_pct']}% sisa</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 Kumulatif % Realisasi per Bulan</div>', unsafe_allow_html=True)
        st.caption("Grafik ini menunjukkan total penyerapan anggaran yang terakumulasi dari bulan ke bulan. Semakin curam naik di awal = penyerapan lebih merata.")
        sel_kum = st.selectbox("Pilih Seksi", tampil_seksi_mon, key='kum_seksi',
                               format_func=lambda x: f"{x} — {SEKSI_NAMA[x]}")
        d = hasil_monitoring[sel_kum]
        fig_kum = go.Figure()
        fig_kum.add_trace(go.Scatter(
            x=BULAN, y=d['kumulatif'], mode='lines+markers',
            fill='tozeroy', fillcolor='rgba(46,134,222,0.1)',
            line=dict(color='#2e86de',width=2.5),
            marker=dict(size=7,color='#2e86de'),
        ))
        fig_kum.update_layout(
            margin=dict(t=10,b=60,l=45,r=10),
            paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#fafafa',
            xaxis=dict(tickangle=-30,gridcolor='#f0f0f0'),
            yaxis=dict(title='% Kumulatif',gridcolor='#f0f0f0'),
            height=300,font=dict(family='Segoe UI',size=12)
        )
        st.plotly_chart(fig_kum, use_container_width=True, config={'displayModeBar':False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🌊 Pertumbuhan Serapan per Bulan</div>', unsafe_allow_html=True)
        st.caption("Grafik ini menunjukkan pertambahan (atau penurunan) penyerapan setiap bulan. Batang hijau = ada penambahan realisasi, merah = realisasi turun dari bulan sebelumnya.")
        sel_delta = st.selectbox("Pilih Seksi", tampil_seksi_mon, key='delta_seksi',
                                 format_func=lambda x: f"{x} — {SEKSI_NAMA[x]}")
        d2 = hasil_monitoring[sel_delta]
        delta_colors = ['#00b894' if v>=0 else '#d63031' for v in d2['delta']]
        fig_delta = go.Figure()
        fig_delta.add_trace(go.Bar(
            x=BULAN, y=d2['delta'],
            marker=dict(color=delta_colors),
        ))
        fig_delta.update_layout(
            margin=dict(t=10,b=60,l=45,r=10),
            paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#fafafa',
            xaxis=dict(tickangle=-30,gridcolor='#f0f0f0'),
            yaxis=dict(title='% Perubahan',gridcolor='#f0f0f0',zeroline=True,zerolinecolor='#ccc'),
            height=300,font=dict(family='Segoe UI',size=12)
        )
        st.plotly_chart(fig_delta, use_container_width=True, config={'displayModeBar':False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📋 Tabel % Realisasi Bulanan per Seksi</div>', unsafe_allow_html=True)
    st.caption("Angka di setiap kolom bulan adalah persentase realisasi NON-KUMULATIF (hanya bulan itu saja, bukan total). Kolom 'Kumulatif' adalah total penyerapan dari Februari s/d Desember.")
    rows = []
    for s in tampil_seksi_mon:
        d = hasil_monitoring[s]
        row = {'Seksi': s}
        for j, b in enumerate(BULAN):
            v = d['pct_bulanan'][j]
            row[b[:3]] = f"{v:.2f}%" if v > 0 else "—"
        row['Kumulatif'] = f"{d['kumulatif'][-1]}%"
        sp = d['sisa']['sisa_pct']
        row['Sisa (%)'] = f"{'🟢' if sp<=20 else '🟡' if sp<=50 else '🔴'} {sp}%"
        rows.append(row)
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption("Kolom 'Sisa (%)': 🟢 ≤ 20% sisa (hampir habis terserap)  |  🟡 21–50% sisa  |  🔴 > 50% sisa (penyerapan rendah)")
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN 3 — ANALISIS & PROYEKSI
# ═══════════════════════════════════════════════════════════════════════════════
elif halaman == "📈 Analisis & Proyeksi":
    st.markdown("<h4 style='color:#1a3a6b;font-weight:800;margin-bottom:4px'>📈 Analisis & Proyeksi Realisasi Anggaran</h4>", unsafe_allow_html=True)
    st.markdown("""
    <div class='info-box'>
    📌 <b>Tentang halaman ini:</b> Halaman ini menyajikan hasil proyeksi realisasi anggaran
    untuk tahun 2026 dan 2027 menggunakan metode regresi linear sederhana, serta analisis
    tren historis dan klasifikasi risiko penyerapan anggaran per seksi.
    </div>
    """, unsafe_allow_html=True)

    tab_proj, tab_tren, tab_risiko = st.tabs(["📅 Proyeksi 2026–2027","📉 Tren 2018–2027","⚠️ Risiko & Toleransi"])

    # ── TAB PROYEKSI ──────────────────────────────────────────────────────────
    with tab_proj:
        st.markdown("### 📅 Proyeksi Realisasi Bulanan per Seksi")
        st.markdown("""
        <div class='info-box'>
        📌 <b>Apa itu proyeksi?</b> Proyeksi adalah perkiraan realisasi anggaran di masa depan
        berdasarkan pola historis yang dihitung menggunakan persamaan regresi linear.
        Nilai yang ditampilkan adalah <b>persentase realisasi non-kumulatif per bulan</b>
        (bukan total tahunan) — artinya, berapa persen anggaran yang diperkirakan terserap
        di tiap bulan tersebut.<br><br>
        <b>2026</b> = dihitung langsung dari persamaan SPSS (data 2018–2025) &nbsp;|&nbsp;
        <b>2027</b> = dihitung ulang dengan menggabungkan data 2018–2025 + proyeksi 2026
        </div>
        """, unsafe_allow_html=True)

        tahun_proj = st.radio("Pilih Tahun Proyeksi", ["2026","2027"], horizontal=True)
        proj_data  = PROYEKSI_2026 if tahun_proj == "2026" else PROYEKSI_2027

        fig_proj = go.Figure()
        for i, s in enumerate(SEKSI_LIST):
            fig_proj.add_trace(go.Bar(
                name=s, x=BULAN, y=proj_data[s],
                marker=dict(color=COLORS[i]),
                hovertemplate=f'<b>{s}</b><br>%{{x}}: %{{y:.2f}}%<extra></extra>'
            ))
        fig_proj.update_layout(
            barmode='group',
            margin=dict(t=20,b=80,l=50,r=20),
            paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#fafafa',
            yaxis=dict(title='% Realisasi per Bulan',gridcolor='#f0f0f0'),
            xaxis=dict(tickangle=-20),
            legend=dict(orientation='h',y=-0.3),
            height=420,font=dict(family='Segoe UI')
        )
        st.plotly_chart(fig_proj, use_container_width=True, config={'displayModeBar':False})
        st.caption("Grafik batang berkelompok ini membandingkan proyeksi penyerapan anggaran tiap seksi di setiap bulan. Semakin tinggi batang = semakin besar penyerapan yang diperkirakan di bulan tersebut.")

        st.markdown("#### 📋 Perbandingan Proyeksi 2026 vs 2027 per Seksi")
        st.caption("Tanda ↑ = proyeksi 2027 lebih tinggi dari 2026 (perkiraan penyerapan meningkat), ↓ = lebih rendah, = sama.")
        rows_cmp = []
        for s in SEKSI_LIST:
            row = {'Seksi': s, 'Nama': SEKSI_NAMA[s]}
            for j, b in enumerate(BULAN):
                p26 = PROYEKSI_2026[s][j]
                p27 = PROYEKSI_2027[s][j]
                selisih = round(p27 - p26, 4)
                arah = "↑" if selisih > 0 else ("↓" if selisih < 0 else "=")
                row[b[:3]] = f"{p26} → {p27} {arah}"
            row['Total 2026'] = round(sum(PROYEKSI_2026[s]), 2)
            row['Total 2027'] = round(sum(PROYEKSI_2027[s]), 2)
            selisih_total = round(sum(PROYEKSI_2027[s]) - sum(PROYEKSI_2026[s]), 2)
            row['Selisih'] = f"{'↑ +' if selisih_total>=0 else '↓ '}{selisih_total}%"
            rows_cmp.append(row)
        st.dataframe(pd.DataFrame(rows_cmp), use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        for col, tahun_t, pdata in [(c1,"2026",PROYEKSI_2026),(c2,"2027",PROYEKSI_2027)]:
            with col:
                st.markdown(f"**📅 Proyeksi {tahun_t} per Seksi (%)**")
                rows = []
                for s in SEKSI_LIST:
                    row = {'Seksi': s}
                    for j, b in enumerate(BULAN):
                        row[b[:3]] = pdata[s][j]
                    row['Total'] = round(sum(pdata[s]),2)
                    rows.append(row)
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption("'Total' = penjumlahan seluruh proyeksi bulanan (Feb–Des). Ini adalah estimasi total penyerapan tahunan dalam persentase.")

    # ── TAB TREN ──────────────────────────────────────────────────────────────
    with tab_tren:
        st.markdown("### 📉 Tren Realisasi Anggaran Tahunan per Seksi (2018–2027)")
        st.markdown("""
        <div class='info-box'>
        📌 <b>Cara membaca grafik ini:</b> Sumbu X adalah tahun, sumbu Y adalah total persentase
        realisasi anggaran tahunan (berapa persen dari total pagu yang berhasil terserap dalam
        satu tahun). Garis vertikal putus-putus memisahkan data <b>aktual</b> (2018–2025) dengan
        <b>proyeksi</b> (2026–2027).
        </div>
        """, unsafe_allow_html=True)

        tahun_all = list(range(2018, 2028))
        fig_tren = go.Figure()
        for i, s in enumerate(SEKSI_LIST):
            vals = []
            for t in tahun_all:
                if t < 2026:
                    vals.append(TREN[s].get(t, None))
                elif t == 2026:
                    vals.append(round(sum(PROYEKSI_2026[s]),2))
                else:
                    vals.append(round(sum(PROYEKSI_2027[s]),2))
            fig_tren.add_trace(go.Scatter(
                name=f"{s} — {SEKSI_NAMA[s][:18]}",
                x=tahun_all, y=vals, mode='lines+markers',
                line=dict(color=COLORS[i],width=2.5),
                marker=dict(size=8),
            ))
        fig_tren.add_vline(x=2025.5,line_dash="dash",line_color="#636e72",line_width=1.5)
        fig_tren.add_annotation(x=2025.5,y=108,text="← Aktual | Proyeksi →",
                                showarrow=False,font=dict(color='#636e72',size=11))
        fig_tren.update_layout(
            margin=dict(t=20,b=60,l=50,r=20),
            paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#fafafa',
            xaxis=dict(title='Tahun',gridcolor='#f0f0f0'),
            yaxis=dict(title='Total % Realisasi Tahunan',gridcolor='#f0f0f0',range=[0,115]),
            legend=dict(orientation='h',y=-0.25),
            height=420,font=dict(family='Segoe UI')
        )
        st.plotly_chart(fig_tren, use_container_width=True, config={'displayModeBar':False})

        st.markdown("**📋 Data Tren Realisasi Tahunan (%)**")
        st.caption("Angka adalah persentase total pagu yang berhasil direalisasikan dalam satu tahun penuh. Kolom bertanda (P) = hasil proyeksi, bukan data aktual.")
        rows = []
        for s in SEKSI_LIST:
            row = {'Seksi': f"{s} — {SEKSI_NAMA[s]}"}
            for t in range(2018,2026):
                row[str(t)] = TREN[s].get(t,0)
            row['2026 (P)'] = round(sum(PROYEKSI_2026[s]),2)
            row['2027 (P)'] = round(sum(PROYEKSI_2027[s]),2)
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── TAB RISIKO ────────────────────────────────────────────────────────────
    with tab_risiko:
        st.markdown("### ⚠️ Klasifikasi Risiko & Toleransi Deviasi")
        st.markdown("""
        <div class='info-box'>
        📌 <b>Apa itu MAE dan klasifikasi risiko?</b><br>
        <b>MAE (Mean Absolute Error)</b> atau <i>Rata-rata Kesalahan Absolut</i> adalah ukuran
        seberapa akurat persamaan regresi dalam memperkirakan realisasi aktual.
        Semakin kecil MAE, semakin akurat proyeksinya.<br><br>
        Contoh: MAE = 2% artinya rata-rata proyeksi meleset ±2% dari nilai aktual.<br><br>
        <b>Klasifikasi risiko</b> didasarkan pada nilai MAE:<br>
        🟢 <b>Rendah</b> → MAE ≤ 1% &nbsp; — proyeksi sangat akurat, deviasi sangat kecil<br>
        🟡 <b>Sedang</b> → 1% &lt; MAE ≤ 3% &nbsp; — proyeksi cukup baik, deviasi dalam batas wajar<br>
        🔴 <b>Tinggi</b> → MAE &gt; 3% &nbsp; — proyeksi kurang akurat, pola realisasi tidak konsisten
        </div>
        """, unsafe_allow_html=True)

        risiko_clr = {'Rendah':'#00b894','Sedang':'#fdcb6e','Tinggi':'#d63031'}
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🔴 Klasifikasi Risiko per Seksi (berdasarkan MAE)**")
            st.caption("Posisi bubble menunjukkan nilai MAE tiap seksi. Semakin tinggi bubble, semakin besar MAE-nya (risiko lebih tinggi). Ukuran bubble juga mencerminkan besarnya MAE.")
            mae_vals    = [REGRESI[s]['mae'] for s in SEKSI_LIST]
            risiko_vals = [REGRESI[s]['risiko'] for s in SEKSI_LIST]
            bubble_colors = [risiko_clr[REGRESI[s]['risiko']] for s in SEKSI_LIST]

            fig_risk = go.Figure()
            for kategori in ['Tinggi', 'Sedang', 'Rendah']:
                idx = [i for i, r in enumerate(risiko_vals) if r == kategori]
                if not idx:
                    continue
                vals_k = [mae_vals[i] for i in idx]
                fig_risk.add_trace(go.Scatter(
                    x=[SEKSI_LIST[i] for i in idx],
                    y=vals_k,
                    mode='markers+text',
                    name=kategori,
                    text=[f"{v:.2f}%" for v in vals_k],
                    textposition='top center',
                    marker=dict(
                        size=[max((v ** 0.5) * 16, 18) for v in vals_k],
                        color=risiko_clr[kategori],
                        line=dict(width=2, color='#fff'),
                    ),
                ))

            fig_risk.add_hline(y=1, line_dash='dot', line_color='#fdcb6e', line_width=2,
                                annotation_text='Batas Sedang (MAE = 1%)', annotation_position='top right')
            fig_risk.add_hline(y=3, line_dash='dot', line_color='#d63031', line_width=2,
                                annotation_text='Batas Tinggi (MAE = 3%)', annotation_position='top right')
            fig_risk.update_layout(
                margin=dict(t=20,b=60,l=50,r=20),
                paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#fafafa',
                yaxis=dict(title='MAE — Rata-rata Kesalahan Absolut (%)',gridcolor='#f0f0f0'),
                xaxis=dict(title='Seksi'),
                legend=dict(title='Kategori Risiko', orientation='h', y=-0.3),
                height=380,font=dict(family='Segoe UI')
            )
            st.plotly_chart(fig_risk, use_container_width=True, config={'displayModeBar':False})

        with c2:
            st.markdown("**⚖️ Nilai MAE per Seksi**")
            st.caption("Grafik batang horizontal menunjukkan nilai MAE tiap seksi. Warna batang sesuai kategori risiko: hijau = rendah, kuning = sedang, merah = tinggi.")
            fig_mae = go.Figure(go.Bar(
                orientation='h',
                x=mae_vals,
                y=[f"{s} — {SEKSI_NAMA[s][:15]}" for s in SEKSI_LIST],
                marker=dict(color=bubble_colors),
                text=[f"{v}%" for v in mae_vals],textposition='outside',
            ))
            fig_mae.update_layout(
                margin=dict(t=20,b=40,l=200,r=60),
                paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#fafafa',
                xaxis=dict(title='MAE (%)',gridcolor='#f0f0f0'),
                height=380,font=dict(family='Segoe UI')
            )
            st.plotly_chart(fig_mae, use_container_width=True, config={'displayModeBar':False})

        st.markdown("**📏 Tabel Toleransi Deviasi ±5% — Proyeksi 2026**")
        st.markdown("""
        <div class='info-box-yellow'>
        📌 <b>Apa itu toleransi deviasi?</b> Toleransi deviasi ±5% adalah batas wajar selisih
        antara realisasi aktual dengan proyeksi. Jika realisasi berada di luar batas ini,
        perlu dilakukan evaluasi dan tindak lanjut.<br>
        Contoh: proyeksi Februari S1 = 7.87% → masih aman jika realisasi berada di 2.87% – 12.87%.
        Jika di bawah 2.87%, penyerapan tertinggal dari rencana.
        </div>
        """, unsafe_allow_html=True)
        rows = []
        for s in SEKSI_LIST:
            for j, b in enumerate(BULAN[:6]):
                proj = PROYEKSI_2026[s][j]
                rows.append({
                    'Seksi': f"{s} — {SEKSI_NAMA[s]}",
                    'Bulan': b,
                    'Proyeksi (%)': proj,
                    'Batas Bawah (-5%)': round(proj-5,2),
                    'Batas Atas (+5%)': round(proj+5,2),
                    'Keterangan': f"Jika realisasi < {round(proj-5,2)}% → perlu tindak lanjut"
                })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.markdown("**📐 Ringkasan Hasil Regresi per Seksi**")
        st.markdown("""
        <div class='info-box'>
        📌 <b>Penjelasan kolom:</b><br>
        <b>a (Intersep)</b> = titik awal persamaan saat X=0 (nilai dasar proyeksi) &nbsp;|&nbsp;
        <b>b (Koefisien)</b> = kemiringan garis, menunjukkan arah perubahan per bulan
        (negatif = realisasi cenderung menurun dari awal ke akhir tahun) &nbsp;|&nbsp;
        <b>Persamaan</b> = rumus untuk menghitung proyeksi: masukkan X (nomor bulan 1–11) untuk
        mendapatkan estimasi % realisasi bulan tersebut &nbsp;|&nbsp;
        <b>MAE</b> = rata-rata selisih antara proyeksi dan aktual &nbsp;|&nbsp;
        <b>Risiko</b> = kategori berdasarkan MAE
        </div>
        """, unsafe_allow_html=True)
        rows_reg = []
        for s in SEKSI_LIST:
            r = REGRESI[s]
            rows_reg.append({
                'Seksi': s, 'Nama': SEKSI_NAMA[s],
                'a (Intersep)': r['a'], 'b (Koefisien)': r['b'],
                'Persamaan': f"Ŷ = {r['a']} + ({r['b']})·X",
                'MAE (%)': r['mae'],
                'Risiko': r['risiko']
            })
        st.dataframe(pd.DataFrame(rows_reg), use_container_width=True, hide_index=True)

        st.markdown("""
        <div class='keterangan-box'>
        <b>📊 Ringkasan Klasifikasi Risiko Berdasarkan MAE:</b><br>
        <span style='color:#d63031'>🔴 <b>S3 — Penataan & Pemberdayaan</b> → Risiko Tinggi (MAE = 4.99%)</span><br>
        &nbsp;&nbsp;&nbsp; Pola realisasi tidak konsisten antar tahun, proyeksi memiliki ketidakpastian lebih besar.<br>
        <span style='color:#fdcb6e'>🟡 <b>S1 — Survei & Pemetaan</b> → Risiko Sedang (MAE = 2.53%)</span><br>
        &nbsp;&nbsp;&nbsp; Pola cukup stabil, proyeksi memadai dengan deviasi dalam batas moderat.<br>
        <span style='color:#00b894'>🟢 <b>S2, S4, S5, S6</b> → Risiko Rendah (MAE ≤ 1%)</span><br>
        &nbsp;&nbsp;&nbsp; Pola realisasi sangat konsisten, proyeksi sangat akurat.<br><br>
        <b>Catatan:</b> X = indeks bulan (1=Feb, 2=Mar, …, 11=Des) &nbsp;|&nbsp;
        Y = % realisasi non-kumulatif per bulan &nbsp;|&nbsp;
        Data gabungan 2018–2025 = 88 observasi per seksi
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN 4 — REGRESI LINEAR
# ═══════════════════════════════════════════════════════════════════════════════
elif halaman == "📐 Regresi Linear":
    st.markdown("<h4 style='color:#1a3a6b;font-weight:800;margin-bottom:4px'>📐 Analisis Regresi Linear</h4>", unsafe_allow_html=True)

    with st.expander("📖 Penjelasan Lengkap Metode Regresi Linear (klik untuk buka)", expanded=False):
        st.markdown("""
        <div style='background:#f0f4f8;border-radius:12px;padding:20px 24px;line-height:1.8'>
        <h5 style='color:#1a3a6b;margin-bottom:12px'>Apa itu Regresi Linear Sederhana?</h5>
        <p>Regresi linear sederhana adalah metode statistik untuk memperkirakan nilai suatu
        variabel berdasarkan variabel lain yang memiliki hubungan linear (garis lurus).
        Dalam konteks ini, metode ini digunakan untuk memperkirakan berapa persen anggaran
        yang akan terserap di bulan tertentu.</p>

        <div style='background:white;border-radius:8px;padding:14px 18px;margin:12px 0;border-left:4px solid #1a3a6b'>
        <b>Persamaan dasar:</b> <span style='font-size:16px;font-family:monospace'><b>Ŷ = a + b·X</b></span><br><br>
        <b>Penjelasan simbol:</b><br>
        • <b>Ŷ</b> (Y topi) = nilai yang diprediksi (% realisasi per bulan)<br>
        • <b>a</b> (intersep) = nilai awal saat X = 0; titik potong garis dengan sumbu Y<br>
        • <b>b</b> (koefisien/kemiringan) = perubahan Y setiap X bertambah 1;
          nilai negatif berarti realisasi cenderung turun dari awal ke akhir tahun<br>
        • <b>X</b> = indeks bulan: 1=Februari, 2=Maret, …, 11=Desember
        </div>

        <div style='background:white;border-radius:8px;padding:14px 18px;margin:12px 0;border-left:4px solid #00b894'>
        <b>Contoh penggunaan:</b><br>
        S1 memiliki persamaan Ŷ = 10.201 + (−0.331)·X<br>
        Untuk bulan Maret (X=2): Ŷ = 10.201 − 0.331×2 = 10.201 − 0.662 = <b>9.539%</b><br>
        Artinya: diperkirakan 9.539% dari total pagu S1 terserap di bulan Maret 2026.
        </div>

        <div style='background:white;border-radius:8px;padding:14px 18px;margin:12px 0;border-left:4px solid #c8a84b'>
        <b>Alur Proyeksi Dua Tahap:</b><br>
        <b>Tahap 1 →</b> Gunakan koefisien dari hasil SPSS (data 2018–2025) →
        substitusi X=1 s/d 11 → hasil = <b>Proyeksi 2026</b><br>
        <b>Tahap 2 →</b> Gabungkan data 2018–2025 dengan Proyeksi 2026 →
        hitung persamaan baru → substitusi X=1 s/d 11 → hasil = <b>Proyeksi 2027</b><br><br>
        <b>Mengapa dua tahap?</b> Agar proyeksi 2027 mempertimbangkan perkiraan kondisi 2026,
        sehingga lebih adaptif terhadap tren terkini.
        </div>

        <div style='background:white;border-radius:8px;padding:14px 18px;margin:12px 0;border-left:4px solid #e17055'>
        <b>Ukuran akurasi:</b><br>
        • <b>R² (R-kuadrat)</b> = seberapa besar variasi data yang bisa dijelaskan oleh persamaan.
          Nilai 0–1; semakin mendekati 1 semakin baik (R²=0.8 artinya 80% pola data terwakili).<br>
        • <b>MAE (Mean Absolute Error)</b> = rata-rata selisih absolut antara nilai proyeksi dan aktual.
          Satuan sama dengan Y (%). MAE=2% artinya rata-rata proyeksi meleset ±2% dari aktual.
        </div>
        </div>
        """, unsafe_allow_html=True)

    tab_r1, tab_r2, tab_r3, tab_r4 = st.tabs([
        "📊 Tahap 1 — Proyeksi 2026",
        "📊 Tahap 2 — Proyeksi 2027",
        "📋 Ringkasan & Akurasi",
        "🧮 Kalkulator Data Baru"
    ])

    # ── TAB 1 ──
    with tab_r1:
        st.markdown("""
        <div class='info-box'>
        <b>📌 Regresi Tahap 1</b> — Data aktual realisasi 2018–2025 digabung menjadi satu dataset.
        Setiap tahun menghasilkan 11 pasang data (X = bulan, Y = % realisasi), sehingga
        total 88 observasi per seksi. Persamaan regresi dihitung menggunakan SPSS dan
        digunakan untuk memproyeksikan realisasi tiap bulan di tahun <b>2026</b>.
        </div>
        """, unsafe_allow_html=True)

        col_sel1, _ = st.columns([1,2])
        with col_sel1:
            sel_s1 = st.selectbox("Pilih Seksi", SEKSI_LIST,
                                   format_func=lambda x: f"{x} — {SEKSI_NAMA[x]}", key='reg_s1')

        rd1 = regresi_data[sel_s1]
        a1v, b1v, r2_1v, mae1v = rd1['a1'], rd1['b1'], rd1['r2_1'], rd1['mae1']
        proj26 = rd1['proj2026']

        col_eq1,col_eq2,col_eq3,col_eq4 = st.columns(4)
        metric_info = [
            (col_eq1,"Konstanta (a)","Nilai awal / intersep persamaan",f"{a1v}","#1a3a6b"),
            (col_eq2,"Koefisien (b)","Kemiringan garis; negatif = tren menurun",f"{b1v}","#e17055"),
            (col_eq3,"R² (R-Kuadrat)","Seberapa baik persamaan menjelaskan data (0–1)",f"{r2_1v}","#00b894"),
            (col_eq4,"MAE (%)","Rata-rata kesalahan proyeksi terhadap aktual",f"{mae1v:.4f}","#c8a84b"),
        ]
        for col, label, keterangan, val, color in metric_info:
            col.markdown(f"""
            <div style='background:white;border-radius:12px;padding:16px 18px;
                        box-shadow:0 2px 12px rgba(0,0,0,0.07);border-top:3px solid {color};text-align:center'>
              <div style='font-size:11px;color:#636e72;margin-bottom:2px'>{label}</div>
              <div style='font-size:20px;font-weight:800;color:{color}'>{val}</div>
              <div style='font-size:10px;color:#b2bec3;margin-top:4px'>{keterangan}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:#1a3a6b;color:white;border-radius:10px;padding:12px 20px;margin:16px 0;text-align:center;font-size:15px'>
        <b>Persamaan (SPSS):</b> &nbsp; Ŷ = {a1v} + ({b1v}) · X &nbsp;|&nbsp;
        X = 1 (Feb) … 11 (Des) &nbsp;|&nbsp; n = {len(rd1['x_gabung'])} observasi
        </div>
        """, unsafe_allow_html=True)

        st.caption("Masukkan X (nomor bulan: 1=Feb s/d 11=Des) ke persamaan di atas untuk mendapatkan proyeksi % realisasi bulan tersebut.")

        fig_r1 = go.Figure()
        fig_r1.add_trace(go.Scatter(
            x=rd1['x_gabung'], y=rd1['y_gabung'], mode='markers',
            name='Data Aktual (2018–2025)',
            marker=dict(size=6,color='#1a3a6b',opacity=0.5),
        ))
        x_line = list(range(1,12))
        y_line = [round(a1v + b1v*x, 4) for x in x_line]
        fig_r1.add_trace(go.Scatter(
            x=x_line, y=y_line, mode='lines',
            name='Garis Regresi (SPSS)',
            line=dict(color='#e17055',width=2.5)
        ))
        fig_r1.add_trace(go.Scatter(
            x=x_line, y=proj26, mode='markers+lines',
            name='Proyeksi 2026',
            marker=dict(size=9,color='#c8a84b',symbol='star'),
            line=dict(color='#c8a84b',dash='dot')
        ))
        fig_r1.update_layout(
            title=f"Sebaran Data & Garis Regresi Tahap 1 — {sel_s1} ({SEKSI_NAMA[sel_s1]})",
            xaxis=dict(title='Indeks Bulan (X): 1=Feb … 11=Des',gridcolor='#f0f0f0',
                       tickvals=list(range(1,12)),ticktext=BULAN),
            yaxis=dict(title='% Realisasi Non-Kumulatif (Y)',gridcolor='#f0f0f0'),
            legend=dict(orientation='h',y=-0.3),
            margin=dict(t=50,b=100,l=50,r=20),
            paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#fafafa',
            height=420,font=dict(family='Segoe UI')
        )
        st.plotly_chart(fig_r1, use_container_width=True, config={'displayModeBar':False})
        st.caption("Titik biru = data aktual historis (2018–2025). Garis merah = garis regresi yang merepresentasikan tren rata-rata. Bintang kuning = proyeksi 2026 hasil substitusi persamaan.")

        st.markdown(f"**📋 Tabel Proyeksi 2026 per Bulan — {sel_s1}**")
        st.caption("Kolom 'Substitusi' menunjukkan cara persamaan digunakan untuk menghitung proyeksi tiap bulan.")
        tbl_proj26 = [{'Bulan': BULAN[i], 'X (Indeks Bulan)': i+1,
                       'Substitusi ke Persamaan': f"Ŷ = {a1v} + ({b1v})×{i+1}",
                       'Proyeksi 2026 (%)': proj26[i]} for i in range(11)]
        st.dataframe(pd.DataFrame(tbl_proj26), use_container_width=True, hide_index=True)

    # ── TAB 2 ──
    with tab_r2:
        st.markdown("""
        <div class='info-box-green'>
        <b>📌 Regresi Tahap 2</b> — Data aktual 2018–2025 (88 observasi per seksi)
        <b>digabungkan dengan Proyeksi 2026</b> (11 observasi) sehingga total menjadi 99 observasi.
        Dari gabungan ini dihitung persamaan regresi baru secara otomatis (OLS/Kuadrat Terkecil),
        yang kemudian digunakan untuk memproyeksikan realisasi tiap bulan di tahun <b>2027</b>.
        </div>
        """, unsafe_allow_html=True)

        col_sel2, _ = st.columns([1,2])
        with col_sel2:
            sel_s2 = st.selectbox("Pilih Seksi", SEKSI_LIST,
                                   format_func=lambda x: f"{x} — {SEKSI_NAMA[x]}", key='reg_s2')

        rd2 = regresi_data[sel_s2]
        a2v,b2v,r2_2v,mae2v = rd2['a2'],rd2['b2'],rd2['r2_2'],rd2['mae2']
        proj27 = rd2['proj2027']

        col_eq1,col_eq2,col_eq3,col_eq4 = st.columns(4)
        metric_info2 = [
            (col_eq1,"Konstanta (a)","Nilai awal / intersep persamaan Tahap 2",f"{a2v}","#1a3a6b"),
            (col_eq2,"Koefisien (b)","Kemiringan garis; negatif = tren menurun",f"{b2v}","#e17055"),
            (col_eq3,"R² (R-Kuadrat)","Seberapa baik persamaan menjelaskan data (0–1)",f"{r2_2v}","#00b894"),
            (col_eq4,"MAE (%)","Rata-rata kesalahan proyeksi terhadap aktual",f"{mae2v:.4f}","#9b59b6"),
        ]
        for col, label, keterangan, val, color in metric_info2:
            col.markdown(f"""
            <div style='background:white;border-radius:12px;padding:16px 18px;
                        box-shadow:0 2px 12px rgba(0,0,0,0.07);border-top:3px solid {color};text-align:center'>
              <div style='font-size:11px;color:#636e72;margin-bottom:2px'>{label}</div>
              <div style='font-size:20px;font-weight:800;color:{color}'>{val}</div>
              <div style='font-size:10px;color:#b2bec3;margin-top:4px'>{keterangan}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:#1a3a6b;color:white;border-radius:10px;padding:12px 20px;margin:16px 0;text-align:center;font-size:15px'>
        <b>Persamaan Tahap 2:</b> &nbsp; Ŷ = {a2v} + ({b2v}) · X &nbsp;|&nbsp;
        n = {len(rd2['x_gabung2'])} observasi (data 2018–2025 + proyeksi 2026)
        </div>
        """, unsafe_allow_html=True)

        fig_r2 = go.Figure()
        n_aktual = len(rd2['x_gabung2']) - 11
        fig_r2.add_trace(go.Scatter(
            x=rd2['x_gabung2'][:n_aktual], y=rd2['y_gabung2'][:n_aktual], mode='markers',
            name='Data Aktual (2018–2025)',
            marker=dict(size=6,color='#1a3a6b',opacity=0.5)
        ))
        fig_r2.add_trace(go.Scatter(
            x=rd2['x_gabung2'][n_aktual:], y=rd2['y_gabung2'][n_aktual:], mode='markers',
            name='Proyeksi 2026 (dimasukkan sebagai input)',
            marker=dict(size=9,color='#e17055',symbol='diamond')
        ))
        x_line2 = list(range(1,12))
        y_line2 = [round(a2v + b2v*x,4) for x in x_line2]
        fig_r2.add_trace(go.Scatter(
            x=x_line2, y=y_line2, mode='lines',
            name='Garis Regresi Tahap 2 (baru)',
            line=dict(color='#9b59b6',width=2.5)
        ))
        fig_r2.add_trace(go.Scatter(
            x=x_line2, y=proj27, mode='markers+lines',
            name='Proyeksi 2027',
            marker=dict(size=9,color='#c8a84b',symbol='star'),
            line=dict(color='#c8a84b',dash='dot')
        ))
        fig_r2.update_layout(
            title=f"Sebaran Data & Garis Regresi Tahap 2 — {sel_s2} ({SEKSI_NAMA[sel_s2]})",
            xaxis=dict(title='Indeks Bulan (X): 1=Feb … 11=Des',gridcolor='#f0f0f0',
                       tickvals=list(range(1,12)),ticktext=BULAN),
            yaxis=dict(title='% Realisasi Non-Kumulatif (Y)',gridcolor='#f0f0f0'),
            legend=dict(orientation='h',y=-0.3),
            margin=dict(t=50,b=100,l=50,r=20),
            paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#fafafa',
            height=420,font=dict(family='Segoe UI')
        )
        st.plotly_chart(fig_r2, use_container_width=True, config={'displayModeBar':False})
        st.caption("Titik biru = data aktual 2018–2025. Berlian merah = proyeksi 2026 yang ikut dimasukkan ke dataset. Garis ungu = garis regresi Tahap 2 yang baru. Bintang kuning = proyeksi 2027.")

        st.markdown(f"**📋 Tabel Proyeksi 2027 per Bulan — {sel_s2}**")
        tbl_proj27 = [{'Bulan': BULAN[i], 'X (Indeks Bulan)': i+1,
                       'Substitusi ke Persamaan': f"Ŷ = {a2v} + ({b2v})×{i+1}",
                       'Proyeksi 2027 (%)': proj27[i]} for i in range(11)]
        st.dataframe(pd.DataFrame(tbl_proj27), use_container_width=True, hide_index=True)

    # ── TAB 3 ──
    with tab_r3:
        st.markdown("### 📋 Ringkasan Semua Seksi — Perbandingan Tahap 1 & Tahap 2")
        st.markdown("""
        <div class='info-box'>
        📌 <b>Tabel ini membandingkan</b> persamaan regresi, nilai akurasi (R² dan MAE),
        serta total proyeksi antara Tahap 1 (untuk 2026) dan Tahap 2 (untuk 2027) untuk
        semua seksi sekaligus. Kolom 'Selisih' menunjukkan apakah proyeksi 2027 lebih tinggi
        atau lebih rendah dari 2026.
        </div>
        """, unsafe_allow_html=True)

        tbl_all = []
        for s in SEKSI_LIST:
            rd = regresi_data[s]
            tbl_all.append({
                'Seksi': s, 'Nama Seksi': SEKSI_NAMA[s],
                'a Tahap1': rd['a1'], 'b Tahap1': rd['b1'],
                'Persamaan Tahap1': f"Ŷ = {rd['a1']} + ({rd['b1']})·X",
                'R² T1': rd['r2_1'], 'MAE T1 (%)': rd['mae1'],
                'a Tahap2': rd['a2'], 'b Tahap2': rd['b2'],
                'Persamaan Tahap2': f"Ŷ = {rd['a2']} + ({rd['b2']})·X",
                'R² T2': rd['r2_2'], 'MAE T2 (%)': rd['mae2'],
                'Total Proj 2026 (%)': round(sum(rd['proj2026']),2),
                'Total Proj 2027 (%)': round(sum(rd['proj2027']),2),
                'Selisih 2027-2026 (%)': round(sum(rd['proj2027'])-sum(rd['proj2026']),2),
                'Risiko (MAE)': REGRESI[s]['risiko'],
            })
        st.dataframe(pd.DataFrame(tbl_all), use_container_width=True, hide_index=True)

        risiko_clr = {'Rendah':'#00b894','Sedang':'#fdcb6e','Tinggi':'#d63031'}
        col_mae1, col_mae2 = st.columns(2)
        for col, tahap, key_mae, warna_judul in [
            (col_mae1,"Tahap 1 (data 2018–2025)",'mae1','#1a3a6b'),
            (col_mae2,"Tahap 2 (data 2018–2026)",'mae2','#9b59b6')
        ]:
            with col:
                st.markdown(f"**MAE per Seksi — {tahap}**")
                mae_vals = [regresi_data[s][key_mae] for s in SEKSI_LIST]
                clrs = [risiko_clr[REGRESI[s]['risiko']] for s in SEKSI_LIST]
                fig_m = go.Figure(go.Bar(
                    x=SEKSI_LIST, y=mae_vals,
                    marker=dict(color=clrs),
                    text=[f"{v:.4f}%" for v in mae_vals],textposition='outside'
                ))
                fig_m.update_layout(
                    margin=dict(t=40,b=40,l=40,r=20),
                    paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#fafafa',
                    yaxis=dict(title='MAE (%)',gridcolor='#f0f0f0'),
                    height=300,font=dict(family='Segoe UI')
                )
                st.plotly_chart(fig_m, use_container_width=True, config={'displayModeBar':False})

        st.markdown("""
        <div class='keterangan-box'>
        <b>📏 Interpretasi MAE & Klasifikasi Risiko:</b><br>
        <span style='color:#00b894'>🟢 <b>Rendah</b> → MAE ≤ 1% — akurasi tinggi, proyeksi sangat mendekati aktual</span>
        &nbsp; (S2, S4, S5, S6)<br>
        <span style='color:#fdcb6e'>🟡 <b>Sedang</b> → 1% &lt; MAE ≤ 3% — akurasi cukup, deviasi dalam batas wajar</span>
        &nbsp; (S1)<br>
        <span style='color:#d63031'>🔴 <b>Tinggi</b> → MAE &gt; 3% — akurasi rendah, pola realisasi tidak konsisten antar tahun</span>
        &nbsp; (S3)<br><br>
        <b>R² (R-Kuadrat)</b>: mendekati 1 = persamaan sangat baik menggambarkan pola data;
        mendekati 0 = data menyebar jauh dari garis regresi.
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 4 ──
    with tab_r4:
        st.markdown("""
        <div class='info-box-yellow'>
        <b>🧮 Kalkulator Data Baru</b> — Masukkan data realisasi aktual tahun baru
        (misalnya setelah data 2026 tersedia), dan sistem akan menghitung ulang persamaan
        regresi secara otomatis serta menghasilkan proyeksi untuk tahun berikutnya.
        Ini berguna untuk memperbarui proyeksi secara berkala seiring data aktual masuk.
        </div>
        """, unsafe_allow_html=True)

        col_inp1, col_inp2 = st.columns([1,2])
        with col_inp1:
            tahun_baru = st.number_input("Tahun Data Baru", min_value=2026, max_value=2035, value=2026, step=1)
            seksi_kalk = st.selectbox("Pilih Seksi", SEKSI_LIST,
                                       format_func=lambda x: f"{x} — {SEKSI_NAMA[x]}", key='kalk_seksi')

        st.markdown(f"**Masukkan % Realisasi Bulanan {seksi_kalk} Tahun {tahun_baru}** (non-kumulatif per bulan)")
        st.caption("Isikan persentase realisasi yang terjadi di setiap bulan secara terpisah (bukan kumulatif). Contoh: Februari = 8.5% berarti 8.5% dari pagu terserap di bulan Februari saja.")
        cols_inp = st.columns(6)
        input_vals = []
        for i, bln in enumerate(BULAN):
            with cols_inp[i % 6]:
                val = st.number_input(bln[:3], min_value=0.0, max_value=30.0, value=0.0,
                                       step=0.01, format="%.2f", key=f"inp_{bln}")
                input_vals.append(val)

        if st.button("🔄 Hitung Ulang Regresi", type="primary"):
            tahun_aktual = list(range(2018, 2026))

            def regresi_manual_kalk(x_vals, y_vals):
                x = np.array(x_vals, dtype=float)
                y = np.array(y_vals, dtype=float)
                n = len(x)
                b = (n*np.sum(x*y) - np.sum(x)*np.sum(y)) / (n*np.sum(x**2) - np.sum(x)**2)
                a = (np.sum(y) - b*np.sum(x)) / n
                y_pred = a + b*x
                mae = float(np.mean(np.abs(y - y_pred)))
                ss_res = np.sum((y-y_pred)**2)
                ss_tot = np.sum((y-np.mean(y))**2)
                r2 = float(1-ss_res/ss_tot) if ss_tot!=0 else 0.0
                return round(a,4), round(b,4), round(r2,4), round(mae,4)

            x_pool_k, y_pool_k = [], []
            for tahun in tahun_aktual:
                pct_list = get_pct_bulanan(df, seksi_kalk, tahun)
                for bi, pct in enumerate(pct_list):
                    x_pool_k.append(bi+1)
                    y_pool_k.append(pct)
            for bi, pct in enumerate(input_vals):
                x_pool_k.append(bi+1)
                y_pool_k.append(pct)

            a_k, b_k, r2_k, mae_k = regresi_manual_kalk(x_pool_k, y_pool_k)
            proj_next = [max(0.0, round(a_k + b_k*x, 4)) for x in range(1,12)]

            # Klasifikasi risiko berdasarkan MAE baru
            if mae_k <= 1:
                risiko_baru = "🟢 Rendah"
                risiko_clr_baru = "#00b894"
            elif mae_k <= 3:
                risiko_baru = "🟡 Sedang"
                risiko_clr_baru = "#c8a84b"
            else:
                risiko_baru = "🔴 Tinggi"
                risiko_clr_baru = "#d63031"

            st.markdown(f"""
            <div style='background:#1a3a6b;color:white;border-radius:10px;padding:14px 20px;margin:12px 0'>
            <div style='text-align:center'>
            Persamaan Baru: <b>Ŷ = {a_k} + ({b_k})·X</b> &nbsp;|&nbsp;
            R² = {r2_k} &nbsp;|&nbsp; MAE = {mae_k:.4f}% &nbsp;|&nbsp;
            Risiko: <span style='color:{risiko_clr_baru};font-weight:800'>{risiko_baru}</span>
            </div>
            <div style='text-align:center;margin-top:8px'>
            Total Proyeksi <b>{tahun_baru+1}</b> untuk <b>{seksi_kalk}</b>:
            <span style='color:#c8a84b;font-size:22px;font-weight:800'> {round(sum(proj_next),2)}%</span>
            </div>
            </div>
            """, unsafe_allow_html=True)

            fig_kalk = go.Figure(go.Bar(
                x=BULAN, y=proj_next,
                marker=dict(color=SEKSI_COLORS[seksi_kalk]),
                text=[f"{v:.2f}%" for v in proj_next],textposition='outside',
            ))
            fig_kalk.update_layout(
                title=f"Proyeksi {tahun_baru+1} per Bulan — {seksi_kalk} ({SEKSI_NAMA[seksi_kalk]})",
                margin=dict(t=50,b=60,l=50,r=20),
                paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#fafafa',
                xaxis=dict(tickangle=-20,gridcolor='#f0f0f0',title='Bulan'),
                yaxis=dict(title='% Realisasi yang Diproyeksikan',gridcolor='#f0f0f0'),
                height=320,font=dict(family='Segoe UI')
            )
            st.plotly_chart(fig_kalk, use_container_width=True, config={'displayModeBar':False})
            st.caption(f"Grafik di atas menunjukkan perkiraan realisasi per bulan untuk tahun {tahun_baru+1} berdasarkan data yang baru dimasukkan.")

            tbl_kalk = [{'Bulan': BULAN[i], 'X (Indeks Bulan)': i+1,
                         'Substitusi ke Persamaan': f"Ŷ = {a_k} + ({b_k})×{i+1}",
                         f'Proyeksi {tahun_baru+1} (%)': proj_next[i]} for i in range(11)]
            st.dataframe(pd.DataFrame(tbl_kalk), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN 5 — MANAJEMEN USER
# ═══════════════════════════════════════════════════════════════════════════════
elif halaman == "👥 Manajemen User":
    st.markdown("<h4 style='color:#1a3a6b;font-weight:800;margin-bottom:4px'>👥 Manajemen User</h4>", unsafe_allow_html=True)

    st.markdown("""
    <div class='info-box-yellow'>
    ⚠️ <b>Catatan penting:</b> Perubahan (tambah/hapus user) disimpan di file <code>users_data.json</code>
    di server. Karena <b>Streamlit Community Cloud</b> bisa mereset filesystem-nya saat app di-reboot
    atau kode di-push ulang, daftar user yang baru diubah lewat menu ini <b>bisa kembali ke versi lama</b>
    setelah reboot. Supaya perubahan permanen, klik tombol <b>"⬇️ Download backup"</b> di tab
    "Daftar User", lalu replace/commit file <code>users_data.json</code> itu di repo GitHub.
    </div>
    """, unsafe_allow_html=True)

    tab_list, tab_add, tab_del = st.tabs(["📋 Daftar User", "➕ Tambah Pegawai", "🗑️ Hapus Pegawai"])

    # ── TAB: DAFTAR USER ─────────────────────────────────────────────────────
    with tab_list:
        st.markdown("""
        <div class='info-box'>
        📌 Tabel ini menampilkan semua akun yang terdaftar di sistem beserta peran
        (<i>role</i>) dan hak aksesnya. <b>Role</b> menentukan menu apa saja yang bisa
        diakses: Admin Keuangan / Kepala Kantor / Kasubbag TU bisa mengakses semua menu,
        sedangkan Pegawai Seksi hanya bisa mengakses Dashboard dan Monitoring Bulanan
        sesuai seksinya masing-masing.
        </div>
        """, unsafe_allow_html=True)

        rows_u = []
        for uname, info in USERS.items():
            role_disp = ROLE_LABEL.get(info.get('role',''), info.get('role',''))
            if info.get('role') == 'seksi':
                seksi_disp = f"{info.get('seksi','—')} — {SEKSI_NAMA.get(info.get('seksi',''), '')}"
            else:
                seksi_disp = "Seluruh Seksi (S1–S6)"
            rows_u.append({
                'Username': uname,
                'Nama': info.get('nama', '—'),
                'Role / Jabatan': role_disp,
                'Hak Akses': seksi_disp,
            })
        st.dataframe(pd.DataFrame(rows_u), use_container_width=True, hide_index=True)
        st.caption(f"Total akun terdaftar: **{len(USERS)}**")

        users_json_str = json.dumps(USERS, indent=2, ensure_ascii=False)
        st.download_button(
            "⬇️ Download backup users_data.json",
            data=users_json_str,
            file_name="users_data.json",
            mime="application/json",
            use_container_width=False,
        )

    # ── TAB: TAMBAH PEGAWAI ──────────────────────────────────────────────────
    with tab_add:
        st.markdown("""
        <div class='info-box'>
        📌 Gunakan form ini untuk mendaftarkan akun baru. Pilih <b>Role / Jabatan</b>
        yang sesuai — Pegawai Seksi hanya bisa melihat data seksinya sendiri,
        sedangkan role lain mendapat akses ke seluruh fitur sistem.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Tambah Pegawai / Akun Baru**")
        with st.form("form_tambah_user", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                new_nama = st.text_input("Nama Pegawai")
                new_username = st.text_input("Username (untuk login)")
            with c2:
                new_password = st.text_input("Password", type="password")
                new_role_disp = st.selectbox(
                    "Role / Jabatan",
                    ["Pegawai Seksi", "Admin Keuangan", "Kepala Kantor", "Kasubbag Tata Usaha"]
                )
            new_seksi = None
            if new_role_disp == "Pegawai Seksi":
                new_seksi = st.selectbox(
                    "Seksi", SEKSI_LIST, format_func=lambda x: f"{x} — {SEKSI_NAMA[x]}"
                )
            else:
                st.caption("ℹ️ Role ini otomatis mendapat akses ke **seluruh seksi (S1–S6)** dan semua menu sistem.")
            submit_add = st.form_submit_button("➕ Tambahkan User", type="primary", use_container_width=True)

        if submit_add:
            role_map_rev = {
                "Pegawai Seksi": "seksi",
                "Admin Keuangan": "keuangan",
                "Kepala Kantor": "kepala_kantor",
                "Kasubbag Tata Usaha": "kasubbag_tu",
            }
            new_username_clean = new_username.strip()
            if not new_nama or not new_username_clean or not new_password:
                st.error("❌ Nama, username, dan password wajib diisi.")
            elif " " in new_username_clean:
                st.error("❌ Username tidak boleh mengandung spasi.")
            elif new_username_clean in USERS:
                st.error(f"❌ Username '{new_username_clean}' sudah dipakai. Pilih username lain.")
            else:
                new_entry = {
                    "password": new_password,
                    "role": role_map_rev[new_role_disp],
                    "nama": new_nama.strip(),
                }
                if role_map_rev[new_role_disp] == "seksi":
                    new_entry["seksi"] = new_seksi
                USERS[new_username_clean] = new_entry
                save_users(USERS)
                st.success(f"✅ User '{new_username_clean}' ({new_nama}) berhasil ditambahkan sebagai {new_role_disp}.")
                st.rerun()

    # ── TAB: HAPUS PEGAWAI ───────────────────────────────────────────────────
    with tab_del:
        st.markdown("""
        <div class='info-box'>
        📌 Pilih akun yang ingin dihapus dari sistem. Penghapusan bersifat permanen
        (selama file <code>users_data.json</code> sudah di-backup ke GitHub).
        Anda tidak bisa menghapus akun yang sedang Anda gunakan untuk login saat ini.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Hapus Pegawai / Akun**")
        deletable_users = [u for u in USERS.keys() if u != st.session_state.get('username')]

        if not deletable_users:
            st.info("Tidak ada akun lain yang bisa dihapus saat ini.")
        else:
            target_user = st.selectbox(
                "Pilih akun yang akan dihapus",
                deletable_users,
                format_func=lambda x: f"{x} — {USERS[x].get('nama','')} ({ROLE_LABEL.get(USERS[x].get('role',''), USERS[x].get('role',''))})"
            )
            info_del = USERS[target_user]
            st.markdown(f"""
            <div style='background:#f8d7da;border-radius:8px;padding:10px 16px;margin:10px 0;font-size:13px;color:#721c24'>
            ⚠️ Akan menghapus: <b>{info_del.get('nama','—')}</b>
            (username: <code>{target_user}</code>,
            jabatan: {ROLE_LABEL.get(info_del.get('role',''), info_del.get('role',''))})
            </div>
            """, unsafe_allow_html=True)
            confirm_del = st.checkbox(f"Saya yakin ingin menghapus akun '{target_user}'")
            if st.button("🗑️ Hapus User", type="primary", disabled=not confirm_del):
                del USERS[target_user]
                save_users(USERS)
                st.success(f"✅ Akun '{target_user}' berhasil dihapus.")
                st.rerun()

        st.caption("ℹ️ Anda tidak bisa menghapus akun yang sedang digunakan untuk login, untuk mencegah terkunci dari sistem.")
