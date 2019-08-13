# webanalyzer rules

通用的指纹识别规则

## 规则编写

### 基础信息

例子:

```json
{
    "name": "wordpress",
    "author": "fate0",
    "version": "0.1.0",
    "description": "wordpress 是世界上最为广泛使用的博客系统",
    "website": "http://www.wordpress.org/",
    "matches": [],
    "condition": "0 and 1 and not 2",
    "implies": "PHP",
    "excludes": "Apache"
}
```

描述:

| FIELD       | TYPE   | DESCRIPTION  | EXAMPLE                                    | REQUIRED |
|-------------|--------|--------------|--------------------------------------------|----------|
| name        | string | 组件名称     | `wordpress`                                | true     |
| author      | string | 作者名       | `fate0`                                    | false    |
| version     | string | 插件版本     | `0.1.0`                                    | false    |
| description | string | 组件描述     | `wordpress 是世界上最为广泛使用的博客系统` | false    |
| website     | string | 组件网站     | `http://www.wordpress.org/`                | false    |
| matches     | array  | 规则         | `[{"regexp": "wordpress"}]`                | true     |
| condition   | string | 规则组合条件 | `0 and 1 and not 2`                        | false    |
| implies     | string/array | 依赖的其他组件 | `PHP`                               | false    |
| excludes    | string/array | 肯定不依赖的其他组件 | `Apache`                       | false    |


### 规则信息

例子:

```
[
    {
        "name": "rule name"
        "search": "all",
        "text": "wordpress"
    }
]
```

描述:

| FIELD      | TYPE   | DESCRIPTION                                                             | EXAMPLE                            |
|------------|--------|-------------------------------------------------------------------------|------------------------------------|
| name       | string | 规则名称                                                                | `rulename`                         |
| search     | string | 搜索的位置，可选值为 `all`, `headers`, `body`, `script`, `cookies`, `headers[key]`, `meta[key]`, `cookies[key]`| `body`                              |
| regexp     | string | 正则表达式                                                              | `wordpress.*`                      |
| text       | string | 明文搜索                                                                | `wordpress`                        |
| version    | string | 匹配的版本号                                                            | `0.1`                              |
| offset     | int    | regexp 中版本搜索的偏移                                                  | `1`                                |
| certainty  | int    | 确信度                                                                  | `75`                               |
| md5        | string | 目标文件的 md5 hash 值                                                  | `beb816a701a4cee3c2f586171458ceec` |
| url        | string | 需要请求的 url                                                          | `/properties/aboutprinter.html`    |
| status     | int    | 请求 url 的返回状态码，默认是 200                                       | `400`                              |


## 返回信息

例子:

```
[
    {
        "name": "4images",
        "version": "1.1",
        "certainty": 100,
        "origin": "custom"
    }
]
```

描述:

| FIELD       | TYPE   | DESCRIPTION  | EXAMPLE                                    | REQUIRED |
|-------------|--------|--------------|--------------------------------------------|----------|
| name        | string | 组件名称     | `wordpress`                                | true     |
| version     | string | 插件版本     | `0.1.0`                                    | false    |
| certainty     | int  | 确信度         | `75`                | false     |
| origin     | string | 插件来源     | `custom`                | false    |


## 检测逻辑

* 如果 match 中存在 url 字段，plugin 是属于 custom 类型且 `aggression` 开启，则请求 url 获取相关信息
* 根据 search 字段选取搜索位置
* 根据 regexp/text 进行文本匹配，或者 status 匹配状态码，或者 md5 匹配 body 的 hash 值
* 如果 match 中存在 version 就表明规则直接出对应版本，如果存在 offset 就表明需要从 regexp 中匹配出版本
* 如果 rule 中存在 condition，则根据 condition 判断规则是否匹配，默认每个 match 之间的关系为 `or`


## 引用

* [WhatWeb](https://github.com/urbanadventurer/WhatWeb)
* [Wappalyzer](https://github.com/AliasIO/Wappalyzer)
