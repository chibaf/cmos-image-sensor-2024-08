##### モジュール #####
import io
import time
import numpy as np
import picamera2
camera = picamera2.Picamera2()

##### カメラ設定の値 #####
ISOpr = 100  # プレビュー用ISO感度 カメラ・モジュール V1
ISO = 100    # キャプチャ用ISO感度(最小値) カメラ・モジュール V1
Fps = 10    # フレーム・レート [fps]

##### キャプチャの条件設定 #####
Nexp = 100      # 蓄積時間を100ポイント振る
Rexp = 10       # 最大蓄積時間の対AE蓄積時間比率
ROIsize = 100   # 信号を取得する画素ブロックのサイズ

##### 画像のフォーマット関係の値 #####
ImSize = (1944, 2592)                           # 画像のサイズ (行数, 列数) カメラ・モジュール V1
Dummy = (8, 24)                                # Dummy (行数, 列数) カメラ・モジュール V1
ByPx = (5, 4)                                   # Byte per Pixel (Byte, Pixel)
Crop = (ImSize[0], int(ImSize[1]/4*5))          # Rawデータの行列サイズ，ダミーなし
Shape = (Crop[0]+Dummy[0], Crop[1]+Dummy[1])    # Rawデータの行列サイズ，ダミーあり
Shft = int(8/ByPx[1])                           # ビットシフト幅

##### 開始 #####
print("[ 応答曲線 ]")
#print("  イメージセンサ =", camera.exif_tags['IFD0.Model'])  # イメージセンサのタイプを表示

##### プレビューのカメラ設定(フレーム・レート，ISO感度) #####
camera.framerate = Fps  # フレーム・レートは標準設定値30fpsのまま
camera.iso = ISOpr  # ISO感度設定

##### プレビュー #####
camera.resolution = (int(ImSize[1]/2), int(ImSize[0]/2))    # HVとも半分(GPUメモリ・サイズ制限のため)
camera.preview_fullscreen = False                           # プレビューの画角制限
camera.preview_window = (0, 0, 640, 480)                    # プレビュー画角の大きさ
camera.start_preview()                                      # プレビュー・スタート
time.sleep(3)                                               # 蓄積時間の安定化時間
print("\nプレビュー")
print("  フレームレート =", camera.framerate, " [fps]")
print("  ISO感度 =", camera.iso)
#print("  AE蓄積時間 =", camera.exposure_speed, " [us]")
input('  改行を押してキャプチャ開始 >')
camera.stop_preview()                                       # プレビュー・ストップ

##### 蓄積時間の自動調整(AE)解除とISO感度の設定およびその表示 #####
camera.shutter_speed = camera.framerate    # AE状態蓄積時間のコピー
camera.exposure_mode = 'off'                    # 蓄積時間の固定化
AutoExpSpeed = camera.shutter_speed             # AE状態蓄積時間の記憶
camera.iso = ISO                                # ISO感度
print("\nキャプチャ開始")
print("  フレームレート =", camera.framerate, " [fps]")
print("  ISO感度 =", camera.iso)
print("  AE蓄積時間 =", camera.shutter_speed, " [us]")

##### 関数定義：キャプチャのバイナリ・ストリームを2次元配列Rawデータに変換 #####
def Strm2Img(strm):
    data = strm.getvalue()[-int(Shape[0]*Shape[1]):]
    data = np.frombuffer(data, dtype=np.uint8)
    data = data.reshape((Shape[0], Shape[1]))[:Crop[0], :Crop[1]]
    data = data.astype(np.uint16) << Shft
    img = np.zeros(ImSize)
    for byte in range(ByPx[1]):
        img[:,byte::ByPx[1]] = data[:,byte::ByPx[0]] | \
                               ((data[:,ByPx[1]::ByPx[0]]>>((byte+1)*2)) & (2**Shft-1))
    return img

##### キャプチャとSig, Var計算 #####
Sig = np.zeros([Nexp, 5])                               # 蓄積時間，信号を保存する配列
ROI = [int(ImSize[0]/2)-ROIsize, int(ImSize[1]/2)-ROIsize, \
       ROIsize*2, ROIsize*2]                            # 画角中央の画素ブロックをROI
for i in range(Nexp):
    camera.shutter_speed = int(i/Nexp*Rexp*AutoExpSpeed)+1  # 蓄積時間振り
    print("  蓄積時間振り =", i+1, ", 蓄積時間 =", camera.shutter_speed, " [us]")
    stream = io.BytesIO()                               # 入出力バイナリ・ストリームからメモリへ
    camera.start_and_capture_file("test.jpg")   # Rawデータ付きJPEG画像のキャプチャ
    raw = Strm2Img(stream)                              # 2次元配列に変換
    Sig[i, 0] = camera.shutter_speed                        # 蓄積時間
    Sig[i, 1] = np.mean(raw[ROI[0]  :ROI[0]+ROI[2]  :2, \
                            ROI[1]  :ROI[1]+ROI[3]  :2])    # B画素
    Sig[i, 2] = np.mean(raw[ROI[0]  :ROI[0]+ROI[2]  :2, \
                            ROI[1]+1:ROI[1]+ROI[3]+1:2])    # Gb画素
    Sig[i, 3] = np.mean(raw[ROI[0]+1:ROI[0]+ROI[2]+1:2, \
                            ROI[1]  :ROI[1]+ROI[3]  :2])    # Gr画素
    Sig[i, 4] = np.mean(raw[ROI[0]+1:ROI[0]+ROI[2]+1:2, \
                            ROI[1]+1:ROI[1]+ROI[3]+1:2])    # R画素

##### 測定結果の保存 #####
np.savetxt('Resp.csv', Sig, delimiter=',')
