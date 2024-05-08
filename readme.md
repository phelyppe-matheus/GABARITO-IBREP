# ORM Server
Modelo de reconhecimento de gabarito

## Routes
### API
[api/exam/review](https://gabarito-ibrep.onrender.com/aí/exam/review/)
> POST

_JSON_
|Campo|Tipo|Descrição|
|---|---|---|
|questionCount|int|Quantidade de questões no gabarito|
|choicesCount|int|Quantidade de alternativas nas questões do gabarito|
|examPhoto|string|Foto do Exame (Padrão: base64_)|
|examPhotoType|int|Veja [Image Input](#image-input)|
|correctAnswers|||

### Teste a API
[exam/review/test](https://gabarito-ibrep.onrender.com/exam/review/test)
> GET

## Envios
### Image Input
|ID|Descrição|
|---|---|
|0|Use esse tipo caso examPhoto esteja em base64|
|1|Use esse tipo caso examPhoto esteja em bits|
|2|Use esse tipo caso examPhoto seja um link|
