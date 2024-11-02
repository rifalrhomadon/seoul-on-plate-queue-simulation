import simpy
import random
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk

PREPARATION_TIMES = {
    'Kimchi Bokkeumbap': 5,
    'Tteokbokki': 3
}

COMPLAINT_THRESHOLD = 7

results = []
detailed_results = []

def choose_menu():
    return random.choice(list(PREPARATION_TIMES.keys()))

def customer(env, name, cashier, kitchen, results):
    arrival_time = env.now
    with cashier.request() as request:
        yield request
        waiting_time = env.now - arrival_time
        yield env.timeout(2)
    
    menu = choose_menu()
    preparation_time = PREPARATION_TIMES[menu]
    
    with kitchen.request() as request:
        start_service_time = env.now
        yield request
        yield env.timeout(preparation_time)

    end_service_time = env.now

    total_time = end_service_time - arrival_time
    waiting_time = start_service_time - arrival_time
    service_time = end_service_time - start_service_time

    if waiting_time > COMPLAINT_THRESHOLD:
        status = "protes"
    else:
        status = "senang"
    
    results.append((waiting_time, total_time, service_time, status))

def restaurant_simulation(env, num_cashiers, num_kitchens, arrival_rate):
    cashier = simpy.Resource(env, capacity=num_cashiers)
    kitchen = simpy.Resource(env, capacity=num_kitchens)
    
    customer_count = 0
    while True:
        yield env.timeout(random.expovariate(1 / arrival_rate))
        customer_count += 1
        env.process(customer(env, f"Pelanggan {customer_count}", cashier, kitchen, results))

def run_simulation():
    global results
    global detailed_results
    try:
        simulation_duration = int(entry_duration.get())
        arrival_rate = float(entry_arrival.get())
    except ValueError:
        messagebox.showerror("Input Error", "Pastikan semua input adalah angka valid.")
        return

    results.clear()
    detailed_results.clear()

    random.seed(42)
    env = simpy.Environment()
    
    env.process(restaurant_simulation(env, num_cashiers=1, num_kitchens=1, arrival_rate=arrival_rate))
    env.run(until=simulation_duration)
    
    if results:
        total_customers = len(results)
        average_wait_time = sum(r[0] for r in results) / total_customers
        result_text = f"Simulasi selesai setelah {simulation_duration} menit.\n\n" \
                      f"Jumlah pelanggan yang dilayani: {total_customers}\n" \
                      f"Rata-rata waktu tunggu pelanggan: {average_wait_time:.2f} menit.\n"
        
        detailed_results = results.copy()
    else:
        result_text = "Tidak ada pelanggan yang datang selama simulasi."

    result_label.config(state=tk.NORMAL)
    result_label.delete(1.0, tk.END)
    result_label.insert(tk.END, result_text)
    result_label.config(state=tk.DISABLED)

def show_customer_details():
    if not detailed_results:
        messagebox.showinfo("Detail Pelanggan", "Tidak ada pelanggan yang dilayani.")
        return

    details_window = tk.Toplevel(root)
    details_window.title("Detail Pelanggan")

    title_label = tk.Label(details_window, text="Detail Pelanggan", font=("Helvetica", 14))
    title_label.pack(pady=10)

    details_text = scrolledtext.ScrolledText(details_window, width=100, height=30)  # Lebih lebar dan lebih tinggi
    details_text.pack(pady=10)

    for idx, (wait_time, total_time, service_time, status) in enumerate(detailed_results):
        details_text.insert(tk.END, 
                            f"Pelanggan {idx + 1}: "
                            f"Waktu Tunggu: {wait_time:.2f} menit, "
                            f"Waktu Dilayani: {service_time:.2f} menit, "
                            f"Total Waktu: {total_time:.2f} menit, "
                            f"Status: {status.capitalize()}\n")

    details_text.config(state=tk.DISABLED)

def clear_fields():
    entry_duration.delete(0, tk.END)
    entry_arrival.delete(0, tk.END)
    result_label.config(state=tk.NORMAL)
    result_label.delete(1.0, tk.END)
    result_label.config(state=tk.DISABLED)

root = tk.Tk()
root.title("Simulasi Antrian Restoran Korea")
root.geometry("600x500")

root.configure(bg="#f0f0f0")
font_label = ("Helvetica", 12)
font_entry = ("Helvetica", 12)
font_button = ("Helvetica", 12, "bold")
font_result = ("Helvetica", 10)

try:
    img = Image.open(r"D:/FROM E/laptop/Semester 5/Permodelan dan Simulasi/Studi Kasus Korean Food/Seoul on Plate.png")
    img = img.resize((150, 150), Image.Resampling.LANCZOS)
    logo_img = ImageTk.PhotoImage(img)
except Exception as e:
    logo_img = None
    print(f"Error loading image: {e}")

if logo_img:
    logo_label = tk.Label(root, image=logo_img, bg="#f0f0f0")
    logo_label.grid(row=0, column=0, columnspan=2, pady=10)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

label_duration = tk.Label(root, text="Durasi Simulasi (menit):", bg="#f0f0f0", font=font_label)
label_duration.grid(row=1, column=0, padx=20, pady=10, sticky="e")
entry_duration = tk.Entry(root, font=font_entry)
entry_duration.grid(row=1, column=1, padx=20, pady=10)

label_arrival = tk.Label(root, text="Rata-rata Kedatangan (menit):", bg="#f0f0f0", font=font_label)
label_arrival.grid(row=2, column=0, padx=20, pady=10, sticky="e")
entry_arrival = tk.Entry(root, font=font_entry)
entry_arrival.grid(row=2, column=1, padx=20, pady=10)

button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.grid(row=3, column=0, columnspan=2, pady=10)

run_button = tk.Button(button_frame, text="Jalankan Simulasi", command=run_simulation, bg="#4CAF50", fg="white", font=font_button)
run_button.grid(row=0, column=0, padx=10, ipadx=10, ipady=5)

clear_button = tk.Button(button_frame, text="Clear", command=clear_fields, bg="#f44336", fg="white", font=font_button)
clear_button.grid(row=0, column=1, padx=10, ipadx=10, ipady=5)

detail_button = tk.Button(button_frame, text="Detail Pelanggan", command=show_customer_details, bg="#2196F3", fg="white", font=font_button)
detail_button.grid(row=0, column=2, padx=10, ipadx=10, ipady=5)

result_label = tk.Text(root, height=10, width=70, state=tk.DISABLED, font=font_result, bg="#e8e8e8")
result_label.grid(row=4, column=0, columnspan=2, padx=20, pady=10)

root.mainloop()
