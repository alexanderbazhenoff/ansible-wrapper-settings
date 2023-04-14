UNIVERSAL WRAPPER PIPELINE SETTINGS
===================================

Набор конфигураций для 
[universal wrapper pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline). Для ознакомления
с функционалом pipeline'а можно перейти по
[этой](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) ссылке, ниже будет представлено 
подробное описание непосредственно самого формата
[конфигурационных файлов](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline). 

# Структура конфигурационных файлов

Конфигурационный файл Universal Wrapper Pipeline должен соответствовать всем
[стандартам yaml-синтаксиса](https://yaml.org/). На каждый wrapper pipeline - один файл (но возможны исключения, при
которых с помощью [регулярных выражений](#пример-1) один конфигурационный файл может конфигурировать несколько копий
wrapper pipeline'ов c разными именами).

## Имена конфигурационных файлов

Файл конфигурации с именем `имя-пайлайна.yaml` и по-умолчанию располагаться внутри репозитория по пути `settings/` 
(можно задать константой pipeline'а `PipelineNameRegexReplace`). В имени pipeline'а допускаются всевозможные префиксы и
постфиксы, а для их удаления и приведения к соответствию к имени конфигурационного файла есть константа pipeline'а 
`PipelineNameRegexReplace`, содержащая список регулярных выражений, совпадения из которого будут удалены из имени 
pipeline'а при формировании имени конфигурационного файла.

#### Пример 1

Константа в pipeline имеет следующее значение:
```groovy
final PipelineNameRegexReplace = ['^(admin|devops|qa)_'] as ArrayList
```
Следовательно, pipeline'ы с именами:
`admin_example-pipeline`, `devops_example-pipeline` и `qa_example-pipeline` будут ссылаться на один и тот же
конфигурационный файл `example-pipeline.yaml`.

*Регулярные выражения и задание пути внутри репозитория предназначены исключительно для упрощения структуризации
конфигурационных файлов внутри репозитория. Можно оставить путь по-умолчанию, а список регулярных выражений - пустым,
тогда конфигурационные файлы будут располагаться: `settings/admin_example-pipeline.yaml`,
`settings/devops_example-pipeline.yaml` и `settings/qa_example-pipeline.yaml` соответственно.*

## Основные ключи конфигурационных файлов

