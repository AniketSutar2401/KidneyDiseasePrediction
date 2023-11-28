from django.db import models


class Patient(models.Model):
    mobile = models.TextField(primary_key=True)
    name = models.TextField()
    address = models.TextField()
    password = models.TextField()

    class Meta:
        db_table = 'tblPatient'


class History(models.Model):
    id = models.TextField(primary_key=True)
    mobile = models.TextField()
    name = models.TextField()
    address = models.TextField()
    age = models.TextField()
    bp = models.TextField()
    sg = models.TextField()
    al = models.TextField()
    su = models.TextField()
    rbc = models.TextField()
    pc = models.TextField()
    pcc = models.TextField()
    ba = models.TextField()
    bgr = models.TextField()
    bu = models.TextField()
    sc = models.TextField()
    sod = models.TextField()
    pot = models.TextField()
    hemo = models.TextField()
    pcv = models.TextField()
    htn = models.TextField()
    appet = models.TextField()
    pe = models.TextField()
    ane = models.TextField()
    result = models.TextField()

    class Meta:
        db_table = 'tblHistory'
