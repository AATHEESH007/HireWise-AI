import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import threading
from tts import speak
from stt import listen
from engine import generate_question, generate_feedback
from resume import parse_resume
from score import score_response

class InterviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ AI Mock Interview Bot")
        self.root.geometry("700x600")
        self.root.configure(bg="#1e1e1e")

        self.chat_log = []
        self.resume_data = None

        # Title
        tk.Label(root, text="AI Mock Interview", font=("Helvetica", 20, "bold"), bg="#1e1e1e", fg="#9cdcfe").pack(pady=20)

        # Upload Button
        self.upload_btn = tk.Button(root, text="📄 Upload Resume", command=self.upload_resume, font=("Helvetica", 12),
                                    bg="#007acc", fg="white", padx=10, pady=5)
        self.upload_btn.pack()

        # Proceed Button
        self.proceed_btn = tk.Button(root, text="🚀 Start Interview", command=self.start_interview_thread,
                                     font=("Helvetica", 12), bg="#28a745", fg="white", padx=10, pady=5)
        self.proceed_btn.pack(pady=10)

        # Chat display area
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=25, font=("Helvetica", 11),
                                                   bg="#252526", fg="#d4d4d4", insertbackground="white")
        self.text_area.pack(padx=10, pady=10)
        self.text_area.configure(state='disabled')

    def upload_resume(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                self.resume_data = parse_resume(file_path)
                messagebox.showinfo("Success", "✅ Resume uploaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to parse resume.\n{str(e)}")

    def start_interview_thread(self):
        if not self.resume_data:
            messagebox.showwarning("No Resume", "Please upload a resume before proceeding.")
            return
        thread = threading.Thread(target=self.run_interview)
        thread.start()

    def run_interview(self):
        self.clear_chat()
        self.add_message("AI", "Welcome to your AI mock interview.")
        speak("Welcome to your AI mock interview.")

        first_question = "Tell me about yourself."
        self.ask_question(first_question)

        all_answers = []
        user_input = listen()
        self.add_message("You", user_input)
        all_answers.append(user_input)

        for i in range(4):
            question = generate_question(user_input, self.resume_data)
            self.ask_question(question)

            user_input = listen()
            self.add_message("You", user_input)
            all_answers.append(user_input)

            if (i + 1) % 2 == 0:
                speak("Analyzing your last few answers...")
                feedback = generate_feedback(" ".join(all_answers[-2:]))
                self.add_message("AI", f"🧠 Feedback: {feedback}")
                speak(feedback)

        speak("Thanks for attending the interview. Here is your final feedback.")
        final_feedback = generate_feedback(" ".join(all_answers))
        self.add_message("AI", f"🏁 Final Feedback: {final_feedback}")
        speak(final_feedback)

        avg_score = sum(score_response(ans) for ans in all_answers) / len(all_answers)
        score_text = f"💯 Final Score: {round(avg_score, 2)} / 100"
        self.add_message("AI", score_text)
        speak(score_text)

    def ask_question(self, question):
        self.add_message("AI", question)
        speak(question)

    def add_message(self, sender, message):
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, f"{sender}: {message}\n\n")
        self.text_area.see(tk.END)
        self.text_area.configure(state='disabled')

    def clear_chat(self):
        self.text_area.configure(state='normal')
        self.text_area.delete('1.0', tk.END)
        self.text_area.configure(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = InterviewApp(root)
    root.mainloop()


   