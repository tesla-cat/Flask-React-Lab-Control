
from QubitEBLdesign import *

def part():
  # config from top to bottom
  markerDistX = 12
  markerVmarkerLDist = 7
  resonatorMarkerVdist = 20
  qubitResonatorDist = 1
  resonatorLength = 20
  qubitClengths = [1, 4e-1, 8e-2, 1e-2]
  testqubitClengths = [2e-1, 4e-1, 8e-2, 1e-2]
  qubitTestQubitDist = 4
  testQubitMarkerLDist = 2
  # calculation
  resonatorTranslateY = np.sum(qubitClengths) + qubitResonatorDist + resonatorLength/2
  markerVtranslateY = resonatorTranslateY + resonatorLength/2 + resonatorMarkerVdist
  markerLtranslateY = markerVtranslateY + markerVmarkerLDist
  testQubitSpacing = markerDistX / 4
  testQubitTranslateY = np.sum(qubitClengths) + np.sum(testqubitClengths) + qubitTestQubitDist
  # group1 parts
  p1 = qubitC(qubitClengths)
  p2 = qubitJJ()
  p3 = resonator().translate(0, resonatorTranslateY)
  p4a = markerV().rotate(0 ).translate(-markerDistX/2, markerVtranslateY)
  p4b = markerV().rotate(pi).translate( markerDistX/2, markerVtranslateY)
  p5a = markerL().rotate(0    ).translate(-markerDistX/2, markerLtranslateY)
  p5b = markerL().rotate(-pi/2).translate( markerDistX/2, markerLtranslateY)
  group1 = p1 + p2 + [p3, p4a, p4b, p5a, p5b]
  # group2 parts
  def qubit():
    return qubitC(testqubitClengths, useJump=False) + qubitJJ()
  p1a = [x.translate(-testQubitSpacing*1.5, -testQubitTranslateY) for x in qubit()]
  p1b = [x.translate(-testQubitSpacing*0.5, -testQubitTranslateY) for x in qubit()]
  p1c = [x.translate( testQubitSpacing*0.5, -testQubitTranslateY) for x in qubit()]
  p1d = [x.translate( testQubitSpacing*1.5, -testQubitTranslateY) for x in qubit()]
  p2a = markerL().rotate(0    ).translate(-markerDistX/2, -testQubitTranslateY + testQubitMarkerLDist)
  p2b = markerL().rotate(-pi/2).translate( markerDistX/2, -testQubitTranslateY + testQubitMarkerLDist)
  p2c = markerL().rotate(pi/2 ).translate(-markerDistX/2, -testQubitTranslateY - testQubitMarkerLDist)
  p2d = markerL().rotate(pi   ).translate( markerDistX/2, -testQubitTranslateY - testQubitMarkerLDist)
  group2 = p1a+p1b+p1c+p1d + [p2a,p2b,p2c,p2d]
  return group1 + group2

if __name__ == '__main__':
  generate(part)