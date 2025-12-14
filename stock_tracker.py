import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
from datetime import datetime
import pandas as pd

class StockTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Performance Tracker")
        self.root.geometry("900x650")
        
        # Dark mode flag
        self.dark_mode = False
        
        # Color schemes
        self.light_colors = {
            'bg': '#f0f0f0',
            'fg': '#000000',
            'entry_bg': 'white',
            'entry_fg': '#000000',
            'frame_bg': '#f0f0f0',
            'tree_bg': 'white',
            'tree_fg': '#000000'
        }
        
        self.dark_colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'entry_bg': '#3c3c3c',
            'entry_fg': '#ffffff',
            'frame_bg': '#2b2b2b',
            'tree_bg': '#3c3c3c',
            'tree_fg': '#ffffff'
        }
        
        # Top bar with dark mode toggle
        top_bar = tk.Frame(root)
        top_bar.pack(fill=tk.X, padx=10, pady=5)
        
        self.dark_mode_button = tk.Button(top_bar, text="🌙 Dark Mode", 
                                         command=self.toggle_dark_mode,
                                         font=("Arial", 10, "bold"),
                                         padx=10, pady=5)
        self.dark_mode_button.pack(side=tk.RIGHT)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create tabs
        self.ytd_tab = tk.Frame(self.notebook)
        self.portfolio_tab = tk.Frame(self.notebook)
        
        self.notebook.add(self.ytd_tab, text="YTD Performance")
        self.notebook.add(self.portfolio_tab, text="My Portfolio")
        
        # Setup each tab
        self.setup_ytd_tab()
        self.setup_portfolio_tab()
        
        # Portfolio holdings list
        self.portfolio_holdings = []
        
        # Apply initial theme
        self.apply_theme()
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.dark_mode_button.config(text="☀️ Light Mode")
        else:
            self.dark_mode_button.config(text="🌙 Dark Mode")
        self.apply_theme()
    
    def apply_theme(self):
        colors = self.dark_colors if self.dark_mode else self.light_colors
        
        # Configure root
        self.root.config(bg=colors['bg'])
        
        # Configure tabs
        self.ytd_tab.config(bg=colors['bg'])
        self.portfolio_tab.config(bg=colors['bg'])
        
        # Configure treeview style
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure("Treeview",
                       background=colors['tree_bg'],
                       foreground=colors['tree_fg'],
                       rowheight=30,
                       fieldbackground=colors['tree_bg'])
        
        style.configure("Treeview.Heading",
                       background='#4CAF50' if not self.dark_mode else '#1e5128',
                       foreground='white',
                       font=("Arial", 11, "bold"))
        
        style.map('Treeview', background=[('selected', '#4CAF50')])
        
        # Update all widgets recursively
        self.update_widget_colors(self.ytd_tab, colors)
        self.update_widget_colors(self.portfolio_tab, colors)
    
    def update_widget_colors(self, widget, colors):
        """Recursively update colors for all widgets"""
        try:
            widget_type = widget.winfo_class()
            
            if widget_type == 'Frame' or widget_type == 'Labelframe':
                widget.config(bg=colors['bg'])
                if widget_type == 'Labelframe':
                    widget.config(fg=colors['fg'])
            elif widget_type == 'Label':
                if widget.cget('bg') != 'SystemButtonFace':  # Skip button-like labels
                    widget.config(bg=colors['bg'], fg=colors['fg'])
            elif widget_type == 'Entry':
                widget.config(bg=colors['entry_bg'], fg=colors['entry_fg'], 
                            insertbackground=colors['fg'])
            
            # Recursively apply to children
            for child in widget.winfo_children():
                self.update_widget_colors(child, colors)
        except:
            pass
    
    def setup_ytd_tab(self):
        # Title Label
        self.ytd_title_label = tk.Label(self.ytd_tab, text="Stock Year-to-Date Performance", 
                                        font=("Arial", 16, "bold"))
        self.ytd_title_label.pack(pady=10)
        
        # Input Frame
        input_frame = tk.Frame(self.ytd_tab)
        input_frame.pack(pady=10)
        
        self.ytd_input_label = tk.Label(input_frame, text="Enter Stock Tickers (comma-separated):", 
                                        font=("Arial", 11))
        self.ytd_input_label.grid(row=0, column=0, padx=5)
        
        self.ticker_entry = tk.Entry(input_frame, width=40, font=("Arial", 11))
        self.ticker_entry.grid(row=0, column=1, padx=5)
        self.ticker_entry.insert(0, "AAPL, TSLA, MSFT, GOOGL")
        
        # Fetch Button
        fetch_button = tk.Button(input_frame, text="Get YTD Performance", 
                                command=self.fetch_ytd_data, 
                                bg="#4CAF50", fg="white", 
                                font=("Arial", 11, "bold"),
                                padx=10, pady=5)
        fetch_button.grid(row=0, column=2, padx=5)
        
        # Refresh Button
        refresh_button = tk.Button(input_frame, text="🔄 Refresh", 
                                  command=self.fetch_ytd_data, 
                                  bg="#2196F3", fg="white", 
                                  font=("Arial", 11, "bold"),
                                  padx=10, pady=5)
        refresh_button.grid(row=0, column=3, padx=5)
        
        # Results Frame
        results_frame = tk.Frame(self.ytd_tab)
        results_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # Treeview (Table)
        columns = ("Ticker", "Current Price", "YTD Start Price", "YTD Change %", "Status")
        self.ytd_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        
        # Define column headings
        for col in columns:
            self.ytd_tree.heading(col, text=col)
            self.ytd_tree.column(col, anchor=tk.CENTER, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.ytd_tree.yview)
        self.ytd_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ytd_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tags for color coding
        self.ytd_tree.tag_configure('positive', background='#c8e6c9')  # Light green
        self.ytd_tree.tag_configure('negative', background='#ffcdd2')  # Light red
        self.ytd_tree.tag_configure('neutral', background='#fff9c4')   # Light yellow
        
        # Status Label
        self.ytd_status_label = tk.Label(self.ytd_tab, text="Ready", font=("Arial", 10), fg="blue")
        self.ytd_status_label.pack(pady=5)
    
    def setup_portfolio_tab(self):
        # Title
        self.portfolio_title_label = tk.Label(self.portfolio_tab, text="My Portfolio Tracker", 
                                              font=("Arial", 16, "bold"))
        self.portfolio_title_label.pack(pady=10)
        
        # Input Frame
        input_frame = tk.LabelFrame(self.portfolio_tab, text="Add New Holding", 
                                    font=("Arial", 12, "bold"), padx=10, pady=10)
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Ticker input
        self.pf_ticker_label = tk.Label(input_frame, text="Ticker:", font=("Arial", 10))
        self.pf_ticker_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.portfolio_ticker_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.portfolio_ticker_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Shares input
        self.pf_shares_label = tk.Label(input_frame, text="Shares:", font=("Arial", 10))
        self.pf_shares_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.shares_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.shares_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Purchase date input
        self.pf_date_label = tk.Label(input_frame, text="Purchase Date (YYYY-MM-DD):", font=("Arial", 10))
        self.pf_date_label.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.purchase_date_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.purchase_date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.purchase_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Add button
        add_button = tk.Button(input_frame, text="Add to Portfolio", 
                              command=self.add_to_portfolio,
                              bg="#2196F3", fg="white", 
                              font=("Arial", 10, "bold"),
                              padx=10, pady=5)
        add_button.grid(row=0, column=6, padx=10, pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(self.portfolio_tab)
        button_frame.pack(pady=5)
        
        calculate_button = tk.Button(button_frame, text="Calculate Portfolio Performance", 
                                     command=self.calculate_portfolio,
                                     bg="#4CAF50", fg="white", 
                                     font=("Arial", 11, "bold"),
                                     padx=10, pady=5)
        calculate_button.pack(side=tk.LEFT, padx=5)
        
        refresh_button = tk.Button(button_frame, text="🔄 Refresh Portfolio", 
                                  command=self.calculate_portfolio,
                                  bg="#2196F3", fg="white", 
                                  font=("Arial", 11, "bold"),
                                  padx=10, pady=5)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(button_frame, text="Clear Portfolio", 
                                command=self.clear_portfolio,
                                bg="#f44336", fg="white", 
                                font=("Arial", 11, "bold"),
                                padx=10, pady=5)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Portfolio table frame
        portfolio_frame = tk.Frame(self.portfolio_tab)
        portfolio_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
        
        # Portfolio Treeview
        columns = ("Ticker", "Shares", "Purchase Date", "Purchase Price", "Current Price", 
                   "Total Cost", "Current Value", "Gain/Loss $", "Gain/Loss %")
        self.portfolio_tree = ttk.Treeview(portfolio_frame, columns=columns, show="headings", height=12)
        
        # Column widths
        column_widths = {
            "Ticker": 80,
            "Shares": 80,
            "Purchase Date": 120,
            "Purchase Price": 100,
            "Current Price": 100,
            "Total Cost": 100,
            "Current Value": 100,
            "Gain/Loss $": 100,
            "Gain/Loss %": 100
        }
        
        for col in columns:
            self.portfolio_tree.heading(col, text=col)
            self.portfolio_tree.column(col, anchor=tk.CENTER, width=column_widths.get(col, 100))
        
        # Configure tags for color coding
        self.portfolio_tree.tag_configure('gain', background='#c8e6c9')  # Light green
        self.portfolio_tree.tag_configure('loss', background='#ffcdd2')  # Light red
        
        # Scrollbar
        portfolio_scrollbar = ttk.Scrollbar(portfolio_frame, orient=tk.VERTICAL, 
                                           command=self.portfolio_tree.yview)
        self.portfolio_tree.configure(yscroll=portfolio_scrollbar.set)
        portfolio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.portfolio_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Summary frame
        summary_frame = tk.LabelFrame(self.portfolio_tab, text="Portfolio Summary", 
                                     font=("Arial", 12, "bold"), padx=10, pady=10)
        summary_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.total_cost_label = tk.Label(summary_frame, text="Total Investment: $0.00", 
                                         font=("Arial", 11))
        self.total_cost_label.grid(row=0, column=0, padx=20, pady=5)
        
        self.total_value_label = tk.Label(summary_frame, text="Current Value: $0.00", 
                                          font=("Arial", 11))
        self.total_value_label.grid(row=0, column=1, padx=20, pady=5)
        
        self.total_gain_label = tk.Label(summary_frame, text="Total Gain/Loss: $0.00 (0.00%)", 
                                         font=("Arial", 11, "bold"))
        self.total_gain_label.grid(row=0, column=2, padx=20, pady=5)
        
        # Status Label
        self.portfolio_status_label = tk.Label(self.portfolio_tab, text="Ready", 
                                              font=("Arial", 10), fg="blue")
        self.portfolio_status_label.pack(pady=5)
    
    def fetch_ytd_data(self):
        # Clear previous results
        for item in self.ytd_tree.get_children():
            self.ytd_tree.delete(item)
        
        # Get tickers from input
        tickers_input = self.ticker_entry.get().strip()
        if not tickers_input:
            messagebox.showwarning("Input Error", "Please enter at least one ticker symbol!")
            return
        
        tickers = [ticker.strip().upper() for ticker in tickers_input.split(",")]
        
        self.ytd_status_label.config(text="Fetching data...", fg="orange")
        self.root.update()
        
        # Get current year start date
        current_year = datetime.now().year
        ytd_start = f"{current_year}-01-01"
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Fetch data for each ticker
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(start=ytd_start, end=today)
                
                if hist.empty:
                    self.ytd_tree.insert("", tk.END, values=(ticker, "N/A", "N/A", "N/A", "No Data"))
                    continue
                
                ytd_start_price = hist['Close'].iloc[0]
                current_price = hist['Close'].iloc[-1]
                ytd_change = ((current_price - ytd_start_price) / ytd_start_price) * 100
                status = "📈 UP" if ytd_change > 0 else "📉 DOWN" if ytd_change < 0 else "→ FLAT"
                
                # Determine tag for color coding
                if ytd_change > 0:
                    tag = 'positive'
                elif ytd_change < 0:
                    tag = 'negative'
                else:
                    tag = 'neutral'
                
                self.ytd_tree.insert("", tk.END, values=(
                    ticker,
                    f"${current_price:.2f}",
                    f"${ytd_start_price:.2f}",
                    f"{ytd_change:+.2f}%",
                    status
                ), tags=(tag,))
                
            except Exception as e:
                self.ytd_tree.insert("", tk.END, values=(ticker, "Error", "Error", "Error", str(e)[:20]))
        
        self.ytd_status_label.config(text="Data fetched successfully!", fg="green")
    
    def add_to_portfolio(self):
        ticker = self.portfolio_ticker_entry.get().strip().upper()
        shares = self.shares_entry.get().strip()
        purchase_date = self.purchase_date_entry.get().strip()
        
        if not ticker or not shares or not purchase_date:
            messagebox.showwarning("Input Error", "Please fill in all fields!")
            return
        
        try:
            shares = float(shares)
            datetime.strptime(purchase_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid shares or date format! Use YYYY-MM-DD for date.")
            return
        
        # Add to holdings list
        self.portfolio_holdings.append({
            'ticker': ticker,
            'shares': shares,
            'purchase_date': purchase_date
        })
        
        # Clear inputs
        self.portfolio_ticker_entry.delete(0, tk.END)
        self.shares_entry.delete(0, tk.END)
        
        messagebox.showinfo("Success", f"Added {shares} shares of {ticker} to portfolio!")
    
    def calculate_portfolio(self):
        if not self.portfolio_holdings:
            messagebox.showwarning("No Holdings", "Please add at least one stock to your portfolio!")
            return
        
        # Clear previous results
        for item in self.portfolio_tree.get_children():
            self.portfolio_tree.delete(item)
        
        self.portfolio_status_label.config(text="Calculating...", fg="orange")
        self.root.update()
        
        total_cost = 0
        total_value = 0
        
        for holding in self.portfolio_holdings:
            ticker = holding['ticker']
            shares = holding['shares']
            purchase_date = holding['purchase_date']
            
            try:
                stock = yf.Ticker(ticker)
                
                # Get historical data from purchase date to today
                hist = stock.history(start=purchase_date)
                
                if hist.empty:
                    self.portfolio_tree.insert("", tk.END, values=(
                        ticker, shares, purchase_date, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
                    ))
                    continue
                
                # Get purchase price and current price
                purchase_price = hist['Close'].iloc[0]
                current_price = hist['Close'].iloc[-1]
                
                # Calculate costs and gains
                cost = purchase_price * shares
                current_val = current_price * shares
                gain_loss_dollar = current_val - cost
                gain_loss_percent = ((current_price - purchase_price) / purchase_price) * 100
                
                total_cost += cost
                total_value += current_val
                
                # Determine tag for color coding
                tag = 'gain' if gain_loss_dollar >= 0 else 'loss'
                
                # Insert into table
                self.portfolio_tree.insert("", tk.END, values=(
                    ticker,
                    f"{shares:.2f}",
                    purchase_date,
                    f"${purchase_price:.2f}",
                    f"${current_price:.2f}",
                    f"${cost:.2f}",
                    f"${current_val:.2f}",
                    f"${gain_loss_dollar:+.2f}",
                    f"{gain_loss_percent:+.2f}%"
                ), tags=(tag,))
                
            except Exception as e:
                self.portfolio_tree.insert("", tk.END, values=(
                    ticker, shares, purchase_date, "Error", "Error", "Error", "Error", "Error", str(e)[:15]
                ))
        
        # Update summary
        total_gain = total_value - total_cost
        total_gain_percent = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
        
        self.total_cost_label.config(text=f"Total Investment: ${total_cost:,.2f}")
        self.total_value_label.config(text=f"Current Value: ${total_value:,.2f}")
        
        gain_color = "green" if total_gain >= 0 else "red"
        self.total_gain_label.config(
            text=f"Total Gain/Loss: ${total_gain:+,.2f} ({total_gain_percent:+.2f}%)",
            fg=gain_color
        )
        
        self.portfolio_status_label.config(text="Portfolio calculated successfully!", fg="green")
    
    def clear_portfolio(self):
        if messagebox.askyesno("Clear Portfolio", "Are you sure you want to clear all holdings?"):
            self.portfolio_holdings = []
            for item in self.portfolio_tree.get_children():
                self.portfolio_tree.delete(item)
            self.total_cost_label.config(text="Total Investment: $0.00")
            self.total_value_label.config(text="Current Value: $0.00")
            self.total_gain_label.config(text="Total Gain/Loss: $0.00 (0.00%)", fg="black")
            self.portfolio_status_label.config(text="Portfolio cleared", fg="blue")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = StockTrackerApp(root)
    root.mainloop()