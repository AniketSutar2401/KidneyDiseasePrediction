import pickle
import datetime
import numpy as np
import pandas as pd
import tensorflow as tf
from django.shortcuts import render, redirect
from keras.layers import Conv1D, Dense, MaxPool1D, Flatten
from keras.layers import Dropout
from keras.models import Sequential, load_model
from sklearn.preprocessing import MinMaxScaler, LabelBinarizer

from app import admin
from app.models import *


def home(request):
    try:
        return render(request, 'app/home.html')
    except Exception as ex:
        return render(request, 'app/home.html', {'message': ex})


def login(request):
    try:
        if request.method == 'POST':
            mobile = str(request.POST.get("mobile")).strip()
            password = str(request.POST.get("password")).strip()
            role = str(request.POST.get("role")).strip()
            if role == 'admin':
                if mobile == admin.mobile and password == admin.password:
                    request.session['alogin'] = True
                    return redirect(upload_dataset)
            else:
                patient = Patient.objects.get(mobile=mobile)
                if patient.password == password:
                    request.session['plogin'] = True
                    request.session['pmobile'] = mobile
                    return redirect(prediction)
            message = 'Invalid username or password'
            return render(request, 'app/login.html', {'message': message})
        else:
            request.session['alogin'] = False
            request.session['plogin'] = False
            return render(request, 'app/login.html')
    except Patient.DoesNotExist:
        message = 'Invalid username or password'
    except Exception as ex:
        message = ex
    return render(request, 'app/login.html', {'message': message})


def upload_dataset(request):
    if 'alogin' in request.session and request.session['alogin']:
        message = ''
        try:
            if request.method == "POST":
                if request.FILES:
                    dataset = request.FILES['dataset']
                    with open(f'media/dataset.csv', 'wb')as fw:
                        fw.write(dataset.read())
                    data = pd.read_csv(f'media/dataset.csv')
                    data['classification'].replace({'ckd': 1, 'notckd': 0}, inplace=True)
                    data.drop(columns=['wc', 'rc', 'dm', 'cad', 'id'], inplace=True)
                    data.dropna(how='any', inplace=True)
                    data["rbc"] = LabelBinarizer().fit_transform(data["rbc"])
                    data["pc"] = LabelBinarizer().fit_transform(data["pc"])
                    data["pcc"] = LabelBinarizer().fit_transform(data["pcc"])
                    data["ba"] = LabelBinarizer().fit_transform(data["ba"])
                    data["htn"] = LabelBinarizer().fit_transform(data["htn"])
                    data["appet"] = LabelBinarizer().fit_transform(data["appet"])
                    data["pe"] = LabelBinarizer().fit_transform(data["pe"])
                    data["ane"] = LabelBinarizer().fit_transform(data["ane"])
                    X = data.drop(columns='classification')
                    y = data['classification']
                    scaler = MinMaxScaler()
                    X = scaler.fit_transform(X)
                    f = open('media/scaler.pkl', 'wb')
                    pickle.dump(scaler, f)
                    f.close()
                    np.random.seed(42)
                    tf.random.set_seed(42)
                    model = Sequential()
                    model.add(
                        Conv1D(filters=256, kernel_size=3, padding="same", input_shape=(20, 1), activation="relu"))
                    model.add(MaxPool1D(pool_size=2))
                    model.add(Flatten())
                    model.add(Dense(128, activation="relu"))
                    model.add(Dropout(0.3))
                    model.add(Dense(1, activation="sigmoid"))
                    model.compile(loss="binary_crossentropy", optimizer="SGD", metrics=["accuracy"])
                    h = model.fit(X, y, epochs=200)
                    model.save("media/model.h5")
                    f = open('media/history.pkl', 'wb')
                    pickle.dump(h.history, f)
                    f.close()
                    message = "Dataset uploaded successfully."
                else:
                    raise Exception("Please select dataset file")
        except Exception as ex:
            message = ex
        return render(request, 'admin/upload_dataset.html', {'message': message})
    else:
        return redirect(login)


def patient_master(request):
    if 'alogin' in request.session and request.session['alogin']:
        patients = None
        message = ''
        try:
            if request.method == "POST":
                mobile = str(request.POST.get('mobile')).strip()
                patient = Patient.objects.get(mobile=mobile)
                patient.delete()
                message = 'Patient deleted successfully'
            patients = Patient.objects.all()
        except Exception as ex:
            message = ex
        return render(request, 'admin/patient_master.html', {'message': message, 'patients': patients})
    else:
        return redirect(login)


