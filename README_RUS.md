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

Конфигурационный файл состоит из нескольких ключей, каждый из которых делит его на несколько "секций":

```yaml
---

parameters:
  # ...
stages:
  # ...
actions:
  # ...
scripts:
  # ...
playbooks:
  # ...
inventories:
  # ...
```

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

Ключ содержит параметры pipeline, которые в свою очередь делятся на три типа:

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

```yaml
# Pipeline содержит три параметра в ключе `required`, но только параметр `LOGIN` является обязательным, пропуск которого
# завершит выполннение pipeline ошибкой. Если параметры `PASSWORD` не указан, то в консоли появится только 
# предупреждение и pipeline продолжит выполннение, а если не указан `LOGIN_2`, то будет выдано предупреждение, а
# значение будет взято из параметра pipeline'а `LOGIN`.

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

```yaml
# Фрагмент конфигурационного файла c обязательным параметром pipline'а `IP_ADDRESSES`, где пробелы будут заменены на
# "перевод строки" для подстановки в ansible inventory.

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

```yaml
# Фрагмент конфигурационного файла pipeline'а содержащего только необязательные параметры `ONE` и `TWO`.

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

Ключ содержит список стадий pipeline, каждый элемент которого имеет следующие ключи:

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
  - **node** `[строка или словарь]` - ключ, определяющий смену node (например, jenkins-ноды для jenkins). Может быть
    задан строкой и тогда это значение будет взято за имя ноды, или же включать в себя ключи:
    - **name** `[строка]` *(обязательный, но не совместим с ключом `label`)* - имя node.
    - **label** `[строка]` *(обязательный, но не совместим с ключом `name`)* - тэг node (node label).
    - **pattern** `[boolean]` *(необязательный)* - если флаг включен (`True`), то поиск jenkins-ноды будет осуществлен
      по строке в ключе `name`, или `label` и будет запущен на первой совпавшей с паттерном поиска (см. 
      [Пример 8](#пример-8)). Если флаг выключен, то нода будет выбрана только при полном совпадении имени (`name`), или
      node label (`label`).
  
#### Пример 5

```yaml
# Фрагмента конфигурационного файла с описанием `stage_1`, действия в котором имеют кастомизированные сообщения. 

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

```yaml
# Фрагмент конфигурационного файла с описанием стадии `stage_name`, действия в котором выполняются параллельно.

  - name: stage_name
    parallel: True
    actions:
      - action: action_name_1
      - action: action_name_2
      - action: action_name_3
```

#### Пример 7

```yaml
# Фрагмент конфигурационного файла с переменной pipeline `PIPELINE_ACTION`, задающей имя действия в `stage_name`.

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

```yaml
# Фрагмент конфигурационного файла с описанием стадии `build_stage` с выбором node (выводится в сообщениях перед
# началом действия - `before_message`)

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

Ключ содержит описание именованных действий, где каждый вложенный ключ является именем этого действия, а его значения -
параметрами действия:

```yaml
actions:
  action_name_1:
    action_parameter_1: value_1
    action_parameter_2: value_2
```
Тип действия определяется по заданным в нем параметрам-ключам. Поддерживаются действия следующих типов:

