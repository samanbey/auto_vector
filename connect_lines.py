# connecting fragmented line segments on current vector layer

import time
import math
import os
from qgis.core import QgsVectorLayer, QgsProject

tureshatar=400 # distance threshold for joining lines in current map units
fokhatar=90 # orientation threshold in degrees

uj_reteg = QgsVectorLayer("MultiLineString", "osszekotott", "memory")
from qgis.PyQt.QtCore import QVariant
pr = uj_reteg.dataProvider()
pr.addAttributes([QgsField("id",  QVariant.Int)])
uj_reteg.updateFields() 

layer = iface.activeLayer()
feats = [feat for feat in layer.getFeatures()]

temp_reteg = QgsVectorLayer("MultiLineString", "temp", "memory")
temp_pr = temp_reteg.dataProvider()
temp_pr.addFeatures(feats)
temp_reteg.updateExtents()

start_time = time.clock()

                    #első-utolsó
                    
count=0
volt_modositas=True
while volt_modositas:
    volt_modositas=False
    feats = [feat for feat in temp_reteg.getFeatures()]
    count+=1
    temp_pr.truncate() 
    temp_reteg.updateExtents()
    for f1 in feats: 
        for f2 in feats:
            poly1=f1.geometry().asMultiPolyline()
            elso1 = poly1[0][0]
            poly2=f2.geometry().asMultiPolyline()
            elso2 = poly2[0][0]
            if elso1!=elso2:     
                utolso2 = poly2[0][-1]
                masodik1 = poly1[0][1]
                ut_elott2 = poly2[0][-2]
                els_ut_tav=elso1.distance(utolso2)             
                if els_ut_tav<tureshatar:
                    poly_uj=[]
                    azi1=elso1.azimuth(masodik1)
                    azi2=ut_elott2.azimuth(utolso2)
                    elteres=abs(azi1-azi2)
                    if elteres<fokhatar:
                        try:
                            feats.remove(f2)         
                            feats.remove(f1)
                        except:
                            continue                      
                        poly_uj=poly2[0]+poly1[0]
                        multi_poly_uj=[poly_uj]
                        feature_uj=QgsFeature()
                        feature_uj.setGeometry(QgsGeometry.fromMultiPolylineXY(multi_poly_uj))
                        feats.append(feature_uj)
                        volt_modositas=True
                        continue
    temp_pr.addFeatures(feats)
    temp_reteg.updateExtents()  

                    #első-első    
    
volt_modositas=True
count=0
while volt_modositas:
    volt_modositas=False
    feats = [feat for feat in temp_reteg.getFeatures()]
    count+=1
    temp_pr.truncate() 
    temp_reteg.updateExtents()
    for f1 in feats: 
        for f2 in feats:
            poly1=f1.geometry().asMultiPolyline()
            elso1 = poly1[0][0]
            poly2=f2.geometry().asMultiPolyline()
            elso2 = poly2[0][0]
            if elso1!=elso2:     
                masodik1 = poly1[0][1]
                masodik2 = poly2[0][1]
                els_els_tav=elso1.distance(elso2) 
                if els_els_tav<tureshatar:
                    poly_uj=[]
                    azi1=elso1.azimuth(masodik1)
                    azi2=masodik2.azimuth(elso2)
                    elteres=abs(azi1-azi2)
                    if elteres<fokhatar:
                        try:
                            feats.remove(f2)         
                            feats.remove(f1)
                        except:
                            continue                      
                        poly_uj=poly2[0][::-1]+poly1[0]
                        multi_poly_uj=[poly_uj]
                        feature_uj=QgsFeature()
                        feature_uj.setGeometry(QgsGeometry.fromMultiPolylineXY(multi_poly_uj))
                        feats.append(feature_uj)
                        volt_modositas=True
                        continue        
    temp_pr.addFeatures(feats)
    temp_reteg.updateExtents()    

                    #utolsó-utolsó  
                    
count=0
volt_modositas=True
while volt_modositas:
    volt_modositas=False
    feats = [feat for feat in temp_reteg.getFeatures()]
    count+=1
    temp_pr.truncate() 
    temp_reteg.updateExtents()
    for f1 in feats: 
        for f2 in feats:
            poly1=f1.geometry().asMultiPolyline()
            utolso1 = poly1[0][-1]
            poly2=f2.geometry().asMultiPolyline()
            utolso2 = poly2[0][-1]
            if utolso1!=utolso2:    
                ut_elott1 = poly1[0][-2]
                ut_elott2 = poly2[0][-2]
                ut_ut_tav=utolso1.distance(utolso2) 
                if ut_ut_tav<tureshatar:
                    poly_uj=[]
                    azi1=utolso1.azimuth(ut_elott1)
                    azi2=ut_elott2.azimuth(utolso2)
                    elteres=abs(azi1-azi2)
                    if elteres<fokhatar:
                        try:
                            feats.remove(f2)         
                            feats.remove(f1)
                        except:
                            continue                         
                        poly_uj=poly2[0]+poly1[0][::-1]
                        multi_poly_uj=[poly_uj]
                        feature_uj=QgsFeature()
                        feature_uj.setGeometry(QgsGeometry.fromMultiPolylineXY(multi_poly_uj))
                        feats.append(feature_uj)
                        volt_modositas=True
                        continue 
                        
    temp_pr.addFeatures(feats)
    temp_reteg.updateExtents()    
    
                    #kiírja az új rétegre

for feat in feats:
    pr.addFeature(feat)
uj_reteg.updateExtents()                     
QgsProject.instance().addMapLayer(uj_reteg)

print("vége") 
print ("\n",  time.clock() - start_time, "másodperc futásidő") 
if time.clock() - start_time >=60:
    print (str(math.floor(time.clock() - start_time)/60) + " perc")


#hiba: ha egy vonalszakaszt kettőhöz is hozzá tudna kötni:
#összeköti az elsővel, hozzáadja, majd kitörli az eredeti két szakaszt
#ezután már nem találja az eredetit amikor a másodikkal is össze akarja kötni 
#elágazásnál jöhet elő, illetve ha vonalhossz+hézag<tűréshatár
#első közelítésben átugorja ha ilyet talál

#hiba: ha túl nagy a tűréshatár, egymással párhuzamos vonalakat keresztbe köt össze
#tűréshatár beállítása a vonalak sűrűségétől függ


