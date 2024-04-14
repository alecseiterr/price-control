# price-control

## <div align="center">Установка EasyOCR</div>

<details open>
<summary>Установка</summary>


Последний стабилный релиз:

``` bash
pip install easyocr
```

Самые актуальные разработки:

``` bash
pip install git+https://github.com/JaidedAI/EasyOCR.git
```

Примечение 1: При установке в ОС Windows, необходимо сначала установить torch и torchvision в соответствии с официальной инструкцией https://pytorch.org. На сайте pytorch, убедитесь, что вы выбрали правильную версию CUDA. Для запуска на CPU, выберите `CUDA = None`.

Примечение 2: По данной ссылке также доступен Dockerfile [here](https://github.com/JaidedAI/EasyOCR/blob/master/Dockerfile).
</details>

## <div align="center">Установка YOLOv8</div>

Ниже представлена краткая инструкция по установке. Полная документация доступна по ссылке [YOLOv8 Docs](https://docs.ultralytics.com).

<details open>
<summary>Установка</summary>

Pip установит все необходимые ultralytics пакеты включая [requirements](https://github.com/ultralytics/ultralytics/blob/main/pyproject.toml) в [**Python>=3.8**](https://www.python.org/) окружение с  [**PyTorch>=1.8**](https://pytorch.org/get-started/locally/).

[![PyPI version](https://badge.fury.io/py/ultralytics.svg)](https://badge.fury.io/py/ultralytics) [![Downloads](https://static.pepy.tech/badge/ultralytics)](https://pepy.tech/project/ultralytics)

```bash
pip install ultralytics
```

Альтернативные методы установки включают [Conda](https://anaconda.org/conda-forge/ultralytics), [Docker](https://hub.docker.com/r/ultralytics/ultralytics), и Git. Пожалуйста, ищите более подробную информацию здесь - [Инструкция по быстрой установке](https://docs.ultralytics.com/quickstart).

</details>
