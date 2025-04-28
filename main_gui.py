import tkinter as tk
from tkinter import ttk, messagebox
from india_land_system import IndiaLandProcurementSystem  # assuming your main class is saved as this

class LandAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("India Land Procurement System")
        self.root.geometry("800x600")
        
        # Set a custom theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.primary_color = "#1a73e8"  # Blue
        self.secondary_color = "#4CAF50"  # Green
        self.accent_color = "#FF9800"  # Orange
        self.bg_color = "#f5f5f5"  # Light gray
        self.text_color = "#333333"  # Dark gray
        
        self.root.configure(bg=self.bg_color)
        
        # Configure styles
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TButton', font=('Helvetica', 11))
        self.style.configure('Header.TLabel', font=('Helvetica', 22, 'bold'), foreground=self.primary_color)
        self.style.configure('Subheader.TLabel', font=('Helvetica', 14), foreground=self.text_color)
        
        # Configure Combobox style
        self.style.map('TCombobox', 
            fieldbackground=[('readonly', 'white')],
            selectbackground=[('readonly', self.primary_color)],
            selectforeground=[('readonly', 'white')])
        
        self.system = IndiaLandProcurementSystem()
        self.analysis_result = None
        
        self.setup_widgets()

    def setup_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20 20 20 20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with logo (using text as logo placeholder)
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        logo_label = ttk.Label(header_frame, text="🏙️", font=('Helvetica', 36), style='TLabel')
        logo_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = ttk.Label(header_frame, text="India Land Procurement System", style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Separator
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 20))
        
        # Content area
        content_frame = ttk.Frame(main_frame, style='TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for controls
        left_panel = ttk.Frame(content_frame, style='TFrame', padding="0 0 20 0")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # City selection section
        city_section = ttk.LabelFrame(left_panel, text="Location Selection", padding="10 10 10 10")
        city_section.pack(fill=tk.X, pady=(0, 20))
        
        city_label = ttk.Label(city_section, text="Select City:", style='TLabel')
        city_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.city_var = tk.StringVar()
        self.city_dropdown = ttk.Combobox(
            city_section,
            textvariable=self.city_var,
            values=list(self.system.city_coordinates.keys()),
            width=30,
            state="readonly"
        )
        self.city_dropdown.set(self.system.default_city)
        self.city_dropdown.pack(fill=tk.X, pady=(0, 10))
        
        # Action buttons section
        action_section = ttk.LabelFrame(left_panel, text="Actions", padding="10 10 10 10")
        action_section.pack(fill=tk.X)
        
        # Custom button style
        analyze_btn = tk.Button(
            action_section, 
            text="Analyze Prices", 
            command=self.analyze_prices,
            bg=self.secondary_color,
            fg="white",
            font=("Helvetica", 11, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=8,
            cursor="hand2"
        )
        analyze_btn.pack(fill=tk.X, pady=(0, 10))
        
        map_btn = tk.Button(
            action_section, 
            text="Generate Map", 
            command=self.generate_map,
            bg=self.primary_color,
            fg="white",
            font=("Helvetica", 11, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=8,
            cursor="hand2"
        )
        map_btn.pack(fill=tk.X, pady=(0, 10))
        
        explore_btn = tk.Button(
            action_section, 
            text="Explore Location (Click Mode)", 
            command=self.launch_blank_map,
            bg=self.accent_color,
            fg="white",
            font=("Helvetica", 11, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=8,
            cursor="hand2"
        )
        explore_btn.pack(fill=tk.X)
        
        # Right panel for results and visualization
        right_panel = ttk.Frame(content_frame, style='TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Results section
        self.results_frame = ttk.LabelFrame(right_panel, text="Analysis Results", padding="10 10 10 10")
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(self.results_frame, wrap=tk.WORD, height=15, font=("Helvetica", 11))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.config(state=tk.DISABLED)
        
        # Status bar
        status_frame = ttk.Frame(main_frame, style='TFrame')
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        status_label = ttk.Label(status_frame, text="Ready", style='TLabel')
        status_label.pack(side=tk.LEFT)
        
        # Version info
        version_label = ttk.Label(status_frame, text="v1.0.0", style='TLabel')
        version_label.pack(side=tk.RIGHT)

    def analyze_prices(self):
        city = self.city_var.get()
        if not city:
            messagebox.showerror("Error", "Please select a city.")
            return

        result = self.system.analyze_city_prices(city)
        if result:
            self.analysis_result = result
            self.update_results_display(result)
        else:
            messagebox.showwarning("No Data", f"No data found for {city}")
            self.analysis_result = None
            self.clear_results_display()

    def update_results_display(self, result):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Format the results with some styling
        self.results_text.insert(tk.END, f"City: {result['city']}\n\n", "header")
        self.results_text.insert(tk.END, f"Average Price: ", "label")
        self.results_text.insert(tk.END, f"₹{result['average_price']:,.2f}/sqm\n\n", "value")
        
        self.results_text.insert(tk.END, "Zone Averages:\n", "subheader")
        for zone, price in result['zone_prices'].items():
            self.results_text.insert(tk.END, f" • {zone}: ", "zone")
            self.results_text.insert(tk.END, f"₹{price:,.2f}/sqm\n", "price")
        
        # Configure tags for text styling
        self.results_text.tag_configure("header", font=("Helvetica", 14, "bold"), foreground=self.primary_color)
        self.results_text.tag_configure("subheader", font=("Helvetica", 12, "bold"), foreground=self.text_color)
        self.results_text.tag_configure("label", font=("Helvetica", 11, "bold"))
        self.results_text.tag_configure("value", font=("Helvetica", 11))
        self.results_text.tag_configure("zone", font=("Helvetica", 11))
        self.results_text.tag_configure("price", font=("Helvetica", 11, "bold"), foreground=self.secondary_color)
        
        self.results_text.config(state=tk.DISABLED)

    def clear_results_display(self):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "No data available for the selected city.")
        self.results_text.config(state=tk.DISABLED)

    def generate_map(self):
        city = self.city_var.get()
        if not city:
            messagebox.showerror("Error", "Please select a city.")
            return

        if hasattr(self, 'analysis_result') and self.analysis_result:
            self.system.create_map(city, self.analysis_result)
        else:
            self.system.create_map(city)
        messagebox.showinfo("Map Created", "Interactive map has been opened in your browser.")

    def launch_blank_map(self):
        self.system.create_map(self.city_var.get())
        messagebox.showinfo("Explore Mode", "Click on the map to explore new land data!")

if __name__ == "__main__":
    root = tk.Tk()
    app = LandAppGUI(root)
    root.mainloop()
