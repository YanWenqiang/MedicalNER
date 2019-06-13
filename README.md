## 医疗命名实体识别项目
使用sklearn_crf工具包，识别身体部位(body)以及疾病(disease)两类实体，其中crf_suite_model.m 是训练好的模型。

### 测试结果：
> f1:  0.885
>
>  entity-level accuracy:  0.891
> 
> sentence-level accuracy:  0.925

||precision|recall|f1-score|support|
|---|---|---|---|---|
|B-Body|0.877|0.856|0.866|6015|
|I-Body|0.823|0.826|0.825|5277|
|B-Disease|0.887|0.902|0.894|10704|
|I-Disease|0.888 |0.909 |0.898|24062|
|micro avg|0.879|0.891|0.885|46058|
|macro avg|0.869|0.873|0.871|46058|
|weighted avg|0.879|0.891|0.885|46058|


### 使用方法：
> 1.单句预测
```sh
python predict.py 
我肚子好痛
我[肚子]{Body}好痛
```
> 2.批量预测
```sh
python predict.py --input=/path/to/inputfile --output=/path/to/outputfile
```