- [**клонирование исходников (git)**](#action-клонирование-исходников-git),
- [**установка ansible-коллекции из Ansible Galaxy**](#action-установка-ansible-коллекции-из-ansible-galaxy),
- [**запуск ansible playbooks**](#action-запуск-ansible-playbooks),
- [**запуск скриптов**](#action-запуск-скриптов),
- [**сборка файлов-артефактов**](#action-сборка-файлов-артефактов),
- [**сборка файлов с jenkins node (stash)**](#action-сборка-файлов-с-node-stash),
- [**перенос файлов на jenkins node (unstash)**](#action-перенос-файлов-на-node-unstash),
- [**запуск другого downstream pipeline**](#action-запуск-нижележащего-pipeline),
- [**отправка уведомлений**](#action-отправка-уведомлений) (email, или mattermost).

Если какое-либо из перечисленных в ключе `actions` конфигурационного файла действий не указано ни в одной из стадий
в ключе `stages` (или не было передано, если имя действия задано переменной), то это действие будет проигнорировано.
Так же, если поле `action` в элементе списка действий в `stages` содержит пустое значение на момент проверки
синтаксиса и параметров конфигурации pipeline (например, переменная будет задана позже в одном из скриптов stage'а - см.
["Запуск кода, как часть pipeline"](#запуск-кода-как-часть-pipeline)), то проверка синтаксиса и параметров этого 
действия не будет произведена.

### Action: клонирование исходников (git)

- **repo_url** `[строка]` *(обязательный)* - ссылка на GitLab/GitHub репозиторий.
- **repo_branch** `[строка]` *(необязательный)* - имя ветки в репозитории. Если ключ отсутствует, то `main`.
- **credentials** `[строка]` *(необязательный)* - CredentialsID для доступа к репозиторию (см. [Пример 9](#пример-9)).
Если ключ отсутствует, то значение берется из константы `GitCredentialsID` в библиотеке 
["jenkins-shared-library"](https://github.com/alexanderbazhenoff/jenkins-shared-library/blob/main/src/org/alx/commonFunctions.groovy).
- **directory** `[строка]` *(необязательный)* - директория внутри workspace для клонирования. Если ключ отсутствует, то
клонирование будет выполнено в workspace.

#### Пример 9

```yaml
# Фрагмент конфигурационного файла с описанием действия: клонирование исходников с GitLab по ssh c указанием 
# CredentialsID и переключение на ветку `develop`:

actions:
  git_clone_action_name:
    repo_url: 'ssh://git@gitlab.com:username/project-name.git
    repo_branch: develop
    directory: subdirectory_name
    credentials: a123b01c-456d-7890-ef01-2a34567890b1
```

### Action: установка ansible-коллекции из Ansible Galaxy

- **collection** `[строка]` *(обязательный)* - namespace и имя коллекции из 
[Ansible Galaxy](https://galaxy.ansible.com/) для установки (см. [Пример 10](#пример-10)).

#### Пример 10

Пример фрагмента конфигурационного файла с описанием действия: установки ansible-коллекции `namespace.collection_name`:

```yaml
actions:
  ansible_galaxy_install_action_name:
    collection: namespace.collection_name
```

### Action: запуск ansible playbooks

- **playbook** `[строка]` *(обязательный)* - имя playbook'а (см. ключ [playbooks](#ключ-playbooks) и 
[Пример 11](#пример-11)).
- **inventory** `[строка]` *(необязательный)* - имя inventory (см. ключ [playbooks](#ключ-inventories). Если ключ
отсутствует, то в ключе [inventories](#ключ-inventories) ищется playbook с именем `default`.

#### Пример 11

```yaml
# Фрагмент конфигурационного файла с описанием действия запуска и непосредственно сам `ping_playbook_name`.

actions:
  ping_action_name:
    playbook: ping_playbook_name

playbooks:
  ping_playbook_name: |
    - hosts: all
      tasks:
        - name: Ping
          ansible.builtin.ping:
```

### Action: запуск скриптов

- **script** `[строка]` *(обязательный)* - имя скрипта для его запуска как отдельный скрипт ([Пример 12](#пример-12)),
или запуска, как часть данного pipeline (см. ключ [scripts](#ключ-scripts)).

#### Пример 12

```yaml
# Фрагмент конфигурационного файла с описанием действия запуска и непосредственно сам `bash_script_name`.

actions:
  run_script_action_name:
    script: bash_script_name

scripts:
  bash_script_name:
    script: |
      #!/usr/bin/env bash
      printf "This is a %s script.\n" "$(cut -d'/' -f4 <<<"$SHELL")"
```

### Action: сборка файлов-артефактов

- **artifacts** `[строка]` *(обязательный)* - маска пути и имен (или список их список через запятую) для
[архивации файлов-артефактов](https://www.jenkins.io/doc/pipeline/tour/tests-and-artifacts/).
- **excludes** `[строка]` *(необязательный)* - маска пути и имен (или список их список через запятую) для исключения из
архивации (см. [Пример 13](#пример-13)).
- **allow_empty** `[boolean]` *(необязательный)* - флаг, разрешающий отсутствие файлов, попадающих под условия, заданные
в `artifacts` и `excludes`. По умолчанию False, то есть отсутствие файлов, удовлетворяющих условиям `artifacts` и
`excludes` вызовет ошибку.
- **fingerprint** `[boolean]` *(необязательный)* - флаг, включающий
[контрольную сумму для файлов-артефактов](https://www.jenkins.io/doc/book/using/fingerprints/).

#### Пример 13

```yaml
# Фрагмент конфигурационного файла с описанием действия сборки логов регрессионных, unit-тестов и общих результатов без
# log'ов unit-тестов в json-формате. Разрешается отсутствие файлов, подсчет контрольной суммы отключен.

actions:
  archive_artifacts_action_name:
    artifacts: regression_tests/**/logs/*, unit_tests/**/logs/*, results.txt
    excludes: unit_tests/**/logs/*.json
    allow_empty: True
    fingerprint: False
```

### Action: сборка файлов с node (stash)

- **name** `[строка]` *(обязательный)* - имя набора файлов для сборки файлов с node (например,
[stash в Jenkins](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/#stash-stash-some-files-to-be-used-later-in-the-build)).
Фактически служит идентификатором набора файлов.
- **includes** `[строка]` *(необязательный)* - маска пути и имен (или список их список через запятую) для сборки файлов 
с node.
- **excludes** `[строка]` *(необязательный)* - маска пути и имен (или список их список через запятую) для исключения из
сборки файлов с node (см. [Пример 14](#пример-14)).
- **default_excludes** `[boolean]` *(необязательный)* - исключения по умолчанию (например, для Jenkins исключения Ant
будут иметь [следующий список](https://ant.apache.org/manual/dirtasks.html#defaultexcludes)). По умолчанию: `True`.
- **allow_empty** `[boolean]` *(необязательный)* - флаг, разрешающий отсутствие файлов, попадающих под условия, заданные
в `artifacts` и `excludes`. По умолчанию False, то есть отсутствие файлов, удовлетворяющих условиям `includes`,
`excludes` и `default_excludes` вызовет ошибку.

### Action: перенос файлов на node (unstash)

- **name** - имя набора файлов для сборки файлов с node (например,
[stash в Jenkins](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/#stash-stash-some-files-to-be-used-later-in-the-build)).
Фактически служит идентификатором набора файлов.
- **directory** - путь в который будет произведено копирование именованного набора файлов (заданного в `name`) (см.
[Пример 14](#пример-14)).

#### Пример 14

```yaml
# Фрагмент конфигурационного файла с описанием стадий и действия сборки файлов с node: из папки logs в workspace
# на node 'my_node' в папку 'my_folder' в workspace на node 'another_node' копируются все файлы за исключением файлов
# в json-формате. Допускается отсутствие файлов.

stages:
  - name: stash_unstash
    actions:
      - action: stash_files_from_node_action_name
        node: my_node
      - action: unstash_files_from_node_action_name
        node: another_node

actions:
  stash_files_from_node_action_name:
    name: my_stash_name
    includes: logs/*
    excludes: logs/*.json
    allow_empty: True
  unstash_files_from_node_action_name:
    name: my_stash_name
    directory: my_folder
```

### Action: запуск нижележащего pipeline

- **pipeline** `[строка]` *(обязательный)* - имя нижестоящего pipeline, или job.
- **parameters** `[список]`- *(необязательный)* - список параметров, если нижестоящий pipeline/job параметризован, где
каждый элемент списка является параметром и имеет следующие ключи (см. [Пример 15](#пример-15)):
    - **name** `[строка]` *(обязательный)* - имя параметра нижестоящего pipeline, или job.
    - **type** `[строка]` *(обязательный)* - тип параметра: `string`, `password`, или `boolean`.
    - **parameter** `[строка|boolean]` *(обязательный)* - строчное или boolean значение параметра в зависимости от типа
      параметра.
- **propagate** `[boolean]` *(необязательный)* - передавать статус завершения из нижестоящего pipeline, или job: если
установлено в `true`, или ключ не указан, то неудачное завершение нижестоящей сборки приведет к ошибке в вышестоящем
(однако, если в вышестоящем pipeline в описании стадий для текущего действия установлен `ignore_fail`, то ошибка будет
передана, но сам pipeline не закончится с ошибкой и продолжит выполнение - см. [ключ stages](#ключ-stages)). Если
`propagate` не установлен, то статус завершения нижестоящего не будет передан в вышестоящий pipeline. По сути, для
Jenkins - это 'Propagate errors'.
- **wait** `[boolean]` *(необязательный)* - ожидать завершения нижестоящего pipeline, или job: если установлен, или не
указан, то ожидать. В противном случае вышестоящий pipeline не будет ожидать и сам статус завершения нижестоящего
pipeline, или job. По сути, для Jenkins - это 'Wait for completion'.
- **copy_artifacts** `[словарь]` *(необязательный)* - параметры, если нужно с нижестоящего pipeline/job копировать
файлы-артефакты (см. [Пример 15](#пример-15) и, например, для Jenkins - описание плагина 
[Copy Artifacts](https://plugins.jenkins.io/copyartifact/)):
    - **filter** `[строка]` *(обязательный)* - маска пути и имен (или список их список через запятую) для сборки файлов 
      с нижестоящего pipeline, или job.
    - **excludes** `[строка]` *(необязательный)* - маска пути и имен (или список их список через запятую) для исключения
      из списка файлов-артефактов.
    - **target_directory** `[строка]` *(необязательный)* - путь внутри workspace в который будут скопированы
      файлы-артефакты. Если ключ не указан, то файлы-артефакты будут скопированы в workspace.
    - **optional** `[boolean]` *(необязательный)* - если `True`, то вышестоящий pipeline не завершится с ошибкой, если
      не будет файлов-артефактов, подходящих под условия в ключах `filter` и `excludes`. В противном случае, если
      не будет файлов, pipeline завершится с ошибкой на шаге вызова нижестоящего pipeline/job в случае отсутствия
      файлов, подходящих под условия (однако, если в вышестоящем pipeline в описании стадий для текущего действия 
      установлен `ignore_fail`, то ошибка будет передана, но сам pipeline не закончится с ошибкой и продолжит
      выполнение - см. [ключ stages](#ключ-stages))
    - **flatten** `[boolean]` *(необязательный)* - если `True`, структура директорий копируемых файлов-артефактов будет
      проигнорирована. Если ключ не указан, или `False`, то будет сохранена вся структура директорий.
    - **fingerprint** `[boolean]` *(необязательный)* - флаг, включающий
      [контрольную сумму для файлов-артефактов](https://www.jenkins.io/doc/book/using/fingerprints/). По умолчанию
      `False`.
  
    Следует обратить внимание, что 
    [universal wrapper pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) копирует
    файлы-артефактов из pipeline'ы (или jobs) вызываемыми им. Выборка "по последнему удачному", "по последнему 
    завешенному" и/или по имени pipeline/job отсутствует. Если ожидание завершения нижестоящего pipeline (или job)
    отключено (см. ключ [`wait`](#action-запуск-нижележащего-pipeline))

#### Пример 15

```yaml
---

# Пример конфигурационного файла с описанием единственного параметра pipeline `UPSTREAM_PARAMETER`, стадии
# `run_downstream_pipeline_stage` и действия с запуском нижестоящего pipeline `downstream_pipeline_name`, в который
# передается значение вышестоящего параметра `UPSTREAM_PARAMETER`. Если выполнение нижестоящего pipeline 
# `downstream_pipeline_name` завершится неудачно, или в при его выполнении папка logs окажется пустой, то это не
# повлечет ошибок при выполнении описанного в данном фрагменте pipeline'а.

parameters:
  required:
    - name: UPSTREAM_PARAMETER
      type: string
      
stages:
  - name: run_downstream_pipeline_stage
    actions:
        action: run_jenkins_pipeline_action_name

actions:
  run_jenkins_pipeline_action_name:
    pipeline: downstream_pipeline_name
    parameters:
      - name: UPSTREAM_PARAMETER
        type: string
        value: ${env.UPSTREAM_PARAMETER}
    propagate: False
    copy_artifacts:
      filter: logs/*
      fingerprint: True
      target_directory: logs
      optional: True
```

### Action: отправка уведомлений

- **report** `[строка]` *(обязательный)* - способ отправки уведомлений. В настоящий момент поддерживается отправка:
    - [**на электронную почту**](#отправка-уведомлений-на-электронную-почту) (см. [Пример 16](#пример-16)) - значение
      `emial`,
    - [**в mattermost**](#отправка-уведомлений-в-mattermost) (см. [Пример 17](#пример-17)) - значение `mattermost`.

Параметры других ключей зависят от способа отправки уведомлений.

#### Отправка уведомлений на электронную почту

Для отправки уведомлений на электронную почту в Jenkins потребуется
[Email Extension](https://plugins.jenkins.io/email-ext/). Требования к значениям в ключах здесь так же зависит от
настроек сервера email (например, ключ `reply_to`), через который осуществляется отправка.

- **to** `[строка]` *(обязательный)* - адреса получателя(-ей).
- **reply_to** `[строка]` *(обязательный)* - адрес электронной почты для ответа на данное уведомление.
- **subject** `[строка]` *(необязательный)* - тема письма.
- **body** `[строка]` *(необязательный)* - текст письма.

```yaml
---

# Пример конфигурационного файла с описанием единственного параметра pipeline `EMAIL`, где указывается список
# получателей через пробел (будет замене на ', '), единственной стаии и действия отправки уведомления не email. Текст
# письма содержит встроенные в Jenkins переменные: `env.JOB_NAME` (имя текущего pipeline), `env.BUILD_URL` (ссылка на
# текущий build), а так же ключ встроенной в universal wrapper pipeline переменной `UNIVERSAL_PIPELINE_WRAPPER` (см.
# встроенные в pipeline переменные) и параметр пайплайна `EMAIL`. Если требуется осуществить подстановку переменных
# не только для Jenkins, то параметры pipeline и встроенные переменные требуется извлекать из ключей переменной
# `UNIVERSAL_PIPELINE_WRAPPER`: вместо `env.JOB_NAME` следует указывать `UNIVERSAL_PIPELINE_WRAPPER.JOB_NAME`,
# вместо `env.EMAIL` - `UNIVERSAL_PIPELINE_WRAPPER.EMAIL`. Данная возможность реализована для универсальности
# конфигурационных файлов и возможности использования в других инструментах помимо Jenkins.

parameters:
  required:
    - name: EMAIL
      type: string
      description: Space separated email recipients list.
      regex_replace:
        regex: ' '
        to: ', '
      
stages:
  - name: email_report_stage_name
    actions:
        action: email_report_action_name

actions:
  email_report_action_name:
    report: email
    to: ${env.EMAIL}
    reply_to: ${env.EMAIL}
    subject: Test email report
    body: |
      Hi,
      
      I've just run a test for universal jenkins wrapper pipeline for '${env.JOB_NAME}' pipeline, finished with
      '${currentBuild.result}' state. As you see sending report to ${env.EMAIL} done.
      
      Overall report is:
      ${UNIVERSAL_PIPELINE_WRAPPER.multilineReport}
      
      Check pipeline console for details: ${env.BUILD_URL}/console
      This report was generated automatically, please do not reply.
      
      Sincerely,
      Your Jenkins.
```

#### Отправка уведомлений в mattermost

- **url** - ссылка на hooks в mattermost, содержащая ключ канала. Например: `https://mattermost.com/hooks/<token>` (см.
[Пример 17](#пример-17)).
- **text** - текст уведомления.

#### Пример 17

```yaml
# Фрагмент конфигурационного файла с описанием действия отправки уведомления в mattermost. URL и токен указаны для
# примера.

actions:
  mattermost_report_action_name:
    report: mattermost
    url: https://mattermost.com/hooks/31895e09lg2m0g44dk4qeb847s
    text: |
      Hi, I've just run a test for universal jenkins wrapper pipeline: ${env.JOB_NAME}.
      Overall report is:
      ```
      ${UNIVERSAL_PIPELINE_WRAPPER.multilineReport}
      ```
      Please ignore this automatic report.
```

## Ключ scripts

Ключ содержит скрипты, которые так же можно выполнять, где каждый вложенный ключ является именем этого скрипта, а его
значения - параметрами скрипта и непосредственно сам скрипт. Скрипты так же можно выполнять "как часть pipeline'а" (см.
[Пример 19](#пример-19)).

- **pipeline** `[boolean]` *(необязательный)* - если указан, то скрипт выполняется "как часть pipeline" (см.
[Пример 19](#пример-19)) и тогда обязательно указание, в каком инструменте для CI (или окружении) должен этот скрипт
  выполняться: `jenkins`, `teamcity` и т.д. В случае, если ключ не указан, или `False`, то необходимо так же указание
  ключа `scripts`, чтобы этот скрипт выполняется как отдельно от pipeline (но при запуске он унаследует все переменные
  окружения) (см. [Пример 18](#пример-18)).
- **script** `[строка]` *(обязательный, если не `pipeline: True`)* - содержимое скрипта. Допускается использование
  hashbang (см. [Пример 18](#пример-18)).
- **jenkins** `[строка]` *(необязательный)* - код, который будет выполняться только при запуске на Jenkins "как часть
  pipeline". Все переменные pipeline и их значения для текущего запуска будут унаследованы (см. 
  [Встроенные в pipeline переменные](#встроенные-в-pipeline-переменные)).
- **teamcity** `[строка]` *(необязательный)* - код, который будет выполняться только при запуске на Teamcity "как часть
  pipeline". Все переменные pipeline и их значения для текущего запуска будут унаследованы (см.
  [Встроенные в pipeline переменные](#встроенные-в-pipeline-переменные)).

Ключи `jenkins` и `teamcity` нужны для обеспечения универсальности конфигурационного файла. В каждом из них следует
указать код, адаптированный для соответствующего runtime-окружения.

#### Пример 18

```yaml

```

## Ключ playbooks

## Ключ scripts

# Встроенные в pipeline переменные
