from tkinter import *            # GUI toolkit
import cv2                       # Library for OpenCV
import threading                 # Library for threading
import playsound                 # Library for alarm sound
import smtplib                   # Library for email sending
from PIL import Image, ImageTk    # Image handling
from email.mime.text import MIMEText
from datetime import datetime     # Library for date and time formatting

class Resize(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        
        # Set up Canvas for background and overlay images
        self.canvas = Canvas(self, width=900, height=600)
        self.canvas.pack(fill=BOTH, expand=YES)
        
        # Load images for background and overlay
        self.image_bg = Image.open("C:/Fire_detection_with_alarm/fire_icon.ico")
        self.img_copy_bg = self.image_bg.copy()
        self.image_overlay = Image.open("C:/Fire_detection_with_alarm/fire_text.png")
        self.img_copy_overlay = self.image_overlay.copy()
        
        # Define images for Tkinter
        self.background_image = ImageTk.PhotoImage(self.image_bg)
        self.overlay_image = ImageTk.PhotoImage(self.image_overlay)
        
        # Display background and overlay images on Canvas
        self.bg_image_obj = self.canvas.create_image(0, 0, image=self.background_image, anchor=NW)
        self.overlay_image_obj = self.canvas.create_image(100, 100, image=self.overlay_image, anchor=NW)
        
        # Create the "Start Fire Detection" button
        self.button1 = Button(
            self.canvas, text="Start Fire Detection", command=self.button_click,
            font=("Helvetica", 15, "bold"), bg="green", fg="white",
            activebackground="cyan", activeforeground="red", padx=10, pady=10,
            relief=RAISED, bd=10
        )
        self.button_window1 = self.canvas.create_window(10, 10, anchor=NW, window=self.button1)
        
        # Create the "Exit" button
        self.button2 = Button(
            self.canvas, text="Exit", command=self.button_click2,
            font=("Helvetica", 15, "bold"), bg="red", fg="white",
            activebackground="purple", activeforeground="red", padx=10, pady=10,
            relief=RAISED, bd=10
        )
        self.button_window2 = self.canvas.create_window(200, 10, anchor=NW, window=self.button2)

        # Create the "Stop Detection" button
        self.button3 = Button(
            self.canvas, text="Stop Detection", command=self.stop_detection,
            font=("Helvetica", 15, "bold"), bg="blue", fg="white",
            activebackground="orange", activeforeground="red", padx=10, pady=10,
            relief=RAISED, bd=10
        )
        self.button_window3 = self.canvas.create_window(400, 10, anchor=NW, window=self.button3)
        
        # Video feed frame setup
        self.video_frame = Frame(self.canvas, width=640, height=480, bg="black")
        self.video_frame.place(x=130, y=420)

        # Label for video feed
        self.video_label = Label(self.video_frame)
        self.video_label.pack(fill=BOTH, expand=YES)
        
        # Resize handling
        self.canvas.bind('<Configure>', self.resize_all)
        self.stop_flag = False
        self.runOnce = False
    
    def resize_all(self, event):
        # Resize the background image
        new_width_bg = event.width
        new_height_bg = event.height
        self.image_bg = self.img_copy_bg.resize((new_width_bg, new_height_bg))
        self.background_image = ImageTk.PhotoImage(self.image_bg)
        self.canvas.itemconfig(self.bg_image_obj, image=self.background_image)
        
        # Resize and update overlay image
        overlay_width = new_width_bg // 1
        overlay_height = new_height_bg // 2
        self.image_overlay = self.img_copy_overlay.resize((overlay_width, overlay_height))
        self.overlay_image = ImageTk.PhotoImage(self.image_overlay)
        self.canvas.itemconfig(self.overlay_image_obj, image=self.overlay_image)
        
        # Adjust the overlay and video feed positions
        overlay_x = new_width_bg // 2 - overlay_width // 2
        overlay_y = new_height_bg // 2.8 - overlay_height // 1
        self.canvas.coords(self.overlay_image_obj, overlay_x, overlay_y)
        self.video_frame.place(x=(new_width_bg - 640) // 2, y=new_height_bg - 500)

    def button_click(self):
        # Start fire detection
        self.stop_flag = False
        fire_cascade = cv2.CascadeClassifier('C:/Fire_detection_with_alarm/fire_detection_cascade_model.xml')
        vid = cv2.VideoCapture(0)

        # Function to play alarm sound
        def play_alarm_sound_function():
            playsound.playsound('C:/Fire_detection_with_alarm/fire_alarm.mp3', True)
            print("Fire alarm end")

        # Function to send email alert
        def send_mail_function():
            recipientmails = ["aravindkumar88170@gmail.com"]
            location = "Chandigarh University, Building E1, Floor 2, Room 208"
            detection_time = datetime.now().strftime("%d-%m-%Y %I:%M:%S:%p")
            severity = "Medium"
            immediate_actions = "Evacuate the building immediately and call the fire department."
            subject = "Urgent: Fire Detected!"
            body = f"""
Dear Team,

This is to alert you that a fire has been detected at the following location:

Location: {location}
Date & Time: {detection_time}
Severity: {severity}
Immediate Actions Required: {immediate_actions}

Please take necessary precautions and follow the emergency protocols immediately.

Stay safe,
[Aravind Kumar]
"""
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = "aravindkumar2107@gmail.com"
            msg['To'] = ", ".join(recipientmails)
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login("aravindkumar2107@gmail.com", 'hrijtkqzxkcwsjul')
                server.sendmail(msg['From'], recipientmails, msg.as_string())
                print("Alert mail sent successfully")
                server.close()
            except Exception as e:
                print(e)

        # Show video frame and detect fire
        def show_frame():
            if self.stop_flag:
                vid.release()
                cv2.destroyAllWindows()
                return
            ret, frame = vid.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fire = fire_cascade.detectMultiScale(frame, 1.2, 5)
            for (x, y, w, h) in fire:
                cv2.rectangle(frame, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)
                print("Fire alarm initiated")
                threading.Thread(target=play_alarm_sound_function).start()
                if not self.runOnce:
                    threading.Thread(target=send_mail_function).start()
                    self.runOnce = True
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            self.video_label.after(10, show_frame)

        show_frame()

    def stop_detection(self):
        # Stop the fire detection
        self.stop_flag = True
        self.runOnce = False

    def button_click2(self):
        # Exit the application
        print("Exiting the application")
        app.quit()

if __name__ == "__main__":
    app = Tk()
    app.title("Fire Detection with Alarm System")
    app.iconbitmap('C:/Fire_detection_with_alarm/fire_icon.ico')
    app.geometry("900x600")
    
    e = Resize(app)
    e.pack(fill=BOTH, expand=YES)
    
    app.mainloop()
