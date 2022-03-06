# TeaImaging

author | Mengwei Jiang  
Email | mengmengjiang.1105@gmail.com

## Instruction
Tealmaging is a tool to collect some traits of tea leaves. Such as the leaf area, leaf aspect ratio, leaf shape，trichome number.
to be continue (2022.3.6)

## Dependenies
- python==3.7  
- opencv==3.4.3  
- numpy  
- plantcv  
## Install
```
git clone https://github.com/mengmeng-jiang/TeaImaging.git
cd TeaImaging
```
## Usage
- lear area
```python
#for the image scanned with iphone
python leaf_area.py <image> <image_name>

#for the original image taken by mobile phone
python python leaf_area_original.py <image> <image_name> <image> <image_name>
```
- trichome counter
```python
python trichome_counter.py <image> <image_name>
```
## Reference

