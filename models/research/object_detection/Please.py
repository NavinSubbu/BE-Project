import cv2 as cv
import imutils
import numpy as np
import pytesseract
import string

def static_image_ocr(frame,show_process):
    
    """This Function Extracts Characters from a static image"""

    # image = cv.imread('C:/Users/Navin Subbu/Documents/BEEP/Project/models/research/object_detection/opencv_frame.png',cv.IMREAD_COLOR)
    image = frame.copy()
    cv.imshow('Original Image',image)
    
    
    image = cv.resize(image, (620,480),interpolation = cv.INTER_AREA )
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY) #convert to grey scale
    
    
    gray = cv.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise
    
    
    edge = cv.Canny(gray, 30, 200) #Perform Edge detection
    
    
    """# find contours in the edge image
    contours, hierarchy = cv.findContours(edge,cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE) 
    cv.drawContours(image, contours, -1, (0, 255, 0), 3) 
    cv.imshow('Contours', image) """
    
    
    
    # Retaining only the contour with number plate
    contours = cv.findContours(edge.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key = cv.contourArea, reverse = True)[:10]
    count = None
    
    # loop over our contours
    for c in contours:
     # approximate the contour
     peri = cv.arcLength(c, True)
     approx = cv.approxPolyDP(c, 0.018 * peri, True)
     
     # if our approximated contour has four points, then
     # we can assume that we have found our screen
     if len(approx) == 4:
      count = approx
      break
    
    if count is None:
     detected = 0
     print("No contour detected")
    else:
     detected = 1
    
    if detected == 1:
     cv.drawContours(image, [count], -1, (0, 255, 0), 3)
    
    # Masking the part other than the number plate
    mask = np.zeros(gray.shape,np.uint8)
    new_image = cv.drawContours(mask,[count],0,255,-1,)
    new_image = cv.bitwise_and(image,image,mask=mask)
    
    
    # Now crop
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    Cropped = gray[topx:bottomx+1, topy:bottomy+1]
    # cv.imshow('image',image)
    
     
    if show_process == True :
        cv.imshow('Grayscale Image',gray)
        cv.imshow('Bilateral Filter',gray)
        cv.imshow('Canny Edge Detection',edge)
        cv.imshow('Mask',new_image)
        cv.imshow('Cropped',Cropped)
    
    
    #Read the number plate
    text = pytesseract.image_to_string(Cropped, config='--psm 11')
    print("Detected Number is:",text)
    
    whitelist = string.digits + 'abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    new_s = ''
    for char in text:
        if char in whitelist:
            new_s += char
        else:
            new_s += ''
            
    print(new_s)
    
    
    out = cv.putText(image, text, (200,150), cv.FONT_HERSHEY_SIMPLEX,1, (255,255,255), 2, cv.LINE_AA)
    cv.imshow('Output', out)
    cv.waitKey(0)
    cv.destroyAllWindows()
    return text