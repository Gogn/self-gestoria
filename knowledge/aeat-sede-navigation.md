# Sede Electrónica AEAT — навигация

> Актуально на: 2026-09 · https://sede.agenciatributaria.gob.es
> Перепроверять: AEAT периодически меняет структуру меню и названия разделов.

## Способы входа

| Способ | Комментарий |
|---|---|
**Cl@ve** (PIN / Permanente) | Проще всего получить, привязывается к телефону |
**Certificado digital** (FNMT) | Файл-сертификат в браузере. Надёжно, но нужен для установки |
**DNIe** | Для граждан Испании с электронным удостоверением, нужен считыватель |

⚠️ Сертификат `.p12` — это ключ ко всем вашим налоговым данным. Храните в менеджере
паролей, не в папке проекта. В этом репозитории `*.p12` внесён в `.gitignore`.

## Основные разделы

| Раздел | Зачем |
|---|---|
**Presentar y consultar declaraciones** | Подача 130, 303, 100 и др. |
**Consultar declaraciones presentadas** | Все ранее поданные декларации с PDF и *justificante* |
**PRE303** | 👉 Официальный помощник заполнения модели 303. Подсказывает актуальные графы под ваш профиль. Использовать для сверки перед подачей |
**Mis datos censales** | Ваш режим налогообложения, заявленные виды деятельности (IAE), обязательные модели. Здесь проверяется профиль |
**Pagar, aplazar y consultar deudas** | Статус долгов, оплата |
**Aplazamientos y fraccionamientos** → *Contestar requerimientos y otras gestiones* | 👉 Управление рассрочкой. **Платежи по рассрочке — только отсюда**, не через общую кнопку оплаты (см. `pitfalls.md` §3) |
**Consultar notificaciones y comunicaciones no leídas** | 👉 Уведомления и требования. Проверять регулярно — бумажных писем не будет. В меню может называться и *Mis notificaciones* |
**Consultar sus domiciliaciones** | 👉 Какие налоговые списания реально привязаны к счёту. Проверять, если домициляция когда-либо не сработала (`pitfalls.md`) |
**Apoderamientos** | Доверенности. Здесь отзывается доступ прежнего гестора |
**Mis expedientes** | Ход дел: рассрочки, apremio, проверки, requerimientos. ⚠️ Поданных 130/303 здесь **нет** — см. раздел ниже |
**Área personal** | Сводная точка входа (`Sede/mi-area-personal.html`). Отсюда ведут ссылки на разделы ниже |
**Mis últimos accesos** | Кто и когда заходил под вашим NIF. Полезно после отзыва apoderamiento |
**Calendario del contribuyente** | Официальные сроки на текущий год |

## Прямые ссылки

> Проверено по живой странице Sede: 2026-09-02. `[NIF]` подставляется свой.
> Работают только внутри авторизованной сессии; AEAT может их менять.

| Раздел | URL |
|---|---|
Consultar declaraciones presentadas | `www1.agenciatributaria.gob.es/wlpl/SCEJ-MANT/CONSUL/index.zul?MODELO=&EJERCICIO=0&NIFOBLIGADO=[NIF]` |
Mis datos censales | `www1.agenciatributaria.gob.es/wlpl/BUGC-JDIT/MdcAcceso?nifRepresentado=[NIF]&E_HNR=&EJERCICIO=0` |
Consultar sus domiciliaciones | `www1.agenciatributaria.gob.es/wlpl/ECDM-MANT/DomQueryN` |
Notificaciones y comunicaciones no leídas | `www1.agenciatributaria.gob.es/wlpl/GNNO-JDIT/ResumenInteresados` |
Mis expedientes | `www1.agenciatributaria.gob.es/wlpl/TEWV-CORE/ResumenVlt` |
Mis últimos accesos | `www1.agenciatributaria.gob.es/wlpl/ADHT-AUTH/UltimasConexionesW` |
Asientos registrales | `www1.agenciatributaria.gob.es/wlpl/REGD-JDIT/SvRegMisAsiIntQue` |
Área personal | `sede.agenciatributaria.gob.es/Sede/mi-area-personal.html` |

