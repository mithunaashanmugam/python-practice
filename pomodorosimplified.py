import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Aesthetic color palette
BG = "#F5F7FB"        # very light neutral background
PANEL = "#FFFFFF"     # card background (white)
ACCENT = "#6C5CE7"    # soft violet (primary accent)
ACCENT2 = "#00C2A8"   # teal (secondary accent)
TEXT = "#0F1724"      # deep slate for primary text
MUTED = "#6B7280"     # muted gray for secondary text
PROGRESS_TROUGH = "#E9EEF8"  # light trough for progressbar

DATA_LOG = "pomodoro_sessions.txt"

class SimplePomodoro:
    def __init__(self, root):
        self.root = root
        root.title("Pomodoro — Focus Timer (Simple)")
        root.geometry("420x450")
        root.configure(bg=BG)
        root.resizable(False, False)

        # State
        self.session_type = None
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.running = False
        self.paused = False
        self.next_break_minutes = 5
        self.reset_confirm = False   # for two-press reset

        # Basic ttk styling for a tidy look
        self.style = ttk.Style(root)
        try:
            self.style.theme_use("clam")
        except:
            pass

        # Card and label styles
        self.style.configure("Card.TFrame", background=PANEL)
        self.style.configure("Title.TLabel", background=BG, foreground=TEXT,
                             font=("Segoe UI", 16, "bold"))
        self.style.configure("Sub.TLabel", background=BG, foreground=MUTED,
                             font=("Segoe UI", 9))
        self.style.configure("Small.TLabel", background=PANEL, foreground=MUTED,
                             font=("Segoe UI", 9))

        # Button styles (Accent and Ghost)
        self.style.configure("Accent.TButton",
                             background=ACCENT, foreground="white",
                             font=("Segoe UI", 10, "bold"), padding=6)
        self.style.map("Accent.TButton",
                       foreground=[("active", "white")],
                       background=[("active", "#5836d1")])

        self.style.configure("Ghost.TButton",
                             background=PANEL, foreground=ACCENT2,
                             font=("Segoe UI", 10, "bold"), borderwidth=0, padding=6)

        # Progressbar style: change trough & bar color
        self.style.configure("TProgressbar", troughcolor=PROGRESS_TROUGH, background=ACCENT)

        # --- UI Layout ---
        top = ttk.Frame(root, padding=(16,12), style="Card.TFrame")
        top.pack(fill="x", padx=16, pady=(16,0))

        ttk.Label(top, text="POMODORO — Focus", style="Title.TLabel").pack(anchor="w")
        ttk.Label(top, text="Simple, clear, and focused", style="Sub.TLabel").pack(anchor="w", pady=(4,0))

        card = ttk.Frame(root, style="Card.TFrame", padding=14)
        card.pack(padx=16, pady=12, fill="both")

        # Large time label (replaces canvas)
        self.time_label = ttk.Label(card, text="00:00", font=("Segoe UI", 32, "bold"),
                                    background=PANEL, foreground=TEXT)
        self.time_label.grid(row=0, column=0, columnspan=4, pady=(6,8))

        # small description label used to show errors/status
        self.timer_desc = ttk.Label(card, text="Ready", style="Sub.TLabel")
        self.timer_desc.grid(row=1, column=0, columnspan=4, pady=(2,8))

        # Inputs
        ttk.Label(card, text="Work (min):", background=PANEL,
                  foreground=TEXT, font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w")
        self.work_entry = ttk.Entry(card, width=6)
        self.work_entry.grid(row=2, column=1, sticky="w")
        self.work_entry.insert(0, "25")

        ttk.Label(card, text="Break (min):", background=PANEL,
                  foreground=TEXT, font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", pady=(6,0))
        self.break_entry = ttk.Entry(card, width=6)
        self.break_entry.grid(row=3, column=1, sticky="w", pady=(6,0))

        # Suggested break label
        self.suggest_label = ttk.Label(card, text="Suggested: 5 min", style="Sub.TLabel")
        self.suggest_label.grid(row=2, column=2, rowspan=2, padx=(12,0), sticky="w")
        self.work_entry.bind("<KeyRelease>", lambda e: self.update_suggest())
        self.update_suggest()

        # Progressbar and percent label
        self.progress = ttk.Progressbar(card, orient="horizontal", length=320, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=4, pady=(12,6))
        self.percent_label = ttk.Label(card, text="0%", style="Sub.TLabel")
        self.percent_label.grid(row=5, column=0, columnspan=4)

        # Buttons
        btn_frame = ttk.Frame(card)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=(12,0))

        self.start_btn = ttk.Button(btn_frame, text="▶ Start Work",
                                    style="Accent.TButton", command=self.start_work)
        self.start_btn.grid(row=0, column=0, padx=6)

        self.pause_btn = ttk.Button(btn_frame, text="⏸ Pause",
                                    style="Ghost.TButton", command=self.pause_resume,
                                    state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=6)

        # Reset uses two-press confirm instead of messagebox
        self.reset_btn = ttk.Button(btn_frame, text="⟲ Reset",
                                    style="Ghost.TButton", command=self.reset,
                                    state="disabled")
        self.reset_btn.grid(row=0, column=2, padx=6)

        footer = ttk.Frame(root, padding=(16,8))
        footer.pack(fill="x")
        self.count_label = ttk.Label(footer, text="Sessions today: 0", style="Sub.TLabel")
        self.count_label.pack(anchor="w")

        # Initialize session count from log (if any)
        self.update_session_count_display()

    # Suggest break based on work minutes
    def compute_suggested_break(self, w):
        return 15 if w >= 50 else 10 if w >= 30 else 5

    def update_suggest(self):
        try:
            w = int(self.work_entry.get())
            self.suggest_label.config(text=f"Suggested: {self.compute_suggested_break(w)} min")
        except:
            self.suggest_label.config(text="Suggested: -")

    # Start a work session
    def start_work(self):
        if self.running:
            return

        # validate work minutes
        try:
            w = int(self.work_entry.get())
            if w <= 0:
                raise ValueError
        except:
            # show simple inline error rather than messagebox
            self.timer_desc.config(text="Enter a positive integer for work minutes.")
            return

        # validate break minutes or use suggested if blank
        try:
            b_text = self.break_entry.get().strip()
            b = int(b_text) if b_text else self.compute_suggested_break(w)
            if b <= 0:
                raise ValueError
        except:
            self.timer_desc.config(text="Enter a positive integer for break minutes or leave blank.")
            return

        self.session_type = "Work"
        self.total_seconds = w * 60
        self.remaining_seconds = self.total_seconds
        self.next_break_minutes = b

        self.running = True
        self.paused = False
        self.reset_confirm = False
        self.reset_btn.config(text="⟲ Reset")

        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal", text="⏸ Pause")
        self.reset_btn.config(state="normal")

        self.timer_desc.config(text="Work session started")
        self.tick()

    # Core ticking function (every 1 second)
    def tick(self):
        if not self.running:
            return

        if self.paused:
            self.root.after(1000, self.tick)
            return

        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        self.time_label.config(text=f"{mins:02d}:{secs:02d}")

        percent = (1 - (self.remaining_seconds / self.total_seconds)) * 100 if self.total_seconds > 0 else 0
        self.progress["value"] = percent
        self.percent_label.config(text=f"{int(percent)}%")

        if self.remaining_seconds <= 0:
            if self.session_type == "Work":
                # short delay then start break
                self.timer_desc.config(text="Work complete — starting break...")
                self.root.after(800, self.start_break)
            else:
                self.finish_break()
            return

        self.remaining_seconds -= 1
        self.root.after(1000, self.tick)

    def start_break(self):
        self.session_type = "Break"
        self.total_seconds = self.next_break_minutes * 60
        self.remaining_seconds = self.total_seconds

        self.timer_desc.config(text="Break session started")
        self.progress["value"] = 0
        self.percent_label.config(text="0%")
        self.time_label.config(text=f"{self.next_break_minutes:02d}:00")
        self.tick()

    def finish_break(self):
        self.timer_desc.config(text="Break finished! Good job!")
        self.running = False

        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.reset_btn.config(state="disabled")

        self.progress["value"] = 100
        self.percent_label.config(text="100%")
        self.time_label.config(text="00:00")

        # Log session (simple append, minimal error handling)
        self.log_session()
        self.update_session_count_display()

    def pause_resume(self):
        if not self.running:
            return

        if not self.paused:
            self.paused = True
            self.pause_btn.config(text="▶ Resume")
            self.timer_desc.config(text=f"{self.session_type} paused")
        else:
            self.paused = False
            self.pause_btn.config(text="⏸ Pause")
            self.timer_desc.config(text=f"{self.session_type} resumed")

    # Two-press reset confirmation: first press changes button text, second press within 4s confirms
    def reset(self):
        if not self.reset_confirm:
            # first press: request confirmation via button text and label
            self.reset_confirm = True
            self.reset_btn.config(text="Confirm Reset")
            self.timer_desc.config(text="Press Reset again to confirm")
            # after 4 seconds, cancel the confirmation state
            self.root.after(4000, self._cancel_reset_confirm)
            return

        # confirmed reset (second press)
        self._perform_reset()

    def _cancel_reset_confirm(self):
        # only revert if still waiting for confirmation
        if self.reset_confirm:
            self.reset_confirm = False
            self.reset_btn.config(text="⟲ Reset")
            self.timer_desc.config(text="Ready" if not self.running else f"{self.session_type} running")

    def _perform_reset(self):
        # Stop timers and reset UI
        self.running = False
        self.paused = False
        self.session_type = None
        self.reset_confirm = False

        self.time_label.config(text="00:00")
        self.progress["value"] = 0
        self.percent_label.config(text="0%")
        self.timer_desc.config(text="Ready")

        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="⏸ Pause")
        self.reset_btn.config(state="disabled", text="⟲ Reset")

        self.update_suggest()

    def log_session(self):
        today = datetime.now().date().isoformat()
        try:
            with open(DATA_LOG, "a") as f:
                f.write(f"{today},Completed\n")
        except Exception:
            # minimal error handling: silently ignore write problems
            pass

    def update_session_count_display(self):
        # Count today's completed lines in the log file
        today = datetime.now().date().isoformat()
        count = 0
        try:
            with open(DATA_LOG, "r") as f:
                for line in f:
                    if line.startswith(today):
                        count += 1
        except FileNotFoundError:
            count = 0
        except Exception:
            # on unexpected read error, keep count as 0 (minimal handling)
            count = 0
        self.count_label.config(text=f"Sessions today: {count}")

if __name__ == "__main__":
    root = tk.Tk()
    SimplePomodoro(root)
    root.mainloop()
