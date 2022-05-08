# coleaf: Leaf phenotype investigation

Author | Mengwei Jiang  
Email | mengmengjiang.1105@gmail.com

## Instruction
coleaf is a tool to collect some traits of tea leaves. Such as the leaf area, leaf aspect ratio, leaf shape，trichome number.  
to be continue (2022.3.22)  
it is small and esay to install. you don't have to make a ruler to calculate leaf size. just a mobelphone, an A4 paper and a glass(need larger than paper), you can get the size of obgects in batches quickly.    
to be continue(2022.4.25)  
 
## Dependenies
- python==3.7 
- click 
- opencv==3.4.3  
- numpy  
- plantcv  
- math  
- imutils  
## Install
```
git clone https://github.com/mengmeng-jiang/coleaf.git
export PYTHONPATH=/path/to/coleaf:$PYTHONPATH
chmod +x /path/to/coleaf/bin/*
export PATH=/path/to/coleaf/bin:$PATH
```
## Usage
<kbd>prepare</kbd>  
```bash
coleaf prepare <image_path>   
```
<kbd>leararea</kbd>
```bash
coleaf leafarea <image_path> 
```
<kbd>trichomes</kbd>
```bash
coleaf trichomes <image_path>
```

## test
If the image is a scanned image or a brighter photo, you can use the "-t scanned" option.
```
mkdir ./test/leaf/scannedOut/
coleaf perpare -c ./test/leaf/scanned/ -o ./test/leaf/scannedOut/
coleaf leafarea -t scanned ./test/leaf/scannedOut/
```
If the image is a darker photo, you don't have to specify options,just run it.
```
mkdir ./test/leaf/photoOut/
coleaf prepare -c ./test/leaf/photo/ -o ./test/leaf/photoOut/
coleaf leafarea ./test/leaf/photoOut/
```

## Reference

## Tips
weahther the picture is vertical or horizontal, the crop( coleaf prepare -c ) option output picture will be horizontal. So that you don't need to rorate the picture. It means that length need larger than height, otherwise the picture will be deformed after processing.
### 
when you use the  crop option, it would be better when the contracst between the backgroud color and the A4 paper color is large, such as the white paper with the black background, and make sure the there would be nothing blocks the edgea of the paper, such as the reflection of lamps on glass.  
the output picture name would end with "_" + [c,p,o,r] +".jpg" to imply the previous opetion.   
