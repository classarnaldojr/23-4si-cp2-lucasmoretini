import os
import os.path
import cv2

TEMPLATEPAPER = cv2.resize(cv2.imread("photos/paper.png", 0), (0, 0), None, 0.400, 0.400)
TEMPLATESCISSOR = cv2.resize(cv2.imread("photos/scissor.png", 0), (0, 0), None, 0.400, 0.400)
TEMPLATEROCK = cv2.resize(cv2.imread("photos/rock.png", 0), (0, 0), None, 0.400, 0.400)

REVERTTEMPLATEPAPEL = cv2.flip(TEMPLATEPAPER, -1)
REVERTTEMPLATETESOURA = cv2.flip(TEMPLATESCISSOR, -1)
REVERTTEMPLATEPEDRA = cv2.flip(TEMPLATEROCK, -1)

SCISSOR = "TESOURA"
ROCK = "PEDRA"
PAPER = "PAPEL"
MOVENOTIDENTIFY = "Jogada não identificada"

MATCHVALUEPAPER = 0.019
MATCHVALUESCISSOR  = 0.030
MATCHVALUEROCK  = 0.0098

PLAYERLEFT = "Jogador 1"
PLAYERRIGHT = "Jogador 2"

scoreboard = [0, 0]
color = [0, 100, 255]

lastMovePlayLeft = ""
lastMovePlayRight = ""
lastPlayerWin = ""
lastScoreView = ""

def drawInScreen(img, text, origem, color):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, str(text), origem, font,0.7,color,2,cv2.LINE_AA)

def movePlayer(imgGray, imgRgb, templatePaper, templateScissor, templateRock):
    matchPaper = cv2.matchTemplate(imgGray, templatePaper, cv2.TM_SQDIFF_NORMED)
    matchScissor = cv2.matchTemplate(imgGray, templateScissor, cv2.TM_SQDIFF_NORMED)
    matchRock = cv2.matchTemplate(imgGray, templateRock, cv2.TM_SQDIFF_NORMED)

    minMatchValuePaper, _, positionMatchPaper, _ = cv2.minMaxLoc(matchPaper)
    minMatchValueScissor, _, positionMatchScissor, _ = cv2.minMaxLoc(matchScissor)
    minMatchValueRock, _, positionMatchRock, _ = cv2.minMaxLoc(matchRock)

    _, heigthTemplatePapel = templatePaper.shape[::-1]
    _, heigthTemplateTesoura = templateScissor.shape[::-1]
    _, heigthTemplatePedra = templateRock.shape[::-1]
    
    if minMatchValuePaper <MATCHVALUEPAPER:
        drawPosition = (positionMatchPaper[0] , positionMatchPaper[1] + heigthTemplatePapel + 30)
        drawInScreen(imgRgb, PAPER, drawPosition, color)
        return [PAPER, positionMatchPaper]
    elif minMatchValueScissor < MATCHVALUESCISSOR:
        drawPosition = (positionMatchScissor[0] , positionMatchScissor[1] + heigthTemplateTesoura + 30)
        drawInScreen(imgRgb, SCISSOR, drawPosition, color)
        return [SCISSOR, positionMatchScissor]
    elif minMatchValueRock < MATCHVALUEROCK: 
        drawPosition = (positionMatchRock[0] , positionMatchRock[1] + heigthTemplatePedra + 30)
        drawInScreen(imgRgb, ROCK, drawPosition, color)
        return [ROCK, positionMatchRock]
    else:
        return [MOVENOTIDENTIFY, [0, 0]]
    
def newRound(movePlayLeft, movePlayRight):
    global lastMovePlayLeft
    global lastMovePlayRight

    if movePlayLeft != lastMovePlayLeft or movePlayRight != lastMovePlayRight:
        lastMovePlayLeft = movePlayLeft
        lastMovePlayRight = movePlayRight
        return True
    
    return False

def score(movePlayerLeft, movePlayerRight):

    if (movePlayerLeft == SCISSOR and movePlayerRight == PAPER) or \
        (movePlayerLeft == PAPER and movePlayerRight == ROCK) or \
        (movePlayerLeft == ROCK and movePlayerRight == SCISSOR):
        scoreboard[0] += 1
        scoreView = str("Placar: ") + str(scoreboard)
        return  ["JOGADOR 1 VENCEU", scoreView]
    elif (movePlayerLeft == PAPER and movePlayerRight == SCISSOR) or \
        (movePlayerLeft == ROCK and movePlayerRight == PAPER) or \
        (movePlayerLeft == SCISSOR and movePlayerRight == ROCK):
        scoreboard[1] += 1
        scoreView = str("Placar: ") + str(scoreboard)
        return ["JOGADOR 2 VENCEU", scoreView]
    else:
        scoreView = str("Placar: ") + str(scoreboard)
        return ["EMPATE", scoreView]

def image_da_webcam(img):
    global lastPlayerWin
    global lastScoreView

    imgScaled = cv2.resize(img, (0, 0), None, 0.400, 0.400)
    imgGray = cv2.cvtColor(imgScaled, cv2.COLOR_BGR2GRAY)

    imgWidth = imgScaled.shape[1]

    movePlayLeft, matchPositionLeft = movePlayer(imgGray, imgScaled, TEMPLATEPAPER, TEMPLATESCISSOR, TEMPLATEROCK)
    movePlayRight, matchPositionRight = movePlayer(imgGray, imgScaled, REVERTTEMPLATEPAPEL, REVERTTEMPLATETESOURA, REVERTTEMPLATEPEDRA)

    isNewRound = newRound(movePlayLeft, movePlayRight)
        
    if isNewRound:
        playerWin, scoreView = score(movePlayLeft, movePlayRight)
        lastPlayerWin = playerWin
        lastScoreView = scoreView

    drawInScreen(imgScaled, lastScoreView, (int(imgWidth / 2) - 120, 20), color)
    drawInScreen(imgScaled, lastPlayerWin, (int(imgWidth / 2) - 190, 90), color)
    drawInScreen(imgScaled, PLAYERLEFT, (matchPositionLeft[0], (matchPositionLeft[1] - 30)), color)
    drawInScreen(imgScaled, PLAYERRIGHT, (matchPositionRight[0], (matchPositionRight[1] - 30)), color)
        
    return imgScaled

vc = cv2.VideoCapture("videos/pedrapapeltesoura.mp4")

if vc.isOpened():
    rval, frame = vc.read()
else:
    rval = False

while rval:
    
    img = image_da_webcam(frame)

    cv2.imshow("checkpoint02", img)

    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27:
        break

cv2.destroyWindow("checkpoint02")
vc.release()