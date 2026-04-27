import fitz

doc = fitz.open(r'C:\Users\NHN\Documents\sensortower_api\MobileGame_Market_Analysis_2022-2026_v3.pdf')

# Slide 18: zoom into chart legend
page18 = doc[17]
rect = page18.rect
crop18_legend = fitz.Rect(rect.width * 0.02, rect.height * 0.12, rect.width * 0.55, rect.height * 0.42)
mat25 = fitz.Matrix(2.5, 2.5)
pix = page18.get_pixmap(matrix=mat25, clip=crop18_legend)
pix.save(r'C:\Users\NHN\Documents\sensortower_api\slide-v3-18-legend.jpg')

# Slide 23: zoom into the country bar panel (left side)
page23 = doc[22]
crop23 = fitz.Rect(0, rect.height * 0.05, rect.width * 0.52, rect.height * 0.90)
mat20 = fitz.Matrix(2.0, 2.0)
pix23 = page23.get_pixmap(matrix=mat20, clip=crop23)
pix23.save(r'C:\Users\NHN\Documents\sensortower_api\slide-v3-23-country.jpg')

# Slide 24: zoom into the country bar panel (left side)
page24 = doc[23]
crop24 = fitz.Rect(0, rect.height * 0.05, rect.width * 0.52, rect.height * 0.90)
pix24 = page24.get_pixmap(matrix=mat20, clip=crop24)
pix24.save(r'C:\Users\NHN\Documents\sensortower_api\slide-v3-24-country.jpg')

doc.close()
print('done')
