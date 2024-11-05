from pdf2image import convert_from_path

from PIL import Image
Image.MAX_IMAGE_PIXELS = 1000000000

images = convert_from_path('C:\\Projects\\GBS_project\\GBS_EE\\SPAIN_POE\\429120.pdf',poppler_path = r"C:\\poppler-24.02.0\\Library\\bin")

for i in range(len(images)):
    images[i].save('C:\\Projects\\GBS_project\\GBS_EE\\images\\page'+str(i)+'.jpg','JPEG')