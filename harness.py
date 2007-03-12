import tiff, jpeg

#t = tiff.Tiff("/home/pieter/tmp/Foto2/test.tif")
#t.writeFile("/home/pieter/tmp/Foto2/test2.tif")
j = jpeg.JPEG("/home/pieter/tmp/Foto2/test.jpg")
j.writeFile("/home/pieter/tmp/Foto2/test2.jpg")