def registration(request):
    if request.method == 'POST':
        try:
            patient = Patient()
            patient.mobile = str(request.POST.get('mobile')).strip()
            patient.name = request.POST.get('name')
            patient.address = request.POST.get('address')
            patient.password = str(request.POST.get('password')).strip()
            patient.save(force_insert=True)
            message = 'Patient registration done'
        except Exception as ex:
            message = ex
        return render(request, 'app/registration.html', {'message': message})
    else:
        return render(request, 'app/registration.html')


def prediction(request):
    try:
        if 'plogin' in request.session and request.session['plogin']:
            class_ = 'success'
            message = ""
            if request.method == "POST":
                history = History()
                id_ = datetime.datetime.now().strftime('%d%m%y%I%M%S')
                mobile = request.session['pmobile']
                patient = Patient.objects.get(mobile=mobile)
                age = float(request.POST.get("age"))
                bp = float(request.POST.get("bp"))
                sg = float(request.POST.get("sg"))
                al = int(request.POST.get("al"))
                su = int(request.POST.get("su"))
                rbc = int(request.POST.get("rbc"))
                pc = int(request.POST.get("pc"))
                pcc = int(request.POST.get("pcc"))
                ba = int(request.POST.get("ba"))
                bgr = float(request.POST.get("bgr"))
                bu = float(request.POST.get("bu"))
                sc = float(request.POST.get("sc"))
                sod = float(request.POST.get("sod"))
                pot = float(request.POST.get("pot"))
                hemo = float(request.POST.get("hemo"))
                pcv = float(request.POST.get("pcv"))
                htn = int(request.POST.get("htn"))
                appet = int(request.POST.get("appet"))
                pe = int(request.POST.get("pe"))
                ane = int(request.POST.get("ane"))
                with open(f'media/scaler.pkl', 'rb') as handle:
                    scaler = pickle.load(handle)
                data = [[age, bp, sg, al, su, rbc, pc, pcc, ba, bgr, bu, sc, sod, pot, hemo, pcv, htn, appet, pe, ane]]
                data = scaler.transform(data)
                model = load_model(f'media/model.h5')

                def save_history(status):
                    history.id = id_
                    history.name = patient.name
                    history.mobile = mobile
                    history.address = patient.address
                    history.age = age
                    history.bp = bp
                    history.sg = sg
                    history.al = al
                    history.su = su
                    history.rbc = rbc
                    history.pc = pc
                    history.pcc = pcc
                    history.ba = ba
                    history.bgr = bgr
                    history.bu = bu
                    history.sc = sc
                    history.sod = sod
                    history.pot = pot
                    history.hemo = hemo
                    history.pcv = pcv
                    history.htn = htn
                    history.appet = appet
                    history.pe = pe
                    history.ane = ane
                    history.result = status
                    history.save(force_insert=True)

                def alert(msg):
                    save_history(msg)
                    raise Exception(msg)

                result = "Health status: Good" if int(
                    (model.predict(data) > 0.5).astype("int32").flatten()[0]) < 1 else alert(
                    "Health status: Chronic Kidney Disease")

                save_history(result)
                message = result
        else:
            return redirect(login)
    except FileNotFoundError:
        class_ = 'danger'
        message = "Error in loading dataset, Try to upload dataset again."
    except Exception as ex:
        class_ = 'danger'
        message = ex
    return render(request, 'patient/prediction.html', {'class': class_, 'message': message})


def history(request):
    if 'plogin' in request.session and request.session['plogin']:
        patients = None
        message = ''
        try:
            if request.method == "POST":
                id_ = str(request.POST.get('id')).strip()
                patient = History.objects.get(id=id_)
                patient.delete()
                message = 'History deleted successfully'
            patients = History.objects.filter(mobile=request.session["pmobile"])
        except Exception as ex:
            message = ex
        return render(request, 'patient/history.html', {'message': message, 'patients': patients})
    else:
        return redirect(login)


def change_password(request):
    if 'plogin' in request.session and request.session['plogin']:
        try:
            message = ''
            if request.method == 'POST':
                mobile = request.session['pmobile']
                patient = Patient.objects.get(mobile=mobile)
                oldpassword = str(request.POST.get('oldpassword')).strip()
                newpassword = str(request.POST.get('newpassword')).strip()
                if patient.password == oldpassword:
                    patient.password = newpassword
                    patient.save(force_update=True)
                    message = 'Password changed successfully'
                else:
                    raise Exception('Password not match')
        except Exception as ex:
            message = ex
        return render(request, 'patient/change_password.html', {'message': message})
    else:
        return redirect(login)
