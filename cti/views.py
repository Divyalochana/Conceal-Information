from django.shortcuts import render, redirect
from .forms import ToDoForm, decForm
from django.views.decorators.http import require_POST
from .models import ToDo, decode
from django.core.files.storage import FileSystemStorage
import smtplib, ssl
import cv2
import numpy as np
from PIL import Image
import random
import os
from tkinter import *
from tkinter import messagebox
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
# Create your views here.

## ENCRYPTION.....

def to_bin(data):
    """Convert `data` to binary format as string"""
    if isinstance(data, str):
        return ''.join([ format(ord(i), "08b") for i in data ])
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [ format(i, "08b") for i in data ]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")


def encode(image_name, secret_data):
    # read the image
    image = cv2.imread(image_name)
    # maximum bytes to encode
    n_bytes = image.shape[0] * image.shape[1] * 3 // 8
    print("[*] Maximum bytes to encode:", n_bytes)
    if len(secret_data) > n_bytes:
        raise ValueError("[!] Insufficient bytes, need bigger image or less data.")
    print("[*] Encoding data...")
    # add stopping criteria
    secret_data += "====="
    data_index = 0
    # convert data to binary
    binary_secret_data = to_bin(secret_data)
    # size of data to hide
    data_len = len(binary_secret_data)
    for row in image:
        for pixel in row:
            # convert RGB values to binary format
            r, g, b = to_bin(pixel)
            # modify the least significant bit only if there is still data to store
            if data_index < data_len:
                # least significant red pixel bit
                pixel[0] = int(r[:-1] + binary_secret_data[data_index], 2)
                data_index += 1
            if data_index < data_len:
                # least significant green pixel bit
                pixel[1] = int(g[:-1] + binary_secret_data[data_index], 2)
                data_index += 1
            if data_index < data_len:
                # least significant blue pixel bit
                pixel[2] = int(b[:-1] + binary_secret_data[data_index], 2)
                data_index += 1
            # if data is encoded, just break out of the loop
            if data_index >= data_len:
                break
    print("encoded successfully")
    return image





html = '''
    <html>
        <body>
            <h1>Here is your file...!</h1>
        </body>
    </html>

'''

def attatch_file(email_message, filename):
    with open(filename, "rb") as f:
        file_attachment = MIMEApplication(f.read())
    file_attachment.add_header(
        "content-Disposition",
        f"attachment; filename = {filename}",
    )
    email_message.attach(file_attachment)


def home(request):
    form = ToDoForm()
    form1 = decForm()
    context = {'form': form, 'form1': form1}
    return render(request,'index.html',context)


@require_POST
def doneTodo(request):
    form = ToDoForm(request.POST, request.FILES)
    if form.is_valid():
        email = request.POST.get('email')
        key = request.POST.get('key')
        description = request.POST.get('description')
        UploadedFile1 = request.FILES['image1']
        UploadedFile2 = request.FILES['image2']
        fs = FileSystemStorage()
        path1 = fs.save(UploadedFile1.name, UploadedFile1)
        path2 = fs.save(UploadedFile2.name, UploadedFile2)
        url1 = fs.url(path1)
        url2 = fs.url(path2)
        model_obj = ToDo(email=email, key=key, description=description)
        model_obj.save()
        actual_path = 'c:/Users/Divyalochana/Documents/concealinfo'
        print(url1)
        #encryption...
        img_one = cv2.imread(actual_path+url1)
        img_one = cv2.resize(img_one,(512,512))
        img_two = cv2.imread(actual_path+url2)
        img_two = cv2.resize(img_two,(512,512))
        merged_path = 'c:/Users/Divyalochana/Documents/concealinfo/media'
        final_img = cv2.addWeighted(img_one,0.9,img_two,0.1,0)
        ext= str(random.randrange(1,100))+".png"
        cv2.imwrite(os.path.join(merged_path , ext), final_img)
        picture = merged_path+'/'+ext
        encoded_image = encode(image_name= picture, secret_data=description+key)
        # save the output image (encoded image)
        output_img=key+".png"
        cv2.imwrite(os.path.join(merged_path, output_img), encoded_image)
        #Mail related...
        from_addr = 'technostar1001@gmail.com'
        to_addr = email
        password = 'Techno@star'
        email_message = MIMEMultipart()
        email_message['From'] = from_addr
        email_message['To'] = to_addr
        email_message.attach(MIMEText(html, "html"))
        attatch_file(email_message, picture)
        email_string = email_message.as_string()
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(from_addr, password)
            server.sendmail(from_addr, to_addr, email_string)
        messagebox.showinfo("showinfo", "Mail sent successfully")
        return render(request, 'index.html')


## DECRYPTION...

def decrypt(output_image):
    print("[+] Decoding...")
    # read the image
    image = cv2.imread(output_image)
    binary_data = ""
    for row in image:
        for pixel in row:
            r, g, b = to_bin(pixel)
            binary_data += r[-1]
            binary_data += g[-1]
            binary_data += b[-1]
    # split by 8-bits
    all_bytes = [ binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]
    # convert from bits to characters
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "=====":
            break
    return decoded_data[:-8]
    print("decoded successfully")

def decTodo(request):
    form = decForm(request.POST, request.FILES)
    if form.is_valid():
        key2 = request.POST.get('key2')
        snap = request.FILES['snap']

        fs = FileSystemStorage()
        path1 = fs.save(snap.name, snap)
        url1 = fs.url(path1)
        actual_path = 'c:/Users/Divyalochana/Documents/concealinfo'
        model_obj = decode(key2=key2)
        model_obj.save()
        output_image = actual_path+url1
        decoded_data = decrypt(output_image)
        print("[+] Decoded data:", decoded_data)
        messagebox.showinfo("showinfo", decoded_data)
        return render(request, 'index.html')