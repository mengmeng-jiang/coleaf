# coleaf: Leaf phenotype investigation

Author | Mengwei Jiang  
Email | mengmengjiang.1105@gmail.com

## Instruction
coleaf is a tool to collect some traits of tea leaves. Such as the leaf area, leaf aspect ratio, leaf shape，trichome number.
to be continue (2022.3.22)

## Dependenies
- python==3.7 
- click 
- opencv==3.4.3  
- numpy  
- plantcv  
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
## Reference

