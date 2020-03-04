# color filter on current raster layer
# outputs new raster layer with one band 0(nodata)/1 raster

from osgeo import gdal, osr
import numpy
import time

t0=time.clock()

def main():
    # kiemelendő színek - ez most a kék
    C=[[135,157,166],[142,162,165],[144,165,169],[154,171,172],[171,186,180],[176,187,178],[130,154,160],[104,126,126],[93,114,101]]
    # nem kell színek
    NC=[[158,131,103],[79,74,68],[230,221,196],[166,182,137],[214,201,178],[159,154,142],[185,183,164],[176,188,142],[96,83,129],[142,110,155],[166,171,156],[120,121,97]]

    # layer
    # legyen az rgb kép kiválasztva!
    l=iface.activeLayer()
    # check layer type
    if (l.type()!=QgsMapLayerType.RasterLayer):
        print('Active layer is not a raster layer!')
        return

    # raster data provider
    dp=l.dataProvider()
    # check for the 3 bands
    if dp.bandCount()<3:
        print('Raster layer with 3 bands required!')
        return

    # image dimensions
    w=dp.xSize()
    h=dp.ySize()

    # red, green, blue channel as raster block
    r=dp.block(1,l.extent(),w,h)
    g=dp.block(2,l.extent(),w,h)
    b=dp.block(3,l.extent(),w,h)

    # channel data as byte array
    rd=r.data()
    gd=g.data()
    bd=b.data()

    # GDAL geotiff driver
    gtd=gdal.GetDriverByName('GTiff')
    fn="d:/geodata/vektorizalas/kek_nagy.tif" # TODO: memory raster?
    # 1 sávos byte-os geotiff létrehozása
    ds=gtd.Create(fn,w,h,1,1)

    # array for new bitmap
    data=numpy.zeros((h,w))

    # dict a már eldöntött színeknek
    CD={}

    for x in range(w):
        for y in range(h):
            RGB=rd[x+y*w]+gd[x+y*w]+bd[x+y*w]
            if RGB in CD:
                c=CD[RGB]
            else:
                R=ord(rd[x+y*w])
                G=ord(gd[x+y*w])
                B=ord(bd[x+y*w])
                # megnézzük, hogy mekkora a színtávolság a C és az NC színektől
                c=0
                cd=255*255
                for s in C:
                    d=(R-s[0])*(R-s[0])+(G-s[1])*(G-s[1])+(B-s[2])*(B-s[2])
                    if cd>d:
                        cd=d
                ncd=255*255
                for s in NC:
                    d=(R-s[0])*(R-s[0])+(G-s[1])*(G-s[1])+(B-s[2])*(B-s[2])
                    if ncd>d:
                        ncd=d
                # Ha inkább C, akkor egy, ha inkáb NC, akkor 0
                if cd<ncd:
                    c=1
                CD[RGB]=c
            data[y][x]=c
    t1=time.clock()
    print("Elapsed time so far: "+str(t1-t0))
    # fill small holes/delete small dots
    for y in range(1,h-1):
        s1=sum(data[y+i][x-1] for i in range(-1,2))
        s2=sum(data[y+i][x] for i in range(-1,2))
        for x in range(1,w-1):
            s3=sum(data[y+i][x+1] for i in range(-1,2))
            s=s1+s2+s3
            if s>=7:
                data[y][x]=1
            if s<=2:
                data[y][x]=0
            s1=s2
            s2=s3
    # save
    rb=ds.GetRasterBand(1)
    rb.SetNoDataValue(0)
    rb.WriteArray(data)
    ext=dp.extent()
    # meters per pixel for geo transform (extent width per image width)
    xmpp=ext.width()/w
    ympp=ext.height()/h
    ds.SetGeoTransform([ext.xMinimum(),xmpp,0,ext.yMaximum(),0,-ympp]) # TODO: kiolvasni a layerből ezeket.
    ds.SetProjection(dp.crs().toWkt())

    ds=None # gondolom ez kell ahhoz, hogy létrehozza, és bezárja a fájlt
    iface.addRasterLayer(fn)
    
main()
t1=time.clock()
print("Elapsed time: "+str(t1-t0))
