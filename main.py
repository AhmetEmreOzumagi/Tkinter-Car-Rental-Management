import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

# Matplotlib kütüphanesini grafik çizimi için kullanacağız.
# Arayüz açılırken hata fırlatmasın diye importu try içine aldık.
# Matplotlib yoksa plt None kalır ve grafik butonuna basınca kullanıcıya uyarı veririz.
try:
    import matplotlib
    matplotlib.use("TkAgg")  # Tkinter ile matplotlib çakışmasın diye TkAgg backend seçiyoruz.
    import matplotlib.pyplot as plt
except Exception:
    plt = None


def verileri_yukle(dosya_adi):
    # Program açılırken daha önce kaydedilen araç listesini JSON dosyasından okuyoruz.
    try:
        with open(dosya_adi, 'r') as f:
            data = json.load(f)

        # Eski kayıtlarda "not" alanı yoksa sonradan eklenmiş özelliği bozmasın diye ekliyoruz.
        for arac in data:
            if "not" not in arac:
                arac["not"] = ""
        return data

    # İlk çalıştırmada dosya yoksa boş liste ile başlarız.
    except FileNotFoundError:
        return []
    # Dosya bozuk/yarım yazılmışsa uygulama çökmesin diye boş liste döndürürüz.
    except json.decoder.JSONDecodeError:
        return []


def verileri_kaydet(liste, dosya_adi):
    # Programdaki güncel araç listesini JSON dosyasına yazarak kalıcı hale getiriyoruz.
    try:
        with open(dosya_adi, 'w') as f:
            json.dump(liste, f, indent=4)
    except Exception as e:
        # Kaydetme sırasında hata olursa arayüzü kilitlememek için sadece konsola yazdırıyoruz.
        print(f"Veri kaydetme hatası: {e}")


def arac_ekle(arac_listesi, plaka, marka, model, ucret):
    # Plaka/marka/model boş olursa kaydın anlamı kalmadığı için eklemeyi iptal ediyoruz.
    if not plaka or not marka or not model:
        return "Hata: Plaka, marka ve model girmek zorunludur."

    # Ücret sayısal olmalı çünkü kiralama ücretini gün sayısı ile çarpıyoruz.
    try:
        ucret_sayisal = int(ucret)
    except ValueError:
        return "Hata: Günlük ücret sayısal bir değer olmalıdır."

    # Aynı plaka tekrar eklenmesin diye kontrol ediyoruz.
    for arac in arac_listesi:
        if arac["plaka"] == plaka:
            return "Hata: Bu plakaya sahip bir araç zaten mevcut."

    # Yeni aracı sistemin kullandığı standart alanlarla bir sözlük olarak oluşturuyoruz.
    yeni_arac = {
        "plaka": plaka,
        "marka": marka,
        "model": model,
        "ucret": ucret_sayisal,
        "durum": "müsait",
        "kiralayan": "",
        "baslangic_tarihi": "",
        "bitis_tarihi": "",
        "not": ""
    }

    arac_listesi.append(yeni_arac)
    return "Başarılı: Araç sisteme eklendi."


def arac_sil(arac_listesi, plaka):
    # Plaka verilmezse hangi araç silinecek belli olmadığı için işlem yapmıyoruz.
    if not plaka:
        return "Geçerli bir plaka girmeniz gereklidir."

    # Plakası eşleşeni bulunca listeden kaldırıyoruz.
    for arac in arac_listesi:
        if arac["plaka"] == plaka:
            arac_listesi.remove(arac)
            return f"Başarılı! {plaka} plakalı araç sistemden kaldırıldı."

    return f"Hata! {plaka} plakalı araç sistemde bulunamadı."


def araci_bakima_al(arac_listesi, plaka):
    # Bakıma alma işlemi için plaka şart.
    if not plaka:
        return "Hata: Plaka seçilmedi."

    # Listeden plakaya göre doğru aracı buluyoruz.
    arac = None
    for a in arac_listesi:
        if a["plaka"] == plaka:
            arac = a
            break

    if arac is None:
        return f"Hata: {plaka} plakalı araç bulunamadı."

    # Araç müsait değilse bakım durumuna geçirmiyoruz.
    if arac["durum"] != "müsait":
        return f"Hata: Araç şu an '{arac['durum']}' durumunda, bakıma alınamaz."

    arac["durum"] = "bakımda"
    return f"Başarılı: {plaka} plakalı araç bakıma alındı."


