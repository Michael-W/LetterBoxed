"""Forms for inputting and displaying data."""
import os
import tkinter as tk
from functools import partial

BGC = 'Bisque1'
FGC = 'dark red'


class InputForm:
    """Form for inputting data."""

    def __init__(self, submit_command):
        """Create the form."""
        self.root = tk.Tk()
        self.root.configure(bg=BGC)
        self.root.title("Letter Boxed")
        self.root.resizable(False, False)
        # Bind the Enter key to the submit button
        self.root.bind('<Return>', lambda event: self.submit_button.invoke())
        self.root.attributes('-fullscreen', False)
        self.entries = []
        frame = tk.Frame(self.root, borderwidth=4, relief=tk.RIDGE, bg=BGC)
        frame.pack(padx=10, pady=10)
        self.entry_values = [tk.StringVar() for _ in range(12)]
        directions = ['North', 'East', 'South', 'West']
        for side in range(4):
            match side:
                case 0:
                    r = 1
                    c = 2
                case 1:
                    r = 2
                    c = 3
                case 2:
                    r = 3
                    c = 2
                case 3:
                    r = 2
                    c = 1
            tk.Label(frame, text=directions[side], bg=BGC, fg=FGC).grid(
                row=r, column=c, padx=10, pady=10)
            for entry_on_side in range(3):
                index = side * 3 + entry_on_side
                entry = tk.Entry(
                    frame, width=3, textvariable=self.entry_values[index], justify='center')
                entry.bind('<KeyRelease>', lambda event,
                           index=index: self.validate_entry(event, index))
                match side:
                    case 0:
                        r = 0
                        c = entry_on_side + 1
                    case 1:
                        r = entry_on_side + 1
                        c = 4
                    case 2:
                        r = 4
                        c = 3 - entry_on_side
                    case 3:
                        r = 3 - entry_on_side
                        c = 0
                entry.grid(row=r, column=c, padx=10, pady=10)
                self.entries.append(entry)
        self.entries[0].focus()

        self.clear_button = tk.Button(
            frame, text="Clear", bg=BGC, fg=FGC,
            command=self.clear_entries)
        self.clear_button.grid(row=5, column=3, pady=10,
                               sticky=tk.EW, rowspan=2)

        self.submit_button = tk.Button(
            frame, text="Submit", bg=BGC, fg=FGC,
            command=lambda: submit_command(
                self.get_data(), self.root), state=tk.DISABLED)
        self.submit_button.grid(row=5, column=1, pady=10,
                                sticky=tk.EW, rowspan=2)

        # Adjust the grid cell widths to make the buttons the same width.
        submit_button_width = self.submit_button.winfo_reqwidth()
        for col in 1, 3:
            frame.grid_columnconfigure(col, minsize=submit_button_width)

    def clear_entries(self):
        """Clear all the entries in the form."""
        for entry in self.entries:
            entry.delete(0, tk.END)
            self.entries[0].focus()
        self.submit_button.config(state=tk.DISABLED)

    def run(self):
        """Run the form."""
        self.root.mainloop()

    def get_data(self):
        """Get the data from the form."""
        return [''.join(self.entries[i*3+j].get().lower()
                        for j in range(3)) for i in range(4)]

    def set_entry_focus(self):
        """Set the focus on the first empty entry."""
        for index in range(12):
            if not self.entry_values[index].get():
                self.entries[index].focus()
                break

    def validate_entry(self, event, index):
        """Validate an entry."""
        value = event.widget.get().strip().upper()
        if len(value) > 1 or not \
            value.isalpha() or \
                value in [ev.get() for i,
                          ev in enumerate(self.entry_values) if i != index]:
            self.entry_values[index].set('')
        else:
            self.entry_values[index].set(value)
            self.set_entry_focus()
            if all(ev.get() for ev in self.entry_values):
                self.submit_button.config(state=tk.NORMAL)
                self.submit_button.focus()


