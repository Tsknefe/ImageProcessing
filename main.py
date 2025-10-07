import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import numpy as np


class GorselEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Görüntü İşleme Editörü")
        self.root.geometry("1500x800")
        self.root.configure(bg="black")

        self.background_frame = tk.Frame(self.root, bg="white")
        self.background_frame.pack(fill=tk.BOTH, expand=True)

        self.image = None
        self.history = []

        self.button_frame = tk.Frame(self.root, bg="#111")
        self.button_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.canvas = tk.Canvas(self.background_frame, bg="red", width=500, height=400)
        self.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.button_frame_left = tk.Frame(self.background_frame, bg="white")
        self.button_frame_left.pack(side="left", padx=10, pady=10)

        # Sağ alt köşe - Aritmetik işlemler
        self.button_frame_bottomright = tk.Frame(self.background_frame, bg="white")
        self.button_frame_bottomright.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.button_frame_right = tk.Frame(self.background_frame, bg="white")
        self.button_frame_right.pack(side="right", padx=10, pady=10)

        self.button_frame0 = tk.Frame(self.background_frame, bg="white", padx=70, pady=10)
        self.button_frame0.pack(side="left")

        self.button_frame1 = tk.Frame(self.background_frame, bg="white")
        self.button_frame1.pack(padx=70, pady=10, side="right")

        self.renk_frame = tk.Frame(self.background_frame, bg="white")
        self.renk_frame.place(relx=1.0, rely=0.0, anchor="ne")  # sağ üst köşe

        self.create_color_buttons(self.renk_frame)

        self.create_buttons(self.button_frame_bottomright, [
            ("Resim Ekle (Topla)", self.resim_ekle),
            ("Resim Çarp", self.resim_carp),
        ])

        self.create_buttons(self.button_frame_left, [
            ("Resim Aç", self.resim_yukle),
            ("Resmi Kaydet", self.resmi_kaydet),
            ("Gri Dönüştür", self.gri_donustur_wrapper),
            ("Binary Dönüşüm", self.binary_donusum),
            ("Parlaklık Artır", self.parlaklik_arttir),
            ("Negatif Dönüşüm", self.negatif_donusum),
            ("Yaklaştır",self.yaklastir),
            ("Uzaklaştır",self.uzaklastir),
            ("Görüntü Döndür", self.goruntu_dondur),
            ("Görüntü Kırp", self.goruntu_kirp),
            ("Histogram Göster", None),
            ("Histogram Germe", self.histogram_germe),
            ("Histogram Genişletme", self.histogram_genisletme),
        ])


        self.create_buttons(self.button_frame_right, [
            ("Mean Filtre", self.ortalama_filtre_uygula),
            ("Median Filtre", self.medyan_filtre_uygula),
            ("Gaussian Filtre (Motion)", self.gauss_filtresi_wrapper),
            ("Salt & Pepper Gürültü", self.gurultu_ekle_salt_pepper),
            ("Sobel Kenar Algılama", self.sobel_kenar_bul),
            ("Adaptif Eşikleme", self.adaptif_esikleme),
            ("Aşınma (Erosion)", self.asinma),
            ("Genişletme (Dilation)", self.genisleme),
            ("Açma (Opening)", self.acma),
            ("Kapama (Closing)", self.kapama),
        ])



    def create_buttons(self, frame, button_list):
        for text, command in button_list:
            if command:
                btn = tk.Button(frame, text=text, command=command, bg="#2a3c42", fg="red", font="Arial 10")
                btn.pack(fill="x", pady=4, padx=4)

        self.crop_start = None
        self.crop_rect = None

        self.zoom_factor = 1.0

        self.history = []

        self.image = None

        self.original_image = None

        self.original_photo = None
        self.processed_photo = None

    def displayImage(self):
        if self.image:
            try:
                img = self.image.convert("RGB")
                img_tk = ImageTk.PhotoImage(img)
                self.canvas.config(width=img.width, height=img.height)
                self.canvas.create_image(0, 0, anchor="nw", image=img_tk)
                self.canvas.image = img_tk
            except Exception as e:
                messagebox.showerror("Görüntüleme Hatası", str(e))

    def resim_yukle(self):
        dosya = filedialog.askopenfilename(title="Bir resim seçin",
                                           filetypes=[("Resim Dosyaları", "*.png;*.jpg;*.jpeg;*.bmp")])
        if dosya:
            try:
                yuklenen_resim = Image.open(dosya)
                yuklenen_resim.load()
                self.image = yuklenen_resim
                self.original_image = yuklenen_resim.copy()
                self.history = [self.original_image.copy()]
                self.displayImage()
            except Exception as e:
                messagebox.showerror("Hata", f"Resim yüklenemedi: {e}")

    def resmi_kaydet(self):
        if self.image is None:
            messagebox.showwarning("Uyarı", "Kaydedilecek bir resim yok!")
            return

        dosya_yolu = filedialog.asksaveasfilename(defaultextension=".png",
                                                  filetypes=[("PNG Dosyası", "*.png"), ("JPEG Dosyası", "*.jpg"),
                                                             ("BMP Dosyası", "*.bmp")])
        if dosya_yolu:
            try:
                self.image.save(dosya_yolu)
                messagebox.showinfo("Başarılı", "Resim başarıyla kaydedildi.")
            except Exception as e:
                messagebox.showerror("Hata", f"Resim kaydedilemedi: {e}")

    def create_color_buttons(self, frame):
        buttons = [
            ("Negatif", self.negatif_donusum),
            ("Kırmızı", self.sadece_kirmizi),
            ("Yeşil", self.sadece_yesil),
            ("Mavi", self.sadece_mavi),
            ("HSV", self.hsv_donusum_kanallari),
        ]

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(frame, text=text, command=command, bg="#2a3c42", fg="red", font="Arial 10", width=12)
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=5)

    def gri_olustur(self, resim):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        genislik, yukseklik = resim.size
        gri_resim = Image.new("L", (genislik, yukseklik))

        for y in range(yukseklik):
            for x in range(genislik):
                r, g, b = resim.getpixel((x, y))
                gri_deger = int(0.2989 * r + 0.5870 * g + 0.1140 * b)
                gri_resim.putpixel((x, y), gri_deger)

        return gri_resim

    def gri_donustur_wrapper(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        gri = self.gri_olustur(self.original_image)
        self.image = gri.convert("RGB")
        self.displayImage()
        self.history.append(self.image.copy())

    def binary_donusum(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Lütfen önce bir resim açın.")
            return

        esik = simpledialog.askinteger("Eşik Değeri", "0-255 arasında bir eşik değeri girin:", minvalue=0, maxvalue=255)
        if esik is None:
            return

        gri = self.gri_olustur(self.image)
        gri_np = np.array(gri)

        # Binary dönüşüm uygulama
        ikili_np = np.where(gri_np >= esik, 255, 0).astype(np.uint8)

        sonuc = Image.fromarray(ikili_np).convert("RGB")
        self.image = sonuc
        self.displayImage()
        self.history.append(self.image.copy())

    def goruntu_dondur(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Lütfen önce bir resim açın.")
            return

        # Resmi numpy dizisine çevir
        img_np = np.array(self.image)
        yukseklik, genislik = img_np.shape[0], img_np.shape[1]

        # Yeni boyutlar (90 derece döndüğü için yer değiştirir)
        dondurulmus = np.zeros((genislik, yukseklik, 3), dtype=np.uint8)

        # Piksel yerlerini değiştir
        for y in range(yukseklik):
            for x in range(genislik):
                dondurulmus[x, yukseklik - 1 - y] = img_np[y, x]

        sonuc = Image.fromarray(dondurulmus)
        self.image = sonuc
        self.displayImage()
        self.history.append(self.image.copy())

    def goruntu_kirp(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Lütfen önce bir resim yükleyin.")
            return

        x1 = simpledialog.askinteger("X Başlangıç", "Kırpılacak alanın X başlangıç değeri:", minvalue=0)
        y1 = simpledialog.askinteger("Y Başlangıç", "Kırpılacak alanın Y başlangıç değeri:", minvalue=0)
        x2 = simpledialog.askinteger("X Bitiş", "Kırpılacak alanın X bitiş değeri:", minvalue=0)
        y2 = simpledialog.askinteger("Y Bitiş", "Kırpılacak alanın Y bitiş değeri:", minvalue=0)

        if None in (x1, y1, x2, y2) or x2 <= x1 or y2 <= y1:
            messagebox.showerror("Hata", "Geçersiz koordinatlar.")
            return

        genislik, yukseklik = self.image.size

        x1 = max(0, min(x1, genislik - 1))
        x2 = max(0, min(x2, genislik))
        y1 = max(0, min(y1, yukseklik - 1))
        y2 = max(0, min(y2, yukseklik))

        yeni_genislik = x2 - x1
        yeni_yukseklik = y2 - y1
        yeni_resim = Image.new("RGB", (yeni_genislik, yeni_yukseklik))

        for y in range(yeni_yukseklik):
            for x in range(yeni_genislik):
                piksel = self.image.getpixel((x + x1, y + y1))
                yeni_resim.putpixel((x, y), piksel)

        self.image = yeni_resim
        self.displayImage()
        self.history.append(self.image.copy())

    def blurring_filtresi(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return

        img_np = np.array(self.image)
        yukseklik, genislik = img_np.shape[0], img_np.shape[1]
        sonuc = np.zeros_like(img_np)

        genisletilmis = np.pad(img_np, ((1, 1), (1, 1), (0, 0)), mode='edge')

        for y in range(yukseklik):
            for x in range(genislik):
                komsular = genisletilmis[y:y + 3, x:x + 3]  # 3x3 pencere
                ortalama = np.mean(komsular, axis=(0, 1))  # Her kanal için ortalama (R, G, B)
                sonuc[y, x] = ortalama

        sonuc = np.clip(sonuc, 0, 255).astype(np.uint8)
        self.image = Image.fromarray(sonuc)
        self.displayImage()
        self.history.append(self.image.copy())

    def asinma(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Önce bir resim açın.")
            return

        gri = self.gri_olustur(self.image)
        ikili = np.where(np.array(gri) > 127, 255, 0).astype(np.uint8)

        yuk, gen = ikili.shape
        sonuc = np.zeros_like(ikili)

        for y in range(1, yuk - 1):
            for x in range(1, gen - 1):
                pencere = ikili[y - 1:y + 2, x - 1:x + 2]
                sonuc[y, x] = 255 if np.all(pencere == 255) else 0

        self.image = Image.fromarray(sonuc).convert("RGB")
        self.displayImage()
        self.history.append(self.image.copy())

    def genisleme(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Önce bir resim açın.")
            return

        gri = self.gri_olustur(self.image)
        ikili = np.where(np.array(gri) > 127, 255, 0).astype(np.uint8)

        yuk, gen = ikili.shape
        sonuc = np.zeros_like(ikili)

        for y in range(1, yuk - 1):
            for x in range(1, gen - 1):
                pencere = ikili[y - 1:y + 2, x - 1:x + 2]
                sonuc[y, x] = 255 if np.any(pencere == 255) else 0

        self.image = Image.fromarray(sonuc).convert("RGB")
        self.displayImage()
        self.history.append(self.image.copy())

    def acma(self):

        self.asinma()
        self.genisleme()

    def kapama(self):
        self.genisleme()
        self.asinma()

    def boyutlandir(self, resim, yeni_genislik, yeni_yukseklik):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        orijinal_genislik, orijinal_yukseklik = resim.size
        yeni_resim = Image.new("RGB", (yeni_genislik, yeni_yukseklik))

        for y in range(yeni_yukseklik):
            for x in range(yeni_genislik):
                eski_x = int(x * orijinal_genislik / yeni_genislik)
                eski_y = int(y * orijinal_yukseklik / yeni_yukseklik)
                piksel = resim.getpixel((eski_x, eski_y))
                yeni_resim.putpixel((x, y), piksel)

        return yeni_resim

    def resim_ekle(self):
        dosya1 = filedialog.askopenfilename(title="Birinci resmi seç")
        if not dosya1:
            return
        dosya2 = filedialog.askopenfilename(title="İkinci resmi seç")
        if not dosya2:
            return

        img1 = Image.open(dosya1).resize((400, 400))
        img2 = Image.open(dosya2).resize((400, 400))

        np1 = np.array(img1, dtype=np.uint16)
        np2 = np.array(img2, dtype=np.uint16)
        toplam = np.clip(np1 + np2, 0, 255).astype(np.uint8)

        self.image = Image.fromarray(toplam)
        self.displayImage()

    def resim_carp(self):
        dosya1 = filedialog.askopenfilename(title="Birinci resmi seç")
        if not dosya1:
            return
        dosya2 = filedialog.askopenfilename(title="İkinci resmi seç")
        if not dosya2:
            return

        img1 = Image.open(dosya1).resize((400, 400))
        img2 = Image.open(dosya2).resize((400, 400))

        np1 = np.array(img1, dtype=np.float32)
        np2 = np.array(img2, dtype=np.float32)
        carpim = np.clip((np1 * np2) , 0, 255).astype(np.uint8)

        self.image = Image.fromarray(carpim)
        self.displayImage()

    def gauss_filtresi(self, boyut, sigma):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        cekirdek = np.zeros((boyut, boyut))
        merkez = boyut // 2
        toplam = 0.0

        for x in range(boyut):
            for y in range(boyut):
                dx = x - merkez
                dy = y - merkez
                deger = (1 / (2 * np.pi * sigma ** 2)) * np.exp(-(dx ** 2 + dy ** 2) / (2 * sigma ** 2))
                cekirdek[x, y] = deger
                toplam += deger

        cekirdek /= toplam

        # Griye çevir
        gri = self.gri_olustur(self.image)
        gri_np = np.array(gri)

        # Konvolüsyon işlemi
        pad = boyut // 2
        genisletilmis = np.pad(gri_np, ((pad, pad), (pad, pad)), mode='edge')
        yuk, gen = gri_np.shape
        sonuc = np.zeros_like(gri_np)

        for y in range(yuk):
            for x in range(gen):
                bolge = genisletilmis[y:y + boyut, x:x + boyut]
                sonuc[y, x] = np.sum(bolge * cekirdek)

        sonuc = np.clip(sonuc, 0, 255).astype(np.uint8)
        sonuc_resim = Image.fromarray(sonuc).convert("RGB")

        self.image = sonuc_resim
        self.displayImage()
        self.history.append(self.image.copy())

    def gauss_filtresi_wrapper(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return

        boyut = simpledialog.askinteger("Çekirdek Boyutu", "Filtre boyutunu girin (tek sayı, örneğin 3):", minvalue=1)
        sigma = simpledialog.askfloat("Sigma Değeri", "Sigma değerini girin (örnek: 1.0):", minvalue=0.1)

        if boyut is None or sigma is None:
            return

        cekirdek = self.gauss_filtresi(boyut, sigma)


    def parlaklik_arttir(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Önce bir resim açmalısınız.")
            return

        artis_miktari = simpledialog.askinteger("Parlaklık Artışı", "0 ile 100 arasında bir artış miktarı girin:",
                                                minvalue=0, maxvalue=100)
        if artis_miktari is None:
            return

        img_array = np.array(self.image, dtype=np.int16)  # Taşma olmaması için int16

        parlak_resim = img_array + artis_miktari
        parlak_resim = np.clip(parlak_resim, 0, 255).astype(np.uint8)

        sonuc = Image.fromarray(parlak_resim)
        self.image = sonuc
        self.displayImage()
        self.history.append(self.image.copy())

    def goruntu_yaklastir_uzaklastir(self, oran):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return

        orijinal_genislik, orijinal_yukseklik = self.image.size
        yeni_genislik = int(orijinal_genislik * oran)
        yeni_yukseklik = int(orijinal_yukseklik * oran)

        yeni_resim = Image.new("RGB", (yeni_genislik, yeni_yukseklik))
        for y in range(yeni_yukseklik):
            for x in range(yeni_genislik):
                eski_x = int(x / oran)
                eski_y = int(y / oran)
                if eski_x < orijinal_genislik and eski_y < orijinal_yukseklik:
                    piksel = self.image.getpixel((eski_x, eski_y))
                    yeni_resim.putpixel((x, y), piksel)

        self.image = yeni_resim
        self.displayImage()
        self.history.append(self.image.copy())

    def yaklastir(self):
        self.goruntu_yaklastir_uzaklastir(1.5)

    def uzaklastir(self):
        self.goruntu_yaklastir_uzaklastir(0.75)

    def negatif_donusum(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Lütfen önce bir resim yükleyin.")
            return

        genislik, yukseklik = self.image.size
        yeni_resim = Image.new("RGB", (genislik, yukseklik))

        for y in range(yukseklik):
            for x in range(genislik):
                r, g, b = self.image.getpixel((x, y))
                yeni_resim.putpixel((x, y), (255 - r, 255 - g, 255 - b))

        self.image = yeni_resim
        self.displayImage()
        self.history.append(self.image.copy())

    def sadece_kirmizi(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Önce bir resim açın.")
            return

        genislik, yukseklik = self.image.size
        yeni_resim = Image.new("RGB", (genislik, yukseklik))

        for y in range(yukseklik):
            for x in range(genislik):
                r, g, b = self.image.getpixel((x, y))
                yeni_resim.putpixel((x, y), (r, 0, 0))

        self.image = yeni_resim
        self.displayImage()
        self.history.append(self.image.copy())

    def sadece_yesil(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Önce bir resim açın.")
            return

        genislik, yukseklik = self.image.size
        yeni_resim = Image.new("RGB", (genislik, yukseklik))

        for y in range(yukseklik):
            for x in range(genislik):
                r, g, b = self.image.getpixel((x, y))
                yeni_resim.putpixel((x, y), (0, g, 0))

        self.image = yeni_resim
        self.displayImage()
        self.history.append(self.image.copy())

    def sadece_mavi(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Önce bir resim açın.")
            return

        genislik, yukseklik = self.image.size
        yeni_resim = Image.new("RGB", (genislik, yukseklik))

        for y in range(yukseklik):
            for x in range(genislik):
                r, g, b = self.image.getpixel((x, y))
                yeni_resim.putpixel((x, y), (0, 0, b))

        self.image = yeni_resim
        self.displayImage()
        self.history.append(self.image.copy())

    def hsv_donusum_kanallari(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Lütfen önce bir resim yükleyin.")
            return

        genislik, yukseklik = self.image.size

        hue_resim = Image.new("L", (genislik, yukseklik))
        sat_resim = Image.new("L", (genislik, yukseklik))
        val_resim = Image.new("L", (genislik, yukseklik))

        for y in range(yukseklik):
            for x in range(genislik):
                r, g, b = self.image.getpixel((x, y))
                r_, g_, b_ = r / 255.0, g / 255.0, b / 255.0

                cmax = max(r_, g_, b_)
                cmin = min(r_, g_, b_)
                delta = cmax - cmin

                if delta == 0:
                    h = 0
                elif cmax == r_:
                    h = (60 * ((g_ - b_) / delta)) % 360
                elif cmax == g_:
                    h = (60 * ((b_ - r_) / delta)) + 120
                else:
                    h = (60 * ((r_ - g_) / delta)) + 240

                if cmax == 0:
                    s = 0
                else:
                    s = delta / cmax

                v = cmax

                hue_resim.putpixel((x, y), int(h / 360 * 255))  # H 0-360 → 0-255
                sat_resim.putpixel((x, y), int(s * 255))  # S 0-1 → 0-255
                val_resim.putpixel((x, y), int(v * 255))  # V 0-1 → 0-255

        self.hue_image = hue_resim.convert("RGB")
        self.sat_image = sat_resim.convert("RGB")
        self.val_image = val_resim.convert("RGB")

        self.image = self.hue_image
        self.displayImage()
        self.history.append(self.image.copy())

    def histogram_germe(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()


        if not self.image:
            messagebox.showwarning("Uyarı", "Lütfen önce bir görüntü açın.")
            return

        gri = self.gri_olustur(self.image)
        gri_np = np.array(gri)

        min_deger = np.min(gri_np)
        max_deger = np.max(gri_np)

        if max_deger == min_deger:
            messagebox.showinfo("Bilgi", "Histogramda yayılacak aralık bulunamadı.")
            return

        # Histogram germe işlemi: (piksel - min) * (255 / (max - min))
        gerilmis = ((gri_np - min_deger) * (255.0 / (max_deger - min_deger)))
        gerilmis = np.clip(gerilmis, 0, 255).astype(np.uint8)

        sonuc = Image.fromarray(gerilmis).convert("RGB")
        self.image = sonuc
        self.displayImage()
        self.history.append(self.image.copy())

    def histogram_genisletme(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Lütfen önce bir görüntü açın.")
            return

        alt_limit = simpledialog.askinteger("Alt Limit", "Yeni minimum gri değeri girin (örneğin 30):", minvalue=0,
                                            maxvalue=255)
        ust_limit = simpledialog.askinteger("Üst Limit", "Yeni maksimum gri değeri girin (örneğin 220):", minvalue=0,
                                            maxvalue=255)

        if alt_limit is None or ust_limit is None or alt_limit >= ust_limit:
            messagebox.showerror("Hata", "Geçersiz aralık.")
            return

        gri = self.gri_olustur(self.image)
        gri_np = np.array(gri)

        min_giris = np.min(gri_np)
        max_giris = np.max(gri_np)

        if max_giris == min_giris:
            messagebox.showinfo("Bilgi", "Histogramda genişletilecek aralık yok.")
            return

        genisletilmis = (gri_np - min_giris) * ((ust_limit - alt_limit) / (max_giris - min_giris)) + alt_limit
        genisletilmis = np.clip(genisletilmis, 0, 255).astype(np.uint8)

        sonuc = Image.fromarray(genisletilmis).convert("RGB")
        self.image = sonuc
        self.displayImage()
        self.history.append(self.image.copy())

    def adaptif_esikleme(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if self.image:
            gri = self.image.convert("L")
            img_array = np.array(gri)
            blok_boyutu = 11
            offset = 10

            # Her piksel için yerel eşik hesapla
            yeni_goruntu = np.zeros_like(img_array)
            yaricap = blok_boyutu // 2

            for y in range(yaricap, img_array.shape[0] - yaricap):
                for x in range(yaricap, img_array.shape[1] - yaricap):
                    bolge = img_array[y - yaricap:y + yaricap + 1, x - yaricap:x + yaricap + 1]
                    lokal_esik = np.mean(bolge) - offset
                    yeni_goruntu[y, x] = 255 if img_array[y, x] > lokal_esik else 0

            self.image = Image.fromarray(yeni_goruntu).convert("RGB")
            self.displayImage()
            self.history.append(self.image.copy())

    def sobel_kenar_bul(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Önce bir resim açmalısınız.")
            return

        gri = self.gri_olustur(self.image)
        gri_np = np.array(gri).astype(float)
        yukseklik, genislik = gri_np.shape
        sonuc = np.zeros((yukseklik, genislik))

        sobel_x = np.array([[-1, 0, 1],
                            [-2, 0, 2],
                            [-1, 0, 1]])

        sobel_y = np.array([[-1, -2, -1],
                            [0, 0, 0],
                            [1, 2, 1]])

        for y in range(1, yukseklik - 1):
            for x in range(1, genislik - 1):
                bolge = gri_np[y - 1:y + 2, x - 1:x + 2]
                gx = np.sum(sobel_x * bolge)
                gy = np.sum(sobel_y * bolge)
                kenarlik = np.sqrt(gx ** 2 + gy ** 2)
                sonuc[y, x] = kenarlik

        sonuc = np.clip(sonuc, 0, 255).astype(np.uint8)
        kenar_resmi = Image.fromarray(sonuc).convert("RGB")

        self.image = kenar_resmi
        self.displayImage()
        self.history.append(self.image.copy())

    def gurultu_ekle_salt_pepper(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Önce bir resim açmalısınız.")
            return

        oran = simpledialog.askfloat("Gürültü Oranı", "0 ile 1 arasında bir oran girin (örnek: 0.05):", minvalue=0.0,
                                     maxvalue=1.0)
        if oran is None:
            return

        gri = self.gri_olustur(self.image)
        gri_np = np.array(gri)
        toplam = gri_np.size
        gurultu_sayisi = int(toplam * oran)

        for _ in range(gurultu_sayisi):
            i = np.random.randint(0, gri_np.shape[0])
            j = np.random.randint(0, gri_np.shape[1])
            gri_np[i, j] = 0 if np.random.rand() < 0.5 else 255

        gurultulu = Image.fromarray(gri_np.astype(np.uint8)).convert("RGB")
        self.image = gurultulu
        self.displayImage()
        self.history.append(self.image.copy())

    def ortalama_filtre_uygula(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Önce bir gürültülü resim açın.")
            return

        gri = self.gri_olustur(self.image)
        gri_np = np.array(gri)
        yukseklik, genislik = gri_np.shape
        sonuc = np.zeros_like(gri_np)

        genisletilmis = np.pad(gri_np, ((1, 1), (1, 1)), mode='edge')

        for y in range(yukseklik):
            for x in range(genislik):
                bolge = genisletilmis[y:y + 3, x:x + 3]
                ortalama = np.mean(bolge)
                sonuc[y, x] = ortalama

        temiz = Image.fromarray(sonuc.astype(np.uint8)).convert("RGB")
        self.image = temiz
        self.displayImage()
        self.history.append(self.image.copy())

    def medyan_filtre_uygula(self):
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir resim yükleyin.")
            return
        img = self.original_image.copy()

        if not self.image:
            messagebox.showwarning("Uyarı", "Önce bir gürültülü resim açın.")
            return

        gri = self.gri_olustur(self.image)
        gri_np = np.array(gri)
        yukseklik, genislik = gri_np.shape
        sonuc = np.zeros_like(gri_np)

        genisletilmis = np.pad(gri_np, ((1, 1), (1, 1)), mode='edge')

        for y in range(yukseklik):
            for x in range(genislik):
                bolge = genisletilmis[y:y + 3, x:x + 3]
                medyan = np.median(bolge)
                sonuc[y, x] = medyan

        temiz = Image.fromarray(sonuc.astype(np.uint8)).convert("RGB")
        self.image = temiz
        self.displayImage()
        self.history.append(self.image.copy())

if __name__ == "__main__":
    root = tk.Tk()
    app = GorselEditor(root)
    root.mainloop()