def kiralama_baslat(arac_listesi, plaka, musteri_adi, baslangic_tarihi_str, bitis_tarihi_str, not_metni=""):
    # Tarihleri aynı formatta almak için tek standart belirliyoruz.
    TARIH_FORMATI = "%d-%m-%Y"

    # Kiralama kaydı eksik kalmasın diye tüm alanların dolu olmasını istiyoruz.
    if not plaka or not musteri_adi or not baslangic_tarihi_str or not bitis_tarihi_str:
        return "Hata: Tüm kiralama alanları doldurulmalıdır."

    # Plakaya göre aracı listeden buluyoruz.
    arac = None
    for a in arac_listesi:
        if a["plaka"] == plaka:
            arac = a
            break

    if arac is None:
        return f"Hata: {plaka} plakalı araç sistemde bulunamadı."

    # Araç müsait değilse aynı aracı iki kişiye birden kiralamayı engelliyoruz.
    if arac["durum"] != "müsait":
        return f"Hata: {plaka} plakalı araç müsait değil. Durum: {arac['durum']}"

    # Girilen tarihleri datetime'a çevirerek kontrol ve hesap yapıyoruz.
    try:
        baslangic_tarihi = datetime.strptime(baslangic_tarihi_str, TARIH_FORMATI)
        bitis_tarihi = datetime.strptime(bitis_tarihi_str, TARIH_FORMATI)
    except ValueError:
        return f"Hata: Tarih formatı geçersiz. Lütfen {TARIH_FORMATI} formatını kullanın."

    # Bitiş tarihi başlangıçtan önce olamaz.
    if bitis_tarihi <= baslangic_tarihi:
        return "Hata: Bitiş tarihi, başlangıç tarihinden sonra olmalıdır."

    # Kiralama süresini gün olarak hesaplayıp toplam ücreti çıkarıyoruz.
    kiralama_suresi = (bitis_tarihi - baslangic_tarihi).days
    toplam_ucret = kiralama_suresi * arac["ucret"]

    # Araç kaydına kiralama bilgilerini yazıyoruz.
    arac["durum"] = "kirada"
    arac["kiralayan"] = musteri_adi
    arac["baslangic_tarihi"] = baslangic_tarihi_str
    arac["bitis_tarihi"] = bitis_tarihi_str
    arac["not"] = not_metni.strip()

    return (f"Başarılı: Kiralama tamamlandı. Süre: {kiralama_suresi} gün. "
            f"Toplam Ücret: {toplam_ucret} TL.")


def arac_iade_et(arac_listesi, plaka):
    # İade işleminde doğru aracı bulmak için plaka zorunlu.
    if not plaka:
        return "Hata: Plaka girmek zorunludur."

    # Plaka ile aracı buluyoruz.
    arac = None
    for a in arac_listesi:
        if a["plaka"] == plaka:
            arac = a
            break

    if arac is None:
        return f"Hata: {plaka} plakalı araç sistemde bulunamadı."

    eski_durum = arac["durum"]
    if eski_durum == "müsait":
        return f"Hata: {plaka} plakalı araç zaten müsait."

    # İade ile birlikte kiralama alanlarını temizleyip aracı tekrar müsait yapıyoruz.
    arac["durum"] = "müsait"
    arac["kiralayan"] = ""
    arac["baslangic_tarihi"] = ""
    arac["bitis_tarihi"] = ""

    # Araç bakımdaysa farklı bir mesaj döndürüyoruz.
    if eski_durum == "bakımda":
        return f"Başarılı: {plaka} plakalı araç bakımdan çıktı."
    else:
        return f"Başarılı: {plaka} plakalı araç iade alındı."


