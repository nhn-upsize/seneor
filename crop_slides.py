import fitz

doc = fitz.open(r'C:\Users\NHN\Documents\sensortower_api\MobileGame_Executive_Report_2026.pdf')

page5 = doc[4]
rect = page5.rect
crop5 = fitz.Rect(0, rect.height * 0.12, rect.width, rect.height * 0.45)
mat = fitz.Matrix(2.0, 2.0)
pix = page5.get_pixmap(matrix=mat, clip=crop5)
pix.save(r'C:\Users\NHN\Documents\sensortower_api\slide-exec-05-boxes.jpg')

page6 = doc[5]
crop6 = fitz.Rect(0, rect.height * 0.10, rect.width, rect.height * 0.50)
pix6 = page6.get_pixmap(matrix=mat, clip=crop6)
pix6.save(r'C:\Users\NHN\Documents\sensortower_api\slide-exec-06-cards.jpg')

doc.close()
print('done')