Обратите внимание: ссылки на разделы с данными несут NIF в query-строке. Не пересылайте
их и не сохраняйте в публичные файлы — подставляйте `[NIF]` сами.

## Mis expedientes — что там есть и чего там нет

Дерево по департаментам, в каждом узле в скобках число expedientes. Четыре закладки:
*Todos*, *En tramitación*, *Buscar expediente* (поиск по номеру из блока
«Identificación del documento»), *Ayuda*. Есть **Exportar** — выгрузка списка в `.csv`.

Типичные ветки:

```
Agencia Estatal de Administración Tributaria
├── Impuestos, tasas y prestaciones patrimoniales
│   └── IRPF → Modelo 100 / Modelo 102
├── Certificados
│   └── Censales → Expedición de certificados tributarios - Situación censal
└── Recaudación
    ├── Procedimiento de Apremio
    └── Aplazamientos y fraccionamientos
```

🔴 **Главная ловушка раздела.** *Mis expedientes* показывает **процедуры**, а не
декларации. Квартальных 130 и 303 здесь не будет никогда — они лежат в
*Consultar declaraciones presentadas*. Пустая ветка IRPF в expedientes **не значит**,
что декларации не подавались; она значит, что по ним не открыто процедур.

Обратное тоже верно и полезно: **expediente в закладке *En tramitación* — это
незакрытая процедура.** Открытый expediente по модели 100 может быть чем угодно —
обработка возврата, *comprobación limitada*, *paralela*. Что именно — видно только
внутри expediente, из истории actuaciones. Не выводить по названию ветки.

💡 Ветка *Certificados → Censales* стоит проверять первой: если сертификат
*Situación censal* уже выдавался, PDF с режимом и кодами IAE можно скачать оттуда, не
запрашивая заново.

## Первые шаги при переходе на самоподачу

- [ ] Получить и проверить собственный доступ (Cl@ve или сертификат)
- [ ] *Mis datos censales* → выписать режим, коды IAE, список обязательных моделей
- [ ] *Consultar declaraciones presentadas* → скачать последние декларации, поданные
      гестором, как образец заполнения
- [ ] *Pagar y consultar deudas* → убедиться, что нет незамеченных долгов
- [ ] *Mis expedientes* → закладка *En tramitación*: нет ли незакрытых процедур
- [ ] *Consultar sus domiciliaciones* → сверить, какие списания привязаны к счёту
- [ ] *Notificaciones y comunicaciones no leídas* → включить оповещения на email
- [ ] *Apoderamientos* → посмотреть, кто имеет к вам доступ
- [ ] Первую самостоятельную подачу прогнать через PRE303 и/или сверить с gestor

## Полезно знать

- У AEAT есть телефонная поддержка и запись на приём (*cita previa*). Для сложных
  случаев это работает и бесплатно.
- *Calendario del contribuyente* — первоисточник по срокам. Внешние календари и боты
  (см. `deadlines.md`) удобны как напоминание, но **не видят** адресованные лично вам
  требования: для этого только *Mis notificaciones*.
- *Justificante de presentación* — единственное доказательство подачи. Сохраняйте PDF
  каждой декларации (в `my-data/`, не в git).
- Интерфейс Sede переключается на **английский** (ES / CA / GL / VA / EN в правом
  верхнем углу). Для неносителя испанского это заметно снижает цену ошибки при чтении
  формы. ⚠️ Названия casillas в переводе иногда расходятся с официальной терминологией —
  сверять номера, а не подписи.
- Срок хранения документов по налоговым обязательствам — не менее **4 лет**
  (срок давности *prescripción*). Практичнее — 6 лет.
