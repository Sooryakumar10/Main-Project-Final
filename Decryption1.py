from datetime import timedelta
from tkinter import *
import hashlib
from random import *
from collections import namedtuple
import numpy
import points as points
Point = namedtuple("Point", "x y")
import pymongo
import time

def decryption():
    # To Establish Connection with Cloud
    start_time = time.time()
    file_id = inputfileID.get()
    file_id= int(file_id)
    input_key_file = inputfilepath.get()
    client = pymongo.MongoClient(
        "mongodb+srv://soorya:soorya@cluster0.hl7ws.mongodb.net/Main?retryWrites=true&w=majority")
    db = client["Main"]
    collections = db["Main"]
    cloud_data = collections.find_one({"_id": file_id})
    print(cloud_data)

    # Getting the encrypted information from cloud
    encrypted_output = cloud_data.get('Encrypted information')
    print(encrypted_output)

    # Getting the key of Dehex From the Cloud
    encrypt_key_from_cloud = cloud_data.get('Key_Dehex')
    print(encrypt_key_from_cloud)

    # Getting the key_id.txt from Local Directory
    message1 = ""

    # Applying SHA to the Key_id.txt
    result = hashlib.sha256(input_key_file.encode())
    print("The hexadecimal equivalent of SHA256 is : ")
    sha_decryption = result.hexdigest()
    print(sha_decryption)

    if (encrypt_key_from_cloud == sha_decryption):
        print("Key matched! Decryption starts.")

        # Decryption for ECC
        # f=open('ECC1_enc.txt','r')
        ct1 = encrypted_output
        # f.close()

        print('TEXT READ FROM FILE:', ct1)
        eO = 'ORIGIN'
        ep = 71
        ea = 1
        eb = 3
        ena = 47
        enb = 8
        k = 30
        eg = '35,10'
        epa = epb = ekpb = nbkg = ''

        radix = []
        for i in range(65, 91):
            radix.append(chr(i))
        for i in range(97, 123):
            radix.append(chr(i))
        for i in range(10):
            radix.append(str(i))
        radix.append('+')
        radix.append(',')

        points = []
        lhs = rhs = 0
        for i in range(ep):
            for j in range(ep):
                lhs = (j * j) % ep
                rhs = ((i * i * i) + (ea * i) + eb) % ep
                if lhs == rhs:
                    points.append(str(i) + ',' + str(j))
        points.append(eO)

        def valid(P):
            if P == eO:
                return True
            else:
                return (
                        (P.y ** 2 - (P.x ** 3 + ea * P.x + eb)) % ep == 0 and
                        0 <= P.x < ep and 0 <= P.y < ep)

        def inv_mod_p(x):
            if x % ep == 0:
                raise ZeroDivisionError("Impossible inverse")
            return pow(x, ep - 2, ep)

        def ec_inv(P):
            if P == eO:
                return P
            return Point(P.x, (-P.y) % ep)

        def ec_add(P, Q):
            if not (valid(P) and valid(Q)):
                raise ValueError("Invalid inputs")

            if P == eO:
                result = Q
            elif Q == eO:
                result = P
            elif Q == ec_inv(P):
                result = eO
            else:
                if P == Q:
                    dydx = (3 * P.x ** 2 + ea) * inv_mod_p(2 * P.y)
                else:
                    dydx = (Q.y - P.y) * inv_mod_p(Q.x - P.x)
                x = (dydx ** 2 - P.x - Q.x) % ep
                y = (dydx * (P.x - x) - P.y) % ep
                result = Point(x, y)

            assert valid(result)
            return result

        nat = k * enb
        if epb == eO:
            P = Q = eO
        else:
            xp = xq = int(eg.split(',')[0])
            yp = yq = ep - int(eg.split(',')[1])
            P = Point(xp, yp)
            Q = Point(xq, yq)
        if nat == 1:
            nbkg = eg
        else:
            while nat != 1:
                r = ec_add(P, Q)
                if r == eO:
                    P = r
                else:
                    xp = r.x
                    yp = r.y
                    P = Point(xp, yp)
                nat = nat - 1
            if r == eO:
                nbkg = r
            else:
                nbkg = str(xp) + ',' + str(yp)

        bina = ''
        ct = []
        for i in ct1:
            ct.append(points[radix.index(i)])
        for ok in ct:
            if ok == eO:
                P = eO
            else:
                t = ok.split(',')
                P = Point(int(t[0]), int(t[1]))
            if nbkg == eO:
                Q = eO
            else:
                Q = Point(int(nbkg.split(',')[0]), int(nbkg.split(',')[1]))
            r = ec_add(P, Q)
            if r == eO:
                ct[ct.index(ok)] = points.index(eO)
            else:
                xp = r.x
                yp = r.y
                ct[ct.index(ok)] = points.index(str(xp) + ',' + str(yp))
        for i in ct:
            bina = bina + format(i, '06b')
        if len(bina) % 8 != 0:
            for i in range((8 - (len(bina) % 8))):
                bina = bina + str(0)
        bina.replace('0b', '')
        i = 0
        ct = []
        while (i != len(bina)):
            t = bina[i:i + 8]
            t = '0b' + t
            t = int(t, 2)
            ct.append(chr(t))
            i = i + 8

        pt1 = ''.join(ct)
        pt1 = pt1.rstrip('\x00')
        print('Decrypted Text=', pt1)

        # Dehex decryption:
        final_number_list = [x for x in pt1]
        final_number_arr = numpy.array(final_number_list)
        print(" Array format of Encrypted Text : ", final_number_arr)

        # Step 2
        result = []
        for elem in final_number_arr:
            result.extend(ord(num) for num in elem)
            new_list_ascii = numpy.array(result)
        print(" ASCII Value of Encrypted array : ", new_list_ascii)

        # Step 3
        # encrypt_key1 = str(encrypt_key)
        message1 = ""
        inputFile = open(input_key_file, 'r')
        for line in inputFile:
            message1 = message1 + line
            message1 = message1.strip()
            message1 = message1.rstrip(']')
            message1 = message1.lstrip('[')
            message1 = message1.replace(" ", "")
            message1 = "".join(message1.splitlines())
        print(message1)

        encrypt_key_list = [x for x in message1]
        print(encrypt_key_list)
        key_array = [int(x) for x in encrypt_key_list]

        encrypt_key_arr = numpy.array(key_array)
        print(encrypt_key_arr)

        # key_array = [int(x) for x in encrypt_key_arr]
        print(" Key as Array format ", encrypt_key_arr)

        # Step 4
        encrypt_key_length = len(key_array)
        print(" The key size is : ", encrypt_key_length)

        # Step 4.1
        encrypt_text_length = len(pt1)
        print("Text Length is : ", encrypt_text_length)

        # Step 5
        quotient = int(encrypt_text_length / encrypt_key_length)

        # Step 6
        reshaped_ASCII_array = new_list_ascii.reshape(quotient, encrypt_key_length)

        # Step 7
        final_dec = []
        final_dec = reshaped_ASCII_array - encrypt_key_arr

        # Step 8
        final_dec = numpy.array(final_dec).flatten()
        print(final_dec)

        # Step 9
        final_1_enc = "".join([chr(c) for c in final_dec])
        print(final_1_enc)
        emptylabel.config(text=final_1_enc, fg='red', font=('Arial', 14), wraplength=1000, justify='left')

        with open('output.txt','w')as f:
            s = str(final_1_enc)
            f.write(s)

    else:
       print("Key not matching! Decryption can't be done.")
       emptylabel.config(text="Key not matching! Decryption can't be done.", fg='red', font=('Arial', 20), wraplength=500, justify='left')

    elapsed_time_secs = time.time() - start_time
    msg_time = "Execution took: %s secs (Wall clock time)" % timedelta(seconds=round(elapsed_time_secs))
    print(elapsed_time_secs)

window=Tk()
window.title("Decryption")
window.geometry('1000x500')

label1 = Label(window,text='Enter the cloud file ID : ',fg = 'blue', font =('Arial',14))
label1.grid(row=1,column=1,padx=5,pady=10)

inputfileID=StringVar()
inputfilepath=StringVar()

textbox1 = Entry(window,textvariable=inputfileID,fg = 'blue', font =('Arial',14))
textbox1.grid(row=1,column=2)

label2 = Label(window,text='Enter key File name or filepath : ',fg = 'red', font =('Arial',14))
label2.grid(row=2,column=1,padx=5,pady=10)

textbox2 = Entry(window,textvariable=inputfilepath,fg = 'red', font =('Arial',14))
textbox2.grid(row=2,column=2)

button1 = Button(window, command=decryption,  text='Decrypt',fg = 'black', font =('Arial',14))
button1.grid(row=4,column=3,padx=10)

window1=Tk()
window1.title("Output")
window1.geometry('500x500')

emptylabel=Label(window1,fg='green',font=('Arial',20))
emptylabel.grid(row=1,column=1)

window.mainloop()

