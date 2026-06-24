import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import threading

# Add models directory to path to import predict logic
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "models"))
import predict

class ZameenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zameen.com Property Price Predictor")
        self.root.geometry("600x750")
        self.root.configure(bg="#f0f2f5")

        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="🏠 Islamabad House Price Predictor", 
                 font=("Helvetica", 18, "bold"), fg="white", bg="#2c3e50").pack(pady=20)

        # Main Container
        main_frame = tk.Frame(self.root, bg="#f0f2f5", padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Input fields
        self.inputs = {}
        
        # Location
        tk.Label(main_frame, text="Location:", font=("Helvetica", 10, "bold"), bg="#f0f2f5").grid(row=0, column=0, sticky="w", pady=5)
        self.loc_var = tk.StringVar()
        self.loc_combo = ttk.Combobox(main_frame, textvariable=self.loc_var, values=predict.LOCATIONS, width=40)
        self.loc_combo.grid(row=1, column=0, columnspan=2, pady=5, sticky="we")
        self.loc_combo.set(predict.LOCATIONS[0])

        # Property Type
        tk.Label(main_frame, text="Property Type:", font=("Helvetica", 10, "bold"), bg="#f0f2f5").grid(row=2, column=0, sticky="w", pady=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, values=predict.PROPERTY_TYPES, width=40)
        self.type_combo.grid(row=3, column=0, columnspan=2, pady=5, sticky="we")
        self.type_combo.set(predict.PROPERTY_TYPES[0])

        # Area and Bedrooms
        tk.Label(main_frame, text="Area (sqft):", font=("Helvetica", 10, "bold"), bg="#f0f2f5").grid(row=4, column=0, sticky="w", pady=5)
        self.area_entry = ttk.Entry(main_frame)
        self.area_entry.grid(row=5, column=0, pady=5, sticky="we", padx=(0, 10))
        self.area_entry.insert(0, "2250")

        tk.Label(main_frame, text="Bedrooms:", font=("Helvetica", 10, "bold"), bg="#f0f2f5").grid(row=4, column=1, sticky="w", pady=5)
        self.beds_entry = ttk.Entry(main_frame)
        self.beds_entry.grid(row=5, column=1, pady=5, sticky="we")
        self.beds_entry.insert(0, "3")

        # Bathrooms and Kitchens
        tk.Label(main_frame, text="Bathrooms:", font=("Helvetica", 10, "bold"), bg="#f0f2f5").grid(row=6, column=0, sticky="w", pady=5)
        self.baths_entry = ttk.Entry(main_frame)
        self.baths_entry.grid(row=7, column=0, pady=5, sticky="we", padx=(0, 10))
        self.baths_entry.insert(0, "3")

        tk.Label(main_frame, text="Kitchens:", font=("Helvetica", 10, "bold"), bg="#f0f2f5").grid(row=6, column=1, sticky="w", pady=5)
        self.kitchens_entry = ttk.Entry(main_frame)
        self.kitchens_entry.grid(row=7, column=1, pady=5, sticky="we")
        self.kitchens_entry.insert(0, "1")

        # Built Year and Parking
        tk.Label(main_frame, text="Built Year:", font=("Helvetica", 10, "bold"), bg="#f0f2f5").grid(row=8, column=0, sticky="w", pady=5)
        self.year_entry = ttk.Entry(main_frame)
        self.year_entry.grid(row=9, column=0, pady=5, sticky="we", padx=(0, 10))
        self.year_entry.insert(0, "2015")

        tk.Label(main_frame, text="Parking Spaces:", font=("Helvetica", 10, "bold"), bg="#f0f2f5").grid(row=8, column=1, sticky="w", pady=5)
        self.parking_entry = ttk.Entry(main_frame)
        self.parking_entry.grid(row=9, column=1, pady=5, sticky="we")
        self.parking_entry.insert(0, "2")

        # Extra features checkboxes
        checkbox_frame = tk.Frame(main_frame, bg="#f0f2f5")
        checkbox_frame.grid(row=10, column=0, columnspan=2, pady=15, sticky="w")
        
        self.servant_var = tk.IntVar()
        ttk.Checkbutton(checkbox_frame, text="Servant Quarter", variable=self.servant_var).pack(side="left", padx=5)
        
        self.store_var = tk.IntVar()
        ttk.Checkbutton(checkbox_frame, text="Store Room", variable=self.store_var).pack(side="left", padx=5)

        # Predict Button
        self.predict_btn = tk.Button(main_frame, text="PREDICT PRICE", font=("Helvetica", 12, "bold"), 
                                     bg="#27ae60", fg="white", command=self.handle_predict, height=2)
        self.predict_btn.grid(row=11, column=0, columnspan=2, pady=20, sticky="we")

        # Result Display
        self.result_frame = tk.LabelFrame(main_frame, text="Prediction Result", font=("Helvetica", 10, "bold"), 
                                          bg="white", padx=15, pady=15)
        self.result_frame.grid(row=12, column=0, columnspan=2, pady=10, sticky="we")
        
        self.result_label = tk.Label(self.result_frame, text="Enter details and click Predict", 
                                     font=("Helvetica", 14), bg="white", fg="#7f8c8d")
        self.result_label.pack()

        self.range_label = tk.Label(self.result_frame, text="", font=("Helvetica", 10), bg="white", fg="#95a5a6")
        self.range_label.pack()

        # Footer / Scraper Button
        footer_frame = tk.Frame(self.root, bg="#f0f2f5")
        footer_frame.pack(side="bottom", fill="x", pady=10)
        
        tk.Button(footer_frame, text="Run Scraper (Update Data)", font=("Helvetica", 9), 
                  bg="#34495e", fg="white", command=self.run_scraper_thread).pack()

    def handle_predict(self):
        try:
            inputs = {
                "area_sqft": float(self.area_entry.get()),
                "bedrooms": int(self.beds_entry.get()),
                "bathrooms": int(self.baths_entry.get()),
                "location": self.loc_var.get(),
                "property_type": self.type_var.get(),
                "parking_spaces": int(self.parking_entry.get()),
                "servant_quarters": self.servant_var.get(),
                "store_rooms": self.store_var.get(),
                "kitchens": int(self.kitchens_entry.get()),
                "drawing_rooms": 1, # Default
                "built_in_year": int(self.year_entry.get())
            }

            price, low, high = predict.predict_price(inputs)
            
            self.result_label.config(text=predict.format_pkr(price), fg="#2c3e50", font=("Helvetica", 20, "bold"))
            self.range_label.config(text=f"Estimate Range: {predict.format_pkr(low)} - {predict.format_pkr(high)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def run_scraper_thread(self):
        if messagebox.askyesno("Update Data", "This will start the web scraper. It may take several minutes. Continue?"):
            self.predict_btn.config(state="disabled", text="SCRAPING DATA...")
            thread = threading.Thread(target=self.execute_scraper)
            thread.daemon = True
            thread.start()

    def execute_scraper(self):
        try:
            import scraper.zameen_scraper as zs
            zs.run_scraper(max_pages=2, max_listings=20) # Small run for demo
            self.root.after(0, lambda: messagebox.showinfo("Success", "Scraping complete! Data saved to data/zameen_islamabad_raw.csv"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Scraper Error", str(e)))
        finally:
            self.root.after(0, lambda: self.predict_btn.config(state="normal", text="PREDICT PRICE"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ZameenApp(root)
    root.mainloop()