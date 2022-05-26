# https://iiif.io/api/cookbook/recipe/0009-book-1/
from IIIFpres import iiifpapi3
import json
iiifpapi3.BASE_URL = "https://qgisexportertest/"
manifest = iiifpapi3.Manifest()
manifest.set_id(extendbase_url="manifest.json")
manifest.add_label("en","Simple Manifest - Book")
manifest.add_behavior("paged")
baseimageurl = r"http://lezioni.meneghetti.univr.it//imageapi/SFMag/"
with open('datacontainer.json') as f: 
   data = json.load(f) 

# test images
a = "http://lezioni.meneghetti.univr.it//imageapi/SFMag/ASVr-SFMag-perg-_-001-_-0001-r-0-aVISPKV-00.jp2/full/max/0/default.jpg"
b = "http://lezioni.meneghetti.univr.it//imageapi/SFMag/ASVr-SFMag-perg-_-001-_-0001-r-0-sUVLPDB-00.jp2/full/max/0/default.jpg"

idx = 0
background = data["rasters"]["background"]
canvas = manifest.add_canvas_to_items()
canvas.set_id(extendbase_url="canvas/p1") # in this case we use the base url
canvas.set_height(background['realheight'])
canvas.set_width(background['realwidth'])
canvas.add_label("en",background['name'])
annopage = canvas.add_annotationpage_to_items()
annopage.set_id(extendbase_url="page/p1/1")
annotation = annopage.add_annotation_to_items(target=canvas.id)
annotation.set_id(extendbase_url="annotation/p%s-image"%str(idx).zfill(4))
annotation.set_motivation("painting")
imageurl =  baseimageurl+ background['source'].split("|")[0].split("/")[-1].replace(".jpeg",".jp2")
annotation.body.set_id(imageurl + "/full/max/0/default.jpg")
annotation.body.set_type("Image")
annotation.body.set_format("image/jpeg")
annotation.body.set_height(background['realheight'])
annotation.body.set_width(background['realwidth'])
s = annotation.body.add_service()
s.set_id(imageurl)
s.set_type("ImageService3")
s.set_profile("level1")
for layername in data['rasters']['data']:
    idx += 1
    obj = data['rasters']['data'][layername]
    fragment = f"#xywh={obj['x']},{obj['y']},{obj['width']},{obj['height']}"
    annotation = annopage.add_annotation_to_items(target=canvas.id+fragment)
    annotation.set_id(extendbase_url="annotation/p%s-image"%str(idx).zfill(4))
    annotation.set_motivation("painting")
    imageurl = baseimageurl + obj['source'].split("|")[0].split("/")[-1].replace(".jpeg",".jp2")
    annotation.body.set_id(imageurl + "/full/max/0/default.jpg")
    annotation.body.set_type("Image")
    annotation.body.set_format("image/jpeg")
    annotation.body.set_height(obj['realheight'])
    annotation.body.set_width(obj['realwidth'])
    s = annotation.body.add_service()
    s.set_id(imageurl)
    s.set_type("ImageService3")
    s.set_profile("level1")

canvasannopage = canvas.add_annotationpage_to_annotations()
canvasannopage.set_id(extendbase_url="page/p2/1")


plygonslayers = 0
for feature in data['vectors']:
    for geometryname,geometryitem in data['vectors'][feature].items():
        print(geometryitem['geomtype'])
        if geometryitem['geomtype'] == 'Polygon' or geometryitem['geomtype'] == 'Line':
            plygonslayers += 1
            d="M" # start the path
            for i in geometryitem['xy']: 
                if d[-1] != "M": 
                    d+="L"
                d+=f"{round(i[0],6)},{round(i[1],6)} "
            d = d.strip()
            svg ="<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><g><path d='%s' /></g></svg>"%d
            annotation2 = canvasannopage.add_annotation_to_items() 
            annotation2.set_motivation("tagging")
            annotation2.set_id(extendbase_url="annotation/p%s-svg" % str(plygonslayers).zfill(4))
            annotation2.body.set_format("text/plain")
            annotation2.body.set_type("TextualBody")
            if 'value' in geometryitem['attribute']:
                annotation2.body.set_value(geometryitem['attribute']['value'])
            annotation2.body.set_language("de")
            annotation2.set_target_specific_resource()
            annotation2.target.set_source(canvas.id)
            annotation2.target.set_selector_as_SvgSelector(value=svg)
        
        if geometryitem['geomtype'] == 'Rectangle':
            plygonslayers += 1
            xys = sorted(geometryitem['xy'])
            width = xys[-1][0] - xys[0][0]
            height = xys[-1][1] - xys[0][1]
            xmin = xys[0][0]
            ymin = xys[0][1]
            roi = f"#xywh={xmin},{ymin},{width},{height}"
            annotation2 = canvasannopage.add_annotation_to_items(target=canvas.id+roi) 
            annotation2.set_motivation("tagging")
            annotation2.set_id(extendbase_url="annotation/p%s-tag" % str(plygonslayers).zfill(4))
            annotation2.body.set_format("text/plain")
            annotation2.body.set_type("TextualBody")
            if 'value' in geometryitem['attribute']:
                annotation2.body.set_value(geometryitem['attribute']['value'])
            annotation2.body.set_language("de")



manifest.json_save("manifesttest.json")    