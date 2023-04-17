UNIVERSAL WRAPPER PIPELINE SETTINGS
===================================

Набор конфигураций для 
[universal wrapper pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline). Для ознакомления
с функционалом pipeline'а можно перейти по
[этой](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) ссылке, ниже будет представлено 
подробное описание непосредственно самого формата
[конфигурационных файлов](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline). 

Конфигурационный файл Universal Wrapper Pipeline должен соответствовать всем
[стандартам yaml-синтаксиса](https://yaml.org/). На каждый wrapper pipeline - один файл (но возможны исключения, при
которых с помощью [регулярных выражений](#пример-1) один конфигурационный файл может конфигурировать несколько копий
wrapper pipeline'ов c разными именами).

# Имена конфигурационных файлов

Файл конфигурации с именем `имя-пайлайна.yaml` и по умолчанию располагаться внутри репозитория по пути `settings/` 
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
конфигурационных файлов внутри репозитория. Можно оставить путь по умолчанию, а список регулярных выражений - пустым,
тогда конфигурационные файлы будут располагаться: `settings/admin_example-pipeline.yaml`,
`settings/devops_example-pipeline.yaml` и `settings/qa_example-pipeline.yaml` соответственно.*

# Основные ключи конфигурационных файлов

- [**parameters**](#ключ-parameters) `[словарь]` *(обязательный, если pipeline параметризованный)* - параметры pipeline.
- [**stages**](#ключ-stages) `[список]` *(обязательный)* - список стадий pipeline.
- [**actions**](#ключ-actions) `[словарь]` *(обязательный)* - описание действий, которые так же могут ссылаться на
  playbook и inventory из ключей [playbooks](#ключ-playbooks) и [inventories](#ключ-inventories), или на скрипт из ключа
  [scripts](#ключ-scripts).
- [**scripts**](#ключ-scripts) `[словарь]` *(необязательный)* - ключ, содержащий скрипты, которые будут запущены при
  выполнении соответствующего action'а.
- [**playbooks**](#ключ-playbooks) `[словарь]` *(необязательный)* - ключ, содержащий ansible playbooks, которые будут
  запущены при выполнении соответствующего action'а.
- [**inventories**](#ключ-inventories) `[словарь]` *(необязательный)* - ключ, содержащий ansible playbooks, которые
  будут запущены при выполнении соответствующего action'а. При наличии ключа playbooks наличие 
  [ключа inventories](#ключ-inventories) и хотя бы одного inventory с именем `default` является обязательным.  

## Ключ parameters

Параметры pipeline делятся на три типа:

  - [**required**](#required) `[список]` - обязательные параметры, без указания которых текущий запуск pipeline
    завершится c ошибкой. Описываются внутри одноименного ключа [required](#required), вложенного в ключ
    [parameters](#ключ-parameters):
```yaml
parameters:
  required:
```
  - [**optional**](#optional) `[список]` - необязательные параметры pipeline, пустые значения которых не приведут ни
    к предупреждениям, ни к остановке выполнения pipeline с ошибкой. Аналогично [**required**](#required) описываются
    внутри одноименного ключа, вложенного в ключ [parameters](#ключ-parameters).
  - **built-in** - "встроенные" параметры: `SETTINGS_GIT_BRANCH`, `NODE_NAME`, `NODE_TAG`, `UPDATE_PARAMETERS`,
    `DRY_RUN`, `DEBUG_MODE`. Эти параметры уже встроены непосредственно в код pipeline (константа 
    `BuiltinPipelineParameters`), задавать их в файле конфигурации не нужно.
  
Если хотя бы один из приведенных в конфигурационном файле параметров pipeline отсутствует в параметрах pipeline в его
настройках, то все параметры pipeline будут заново синхронизированы с параметрами в конфигурационном файле. Сравнение
производится только по именам параметров, тип, значения по умолчанию и другие ключи параметров игнорируются.

Pipeline может не иметь обязательных параметров (ключ [required](#required)) и все параметры могут быть размещены в
[optional](#optional). Так же любой обязательный параметр может стать необязательным и наоборот без перемещения его
в соответствующий словарь (required/optional) за-счет указания дополнительных опций ключа [`on_empty`](#required) (см.
[Пример 2](#пример-2)). Pipeline может так же иметь только необязательные параметры (см. [Пример 4](#пример-4)), или
вовсе их не иметь (непараметризировання сборка).

### required

Ключ [required](#required) находится внутри ключа [parameters](#ключ-parameters) и состоит из списка параметров pipeline
каждый из которых имеет следующие ключи:

- **name** `[строка]` *(обязательный)* - имя параметра pipeline.
- **type** `[строка]` *(обязательный)* - тип параметра, который полностью соответствует типам параметров для jenkins
  pipeline. Варианты: `string` (строковый), `text` (многострочный), `password`, `choice`, `boolean`. Указание типа 
  параметра pipeline является обязательным, хотя в некоторых случаях возможно автоопределение типа с выводом
  соответствующего предупреждения.
- **description** `[строка]` *(необязательный)* - описание параметра pipeline.
- **default** [зависит от `type`] *(необязателен и не совместим с типом параметра choice)* - значение
  параметра pipeline по умолчанию. Если не указан, то значение параметра pipeline по умолчанию будет `false` для 
  *boolean* и пустое поле для строковых (в том числе password) параметров.
- **choices** `[список]` *(совместим только с типом параметров choice)* - опции выбора для choice-параметров. Параметры
  без опций выбора (choices не указан, или пуст) допустимы.
- **trim** `[boolean]` *(совместим только с типом параметров string, но необязателен)* - удалять начальные и конечные
  пробелы в строковом значении параметра. По умолчанию для строк: `false`.
- **on_empty** `[словарь]` *(необязательный)* - опции для управления действий, если параметр при запуске pipeline не 
  указан (пустой) [Пример 2](#пример-2). Содержит следующие вложенные ключи:
    - **assign** `[строка]` *(необязательный)* - имя параметра pipeline'а, значение которого будет присвоено, если
      параметр не указан (пуст). Возможно так же присвоение переменных окружения, а следовательно, переменных Jenkins:
      `NODE_NAME`, `JOB_NAME` и т.д.
    - **fail** `[boolean]` *(необязательный, не совместим с ключом `warn`)* - завершить pipeline с ошибкой, если
      параметр pipeline не указан.
    - **warn** `[boolean]` *(необязательный, не совместим с ключом `fail`)* - вывести предупреждение, но продолжить
      выполнение pipeline'а, если параметр не указан.

  Если параметр pipeline находится внутри [required](#required) и ключ `on_empty` не указан, то по умолчанию пустой
  обязательный параметр завершит pipeline с ошибкой. Таким образом, обязательность параметра можно отменить без
  перемещения его в [optional](#optional).
- **regex** `[строка, или список]` *(необязательный)* - регулярное выражение, или список строк регулярного выражения,
  которые будут объеденины в единую строку для проверки параметра pipeline: если значения параметра не попадает под
  регулярное выражение, текущий запуск pipeline будет остановлен с ошибкой.
- **regex_replace** `[словарь]` *(необязательный)* - опции для управления заменой значений параметров pipeline, которые
  будут произведены при подстановке параметров pipeline'а. Допустим только для строковых (за исключением password)
  параметров. Содержит следующие вложенные ключи:
    - **regex** `[строка]` *(обязательный)* - регулярное значение для поиска заменяемого содержимого параметра.
    - **to** `[строка]` *(необязательный)* - заменить совпадения на указанное в данном ключе содержимое (см. 
      [Пример 3](#пример-3)). Если значение или сам ключ `to` не указан, то все совпадения регулярного выражения в ключе
     `regex` будут удалены.

#### Пример 2

Pipeline содержит три параметра в [ключе required](#required), но только параметр `LOGIN` является обязательным, пропуск
которого завершит выполннение pipeline ошибкой. Если параметры `PASSWORD` не указан, то в консоли появится только
предупреждение и pipeline продолжит выполннение, а если не указан `LOGIN_2`, то будет выдано предупреждение, а значение
будет взято из параметра pipeline'а `LOGIN`.

```yaml
parameters:
  required:
    - name: LOGIN
      type: string
    - name: LOGIN_2
      type: string
      on_empty:
        assign: $LOGIN
        warn: True
    - name: PASSWORD
      type: password
      on_empty:
        warn: True
```

#### Пример 3

Обязательный параметр pipline'а `IP_ADDRESSES`, где в списке пробелы будут заменены на "перевод строки" для подстановки
в ansible inventory:

```yaml
parameters:
  required:
    - name: IP_ADDRESSES
      type: string
      description: Space separated IP or DNS list of the host(s) to perform PIPELINE_ACTION and ROLE_SUBJECT.
      regex_replace:
        regex: ' '
        to: \n
```

### optional

Ключ [optional](#optional) находится внутри ключа [parameters](#ключ-parameters) и состоит из списка необязательных
параметров pipeline. Структура и список ключей аналогична ключу [required](#required) за исключением того, что задавать
здесь значения ключа `on_empty` не нужно, так как они будут проигнорированы.

#### Пример 4

Pipeline содержит только необязательные параметры `ONE` и `TWO`:

```yaml
parameters:
  optional:
    - name: ONE
      type: string
      description: Description of parameter ONE which type is string and default value is 'something'.
      default: something
    - name: ONE
      type: choice
      description: |
        Description of parameter TWO which type is choices.
        TWO parameters includes three choices ('one', 'two' and 'three')
      choices:
        - one
        - two
        - three 
```

## Ключ stages

Список стадий pipeline, каждый элемент которого имеет следующие ключи:

- **name** `[строка]` *(обязательный)* - имя стадии pipeline.
- **parallel** `[boolean]` *(необязательный)* - флаг, установка которого приводит к параллельному запуску списка 
  действий (ключ `actions`) в текущий стадии (см. [Пример 6](#пример-6)).
- **actions** `[список]` *(обязательный)* - список действий в текущей стадии, каждый элемент которого имеет ключи:
  - **before_message** `[строка]` *(необязательный)* - строка сообщения перед началом действия (см. следующий ключ 
    `action`).
  - **action** `[строка]` *(обязательный)* - имя действия, которое задается в ключе [actions](#ключ-actions) файла
    настроек pipeline (см. [ключ actions](#ключ-actions)). Допускается подстановка в качестве значения параметра
    pipeline (см. [Пример 7](#пример-7)).
  - **after_message** `[строка]` *(необязательный)* - строка сообщения по завершению действия, будет выведена вне
    зависимости от результата выполнения (см. [Пример 5](#пример-5)).
  - **fail_message** `[строка]` *(необязательный)* - строка сообщения при неудачном завершении текущего действия.
  - **success_message** `[строка]` *(необязательный)* - строка сообщения при успешном завершении текущего действия.
  - **ignore_fail** `[boolean]` - флаг игнорирования неудачного выполнения текущего действия.
  - **node** `[строка или словарь]` - ключ, определяющий смену jenkins-ноды. Может быть задан строкой и тогда это
    значение будет взято за имя ноды, или же включать в себя ключи:
    - **name** `[строка]` *(обязательный, но не совместим с ключом `label`)* - имя jenkins-ноды.
    - **label** `[строка]` *(обязательный, но не совместим с ключом `name`)* - тэг jenkins-ноды (node label).
    - **pattern** `[boolean]` *(необязательный)* - если флаг включен (`True`), то поиск jenkins-ноды будет осуществлен
      по строке в ключе `name`, или `label` и будет запущен на первой совпавшей с паттерном поиска (см. 
      [Пример 8](#пример-8)). Если флаг выключен, то нода будет выбрана только при полном совпадении имени (`name`), или
      node label (`label`).
  
#### Пример 5

Пример фрагмента конфигурационного файла с описанием `stage_1`, действия в котором имеют свои кастомизированные 
сообщения:

```yaml
stages:
  - name: stage_1
    actions:
      - before_message: Starting 'action_name_1'...
        action: action_name_1
        after_message: Just finished 'action_name_1' execution.
      - before_message: Then starting 'action_name_2'...
        action: action_name_2
        fail_message: A custom message for 'action_name_2' that means it was failed.
        success_message: A custom message for 'action_name_2' that means it was complete without errors.
```

#### Пример 6

Пример фрагмента конфигурационного файла с описанием стадии `stage_name`, действия внутри которого запускаются в 
параллель:

```yaml
  - name: stage_name
    parallel: True
    actions:
      - action: action_name_1
      - action: action_name_2
      - action: action_name_3
```

#### Пример 7

Пример фрагмента конфигурационного файла с описанием переменной `PIPELINE_ACTION` задающей единственное действие в
`stage_name`: 

```yaml
parameters:
  required:
    - name: PIPELINE_ACTION
      type: choice
      description: Action to perform.
      choices:
        - action_one
        - action_two
stages:
  - name: stage_name
    actions:
      - action: $PIPELINE_ACTION
```

#### Пример 8

Пример фрагмента конфигурационного файла с описанием стадии `build_stage` с указанием условий выбора jenkins-node,
которые выводятся сообщением перед запуском действия:

```yaml
stages:
  - name: build_stage
    actions:
      - before_message: Starting build on 'build-x64-node-01.domain.com' jenkins node...
        action: build_action
        node: build-x64-node-01.domain.com
      - before_message: Starting build on any jenkins node name starts with 'build-x64-node-'...
        action: build_action
        node:
          name: build-x64-node-
          pattern: True
      - before_message: Starting build on any jenkins node with label 'build_nodes'...
        action: build_action
        node:
          label: build_nodes
      - before_message: Starting build on any jenkins node with label contains '_nodes'...
        action: build_action
        node:
          label: _nodes
```

## Ключ actions

Описание именованных действий, где каждый вложенный ключ является именем этого действия, а его значения - параметрами
действия:
```yaml
actions:
  action_name_1:
    action_parameter_1: value_1
    action_parameter_2: value_2
```
Тип действия определяется по заданным в нем параметрам-ключам. Поддерживаются действия следующих типов:

- клонирование git исходников,
- установка ansible-коллекции из Ansible Galaxy,
- запуск ansible playbooks,
- запуск скриптов,
- сборка jenkins-артефактов,
- сборка файлов с jenkins node (stash),
- перенос файлов на jenkins node (unstash),
- запуск другого jenkins pipeline,
- отправка уведомлений (email, или mattermost).

Если какое-либо из перечисленных в конфигурационном файле действий не указано ни в одной стадий pipeline'а (или не
передано переменной), то это действие будет проигнорировано.
