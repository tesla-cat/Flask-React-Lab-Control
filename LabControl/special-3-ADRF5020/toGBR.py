
import os, sys

folder = r'C:\Users\e0134117\Desktop\ADRF5020\ADRF5020-ADRF5021-Gerbers'

for filename in os.listdir(folder):
  infilename = os.path.join(folder, filename)
  if not os.path.isfile(infilename): continue
  oldbase = os.path.splitext(filename)
  newname = infilename.replace('.pho', '.gbr')
  output = os.rename(infilename, newname)