class CarRentalAppGUI:
    def __init__(self, master, arac_listesi):
        # GUI tarafında ana pencere ve araç listesini tek sınıfta yönetiyoruz.
        self.master = master
        self.arac_listesi = arac_listesi
        self.dosya_adi = "araclar.json"

        master.title("Araç Kiralama Sistemi")
        master.geometry("1100x700")

        self.arayuz_olustur()

    def kapanis_islemi(self):
        # Program kapanırken verileri kaydedip çıkıyoruz.
        verileri_kaydet(self.arac_listesi, self.dosya_adi)
        self.master.destroy()

    def arayuz_olustur(self):
        # X'e basıldığında direkt kapanmak yerine kapanış fonksiyonumuz çalışsın istiyoruz.
        self.master.protocol("WM_DELETE_WINDOW", self.kapanis_islemi)

        # Sol tarafta liste, sağ tarafta işlemler olacak şekilde iki panel kuruyoruz.
        list_frame = ttk.Frame(self.master, padding="10")
        list_frame.grid(row=0, column=0, sticky="nsew")

        action_frame = ttk.Frame(self.master, padding="10")
        action_frame.grid(row=0, column=1, sticky="nsew")

        # Sol panel daha geniş dursun diye weight veriyoruz.
        self.master.grid_columnconfigure(0, weight=3)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        self.arac_listesi_alani_kur(list_frame)
        self.form_ve_butonlari_kur(action_frame)
        self.arac_listesini_guncelle()

    def arac_listesi_alani_kur(self, frame):
        # Üstte filtre alanı ile kullanıcıya durum bazlı görüntüleme yaptırıyoruz.
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill='x', pady=5)

        ttk.Label(filter_frame, text="Listeyi Filtrele:").pack(side='left', padx=5)

        self.filter_var = tk.StringVar(value="Tümü")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, state="readonly")
        filter_combo['values'] = ("Tümü", "Müsait", "Kirada", "Bakımda")
        filter_combo.pack(side='left', padx=5)
        filter_combo.bind("<<ComboboxSelected>>", self.arac_listesini_guncelle)

        # Araçları tablo gibi göstermek için Treeview kullanıyoruz.
        columns = ("plaka", "marka", "model", "ucret", "durum")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree.pack(fill="both", expand=True)

        self.tree.heading("plaka", text="Plaka")
        self.tree.heading("marka", text="Marka")
        self.tree.heading("model", text="Model")
        self.tree.heading("ucret", text="Günlük Ücret")
        self.tree.heading("durum", text="Durum")

        for col in columns:
            self.tree.column(col, width=100, anchor=tk.CENTER)

        # Liste uzayınca kaydırma ile rahatça gezilsin diye scrollbar ekliyoruz.
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Kullanıcı satır seçince alttaki detay alanını doldurmak için event bağlıyoruz.
        self.tree.bind("<<TreeviewSelect>>", self.secili_arac_detay_goster)

        # Detay paneli seçili araç olunca görünsün diye ilk başta pack etmiyoruz.
        self.detay_frame = ttk.LabelFrame(frame, text="Seçili Araç Detayı", padding=10)
        self.detay_visible = False

        # Detay değerlerini StringVar ile tutuyoruz ki ekranda anında güncellenebilsin.
        self.detay_plaka_var = tk.StringVar(value="-")
        self.detay_durum_var = tk.StringVar(value="-")
        self.detay_kiraci_var = tk.StringVar(value="-")
        self.detay_tarih_var = tk.StringVar(value="-")
        self.detay_sure_var = tk.StringVar(value="-")

        row1 = ttk.Frame(self.detay_frame)
        row1.pack(fill='x', pady=2)
        ttk.Label(row1, text="Plaka:").pack(side='left')
        ttk.Label(row1, textvariable=self.detay_plaka_var, font=('Arial', 10, 'bold')).pack(side='left', padx=6)
        ttk.Label(row1, text="Durum:").pack(side='left', padx=15)
        ttk.Label(row1, textvariable=self.detay_durum_var, font=('Arial', 10, 'bold')).pack(side='left', padx=6)

        row2 = ttk.Frame(self.detay_frame)
        row2.pack(fill='x', pady=2)
        ttk.Label(row2, text="Kiracı:").pack(side='left')
        ttk.Label(row2, textvariable=self.detay_kiraci_var).pack(side='left', padx=6)
        ttk.Label(row2, text="Süre:").pack(side='left', padx=15)
        ttk.Label(row2, textvariable=self.detay_sure_var).pack(side='left', padx=6)

        row3 = ttk.Frame(self.detay_frame)
        row3.pack(fill='x', pady=2)
        ttk.Label(row3, text="Tarih Aralığı:").pack(side='left')
        ttk.Label(row3, textvariable=self.detay_tarih_var).pack(side='left', padx=6)

        # Not kısmını çok satırlı olduğu için Text widget ile alıyoruz.
        ttk.Label(self.detay_frame, text="Not:").pack(fill='x', pady=(8, 2))
        self.not_text = tk.Text(self.detay_frame, height=4, wrap="word")
        self.not_text.pack(fill='x')

        # Notu güncellemek için seçili aracın kaydına yazıp JSON'a kaydediyoruz.
        ttk.Button(self.detay_frame, text="💾 Notu Kaydet", command=self.secili_arac_notu_kaydet).pack(
            fill='x', pady=8
        )

    def detay_goster(self):
        # Detay paneli görünmüyorsa pack edip ekrana getiriyoruz.
        if not self.detay_visible:
            self.detay_frame.pack(fill='x', pady=8)
            self.detay_visible = True

    def detay_gizle(self):
        # Detay paneli görünüyorsa kaldırıyoruz.
        if self.detay_visible:
            self.detay_frame.pack_forget()
            self.detay_visible = False

    def secili_arac_detay_goster(self, event=None):
        # Treeview'den seçili satırı alıyoruz.
        secili_ogeler = self.tree.selection()
        if not secili_ogeler:
            self.detay_gizle()
            return

        self.detay_goster()

        secili_plaka = self.tree.item(secili_ogeler[0], 'values')[0]

        # Seçilen plakaya göre araç kaydını listeden buluyoruz.
        arac = None
        for a in self.arac_listesi:
            if a["plaka"] == secili_plaka:
                arac = a
                break

        if arac is None:
            self.detay_gizle()
            return

        self.detay_plaka_var.set(arac.get("plaka", "-"))
        self.detay_durum_var.set(arac.get("durum", "-"))

        # Araç kiradaysa kiracı, tarih ve süre bilgisini dolduruyoruz.
        if arac.get("durum") == "kirada":
            self.detay_kiraci_var.set(arac.get("kiralayan", "-") or "-")

            bas_str = arac.get("baslangic_tarihi", "")
            bit_str = arac.get("bitis_tarihi", "")
            self.detay_tarih_var.set(f"{bas_str} - {bit_str}" if bas_str and bit_str else "-")

            try:
                TARIH_FORMATI = "%d-%m-%Y"
                bas = datetime.strptime(bas_str, TARIH_FORMATI)
                bit = datetime.strptime(bit_str, TARIH_FORMATI)
                gun = (bit - bas).days
                self.detay_sure_var.set(f"{gun} gün")
            except:
                self.detay_sure_var.set("-")
        else:
            self.detay_kiraci_var.set("-")
            self.detay_tarih_var.set("-")
            self.detay_sure_var.set("-")

        # Notu araç kaydından çekip Text içine yazıyoruz.
        self.not_text.delete("1.0", tk.END)
        self.not_text.insert(tk.END, arac.get("not", ""))

    def secili_arac_notu_kaydet(self):
        # Not kaydetme için önce araç seçilmiş mi kontrol ediyoruz.
        secili_ogeler = self.tree.selection()
        if not secili_ogeler:
            messagebox.showwarning("Uyarı", "Lütfen listeden bir araç seçin.")
            return

        secili_plaka = self.tree.item(secili_ogeler[0], 'values')[0]
        yeni_not = self.not_text.get("1.0", tk.END).strip()

        # Notu doğru araca yazıp JSON'a kaydediyoruz.
        for a in self.arac_listesi:
            if a["plaka"] == secili_plaka:
                a["not"] = yeni_not
                verileri_kaydet(self.arac_listesi, self.dosya_adi)
                messagebox.showinfo("Başarılı", "Not kaydedildi.")
                return

        messagebox.showerror("Hata", "Seçili araç bulunamadı.")

    def arac_listesini_guncelle(self, event=None):
        # Tabloyu sıfırlayıp filtreye göre yeniden dolduruyoruz.
        for i in self.tree.get_children():
            self.tree.delete(i)

        secilen_filtre = self.filter_var.get().lower()

        for arac in self.arac_listesi:
            if secilen_filtre != "tümü" and arac["durum"] != secilen_filtre:
                continue

            self.tree.insert('', tk.END, values=(
                arac["plaka"],
                arac["marka"],
                arac["model"],
                arac["ucret"],
                arac["durum"]
            ))

        # Liste yenilenince eski seçim boşa düşmesin diye detay panelini kapatıyoruz.
        self.detay_gizle()

    def form_ve_butonlari_kur(self, frame):
        # Sağ tarafta giriş formu ve butonları tek panelde topluyoruz.
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="ARAÇ YÖNETİM PANELİ", font=('Arial', 12, 'bold')).grid(row=0, column=0, pady=10)

        input_frame = ttk.LabelFrame(frame, text="Yeni Araç Ekle", padding=10)
        input_frame.grid(row=1, column=0, sticky="ew", pady=5)

        ttk.Label(input_frame, text="Plaka:").pack(fill='x')
        self.plaka_entry = ttk.Entry(input_frame)
        self.plaka_entry.pack(fill='x', pady=2)

        ttk.Label(input_frame, text="Marka:").pack(fill='x')
        self.marka_entry = ttk.Entry(input_frame)
        self.marka_entry.pack(fill='x', pady=2)

        ttk.Label(input_frame, text="Model:").pack(fill='x')
        self.model_entry = ttk.Entry(input_frame)
        self.model_entry.pack(fill='x', pady=2)

        ttk.Label(input_frame, text="Günlük Ücret:").pack(fill='x')
        self.ucret_entry = ttk.Entry(input_frame)
        self.ucret_entry.pack(fill='x', pady=2)

        ttk.Button(input_frame, text="➕ Araç Ekle", command=self.arac_ekle_islemi).pack(fill='x', pady=10)

        # Seçili araç butonları tabloda seçilmiş plakaya göre işlem yapar.
        op_frame = ttk.LabelFrame(frame, text="Seçili Araç İşlemleri", padding=10)
        op_frame.grid(row=2, column=0, sticky="ew", pady=10)

        ttk.Button(op_frame, text="🚗 SEÇİLİ ARACI KİRALA", command=self.secili_araci_kirala_penceresi).pack(fill='x', pady=5)
        ttk.Button(op_frame, text="↩️ SEÇİLİ ARACI İADE ET", command=self.secili_araci_iade_et).pack(fill='x', pady=5)
        ttk.Separator(op_frame, orient='horizontal').pack(fill='x', pady=5)
        ttk.Button(op_frame, text="🛠️ Aracı Bakıma Al", command=self.bakima_al_islemi).pack(fill='x', pady=5)
        ttk.Button(op_frame, text="🗑️ Seçili Aracı Sil", command=self.arac_sil_islemi).pack(fill='x', pady=5)

        # Raporlama bölümünde hem yazılı rapor hem grafik seçenekleri var.
        report_frame = ttk.LabelFrame(frame, text="Raporlama ve Analiz", padding=10)
        report_frame.grid(row=3, column=0, sticky="ew", pady=10)

        ttk.Button(report_frame, text="📄 Genel Durum Raporu", command=self.genel_rapor_goster).pack(fill='x', pady=2)
        ttk.Button(report_frame, text="📊 Durum Grafiği (Pasta)", command=self.durum_grafigi_goster).pack(fill='x', pady=2)
        ttk.Button(report_frame, text="📈 Marka Dağılımı (Sütun)", command=self.marka_grafigi_goster).pack(fill='x', pady=2)

        frame.grid_rowconfigure(4, weight=1)

    def arac_ekle_islemi(self):
        # Formdan alınan bilgileri arka plandaki fonksiyona veriyoruz.
        plaka = self.plaka_entry.get()
        marka = self.marka_entry.get()
        model = self.model_entry.get()
        ucret = self.ucret_entry.get()

        result = arac_ekle(self.arac_listesi, plaka, marka, model, ucret)

        if result.startswith("Hata"):
            messagebox.showerror("Hata", result)
        else:
            messagebox.showinfo("Başarılı", result)
            # Ekleme başarılı olunca formu temizleyip tabloyu güncelliyoruz.
            self.plaka_entry.delete(0, tk.END)
            self.marka_entry.delete(0, tk.END)
            self.model_entry.delete(0, tk.END)
            self.ucret_entry.delete(0, tk.END)
            self.arac_listesini_guncelle()
            verileri_kaydet(self.arac_listesi, self.dosya_adi)

    def arac_sil_islemi(self):
        # Silme işlemi sadece seçili satır üzerinden yapılır.
        secili_ogeler = self.tree.selection()
        if not secili_ogeler:
            messagebox.showwarning("Uyarı", "Lütfen silinecek bir araç seçin.")
            return

        secili_plaka = self.tree.item(secili_ogeler[0], 'values')[0]
        onay = messagebox.askyesno("Onay", f"{secili_plaka} plakalı araç silinecek. Emin misiniz?")

        if onay:
            result = arac_sil(self.arac_listesi, secili_plaka)
            if result.startswith("Hata"):
                messagebox.showerror("Hata", result)
            else:
                messagebox.showinfo("Başarılı", result)
                self.arac_listesini_guncelle()
                verileri_kaydet(self.arac_listesi, self.dosya_adi)

    def bakima_al_islemi(self):
        # Bakıma alma da seçili satır üzerinden çalışır.
        secili_ogeler = self.tree.selection()
        if not secili_ogeler:
            messagebox.showwarning("Uyarı", "Lütfen bakıma alınacak aracı seçin.")
            return

        secili_plaka = self.tree.item(secili_ogeler[0], 'values')[0]
        onay = messagebox.askyesno("Onay", f"{secili_plaka} plakalı araç bakıma alınacak. Emin misiniz?")

        if onay:
            result = araci_bakima_al(self.arac_listesi, secili_plaka)
            if result.startswith("Hata"):
                messagebox.showerror("Hata", result)
            else:
                messagebox.showinfo("Başarılı", result)
                self.arac_listesini_guncelle()
                verileri_kaydet(self.arac_listesi, self.dosya_adi)

    def genel_rapor_goster(self):
        # Raporda durum sayılarını ve kiradaki araçların toplam gelirini hesaplıyoruz.
        toplam = len(self.arac_listesi)
        m = k = b = 0
        gelir = 0
        TARIH_FORMATI = "%d-%m-%Y"

        for a in self.arac_listesi:
            if a['durum'] == 'müsait':
                m += 1
            elif a['durum'] == 'kirada':
                k += 1
                # Tarihler doğruysa gün sayısını hesaplayıp toplam gelire ekliyoruz.
                try:
                    bas = datetime.strptime(a["baslangic_tarihi"], TARIH_FORMATI)
                    bit = datetime.strptime(a["bitis_tarihi"], TARIH_FORMATI)
                    gun = (bit - bas).days
                    gelir += gun * a["ucret"]
                except:
                    pass
            elif a['durum'] == 'bakımda':
                b += 1

        msg = (f"GENEL DURUM RAPORU\n\n"
               f"Toplam Araç: {toplam}\n"
               f"Müsait: {m}\n"
               f"Kirada: {k}\n"
               f"Bakımda: {b}\n\n"
               f"Kiradakilerden Beklenen Ciro: {gelir} TL")
        messagebox.showinfo("Rapor", msg)

    def durum_grafigi_goster(self):
        # Matplotlib yoksa kullanıcıya direkt kurulum hatasını gösteriyoruz.
        if plt is None:
            messagebox.showerror("Hata", "Matplotlib kütüphanesi yüklü değil.\nTerminal: pip install matplotlib")
            return

        # Durumları sayıp pasta grafiği için hazırlıyoruz.
        durumlar = {}
        for a in self.arac_listesi:
            d = a['durum']
            durumlar[d] = durumlar.get(d, 0) + 1

        if not durumlar:
            messagebox.showwarning("Uyarı", "Grafik çizecek veri yok.")
            return

        labels = list(durumlar.keys())
        sizes = list(durumlar.values())

        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title('Araç Durum Dağılımı')
        plt.show()

    def marka_grafigi_goster(self):
        # Matplotlib yoksa grafik çizdirmeyip uyarı veriyoruz.
        if plt is None:
            messagebox.showerror("Hata", "Matplotlib kütüphanesi yüklü değil.\nTerminal: pip install matplotlib")
            return

        # Markaları sayıp sütun grafiğine çeviriyoruz.
        markalar = {}
        for a in self.arac_listesi:
            m = a['marka']
            markalar[m] = markalar.get(m, 0) + 1

        if not markalar:
            messagebox.showwarning("Uyarı", "Grafik çizecek veri yok.")
            return

        plt.figure(figsize=(8, 5))
        plt.bar(markalar.keys(), markalar.values())
        plt.xlabel('Markalar')
        plt.ylabel('Araç Sayısı')
        plt.title('Marka Dağılımı')
        plt.show()

    def secili_araci_kirala_penceresi(self):
        # Kiralama için önce listeden araç seçilmiş mi kontrol ediyoruz.
        secili_ogeler = self.tree.selection()
        if not secili_ogeler:
            messagebox.showwarning("Uyarı", "Lütfen kiralamak istediğiniz aracı listeden seçin.")
            return

        secili_plaka = self.tree.item(secili_ogeler[0], 'values')[0]

        # Araç müsait değilse kullanıcıyı uyarıp kiralama penceresini açmıyoruz.
        for arac in self.arac_listesi:
            if arac["plaka"] == secili_plaka and arac["durum"] != "müsait":
                messagebox.showerror("Hata", f"Bu araç şu an '{arac['durum']}' durumunda, kiralanamaz.")
                return

        # Kiralama için ayrı bir pencere açıp bilgileri oradan alıyoruz.
        self.rental_window = tk.Toplevel(self.master)
        self.rental_window.title(f"Kiralama: {secili_plaka}")
        self.rental_window.geometry("400x430")

        frame = ttk.Frame(self.rental_window, padding="15")
        frame.pack(expand=True, fill='both')

        ttk.Label(frame, text="Seçilen Araç Plakası:").pack(fill='x', pady=5)
        self.rental_plaka_entry = ttk.Entry(frame)
        self.rental_plaka_entry.insert(0, secili_plaka)
        self.rental_plaka_entry.config(state='readonly')
        self.rental_plaka_entry.pack(fill='x', pady=5)

        ttk.Label(frame, text="Müşteri Adı:").pack(fill='x', pady=5)
        self.musteri_adi_entry = ttk.Entry(frame)
        self.musteri_adi_entry.pack(fill='x', pady=5)

        ttk.Label(frame, text="Başlangıç (GG-AA-YYYY):").pack(fill='x', pady=5)
        self.baslangic_tarihi_entry = ttk.Entry(frame)
        self.baslangic_tarihi_entry.pack(fill='x', pady=5)

        ttk.Label(frame, text="Bitiş (GG-AA-YYYY):").pack(fill='x', pady=5)
        self.bitis_tarihi_entry = ttk.Entry(frame)
        self.bitis_tarihi_entry.pack(fill='x', pady=5)

        ttk.Label(frame, text="Not:").pack(fill='x', pady=(10, 2))
        self.rental_not_text = tk.Text(frame, height=4, wrap="word")
        self.rental_not_text.pack(fill='x')

        ttk.Button(frame, text="KİRALAMAYI TAMAMLA", command=self.kiralama_baslat_islemi).pack(fill='x', pady=15)

    def kiralama_baslat_islemi(self):
        # Kiralama formundaki değerleri okuyup kiralama fonksiyonuna gönderiyoruz.
        plaka = self.rental_plaka_entry.get()
        musteri = self.musteri_adi_entry.get()
        baslangic = self.baslangic_tarihi_entry.get()
        bitis = self.bitis_tarihi_entry.get()
        not_metni = self.rental_not_text.get("1.0", tk.END).strip()

        result = kiralama_baslat(self.arac_listesi, plaka, musteri, baslangic, bitis, not_metni)

        if result.startswith("Hata"):
            messagebox.showerror("Kiralama Hatası", result)
        else:
            messagebox.showinfo("Başarılı", result)
            # Kiralama bitince listeyi ve dosyayı güncel tutuyoruz.
            self.arac_listesini_guncelle()
            verileri_kaydet(self.arac_listesi, self.dosya_adi)
            self.rental_window.destroy()

    def secili_araci_iade_et(self):
        # İade işlemi için de seçili satır şart.
        secili_ogeler = self.tree.selection()
        if not secili_ogeler:
            messagebox.showwarning("Uyarı", "Lütfen iade edilecek aracı listeden seçin.")
            return

        secili_plaka = self.tree.item(secili_ogeler[0], 'values')[0]
        onay = messagebox.askyesno("İade Onayı", f"{secili_plaka} plakalı araç iade alınacak. Onaylıyor musunuz?")

        if onay:
            result = arac_iade_et(self.arac_listesi, secili_plaka)
            if result.startswith("Hata"):
                messagebox.showerror("İade Hatası", result)
            else:
                messagebox.showinfo("Başarılı", result)
                self.arac_listesini_guncelle()
                verileri_kaydet(self.arac_listesi, self.dosya_adi)


if __name__ == "__main__":
    # Program açılırken dosyadan veriyi çekip arayüzü başlatıyoruz.
    DOSYA_ADI = "araclar.json"
    arac_listesi = verileri_yukle(DOSYA_ADI)
    root = tk.Tk()
    app = CarRentalAppGUI(root, arac_listesi)
    root.mainloop()
