UNIVERSAL WRAPPER PIPELINE SETTINGS
===================================

Набор конфигураций для 
[universal wrapper pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline). Для ознакомления
с функционалом pipeline'а можно перейти по
[этой](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) ссылке, ниже будет представлено 
подробное описание непосредственно самого формата [конфигурационных файлов](#основные-ключи-конфигурационных-файлов). 

Конфигурационный файл Universal Wrapper Pipeline должен соответствовать всем
[стандартам yaml-синтаксиса](https://yaml.org/). На каждый wrapper pipeline - один файл (но возможны исключения с
использованием [регулярных выражений](#пример-1), когда один конфигурационный файл может конфигурировать несколько копий
wrapper pipeline'ов c разными именами).

# Имена конфигурационных файлов

Файл конфигурации с именем `имя-пайлайна.yaml` и по умолчанию располагаться внутри репозитория по пути `settings/` 
(можно задать константой pipeline'а `PipelineNameRegexReplace`). В имени pipeline'а допускаются префиксы и постфиксы, а
для их удаления и приведения к единообразию имен конфигурационных файлов имеется константа pipeline'а 
`PipelineNameRegexReplace`, содержащая список регулярных выражений: совпадения заданные этой константой будут удалены из
имени pipeline'а при формировании имени конфигурационного файла.

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
  # Ключи вложенные в словарь parameters...
stages:
  # Элементы списка stages...
actions:
  # Ключи вложенные в словарь actions...
scripts:
  # Ключи вложенные в словарь scripts...
playbooks:
  # Ключи вложенные в словарь playbooks...
inventories:
  # Ключи вложенные в словарь inventories...
```

- [**parameters**](#ключ-parameters) `[словарь]` *(обязательный, если pipeline параметризованный)* - параметры pipeline.
- [**stages**](#ключ-stages) `[список]` *(обязательный)* - список стадий pipeline.
- [**actions**](#ключ-actions) `[словарь]` *(обязательный)* - описание действий, которые так же могут ссылаться на
  playbook и inventory внутри ключей [playbooks](#ключ-playbooks) и [inventories](#ключ-inventories), или на скрипт из
  ключа [scripts](#ключ-scripts).
- [**scripts**](#ключ-scripts) `[словарь]` *(необязательный)* - ключ, содержащий скрипты, которые будут запущены при
  выполнении соответствующего action'а.
- [**playbooks**](#ключ-playbooks) `[словарь]` *(необязательный)* - ключ, содержащий ansible playbook'и, который(-ые)
  будут запущены при выполнении соответствующего action'а.
- [**inventories**](#ключ-inventories) `[словарь]` *(необязательный)* - ключ, содержащий ansible playbooks, которые
  использованы вместе с playbook'ами при выполнении action'а. При наличии хотя бы одного playbook'а в ключе 
  [playbooks](#ключ-playbooks) наличие [ключа inventories](#ключ-inventories) и хотя бы одного inventory с именем
  `default` являются обязательными.  

## Ключ parameters

Ключ содержит параметры pipeline, представленные в виде словаря, которые делятся на три типа:

  - [**required**](#required) `[список]` - обязательные параметры, без указания значений которых текущий запуск pipeline
    завершится c ошибкой. Описываются внутри одноименного ключа [required](#required), вложенного в ключ
    [parameters](#ключ-parameters):
```yaml
parameters:
  required:
```
  - [**optional**](#optional) `[список]` - необязательные параметры pipeline, пустые значения которых не приведут ни
    к предупреждениям, ни к остановке выполнения pipeline с ошибкой. Аналогично [**required**](#required) описываются
    внутри одноименного ключа, вложенного в ключ [parameters](#ключ-parameters).
  - [**built-in**](#встроенные-в-pipeline-параметры) - "встроенные" параметры: `SETTINGS_GIT_BRANCH`, `NODE_NAME`,
    `NODE_TAG`, `UPDATE_PARAMETERS`, `DRY_RUN`, `DEBUG_MODE`. Эти параметры уже встроены непосредственно в код pipeline
    (константой `BuiltinPipelineParameters`). Задавать их в файле конфигурации не нужно, но можно использовать в 
    конфигурационном файле pipeline: присваивать другим переменным pipeline (cм. `assign` в [Примере 2](#пример-2)),
    использовать в plyabook'ах и скриптах. 
  
Если хотя бы один из приведенных в конфигурационном файле параметров pipeline не соответствует текущим параметрам 
pipeline, то все параметры будут заново синхронизированы с параметрами в конфигурационном файле. Сравнение производится
только по именам параметров, тип, значения по умолчанию и другие ключи параметров игнорируются.

Pipeline может не иметь обязательных параметров (ключ [required](#required)) и все параметры могут быть размещены в
[optional](#optional). Так же любой обязательный параметр может стать необязательным без перемещения его в 
соответствующий словарь [`optional`](#optional) за-счет указания дополнительных опций ключа [`on_empty`](#required)
(см. [Пример 2](#пример-2)). Pipeline может так же иметь только необязательные параметры (см. [Пример 4](#пример-4)),
когда все параметры задаются внутри ключа [`optional`](#optional), или вовсе не иметь ни одного параметра: в этом 
случае указывается только пустой ключ `parameters`).

### required

Ключ [required](#required) находится внутри ключа [parameters](#ключ-parameters) и состоит из списка параметров 
pipeline, каждый из которых имеет следующие ключи:

- **name** `[строка]` *(обязательный)* - имя параметра pipeline.
- **type** `[строка]` *(обязательный)* - тип параметра, который полностью соответствует стандартным типам параметров для
  pipeline. Варианты: `string` (строковый), `text` (многострочный), `password` (пароль), `choice` (выбор), `boolean`
  (логический). Указание типа параметра pipeline является обязательным, хотя в некоторых случаях возможно 
  автоопределение типа с выводом соответствующего замечания к исправлению.
- **description** `[строка]` *(необязательный)* - описание параметра pipeline.
- **default** [зависит от `type`] *(необязателен и не совместим с типом параметра choice)* - значение параметра pipeline
  по умолчанию. Если не указан, то значение параметра pipeline по умолчанию будет `False` для *boolean* и пустое поле
  для строковых (в том числе *password*) параметров.
- **choices** `[список]` *(совместим только с типом параметров choice)* - опции выбора для choice-параметров.
- **trim** `[логический]` *(совместим только с типом параметров string, но необязателен)* - удалять начальные и конечные
  пробелы в строковом значении параметра. По умолчанию: `False`.
- **on_empty** `[словарь]` *(необязательный)* - опции для управления действий, если параметр при запуске pipeline не 
  указан (или пустой) (см. [Пример 2](#пример-2)). Содержит следующие вложенные ключи:
    - **assign** `[строка]` *(необязательный)* - имя параметра pipeline'а, значение которого будет присвоено, если
      параметр не указан (пуст). Возможно так же присвоение переменных окружения, а следовательно, переменных 
      Jenkins, или Teamcity: `$NODE_NAME`, `$JOB_NAME` и т.д (см. [Подстановка переменных](#подстановка-переменных). 
    - **fail** `[логический]` *(необязательный, не совместим с ключом `warn`)* - завершить pipeline с ошибкой, если
      параметр pipeline не указан. Если параметр pipeline обязательный и вложен в [required](#required), то указывать
      `fail: True` нет необходимости.
    - **warn** `[логический]` *(необязательный, не совместим с ключом `fail`)* - вывести предупреждение, но продолжить
      выполнение pipeline'а, если параметр не указан.

  Если параметр pipeline находится внутри [required](#required) и ключ `on_empty` не указан, то пустое значение такого
  параметра завершит pipeline с ошибкой.
- **regex** `[строка, или список]` *(необязательный)* - регулярное выражение, или список строк регулярного выражения,
  которые будут объеденины в единую строку для проверки параметра pipeline: если значение параметра не попадает под
  регулярное выражение, текущий запуск pipeline будет остановлен с ошибкой.
- **regex_replace** `[словарь]` *(необязательный)* - опции для управления заменой значений параметров pipeline, которые
  будут произведены при подстановке, или задании значений параметров pipeline'а. Допустим только для строковых
  (за исключением *password*) параметров. Содержит следующие вложенные ключи:
    - **regex** `[строка]` *(обязательный)* - регулярное значение для поиска заменяемого содержимого параметра.
    - **to** `[строка]` *(необязательный)* - заменить совпадения на указанное в данном ключе содержимое (см. 
      [Пример 3](#пример-3)). Если значение ключа `to` или сам не указан, то все совпадения регулярного выражения,
      заданные в ключе `regex`, будут удалены.

  Замена значений параметров pipeline (данные ключа `regex_replace`) производится в самом начала запуска pipeline: 
  после возможной подстановки других значений параметров pipeline (данные ключа `on_empty`) и проверки этих значений
  на соответствие в `regex`. Таким образом, в `regex` задаются условия для проверки исходных значений после возможной
  их подстановки, а в `regex_replace` - параметры для изменения значений параметров pipeline для использования в
  [стадиях pipeline](#ключ-stages) (см. [Пример 3](#пример-3)). 

#### Пример 2

```yaml
# Pipeline содержит три параметра в ключе `required`, но только параметр `LOGIN` является обязательным, пропуск которого
# (пустое значение параметра) завершит выполннение pipeline ошибкой. Если параметры `PASSWORD` не указан, то в консоли
# появится только предупреждение и pipeline продолжит выполннение, а если не указан `LOGIN_2`, то будет выдано 
# предупреждение, а значение будет взято из параметра pipeline'а `LOGIN`.

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
# "перевод строки" для подстановки в ansible inventory. Если стадии pipeline будут эту переменную, то ее значение
# будет уже иметь отформатированный вид: IP (или хосты) будут разделены переводом строк, а не пробелом.

parameters:
  required:
    - name: IP_ADDRESSES
      type: string
      description: Space separated IP or DNS list of the host(s).
      regex_replace:
        regex: ' '
        to: \n
```

### optional

Ключ [optional](#optional) находится внутри ключа [parameters](#ключ-parameters) и состоит из списка необязательных
параметров pipeline. Структура и список ключей аналогична ключу [required](#required) за исключением того, что задавать
здесь значения ключа `on_empty` не нужно, так как они будут проигнорированы. Таким образом, в этом ключе задаются только
необязательные параметры pipeline - здесь нет возможности управлять поведением pipeline при пустом значении этих 
параметров.

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
- **parallel** `[логический]` *(необязательный)* - флаг, установка которого приводит к параллельному запуску списка 
  действий (ключ `actions`) в текущий стадии (см. [Пример 6](#пример-6)).
- **actions** `[список]` *(обязательный)* - список действий в текущей стадии, каждый элемент которого имеет ключи:
  - **before_message** `[строка]` *(необязательный)* - строка сообщения перед началом действия (см. следующий ключ 
    `action`).
  - **action** `[строка]` *(обязательный)* - имя действия, которое задается в ключе [actions](#ключ-actions) в файле
    настроек pipeline (см. [ключ actions](#ключ-actions)). Допускается подстановка в качестве значения параметра
    pipeline (см. [Пример 7](#пример-7)).
  - **after_message** `[строка]` *(необязательный)* - строка сообщения по завершению действия, будет выведена вне
    зависимости от результата выполнения (см. [Пример 5](#пример-5)).
  - **fail_message** `[строка]` *(необязательный)* - строка сообщения при неудачном завершении текущего действия.
  - **success_message** `[строка]` *(необязательный)* - строка сообщения при успешном завершении текущего действия.
  - **ignore_fail** `[логический]` - флаг игнорирования неудачного выполнения текущего действия.
  - **node** `[строка или словарь]` - ключ, определяющий смену node (например, ноды Jenkins, или Teamcity). Может быть
    задан строкой и тогда это значение будет являться именем ноды, или словарем и включать в себя следующие ключи:
    - **name** `[строка]` *(обязательный, но не совместим с ключом `label`)* - имя node.
    - **label** `[строка]` *(обязательный, но не совместим с ключом `name`)* - тег node'ы (или *node label*).
    - **pattern** `[логический]` *(необязательный)* - если флаг включен (`True`), то поиск node будет осуществлен по
      строке в ключе `name`, или `label` и будет запущен на первой совпавшей с паттерном поиска (см.
      [Пример 8](#пример-8)). Если флаг выключен, то node будет выбрана только при полном совпадении имени (в ключе
      `name`), или node label (в ключе `label`).
  
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
# Фрагмент конфигурационного файла с описанием стадии `build_stage` с выбором node (выводится сообщением в консоль перед
# началом действия - `before_message`).

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

Ключ представляется в виде словаря и содержит описание именованных действий, где каждый вложенный ключ является именем
этого действия, а его значения - параметрами действия:

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
- [**запуск другого downstream pipeline**](#action-запуск-нижестоящего-pipeline),
- [**отправка уведомлений**](#action-отправка-уведомлений) ([email](#отправка-уведомлений-на-электронную-почту), или
  [mattermost](#отправка-уведомлений-в-mattermost)).

Если какое-либо из действий указано в ключе `actions`, но не указано ни в одной из стадий в ключе `stages` (или не было
передано переменной), то это действие будет проигнорировано. Так же, если поле `action` в элементе списка действий в
`stages` содержит пустое значение на момент проверки синтаксиса и параметров конфигурации pipeline (например, переменная
будет задана позже в одном из скриптов stage'а - см. [Пример 18](#пример-18)), то проверка синтаксиса и параметров этого
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
# CredentialsID в папку `subdirectory_name`, расположенную в workspace, и переключение на ветку `develop`.

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

Коллекция всегда устанавливается принудительно (ключ `force`), что обеспечивает постоянное их обновление.

#### Пример 10

```yaml
# Пример фрагмента конфигурационного файла с действием: установкой ansible-коллекции `namespace.collection_name`.

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
# Фрагмент конфигурационного файла с действием запуска и непосредственно сам `ping_playbook_name`.

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
# Фрагмент конфигурационного файла с действием запуска и непосредственно сам `bash_script_name`.

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

- **artifacts** `[строка]` *(обязательный)* - маска пути и имен (или их список через запятую) для
[архивации файлов-артефактов](https://www.jenkins.io/doc/pipeline/tour/tests-and-artifacts/).
- **excludes** `[строка]` *(необязательный)* - маска пути и имен (или их список через запятую) для исключения из
архивации (см. [Пример 13](#пример-13)).
- **allow_empty** `[логический]` *(необязательный)* - флаг, разрешающий отсутствие файлов, попадающих под условия,
заданные в `artifacts` и `excludes`. По умолчанию False, то есть отсутствие файлов, удовлетворяющих условиям `artifacts` и
`excludes` вызовет ошибку.
- **fingerprint** `[логический]` *(необязательный)* - флаг, включающий
[контрольную сумму для файлов-артефактов](https://www.jenkins.io/doc/book/using/fingerprints/).

#### Пример 13

```yaml
# Фрагмент конфигурационного файла с описанием действия сборки логов регрессионного тестирования, unit-тестов и общих
# результатов за исключением log'ов unit-тестов в json-формате. Разрешается отсутствие файлов, подсчет контрольной
# суммы отключен.

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
- **includes** `[строка]` *(необязательный)* - маска пути и имен (или их список через запятую) для сборки файлов с node.
- **excludes** `[строка]` *(необязательный)* - маска пути и имен (или их список через запятую) для исключения из сборки
файлов с node (см. [Пример 14](#пример-14)).
- **default_excludes** `[логический]` *(необязательный)* - исключения по умолчанию (например, для Jenkins исключения Ant
будут иметь [следующий список](https://ant.apache.org/manual/dirtasks.html#defaultexcludes)). По умолчанию: `True`.
- **allow_empty** `[логический]` *(необязательный)* - флаг, разрешающий отсутствие файлов, попадающих под условия,
заданные в `artifacts` и `excludes`. По умолчанию `False`, то есть отсутствие файлов удовлетворяющих условиям 
`includes`, `excludes` и `default_excludes` вызовет ошибку.

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

### Action: запуск нижестоящего pipeline

Действие описывает вызов нижестоящего pipeline, или job (в дальнейшем просто "pipeline"), получение результатов и 
файлов-артефактов сборки этого pipeline.

- **pipeline** `[строка]` *(обязательный)* - имя нижестоящего pipeline.
- **parameters** `[список]`- *(необязательный)* - список параметров, если нижестоящий pipeline параметризован, где 
каждый элемент списка является параметром и имеет следующие ключи (см. [Пример 15](#пример-15)):
    - **name** `[строка]` *(обязательный)* - имя параметра нижестоящего pipeline.
    - **type** `[строка]` *(обязательный)* - тип параметра: `string`, `password`, или `boolean`.
    - **parameter** `[строка|boolean]` *(обязательный)* - строчное или boolean значение параметра в зависимости от типа
      параметра.
- **propagate** `[логический]` *(необязательный)* - передавать статус завершения из нижестоящего pipeline: если
установлено в `True`, или ключ не указан, то неудачное завершение сборки нижестоящего pipeline приведет к ошибке в
вышестоящем. Однако, если в вышестоящем pipeline в описании стадий для текущего действия установлен `ignore_fail`, то
ошибка будет передана, но сам pipeline не закончится с ошибкой и продолжит выполнение - см.
[ключ stages](#ключ-stages)). Если `propagate` не установлен, то статус завершения нижестоящего не будет передан в 
вышестоящий pipeline (для Jenkins - это *'Propagate errors'*).
- **wait** `[логический]` *(необязательный)* - ожидать завершения нижестоящего pipeline: если установлен, или не указан,
то ожидать. В противном случае вышестоящий pipeline не будет ожидать и получить из нижестоящего pipeline статус
завершения и файлы-артефакты в вышестоящий pipeline будет невозможно. По сути, в Jenkins - это 'Wait for completion'.
- **copy_artifacts** `[словарь]` *(необязательный)* - дополнительные параметры для копирования файлов-артефактов с
нижестоящего pipeline (см. [Пример 15](#пример-15) и описание плагина для Jenkins 
[Copy Artifacts](https://plugins.jenkins.io/copyartifact/)):
    - **filter** `[строка]` *(обязательный)* - маска пути и имен (или их список через запятую) для сборки файлов c 
      нижестоящего pipeline.
    - **excludes** `[строка]` *(необязательный)* - маска пути и имен (или список их список через запятую) для исключения
      из списка файлов-артефактов.
    - **target_directory** `[строка]` *(необязательный)* - путь внутри workspace, в который будут скопированы
      файлы-артефакты. Если ключ не указан, то файлы-артефакты будут скопированы в workspace.
    - **optional** `[логический]` *(необязательный)* - если `True`, то вышестоящий pipeline не завершится с ошибкой при
      отсутствии файлов-артефактов, подходящих под условия в ключах `filter` и `excludes`. В противном случае при
      отсутствии файлов-артефактов, pipeline завершится с ошибкой на шаге вызова нижестоящего pipeline. Однако, если в
      вышестоящем pipeline в описании стадий для текущего действия установлен `ignore_fail`, то ошибка будет передана в
      вышестоящий pipeline, но сам pipeline не закончится с ошибкой и продолжит выполнение (см.
      [ключ stages](#ключ-stages)).
    - **flatten** `[логический]` *(необязательный)* - если `True`, то структура директорий копируемых файлов-артефактов
      будет проигнорирована. Если ключ не указан, или `False`, то будет сохранена вся структура директорий.
    - **fingerprint** `[логический]` *(необязательный)* - флаг, включающий
      [контрольную сумму для файлов-артефактов](https://www.jenkins.io/doc/book/using/fingerprints/). По умолчанию
      `False`.
  
    Следует обратить внимание, что 
    [universal wrapper pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) копирует
    файлы-артефактов из pipeline вызываемыми им. Выборка "по последнему удачному", "по последнему завешенному" и/или по
    имени pipeline/job отсутствует. Если ожидание завершения нижестоящего pipeline отключено (см. ключ
    [`wait`](#action-запуск-нижестоящего-pipeline)).

#### Пример 15

```yaml
---

# Пример конфигурационного файла с описанием единственного параметра pipeline `UPSTREAM_PARAMETER`, стадии
# `run_downstream_pipeline_stage_name` и действия с запуском нижестоящего pipeline `downstream_pipeline_name`, в который
# передается значение вышестоящего параметра `UPSTREAM_PARAMETER`. Если выполнение нижестоящего pipeline 
# `downstream_pipeline_name` завершится неудачно, или при его выполнении папка logs окажется пустой, то это не повлечет
# ошибок при выполнении pipeline.

parameters:
  required:
    - name: UPSTREAM_PARAMETER
      type: string
      
stages:
  - name: run_downstream_pipeline_stage_name
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
      `email`,
    - [**в mattermost**](#отправка-уведомлений-в-mattermost) (см. [Пример 17](#пример-17)) - значение `mattermost`.

Параметры других ключей зависят от способа отправки уведомлений.

#### Отправка уведомлений на электронную почту

Для отправки уведомлений на электронную почту в Jenkins потребуется
[Email Extension](https://plugins.jenkins.io/email-ext/).

- **to** `[строка]` *(обязательный)* - адреса получателя(-ей).
- **reply_to** `[строка]` *(обязательный)* - адрес электронной почты для ответа на данное уведомление.
- **subject** `[строка]` *(необязательный)* - тема письма.
- **body** `[строка]` *(необязательный)* - текст письма.

#### Пример 16

```yaml
---

# Пример конфигурационного файла с описанием единственного параметра pipeline `EMAIL`, где указывается список
# получателей через пробел (будет замене на ', '), единственной стадии и действия отправки уведомления не email. Текст
# письма содержит встроенные в Jenkins переменные: `env.JOB_NAME` (имя текущего pipeline), `env.BUILD_URL` (ссылка на
# текущий build), а так же ключ встроенной в universal wrapper pipeline переменной `universalPipelineWrapperBuiltIns`
# (см. встроенные в pipeline переменные) и параметр pipeline'а `EMAIL`.

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
      ${universalPipelineWrapperBuiltIns.multilineReport}
      
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
      ${universalPipelineWrapperBuiltIns.multilineReport}
      ```
      Please ignore this automatic report.
```

## Ключ scripts

Ключ содержит скрипты, где каждый вложенный ключ является именем этого скрипта, а его значение - словарем с параметрами
скрипта и содержимым скрипта. Скрипты так же можно выполнять "как часть pipeline'а" (см. [Пример 18](#пример-18)).

- **pipeline** `[логический]` *(необязательный)* - если указан, то скрипт выполняется "как часть pipeline" (см.
  [Пример 18](#пример-18)) и тогда необходимо так же задать ключ, указывающий, в каком инструменте для CI (или
  окружении) должен этот скрипт выполняться: `jenkins`, `teamcity` и т.д. А в случае, если ключ не указан, или `False`,
  необходимо задать ключ `scripts`, чтобы этот скрипт выполняется "отдельно от pipeline" (хотя при запуске он так же
  унаследует все переменные окружения) (см. [Пример 18](#пример-12)). Разница в том, что в первом случае можно
  выполнять нативный для инструмента CI код (groovy - для Jenkins, или Kotlin - для Teamcity), во втором - скрипт на
  любом языке (возможно, на node потребуется его установка).
- **script** `[строка]` *(обязательный, если не `pipeline: True`)* - содержимое скрипта. Допускается использование
  hashbang (см. [Пример 18](#пример-12)).
- **jenkins** `[строка]` *(необязательный)* - код, который будет выполняться только при запуске на Jenkins "как часть
  pipeline". Все переменные pipeline и их значения для текущего запуска будут унаследованы (см. 
  [Встроенные в pipeline переменные](#встроенные-в-pipeline-переменные)).
- **teamcity** `[строка]` *(необязательный)* - код, который будет выполняться только при запуске на Teamcity "как часть
  pipeline". Все переменные pipeline и их значения для текущего запуска будут унаследованы (см.
  [Встроенные в pipeline переменные](#встроенные-в-pipeline-переменные)).

Ключи `jenkins` и `teamcity` нужны для обеспечения универсальности конфигурационного файла: в каждом из них должен
находиться соответствующий runtime-окружению код (см. [Пример 18](#пример-18)).

#### Пример 18

```yaml
# Фрагмент конфигурационного файла с описанием действия по запуску кода "как часть pipeline" и кодом для Jenkins и
# Teamcity.

actions:
  run_part_of_pipeline_action_name:
    script: script_name

scripts:
  pipeline: True
  script_name:
    jenkins: |
      println String.format('EMAIL provided for %s action is awesome: %s', env.PIPELINE_ACTION, env.EMAIL)
    teamcity: |
      println(String.format("EMAIL provided for %s action is awesome: %s", env.PIPELINE_ACTION, env.EMAIL))
```

## Ключ playbooks

Ключ содержит ansible playbook'и, где каждый вложенный ключ является именем этого скрипта, а его значения - содержимым
playbook'а (см. [Пример 19](#пример-19)).

## Ключ inventories

Ключ содержит ansible inventory, где каждый вложенный ключ является именем этого inventory, а его значения - содержимым
inventory. Для всех playbook'ов в конфигурационном файле должен быть задан хотя бы один inventory с именем `default`,
который будет использоваться для всех playbook'ов (см. [Пример 19](#пример-19)), заданных в конфигурационном файле. Для
каждого playbook'а может быть так же задан свой inventory: в этом случае inventory создаются с тем же именем, что и
playbook, которому он соответствует (см. [Пример 20](#пример-20)).

#### Пример 19

```yaml
---

# Пример конфигурационного файла с параметрами pipeline, стадиями, действиями, playbook'ом и default inventory.
# В параметрах задаются IP адреса (или hosts) для которых будет выполнен anisble ping. Указан один единственный
# inventory с именем `default`, но в данном примере inventory может так же иметь имя `run_ansible_playbook_action_name`.

parameters:
  required:
    - name: IP_ADDRESSES
      type: string
      description: |
        Space separated IP or DNS list of the host(s) to asnible ping: try to connect to host, verify a usable python
        and return.
      regex_replace:
        regex: ' '
        to: \n
    - name: SSH_LOGIN
      type: string
      description: SSH login for all specified hosts.
    - name: SSH_PASSWORD
      type: password
      description: SSH password for all specified hosts.

stages:
  - name: stage_name
    actions:
      - action: run_ansible_playbook_action_name

actions:
  run_ansible_playbook_action_name:
    playbook: playbook_name

playbooks:
  playbook_name: |
    - hosts: all
      tasks:
        - name: Perform ansible ping on the host(s)
          ansible.builtin.ping:

inventories:
  default: |
    [all]
    $IP_ADDRESSES
    [all:vars]
    ansible_connection=ssh
    ansible_become_user=root
    ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    ansible_ssh_user=$SSH_LOGIN
    ansible_ssh_pass=$SSH_PASSWORD
```

#### Пример 20

```yaml
# Фрагмент конфигурационного файла с двумя playbook'ами `ansible_ping_playbook_name` и `install_curl_playbook_name`,
# а так же inventory к каждому из них: при выполнении `ansible_ping_playbook_name` аутентификация происходит по паролю,
# при выполнении `install_curl_playbook_name` по ssh-ключу.

playbooks:
  ansible_ping_playbook_name: |
    - hosts: all
      tasks:
        - name: Perform ansible ping on the host(s)
          ansible.builtin.ping:
  install_curl_playbook_name: |
    - hosts: all
      become: True
      become_method: sudo
      gather_facts: True
      tasks:
        - name: Install curl using ansible.builtin.package ansible module Generic OS package manager
          ansible.builtin.package:
          name: curl
          state: present

inventories:
  ansible_ping_playbook_name: |
    [all]
    $IP_ADDRESSES
    [all:vars]
    ansible_connection=ssh
    ansible_become_user=root
    ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    ansible_ssh_user=$SSH_LOGIN
    ansible_ssh_pass=$SSH_PASSWORD
  install_curl_playbook_name: |
    [all]
    $IP_ADDRESSES

    [all:vars]
    ansible_connection=ssh
    ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    ansible_user=$SSH_LOGIN
    ansible_ssh_private_key_file=~/.ssh/id_rsa
```

# Встроенные в pipeline параметры

- `SETTINGS_GIT_BRANCH` - ветка из которой будут загружаться pipeline settings.
- `NODE_NAME` - имя node, на которой будет запущен 
[universal wrapper pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline).
- `NODE_TAG` - тег ноды (или *node label*).
[Universal wrapper pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) будет запущен
на той node, которой присвоен данный тег.
- `UPDATE_PARAMETERS` - просто обновить параметры pipeline из конфигурационного файла без выполнения стадий и действий.
Необходимо в том случае, если в конфигурационном файле изменены параметры pipeline (например: тип, значения по
умолчанию, описание, или обработка самого параметра), а не его имя.
- `DRY_RUN` - "пробный прогон" при котором никаких изменений не будет произведено, но в консоли будут отображаться
сообщения, как если бы пробный прогон не был включен.
- `DEBUG_MODE` - режим отладки для детализированного логирования в консоль.

Все [встроенные в pipeline параметры](#встроенные-в-pipeline-параметры) доступны для использования в playbook'ах,
inventory и скриптах через переменные окружения: например, `DRY_RUN` в скриптах, или `env.DRY_RUN` для скриптов,
выполняемых "как часть pipeline". Для Jenkins параметры pipeline так же являются ключами `params`: например, 
`params.NODE_TAG`.

# Встроенные в pipeline переменные

Переменная universal wrapper pipeline `universalPipelineWrapperBuiltIns` *[словарь, или Map]* содержит вспомогательные
ключи, которые можно использовать в конфигурационном файле (например, при формировании отчетов):

- `universalPipelineWrapperBuiltIns.multilineReportMap` *[словарь, или Map]* - содержит словарь статусов и информацию о
каждом действии и стадии pipeline. Удобно использовать исключительно в кодовых вставках "запуск кода как часть 
pipeline". Структура Map'а идентична с той, что описана в 
[jenkins-shared-library](https://github.com/alexanderbazhenoff/jenkins-shared-library) в функции
`addPipelineStepsAndUrls()` и выглядит примерно следующим образом:

```groovy
universalPipelineWrapperBuiltIns.multilineReport = [
        stage_1_name: [
            name  : 'stage_1_name',
            state : true|false
            jobUrl: 'Information about stage_1_name.'
        ],
        action_1_name: [
            name  : 'action_2_name',
            state : true|false
            jobUrl: 'Information about action_2_name.'
        ],
        stage_2_name: [
            name  : 'stage_2_name',
            state : true|false
            jobUrl: 'Information about stage_2_name.'
        ]
]
```

- `universalPipelineWrapperBuiltIns.multilineStagesReportMap` *[словарь, или Map]* - содержит только словарь статусов 
стадий. Структура аналогична *multilineReportMap*.
- `universalPipelineWrapperBuiltIns.multilineActionsReportMap` *[словарь, или Map]* - содержит только словарь статусов 
действий. Структура аналогична *multilineReportMap*.

- `universalPipelineWrapperBuiltIns.multilineReport` *[строка]* - содержит текстовую таблицу статусов и информацию о 
каждом действии и стадии pipeline. Содержимое идентично *multilineReport*, только имеет удобный для чтения формат.
В отличие от вывода такой же таблицы в console Jenkins, или Teamcity эта переменная не содержит цветовых кодов (ASCII
colours) и, таким образом, удобна для отправки различных уведомлений.
- `universalPipelineWrapperBuiltIns.multilineStagesReport` *[строка]* - содержит только текстовую таблицу статусов 
стадий.
- `universalPipelineWrapperBuiltIns.multilineActionsReport` *[строка]* - содержит только текстовую таблицу статусов 
действий.
- `universalPipelineWrapperBuiltIns.multilineFailedReport` *[строка]* - содержит текстовую таблицу только неудачно
завершенных стадий и действий.

# Подстановка переменных

В качестве значений ключа может быть установлено значение любого параметра pipeline, или переменной окружения. Если в 
ключе ['assign'](#required) параметра pipeline (см. [Пример 2](#пример-2)), или ключе ['action'](#ключ-stages) внутри
списка `actions` (см. [Пример 7](#пример-7)) перед запуском стадий pipeline требуется проверить наличие переменной, или
параметра pipeline, то переменную `VAR_NAME` в качестве значения ключа следует указывать как `$VAR_NAME`. Если указанная
переменная не задана (параметр pipeline отсутствует), или же имя переменной, или pipeline не соответствует стандартам
POSIX, то текущий запуск pipeline будет завершен ошибкой с указанием о том, что не удается присвоить значение 
`VAR_NAME`. В качестве значений других ключей, или же в случае, если проверка не требуется, следует указывать:
`"${VAR_NAME}"` (см. [Пример 21](#пример-21))).

#### Пример 21

```yaml
---

# Пример конфигурационного файла для запуска ansible playbook, или pipeline (параметр `ACTION`), имя которых задается
# переменной `ACTION_SUBJECT`. Имя пользователя `USERNAME` так же передается в playbook, или pipeline.
# Обратите внимание, что задание параметра pipeline, или переменной как `$VAR_NAME` и проверка будет произведена только
# в parameters и actions. В остальных ключах можно так же указывать `$VAR_NAME`, но проверка на несуществующую 
# переменную и соответствие имен стандартам POSIX осуществляться не будет. Однако ниже для наглядности и удобства чтения
# в таких случаях указывается как: `${ACTION}`, `${USERNAME}` и т.д.

parameters:
  required:
    - name: USERNAME
      type: string
      default: 'jenkins'
      description: |
        Run action under specified username (use in ansible inventory for login or pass to downstream pipeline).
    - name: ACTION
      type: choice
      choices:
        - run playbook
        - run pipeline
      description: Choose an action to perform.
    - name: ACTION_SUBJECT
      type: string
      # В качестве значения по умолчанию задан существующий ansible playbook, или одноименный pipeline.
      default: subject_name
      description: Specify an ansible playbook or downstream pipeline name here.

stages:
  - name: own stage
    actions:
      - before_message: Ready to ${ACTION} under ${USERNAME}
        # Будет произведена проверка, возможна ли подстановка параметра pipeline `ACTION`.
        action: $ACTION

actions:
  run playbook:
    playbook: ${ACTION_SUBJECT}
  run pipeline:
    pipeline: ${ACTION_SUBJECT}
    parameters:
      - name: USERNAME
        type: string
        value: ${USERNAME}
        
playbooks:
  subject_name: |
    - hosts: all
      tasks:
        - name: "Perform ansible ping on the host(s)"
          ansible.builtin.ping:

inventories:
  default: |
    [all]
    192.168.0.200
    192.168.0.201
    [all:vars]
    ansible_connection=ssh
    ansible_become_user=root
    ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    ansible_ssh_user=${USERNAME}
    ansible_ssh_pass=my_password
    ansible_become_pass=my_password
```

# Примеры использования

Директория [settings](settings) данного проекта содержит наглядные рабочие примеры (включая абстрактный пример 
[example-pipeline.yml](settings/example-pipeline.yaml) с максимально поддерживаемым набором опций и комментариями).

# Ссылки

- Исходный код
[**jenkins universal wrapper pipeline**](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline).
