from tkinter import *   # GUI toolkit
import cv2              # Library for OpenCV
import threading         # Library for threading
import playsound         # Library for alarm sound
import smtplib           # Library for sending emails
from PIL import Image, ImageTk
from email.mime.text import MIMEText
from datetime import datetime

class Resize(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        
        # Create a Canvas widget
        self.canvas = Canvas(self, width=900, height=600)
        self.canvas.pack(fill=BOTH, expand=YES)
        
        # Load the background image
        self.image_bg = Image.open("C://Fire_detection_with_alarm//fire1.png")
        self.img_copy_bg = self.image_bg.copy()  # Copy for resizing
        
        # Load the overlay image
        self.image_overlay = Image.open("fire_text.png")
        self.img_copy_overlay = self.image_overlay.copy()  # Copy for resizing
        
        # Define images using PhotoImage function
        self.background_image = ImageTk.PhotoImage(self.image_bg)
        self.overlay_image = ImageTk.PhotoImage(self.image_overlay)
        
        # Create and display the background image on the Canvas
        self.bg_image_obj = self.canvas.create_image(0, 0, image=self.background_image, anchor=NW)
        
        # Create and display the overlay image on the Canvas
        self.overlay_image_obj = self.canvas.create_image(100, 100, image=self.overlay_image, anchor=NW)  # Adjust coordinates as needed
        
        # Create the first button
        self.button1 = Button(
            self.canvas, text="Start Fire Detection", command=self.button_click, font=("Helvetica", 15, "bold"), bg="green", fg="white", activebackground="cyan", activeforeground="red", padx=10, pady=10, relief=RAISED, bd=10
        )
        self.button_window1 = self.canvas.create_window(10, 10, anchor=NW, window=self.button1)  # Initial coordinates
        
        # Create the second button
        self.button2 = Button(
            self.canvas, text="Exit", command=self.button_click2, font=("Helvetica", 15, "bold"), bg="red", fg="white", activebackground="purple", activeforeground="red", padx=10, pady=10, relief=RAISED, bd=10
        )
        self.button_window2 = self.canvas.create_window(200, 10, anchor=NW, window=self.button2)  # Initial coordinates

        # Create the third button
        self.button3 = Button(
            self.canvas, text="Stop Detection", command=self.stop_detection, font=("Helvetica", 15, "bold"), bg="blue", fg="white", activebackground="orange", activeforeground="red", padx=10, pady=10, relief=RAISED, bd=10
        )
        self.button_window3 = self.canvas.create_window(400, 10, anchor=NW, window=self.button3)  # Initial coordinates
        
        # Create a frame to hold the video feed
        self.video_frame = Frame(self.canvas, width=640, height=480, bg="black")
        self.video_frame.place(x=130, y=420)  # Adjust coordinates to place it at the bottom

        # Create a label to display the video feed within the frame
        self.video_label = Label(self.video_frame)
        self.video_label.pack(fill=BOTH, expand=YES)
        
        # Bind function resize_background to screen resize
        self.canvas.bind('<Configure>', self.resize_all)

        self.stop_flag = False  # Flag to control the video feed loop
        self.runOnce = False  # Flag to track whether actions have been initiated
    
    def resize_all(self, event):
        # Get the new width and height for background image
        new_width_bg = event.width
        new_height_bg = event.height
        
        # Resize the background image according to new dimensions
        self.image_bg = self.img_copy_bg.resize((new_width_bg, new_height_bg))
        
        # Define new background image using PhotoImage function
        self.background_image = ImageTk.PhotoImage(self.image_bg)
        
        # Update background image on the Canvas
        self.canvas.itemconfig(self.bg_image_obj, image=self.background_image)
        
        # Calculate new size for the overlay image
        overlay_width = new_width_bg // 1  # Example: Resize to quarter the width of the background
        overlay_height = new_height_bg // 2  # Example: Resize to quarter the height of the background
        
        # Resize the overlay image according to new dimensions
        self.image_overlay = self.img_copy_overlay.resize((overlay_width, overlay_height))
        
        # Define new overlay image using PhotoImage function
        self.overlay_image = ImageTk.PhotoImage(self.image_overlay)
        
        # Update overlay image on the Canvas
        self.canvas.itemconfig(self.overlay_image_obj, image=self.overlay_image)
        
        # Reposition the overlay image on the Canvas
        overlay_x = new_width_bg // 2 - overlay_width // 2  # Centered horizontally
        overlay_y = new_height_bg // 2.8 - overlay_height // 1  # Centered vertically
        self.canvas.coords(self.overlay_image_obj, overlay_x, overlay_y)
        
        # Calculate new coordinates for the first button
        button_x1 = new_width_bg // 2 - overlay_width // 2.5 # Adjust for button width
        button_y1 = new_height_bg // 2 - overlay_height // 2  # Below the overlay image
        
        # Reposition the first button on the Canvas
        self.canvas.coords(self.button_window1, button_x1, button_y1)
        
        # Calculate new coordinates for the second button
        button_x2 = new_width_bg // 1 - overlay_width // 3   # Adjust for button width
        button_y2 = new_height_bg // 2 - overlay_height // 2  # Below the overlay image
        
        # Reposition the second button on the Canvas
        self.canvas.coords(self.button_window2, button_x2, button_y2)

        # Calculate new coordinates for the third button
        button_x3 = new_width_bg // 2 - overlay_width // 8 # Adjust for button width
        button_y3 = new_height_bg // 2 - overlay_height // 2  # Below the overlay image
        
        # Reposition the third button on the Canvas
        self.canvas.coords(self.button_window3, button_x3, button_y3)
        
        # Adjust the video frame position to the center of the bottom
        self.video_frame.place(x=(new_width_bg - 640) // 2, y=new_height_bg - 500)

    def button_click(self):
        self.stop_flag = False  # Reset the stop flag
        fire_cascade = cv2.CascadeClassifier('C://Fire_detection_with_alarm//fire_detection_cascade_model.xml') # Load fire detection model

        vid = cv2.VideoCapture(0)  # Use 0 for the default camera or change to 1 for external camera

        def play_alarm_sound_function():  # Play alarm sound
            playsound.playsound('C://Fire_detection_with_alarm//fire_alarm.mp3', True)
            print("Fire alarm ended") 

        def send_mail_function():  # Send email alert
            recipientmails = ["codewithprem12345@gmail.com", "premst12345@gmail.com", "premkrst12345@gmail.com"]  
            location = "Annada College Hzb, Building A, Floor 1, Room 48"
            detection_time = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
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
[Prem Kumar Team]
            """
            
            # Create the MIMEText object
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = "premkumar123456b1@gmail.com"  # Sender's email address
            msg['To'] = ", ".join(recipientmails)

            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.ehlo()
                server.starttls()
                server.login("premkumar123456b1@gmail.com", 'your_password_here')  # Sender's email login
                server.sendmail(msg['From'], recipientmails, msg.as_string())
                print("Alert mail sent successfully to {}".format(", ".join(recipientmails)))
                server.close()
            except Exception as e:
                print(e)  # Print any errors encountered
        
        def show_frame():
            if self.stop_flag:
                vid.release()
                cv2.destroyAllWindows()
                return

            ret, frame = vid.read()  # Read the video frame
            if not ret:
                print("Failed to capture frame")
                return

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale
            fire = fire_cascade.detectMultiScale(gray, 1.2, 5)  # Detect fire

            for (x, y, w, h) in fire:
                cv2.rectangle(frame, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)
                print("Fire alarm initiated")
                threading.Thread(target=play_alarm_sound_function).start()

                if not self.runOnce:
                    print("Mail send initiated")
                    threading.Thread(target=send_mail_function).start()
                    self.runOnce = True
            
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # Convert to RGBA
            img = Image.fromarray(cv2image)  # Convert to PIL format
            imgtk = ImageTk.PhotoImage(image=img)  # Convert to ImageTk format

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            self.video_label.after(10, show_frame)

        show_frame()

    def stop_detection(self):
        self.stop_flag = True

    def button_click2(self):
        print("Exiting the application")
        app.quit()  # Exit the application

if __name__ == "__main__":
    app = Tk()
    app.title("Fire Detection with Alarm System")
    app.iconbitmap('C:/Fire_detection_with_alarm/fire_icon.ico')
    app.geometry("900x600")
    
    e = Resize(app)
    e.pack(fill=BOTH, expand=YES)
    
    app.mainloop()
