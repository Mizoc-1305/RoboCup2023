import sensor, time, math, pyb, ustruct, image
from pyb import UART

uart = UART(3, 4800)

led_R = pyb.LED(1)
led_G = pyb.LED(2)
led_B = pyb.LED(3)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()


thresholds_resqKit_binary = (5, 40, -10, 20, -40, -10)
thresholds_resqKit = [(3, 100, -128, 127, -128, 127)]
thresholds_victim = (41, 98, -128, 127, -128, 127)
thresholds_marker = [(15, 90, -100, -35, -90, 75)]

area_flag = 0 #ラインエリア:0, レスキューエリア:1


while(True):
    led_R.on()
    led_G.on()
    led_B.on()
    clock.tick()
    detected_flag = 0
    img = sensor.snapshot()
    img.rotation_corr(0, 0, 180)#上下反転

    if area_flag == 0:
        img.binary([thresholds_resqKit_binary])
        for blob in img.find_blobs(thresholds_resqKit, pixels_threshold=2500, area_threshold=2500): #ここの値でピクセル数、面積の閾値を指定する
            detected_flag = detected_flag + 0b0001
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            img.draw_string(blob.cx(), blob.cy(), "Resque Kit", color=(255,0,0), scale=1)
            # Note - the blob rotation is unique to 0-180 only.
            img.draw_keypoints([(blob.cx(), blob.cy(), int(math.degrees(blob.rotation())))], size=20)
            corner_tuple = blob.min_corners()
            print(corner_tuple)
            deteted_flag = 1
            #if blob.cx() >= 0 and blob.cx() < 100 :
            #    print("Rescue Kit position is RIGHT.")
            #    detected_flag = 3
            #elif blob.cx() >= 100 and blob.cx() < 150 :
            #    print("Rescue Kit position is CENTER.")
            #    detected_flag = 2
            #elif blob.cx() >= 150 and blob.cx() <= 320 :
            #    print("Rescue Kit position is LEFT.")
            #    detected_flag = 1

 #マーカー検出の部分をコメントアウト中
 #       for blob in img.find_blobs(thresholds_marker, pixels_threshold=200, area_threshold=200):
 #           detected_flag = detected_flag + 0b0010
 #           img.draw_rectangle(blob.rect())
 #           img.draw_cross(blob.cx(), blob.cy())
 #           img.draw_string(blob.cx(), blob.cy(), "Marker", color=(0,255,0), scale=3)
 #           # Note - the blob rotation is unique to 0-180 only.
 #           img.draw_keypoints([(blob.cx(), blob.cy(), int(math.degrees(blob.rotation())))], size=20)
 #           corner_tuple = blob.min_corners()
 #           print(corner_tuple)

    elif area_flag == 1:
        sensor.set_framesize(sensor.QQVGA)
        img.binary([thresholds_victim])
        for c in img.find_circles(threshold = 3800, x_margin = 10, y_margin = 10, r_margin = 10, r_min = 30, r_max = 80, r_step = 2):
            img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))
            img.draw_string(c.x(), c.y(), "Victim", color=(0,0,255), scale=1)
            detected_flag = 0b0100
            print(c)

    tx_data = detected_flag
    try:
        uart.write(ustruct.pack('B', detected_flag))
        print("Transmited.")
        time.sleep_ms(100)
    except OSError as err:
        pass

