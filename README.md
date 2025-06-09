# Vonoroi
中山大學 資訊工程學系 碩士班二年級 M103040071 陳啟嘉

主介面
![](https://raw.githubusercontent.com/GasorinP/vonoroi-school-project/master/readme_img/main_view.jpg)

# 軟體規格書
## -輸出與輸入（資料）規格
### 輸入
1. 可用滑鼠在600*600的畫布中隨意點選輸入點
2. 點選 open file 讀取輸入文件

### 輸出
1. 點選 run (or step by step)後，畫布上直接呈現
2. 可點選 save result 儲存計算後結果

## 功能規格與介面規格
1. open file : 讀取輸入點檔案
2. next graph : 若讀取檔案中有多個圖，按此按鈕前進到下一張圖
3. clean : 清空畫布
4. step by step : 按照步驟慢慢呈現演算法執行過程
5. run : 直接輸出演算法執行結果
6. save result : 儲存執行完的結果
7. load result : 讀取執行完的結果
8. 畫布 : 呈現輸入點和演算法執行結果

## 軟體測試規劃書
針對軟體能力測試，將輸入點分為1點、2點、3點、4點、5點、6點、7點和7點以上等數據依序測試

# 軟體說明
請執行 VD_2022_final_exe\dist\start.exe

# 程式設計
## 資料結構
1. Theta : 儲存任兩向量之間的角度
2. Intersection : 儲存任兩條線之間的交點
3. Point : 儲存輸入點
4. Edge : 儲存任兩點連成的線

## 演算法
皆參照教授提供的PPT內容實作

# 軟體測試與實驗結果
## 執行環境
電腦硬體系統 : CPU 12th Gen Intel(R) Core(TM) i5-12400 2.50 GHz， RAM 16.0 GB
作業系統 : Windows
編譯器名稱及版本 : python 3.9.12
## 測試數據(範例)
left graph : 

![](https://raw.githubusercontent.com/GasorinP/vonoroi-school-project/master/readme_img/left_graph.jpg)

right graph : 

![](https://raw.githubusercontent.com/GasorinP/vonoroi-school-project/master/readme_img/right_graph.jpg)

sub hull : 

![](https://raw.githubusercontent.com/GasorinP/vonoroi-school-project/master/readme_img/sub_hull.jpg)

complete hull : 

![](https://raw.githubusercontent.com/GasorinP/vonoroi-school-project/master/readme_img/complete_hull.jpg)

HP :

![](https://raw.githubusercontent.com/GasorinP/vonoroi-school-project/master/readme_img/HP.jpg)

over :

![](https://raw.githubusercontent.com/GasorinP/vonoroi-school-project/master/readme_img/over.jpg)

# 結論與心得
當輸入點多於11點時，有機率發生HP生成錯誤導致結果有誤。初步推斷為設計程式時為了可以輸出到畫面上，在創建Edge時有加上額外的限制，導致在某種情況下此限制會和演算法的計算衝突使得結果有誤。

往後若想完善此軟體，應對實作的方法進行調整，將抽象的概念和實際畫面切割的更明確避免上述問題發生。
