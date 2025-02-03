import tkinter as tk
from tkinter import ttk
import pandas as pd
import plotly.graph_objects as go
import webbrowser
import tempfile
import os
from datetime import datetime
from config import LOG_FILE_PATH 


def generate_price_chart(prices, timestamps, product_title, url):
    """
    Generate an interactive price chart using Plotly and save it as an HTML file.
    """
    # Create the chart
    product_url = url
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamps, y=prices, mode='lines+markers', name='Price'))
    fig.update_layout(
        title=f'Price Trend for "{product_title[:50]}..." <a href="{product_url}" target="_blank" style="text-decoration: none;fill: #1819ed;font-size: 14px;text-decoration-skip-ink: none;cursor:pointer;text-decoration-line: underline;">Go to the product page</a>',
        xaxis_title="Time",
        yaxis_title="Price ($)",
        template="plotly_white"
    )

    # Save the chart to a temporary HTML file
    temp_dir = tempfile.gettempdir()
    chart_path = os.path.join(temp_dir, 'price_chart.html')
    fig.write_html(chart_path)

    return chart_path

class CustomNotification:
    def __init__(self, title, product_title, previous_price, price, asin, url, timeout=None):
        self.window = tk.Tk()
        self.window.title("")
        self.window.overrideredirect(True)  # Remove window decorations
        self.asin = asin
        self.price = price
        self.product_title = product_title
        self.url = url
        
        # Get screen width and height
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Set window size and position (bottom right corner)
        window_width = 300
        window_height = 130
        x_position = screen_width - window_width - 20
        y_position = screen_height - window_height - 60
        
        self.window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Make window stay on top
        self.window.attributes("-topmost", True)
        
        # Style
        style = ttk.Style()
        style.configure("Notification.TFrame", background="#f0f0f0")
        style.configure("Title.TLabel", background="#f0f0f0", font=("Helvetica", 10, "bold"))
        style.configure("Message.TLabel", background="#f0f0f0", font=("Helvetica", 9))
        
        # Main frame
        self.frame = ttk.Frame(self.window, style="Notification.TFrame", padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(self.frame, text=title, style="Title.TLabel").pack(anchor="w")
        
        # Message
        ttk.Label(self.frame, text=f'Price dropped for "{product_title[:50]}...": {previous_price} -> {price}', style="Message.TLabel", wraplength=280).pack(pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # View Chart button
        ttk.Button(button_frame, text="View Chart", command=self.view_chart).pack(side=tk.LEFT, padx=5)
        
        # Dismiss button
        ttk.Button(button_frame, text="Dismiss", command=self.dismiss).pack(side=tk.RIGHT, padx=5)
        
        # Auto-dismiss after timeout (if specified)
        if timeout:
            self.window.after(timeout * 1000, self.dismiss)
    
    def view_chart(self):
        # Add your chart viewing logic here
        print("Opening chart...")
        
        df = pd.read_csv(LOG_FILE_PATH)
        # Ensure timestamp is in datetime format
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Sort by timestamp (most recent first)
        df_sorted = df.sort_values(by='timestamp', ascending=True)
        
        # Filter rows with the corresponding ASIN
        filtered_rows = df_sorted[df_sorted['asin'] == self.asin]
        
        # Access price and timestamp for all rows
        prices = filtered_rows['price'].tolist()
        timestamps = filtered_rows['timestamp'].tolist()
        prices.append(self.price)
        timestamps.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        chart_path = generate_price_chart(prices, timestamps, self.product_title, self.url)

        # Open the chart in the default web browser
        webbrowser.open(f"file://{chart_path}")
        
        # Dismiss the notification window
        self.dismiss()
    
    def dismiss(self):
        self.window.destroy()
    
    def show(self):
        self.window.mainloop()

def display_notification(product_title, previous_price, price, asin, url, timeout=None):
    notification = CustomNotification(
        title="Price Drop Alert",
        previous_price=previous_price,
        product_title=product_title,
        price=price,
        timeout=timeout,
        asin=asin,
        url=url,
    )
    notification.show()