class OutputForm:
    """Form for displaying data."""

    def __init__(self,
                 the_results, answer_pair, pair_count, input_form, lock_file,
                 linked_form=None):
        self.root = tk.Toplevel()
        self.root.title("Letter Boxed Results")
        self.root.configure(bg=BGC)
        self.root.resizable(False, False)
        self.root.attributes('-fullscreen', False)

        linked_form = HintSubForm

        self.the_results = the_results
        self.answer_pair = answer_pair
        self.pair_count = pair_count
        self.input_form = input_form
        self.lock_file = lock_file
        self.linked_form = linked_form

        input_form.withdraw()

        # Bind a function to the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_form_x_click)

        # Create a frame inside a frame for appearance sake.
        mainframe = tk.Frame(self.root, relief=tk.RIDGE, borderwidth=4, bg=BGC)
        mainframe.pack(padx=10, pady=10)
        frame = tk.Frame(mainframe, relief=tk.RIDGE, borderwidth=4, bg=BGC)
        frame.pack(padx=10, pady=10)

        # Add the exit button to the frame
        action = "Exit"
        if pair_count == 0:
            action = "Correct the error."
        self.btn_exit = tk.Button(
            frame, text=action, bg=BGC, fg=FGC,
            command=lambda: self.on_close(input_form, pair_count), padx=10, pady=10)
        self.btn_exit.grid(row=0, column=2, sticky=tk.NSEW)

        # Add the hints to the frame
        if pair_count != 0:
            self.hint_subform = HintSubForm(
                frame, self.answer_pair[0], self.answer_pair[1])
            self.hint_subform.grid(row=0, column=1)
        else:
            self.label = tk.Label(
                frame,
                text="No pairs found.\nCheck your entries.",
                padx=10, pady=10, font=("Arial", 10), bg=BGC, fg=FGC)
            self.label.grid(row=0, column=1)

        # Add the show button to the frame
        plural = '' if pair_count == 1 else 's'
        self.btn_show = tk.Button(
            frame, text=f"Show The {pair_count} Pair{plural}",
            command=lambda: self.text_box(self.the_results),
            padx=10, pady=20, bg=BGC, fg=FGC)
        self.btn_show.grid(row=0, column=0, sticky=tk.NSEW)

        # Adjust the grid cell sizes to make the buttons the same size.
        for col in 0, 2:
            frame.grid_columnconfigure(
                col, minsize=self.btn_show.winfo_reqwidth())

        if pair_count == 0:
            self.btn_show.grid_forget()
            self.btn_exit.focus()

    def update_linked_form(self):
        """Update the linked form with the chosen pair and more."""
        self.linked_form.update_text_box(self.hint_subform,
            f"{len(self.answer_pair[0] + self.answer_pair[1])}: {
                self.answer_pair[0]} {self.answer_pair[1]}")
        # Hide the show button to prevent multiple clicks
        self.btn_show.grid_forget()

    def text_box(self, the_results):
        """Create a text box for the results if more than one."""
        if self.pair_count == 1:
            self.update_linked_form()
            return
        num_lines = len(the_results)  # Height of the text box
        num_chars = max(len(line) for line in the_results)  # Width of the text box
        # Create a scrollbar if the number of lines is greater than box_height
        box_height = 30
        if num_lines > box_height:
            self.scrollbar = tk.Scrollbar(self.root, bg=FGC, troughcolor=BGC)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.text = tk.Text(
                self.root,
                height=box_height,
                width=num_chars,
                bg=BGC, fg=FGC,
                yscrollcommand=self.scrollbar.set)
            self.text.pack(side=tk.LEFT, fill=tk.BOTH, ipadx=10, ipady=2)
            self.scrollbar.config(command=self.text.yview)
        else:
            # Create a text box sized to fit the results
            self.text = tk.Text(
                self.root,
                height=num_lines,
                width=num_chars,
                bg=BGC, fg=FGC)
            self.text.pack(ipadx=10, ipady=2)

        # Insert the results into the text box
        self.text.insert(tk.END, "\n".join(the_results))
        self.text.config(state=tk.DISABLED)
        # show the chosen pair in the linked form
        self.update_linked_form()

    def on_form_x_click(self):
        """Called when the window is closed with the 'x' button."""
        input_form = self.input_form
        pair_count = self.pair_count
        self.on_close(input_form, pair_count)

    def on_close(self, input_form, pair_count):
        """Handle the window close event."""
        if pair_count == 0:
            # Show the input form to allow the user to check the entries
            input_form.deiconify()
            self.root.withdraw()
        else:
            # Remove the lock file
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
            # Destroy the window and the input form
            self.root.destroy()
            input_form.destroy()


class HintSubForm(tk.Frame):
    """ Hints for the user """

    def __init__(self, master, first_word, second_word):
        super().__init__(master)

        self.hint_instruction = "Click and hold below for a hint."  # Default message
        self.display_label = tk.Label(self,
                                 text=self.hint_instruction,
                                 bg=BGC,
                                 fg=FGC,
                                 font=("Arial", 10, "bold"),
                                 relief=tk.RAISED, height=1, width=28)
        self.display_label.pack()
        self.master.configure(bg=BGC)
        self.first_word = first_word
        self.second_word = second_word

        self.labels = [
            ('First letter of first word', self.first_word[0]),
            ('Second Letter of first word', self.first_word[1]),
            ('Joining Letter', self.first_word[-1]),
            ('Length of first word', len(self.first_word)),
            ('Length of second word', len(self.second_word))
        ]

        for text, answer in self.labels:
            button = tk.Button(self,
                        text=text,
                        bg=BGC,
                        fg=FGC,
                        font=("Arial", 10),
                        width=28,
                        relief=tk.RAISED)
            button.pack()
            button.bind('<ButtonPress-1>', partial(self.display_answer, answer))
            button.bind('<ButtonRelease-1>', self.display_hint_instruction)

    def display_answer(self, answer, _):
        """Display the answer in the display label."""
        self.display_label.configure(text=answer)

    def display_hint_instruction(self, _):
        """Display the default hint instruction."""
        self.display_label.configure(text=self.hint_instruction)

    def remove_hint_labels(self):
        """Remove the hint labels from the form."""
        for widget in self.winfo_children():
            if widget.cget("text") in [text for text, _ in self.labels]:
                widget.destroy()

    def hide_info(self, _):
        """Hide the hint for the label."""
        self.display_label.configure(text=self.hint_instruction)

    def update_text_box(self, new_text):
        """Update the text box's content to show the solution pair."""
        self.display_label.configure(font=("Courier", 10), width=34, text=new_text, relief=tk.FLAT)
        self.remove_hint_labels()
