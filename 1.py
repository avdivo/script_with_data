import tkinter as tk

root = tk.Tk()
textbox = tk.Text(root, width=30, height=15, padx=10, pady=5, wrap='word')
textbox.pack(pady=10, padx=10)

# Bind changes in textbox to callback function.
def modify_callback(event):
    print('modify_callback')
    textbox.edit_modified(False)    # Reset the modified flag for text widget.
textbox.bind('<<Modified>>', modify_callback)

# Insert text, modifies text widget.
textbox.insert('end', 'Example text.')

root.mainloop()