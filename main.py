import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont


class ModernImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nowoczesny Skalownik Zdjęć")
        self.root.geometry("700x750")

        # Ustawienie motywu (System, Dark, Light)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.tk_image = None
        self.aspect_ratio = 1.0

        # --- Konfiguracja siatki (grid) ---
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # --- Ramki ---
        top_frame = ctk.CTkFrame(root, corner_radius=0)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.image_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.image_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        controls_frame = ctk.CTkFrame(root)
        controls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        controls_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        action_frame = ctk.CTkFrame(root)
        action_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        action_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # --- Elementy interfejsu ---
        self.load_button = ctk.CTkButton(top_frame, text="Wybierz zdjęcie", command=self.load_image, height=40)
        self.load_button.pack(side="left", padx=10, pady=10)

        self.status_label = ctk.CTkLabel(top_frame, text="Wybierz zdjęcie, aby rozpocząć...")
        self.status_label.pack(side="left", padx=10, pady=10)

        ctk.CTkLabel(controls_frame, text="Szerokość:").grid(row=0, column=0, padx=(10, 0), pady=10)
        self.width_entry = ctk.CTkEntry(controls_frame, placeholder_text="np. 1920")
        self.width_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.width_entry.bind("<KeyRelease>", self.on_width_change)

        ctk.CTkLabel(controls_frame, text="Wysokość:").grid(row=0, column=2, padx=(10, 0), pady=10)
        self.height_entry = ctk.CTkEntry(controls_frame, placeholder_text="np. 1080")
        self.height_entry.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        self.height_entry.bind("<KeyRelease>", self.on_height_change)

        self.keep_aspect_ratio_var = ctk.StringVar(value="on")
        self.aspect_ratio_check = ctk.CTkCheckBox(controls_frame, text="Zachowaj proporcje",
                                                  variable=self.keep_aspect_ratio_var, onvalue="on", offvalue="off")
        self.aspect_ratio_check.grid(row=0, column=4, padx=10, pady=10)

        self.image_label = ctk.CTkLabel(self.image_frame, text="", fg_color="gray20")
        self.image_label.pack(expand=True, fill="both", padx=5, pady=5)

        self.resize_button = ctk.CTkButton(action_frame, text="Zmień rozmiar", command=self.resize_image,
                                           state="disabled")
        self.resize_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.watermark_button = ctk.CTkButton(action_frame, text="Dodaj znak wodny", command=self.add_watermark,
                                              state="disabled")
        self.watermark_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.rotate_left_button = ctk.CTkButton(action_frame, text="Obróć ⟲", command=lambda: self.rotate_image(90),
                                                state="disabled")
        self.rotate_left_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.rotate_right_button = ctk.CTkButton(action_frame, text="Obróć ⟳", command=lambda: self.rotate_image(-90),
                                                 state="disabled")
        self.rotate_right_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.save_button = ctk.CTkButton(self.root, text="Zapisz zdjęcie", command=self.save_image, state="disabled",
                                         height=40, font=("", 16, "bold"))
        self.save_button.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="ew")

    def load_image(self):
        self.image_path = filedialog.askopenfilename(
            title="Wybierz plik obrazu",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        if not self.image_path:
            return

        try:
            self.original_image = Image.open(self.image_path)
            self.processed_image = self.original_image.copy()
            self.aspect_ratio = self.original_image.width / self.original_image.height

            self.width_entry.delete(0, "end")
            self.width_entry.insert(0, str(self.original_image.width))
            self.height_entry.delete(0, "end")
            self.height_entry.insert(0, str(self.original_image.height))

            self.display_image(self.processed_image)
            self.update_status(f"Załadowano: ...{self.image_path[-30:]}", text_color="green")
            self.enable_buttons()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można otworzyć zdjęcia: {e}")
            self.disable_buttons()

    def display_image(self, img_to_display):
        frame_width = self.image_label.winfo_width()
        frame_height = self.image_label.winfo_height()

        if frame_width < 2 or frame_height < 2:
            frame_width, frame_height = 600, 500

        img_aspect = img_to_display.width / img_to_display.height
        frame_aspect = frame_width / frame_height

        if img_aspect > frame_aspect:
            new_width = frame_width
            new_height = int(new_width / img_aspect)
        else:
            new_height = frame_height
            new_width = int(new_height * img_aspect)

        preview_image = img_to_display.resize((new_width, new_height), Image.Resampling.LANCZOS)

        self.tk_image = ctk.CTkImage(light_image=preview_image, dark_image=preview_image,
                                     size=(preview_image.width, preview_image.height))
        self.image_label.configure(image=self.tk_image, text="")

    def on_width_change(self, event=None):
        if self.keep_aspect_ratio_var.get() == "on" and self.width_entry.get():
            try:
                new_width = int(self.width_entry.get())
                new_height = int(new_width / self.aspect_ratio)
                self.height_entry.delete(0, "end")
                self.height_entry.insert(0, str(new_height))
            except (ValueError, ZeroDivisionError):
                pass

    def on_height_change(self, event=None):
        if self.keep_aspect_ratio_var.get() == "on" and self.height_entry.get():
            try:
                new_height = int(self.height_entry.get())
                new_width = int(new_height * self.aspect_ratio)
                self.width_entry.delete(0, "end")
                self.width_entry.insert(0, str(new_width))
            except (ValueError, ZeroDivisionError):
                pass

    def resize_image(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())

            if width <= 0 or height <= 0:
                messagebox.showerror("Błąd", "Wymiary muszą być dodatnie.")
                return

            self.processed_image = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
            self.display_image(self.processed_image)
            self.update_status(f"Zmieniono rozmiar na {width}x{height}", text_color="yellow")

        except ValueError:
            messagebox.showerror("Błąd", "Wprowadź prawidłowe wartości liczbowe.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

    # --- ZAKTUALIZOWANA FUNKCJA ZNAKU WODNEGO ---
    def add_watermark(self):
        dialog = ctk.CTkInputDialog(text="Wpisz tekst znaku wodnego:", title="Znak wodny")
        text = dialog.get_input()
        if not text:
            return

        try:
            image_with_watermark = self.processed_image.copy().convert("RGBA")
            draw = ImageDraw.Draw(image_with_watermark)

            # ZWIĘKSZONY ROZMIAR: Dzielnik zmieniony z 20 na 12 dla większej czcionki
            font_size = int(image_with_watermark.width / 12)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font)
            textwidth = bbox[2] - bbox[0]
            textheight = bbox[3] - bbox[1]

            margin = 20  # Lekko zwiększony margines
            x = image_with_watermark.width - textwidth - margin
            y = image_with_watermark.height - textheight - margin

            # LEPSZA WIDOCZNOŚĆ: Zwiększona nieprzezroczystość i dodany czarny kontur
            stroke_width = int(font_size / 20) + 1  # Kontur skaluje się z czcionką

            draw.text(
                (x, y),
                text,
                font=font,
                fill=(255, 255, 255, 220),  # Bardziej widoczny biały
                stroke_width=stroke_width,
                stroke_fill=(0, 0, 0, 220)  # Ciemny, widoczny kontur
            )

            self.processed_image = image_with_watermark
            self.display_image(self.processed_image)
            self.update_status("Dodano znak wodny.", text_color="yellow")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można dodać znaku wodnego: {e}")

    def rotate_image(self, angle):
        self.processed_image = self.processed_image.rotate(angle, expand=True)
        self.display_image(self.processed_image)
        self.update_status(f"Obrócono obraz.", text_color="yellow")

    def save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("Uwaga", "Brak zdjęcia do zapisania.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if not file_path:
            return

        try:
            img_to_save = self.processed_image
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                if img_to_save.mode == 'RGBA':
                    img_to_save = img_to_save.convert('RGB')

            img_to_save.save(file_path)
            messagebox.showinfo("Sukces", f"Zdjęcie zostało zapisane w:\n{file_path}")
            self.update_status("Zapisano pomyślnie.", text_color="green")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać zdjęcia: {e}")

    def enable_buttons(self):
        for btn in [self.resize_button, self.watermark_button, self.rotate_left_button, self.rotate_right_button,
                    self.save_button]:
            btn.configure(state="normal")

    def disable_buttons(self):
        for btn in [self.resize_button, self.watermark_button, self.rotate_left_button, self.rotate_right_button,
                    self.save_button]:
            btn.configure(state="disabled")

    def update_status(self, text, text_color="white"):
        self.status_label.configure(text=text, text_color=text_color)


if __name__ == "__main__":
    root = ctk.CTk()
    app = ModernImageResizerApp(root)
    root.mainloop()

