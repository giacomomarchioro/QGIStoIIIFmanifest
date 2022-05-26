layers = QgsProject.instance().mapLayers()
cnvXmax,cnvXmin,cnvYmin,cnvYmax = False,False,False,False
# select only the raster layers
raster_layers = [l for lid,l in layers.items() if isinstance(l, QgsRasterLayer)]
# find maximum extent of all the raster layers and the backround layer if any
backgroundlayer = None
bgxmin,bgxmax,bgymin,bgymax = None,None,None,None
for mylayer in raster_layers:
    extent = mylayer.extent()
    if not cnvXmax or cnvXmax < extent.xMaximum():
        cnvXmax = extent.xMaximum()
        bgxmax = True
    if not cnvXmin or cnvXmin > extent.xMinimum():
        cnvXmin = extent.xMinimum()
        bgxmin = True
    if not cnvYmax or cnvYmax < extent.yMaximum():
        cnvYmax = extent.yMaximum()
        bgymax = True
    if not cnvYmin or cnvYmin > extent.yMinimum():
        cnvYmin = extent.yMinimum()
        bgymin = True
    if bgxmax and bgxmin and bgymax and bgymin:
        backgroundlayer = mylayer
    print(mylayer.name())
    print(mylayer.extent())
    print(mylayer.width())
    print(mylayer.height())
    bgxmin,bgxmax,bgymin,bgymax = None,None,None,None

if backgroundlayer is None:
    raise ValueError("Could not find a background layer")

# conversion factor from QGIS units to pixels
bgextent = backgroundlayer.extent()
conversionfactor = backgroundlayer.width()/(bgextent.xMaximum() - bgextent.xMinimum())
bgdata = {}
bgdata['name'] = backgroundlayer.name()
bgdata['source'] = backgroundlayer.source()
bgdata['x'] = round((extent.xMinimum() - bgextent.xMinimum())*conversionfactor)
bgdata['y'] = round((extent.yMaximum() - bgextent.yMaximum())*conversionfactor)
bgdata['width'] = round(extent.width()*conversionfactor)
bgdata['height'] = round(extent.height()*conversionfactor)
bgdata['realheight'] = round(backgroundlayer.height())
bgdata['realwidth'] = round(backgroundlayer.width())
data= {}
for layer in raster_layers:
    if layer is not backgroundlayer:
        data[layer.name()] = {}
        extent = layer.extent()
        data[layer.name()]['source'] = layer.source()
        data[layer.name()]['x'] = round((extent.xMinimum() - bgextent.xMinimum())*conversionfactor)
        data[layer.name()]['y'] = -(round((extent.yMaximum() - bgextent.yMaximum())*conversionfactor))
        data[layer.name()]['width'] = round(extent.width()*conversionfactor)
        data[layer.name()]['height'] = round(extent.height()*conversionfactor)
        data[layer.name()]['realheight'] = round(layer.height())
        data[layer.name()]['realwidth'] = round(layer.width())

rasterdatacontainer = {}
rasterdatacontainer['background'] = bgdata
rasterdatacontainer['data'] = data






polygons_exported = {}
vector_layers = [l for l in QgsProject().instance().mapLayers().values() if isinstance(l, QgsVectorLayer)]
dict_vector_layers = {}

def isRectangle(xy):
    if len(xy) == 5:
        a = xy[0].x() == xy[1].x() and xy[1].y() == xy[2].y() and xy[2].x() == xy[3].x() and xy[3].y() == xy[4].y() 
        b = xy[0].y() == xy[1].y() and xy[1].x() == xy[2].x() and xy[2].y() == xy[3].y() and xy[3].x() == xy[4].x()
        if a or b:
            return True

for layer in vector_layers:
    features = layer.getFeatures()
    featurexy = {}
    for feature in features:
        print(feature)
        geom = feature.geometry()
        attributemap = feature.attributeMap()
        xy = []
        geomtype = "Unknown"
        if geom.type() == QgsWkbTypes.PointGeometry:
            geomtype = "Point"
            for point in geom.vertices():
                print(point.x)
                print(point.y)
                xy.append([point.x()*conversionfactor,-point.y()*conversionfactor])
        if geom.type() == QgsWkbTypes.PolygonGeometry:
            geomtype = "Polygon"
            poligons = geom.asPolygon()
            for pol in poligons:
                if isRectangle(pol):
                    geomtype = "Rectangle"
                    for point in pol:
                        xy.append([point.x()*conversionfactor,-point.y()*conversionfactor])
                else:
                    for point in pol:
                        xy.append([point.x()*conversionfactor,-point.y()*conversionfactor])
                        print(point.x())
                        print(point.y())
        if geom.type() == QgsWkbTypes.LineGeometry:
            geomtype = "Line"
            line = geom.asPolyline()
            for point in line:
                xy.append([point.x()*conversionfactor,-point.y()*conversionfactor])
        # [<QgsPointXY: POINT(165.77115160143694084 -4461.16778909379627294)>, <QgsPointXY: POINT(165.77115160143694084 -3743.32905824344197754)>, <QgsPointXY: POINT(7093.74960050601202965 -3743.32905824344197754)>, <QgsPointXY: POINT(7093.74960050601202965 -4461.16778909379627294)>, <QgsPointXY: POINT(165.77115160143694084 -4461.16778909379627294)>]
        # è un rettangolo se poligons[0] len(poligons)
        featurexy[feature.id()] = {'geomtype':geomtype,'xy':xy,'attribute':attributemap}
        dict_vector_layers[layer.name()] = featurexy

import json
datacontaier = {}
datacontaier['rasters'] = rasterdatacontainer
datacontaier['vectors'] = dict_vector_layers
with open(r'/Users/univr/Documents/QGISIIIF/'+'datacontainer.json', 'w') as outfile:
    json.dump(datacontaier, outfile,indent=3)