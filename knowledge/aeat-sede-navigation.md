# Sede Electrónica AEAT — навигация

> Актуально на: 2026-09 · пути и ссылки сверены на живой Sede 2026-09-02
> Перепроверять: AEAT периодически меняет структуру меню и названия разделов.

## Способы входа

| Способ | Комментарий |
|---|---|
**Cl@ve Móvil** | Проще всего получить, привязывается к телефону. Именно эта форма указана как допустимая для разделов *Mi área personal* |
**Certificado digital** (FNMT) | Файл-сертификат в браузере. Надёжно, но нужна установка |
**DNIe** | Для граждан Испании с электронным удостоверением, нужен считыватель |
**Número de referencia** | Ограниченный доступ, в основном по кампании Renta. Для квартальных подач не полагаться |

⚠️ Сертификат `.p12` — это ключ ко всем вашим налоговым данным. Храните в менеджере
паролей, не в папке проекта. В этом репозитории `*.p12` внесён в `.gitignore`.

## Три домена — и почему это путает

AEAT живёт на нескольких доменах, и в меню они перемешаны. Это не разные организации:

| Домен | Что там | Нужен ли вход |
|---|---|---|
`sede.agenciatributaria.gob.es` | **Sede Electrónica.** Описания процедур, каталог моделей, ссылки на сервисы. Все страницы имеют путь `/Sede/…` | нет |
`www1.agenciatributaria.gob.es` | **Сами приложения.** Пути вида `/wlpl/…`. Здесь вы реально смотрите декларации и подаёте | да |
`www2.agenciatributaria.gob.es` | Открытые симуляторы и статика | нет |
`www.agenciatributaria.es` | Информационный портал: справочные материалы, региональные налоги | нет |

👉 «Sede» — это **не отдельный сайт**, а раздел того же agenciatributaria.gob.es. Слово
`Sede` в пути `/Sede/…` — просто префикс страниц электронной приёмной.

Практический вывод: вы **начинаете** на `sede.…` (там навигация), а **работаете** на
`www1.…` (там данные). Прыжок между доменами при клике — норма, не сбой.

Между ними стоит промежуточный экран **`SelectorAccesos.html`** — он спрашивает, чем
вы будете идентифицироваться, и уже потом пускает в приложение.

## Два входа: «по разделу» и «по модели»

Это ключ ко всей навигации Sede. Сервисы разложены **двумя разными способами**, и
нужное лежит то в одном, то в другом.

### Вход 1. Mi área personal — «что у меня происходит»

`sede.agenciatributaria.gob.es/Sede/mi-area-personal.html`

Ровно пять пунктов, и больше там нет ничего:

| Пункт | Зачем |
|---|---|
**Mis datos censales** | 👉 Режим, коды IAE, дата alta, перечень обязательных моделей. Здесь проверяется профиль |
**Mis notificaciones** | 👉 Уведомления и требования. Считаются полученными без вашего прочтения |
**Mis expedientes** | Ход процедур: рассрочки, апремио, проверки |
**Mis apoderamientos otorgados** | Доверенности. Здесь отзывается доступ прежнего гестора |
**Mis documentos pendientes de firma** | Документы, ждущие вашей подписи |

🔴 **Поданных деклараций здесь нет.** Ни 130, ни 303, ни 100. Это самая частая ошибка
навигации: логично искать «мои декларации» в «моём личном разделе», но их там не бывает.
Декларации разложены по моделям — см. вход 2.

Доступ к каждому пункту: **Cl@ve Móvil, сертификат или DNIe**.

### Вход 2. Каталог моделей — «что я делаю с моделью N»

Путь с главной, четыре клика:

```
Главная (sede.agenciatributaria.gob.es)
└── Presentación de declaraciones, calendario del contribuyente     ← блок «Destacados»
    └── Todas las declaraciones por modelo
        └── Presentar y consultar declaraciones                      ← каталог: 01, 04, 030, 036, 100, 130, 303…
            └── Modelo 303
                └── Todas las gestiones                              ← вот здесь всё по этой модели
```

⚠️ В блоке «Destacados» на главной пункт называется **«Presentación de declaraciones,
calendario del contribuyente»** — а не «Presentar y consultar declaraciones». Последнее
появляется только двумя уровнями ниже, как название каталога.

Короткий путь — сразу на страницу модели по её процедурному коду:

| Модель | Страница | Все gestiones |
|---|---|---|
100 (Renta) | `/Sede/procedimientoini/G229.shtml` | `/Sede/tramitacion/G229.shtml` |
130 (аванс IRPF) | `/Sede/procedimientoini/G601.shtml` | `/Sede/tramitacion/G601.shtml` |
303 (НДС) | `/Sede/procedimientoini/G414.shtml` | `/Sede/tramitacion/G414.shtml` |

💡 Эти же `G`-коды видны в дереве *Mis expedientes* (`…-01001-G229`). Удобно для сверки,
к какой модели относится expediente.

### Вход 3. Разделы вне моделей

Часть сервисов не привязана ни к личному разделу, ни к модели — они по задаче:

| Раздел | Зачем |
|---|---|
**Pagar, aplazar y consultar deudas** | Статус долгов, оплата. На главной — блок «Destacados» → *Pagar, aplazar y consultar* |
**Aplazamientos y fraccionamientos** → *Contestar requerimientos y otras gestiones* | 👉 Управление рассрочкой. **Платежи по рассрочке — только отсюда**, не через общую кнопку оплаты (см. `pitfalls.md` §3) |
**Calendario del contribuyente** | 🔴 Официальные сроки — первоисточник. Есть формат **iCalendar** для подписки |
**Registro electrónico** | Ответ на requerimiento, подача документов и alegaciones |
**Certificados tributarios** | Справки о налоговом положении: *Situación censal* и 👉 **Estar al corriente de obligaciones tributarias** (модель 01). Запрашивать можно заранее — см. `estar-al-corriente.md` |
**Suscripción a avisos informativos** | 👉 Оповещения на email/телефон. Включить сразу |
**Asientos registrales** | Ваши записи в электронном реестре AEAT |

## Что лежит в «Todas las gestiones» модели

Одинаковая структура блоков у 130 и 303:

| Блок | Что внутри |
|---|---|
**Presentación** | Подача + помощник (**Pre303** / **Pre 130**), предекларация-формуляр, подача по лотам |
**Simuladores** (только 303) | 👉 **Simulador 303 (OPEN)** — без входа. Свободно гонять цифры |
**Domiciliación** | Консультация, отзыв, реабилитация, исправление счёта списания |
**Consultar** | 👉 **«Modelo NNN. Consulta de declaraciones presentadas»** — вот где justificantes |
**Aportar documentación** | Ответ на requerimiento, досылка документов |
**Ejercicios anteriores** | Прошлые годы отдельной ссылкой |

### Отдельно отмечено — специфика 303

- 🔴 **Consulta de la cartera de cuotas de IVA a compensar** →
  `/wlpl/DAI3-RUTI/CarteraCuotas`
  Официальный «портфель» накопленного НДС-кредита. Это **первоисточник** по величине для
  casilla 110 — надёжнее, чем восстанавливать её вычитанием из прошлых деклараций.

  **Как заполнять форму** (проверено 2026-09-02):

  | Поле | Что вводить |
  |---|---|
  NIF | свой; titular — сам налогоплательщик |
  APELLIDOS Y NOMBRE / RAZÓN SOCIAL | свои; часто подставляется после NIF |
  EJERCICIO | **самый поздний** год |
  PERÍODO | **самый поздний** квартал, **только цифра** (`3`, не `3T`) |

  👉 Указывается последний период, а не каждый по очереди: сервис выводит остатки
  **за все предыдущие периоды сразу**. Формулировка на экране — *«cuotas a compensar
  pendientes de períodos anteriores»* — то есть кредит, пришедший в указанный период
  из прошлых. `[официальное разъяснение]`

  ⚠️ **Экспорта в PDF нет.** Сохранять страницу как HTML или печатью в PDF из браузера.
  Кладётся в корень `my-data/history/` как `cartera-cuotas-iva.html` — документ не
  привязан к одному году.

  ⚠️ Если в списке PERÍODO нет кварталов, а только месяцы `01`–`12` — периодичность НДС
  месячная, а не квартальная. Это меняет набор и сроки подач: остановиться и
  перепроверить профиль.
- **Instrucciones 2026** — официальные инструкции к форме за конкретный год. 👉 Именно
  здесь сверяется нумерация casillas, а не по памяти. Лежат и за прошлые годы (2025, 2024)
  — удобно, когда нужно понять, что означала графа в старой декларации.
- **Autoliquidación rectificativa** — с 2026 механика исправления собственной 303.

### Отдельно отмечено — специфика 130

- **«Ejercicio 2020 y siguientes. Presentación, utilizando datos de declaraciones
  anteriores»** — подача с подтягиванием данных прошлых деклараций года. Помогает не
  потерять накопительные графы (доход/расходы YTD, casilla 05). ⚠️ Подтянутое всё равно
  проверять: это удобство, а не гарантия.

## Прямые ссылки

> Проверено на живой Sede: 2026-09-02. `[NIF]` подставляется свой.
> Ссылки на `/wlpl/…` работают только внутри авторизованной сессии.

| Сервис | URL |
|---|---|
Все поданные декларации, любые модели | `www1.agenciatributaria.gob.es/wlpl/SCEJ-MANT/CONSUL/index.zul?MODELO=&EJERCICIO=0&NIFOBLIGADO=[NIF]` |
То же по одной модели | тот же URL с `MODELO=303` |
Mis datos censales | `www1.agenciatributaria.gob.es/wlpl/BUGC-JDIT/MdcAcceso?nifRepresentado=[NIF]&E_HNR=&EJERCICIO=0` |
Cartera de cuotas de IVA a compensar | `www1.agenciatributaria.gob.es/wlpl/DAI3-RUTI/CarteraCuotas` |
Consultar sus domiciliaciones | `www1.agenciatributaria.gob.es/wlpl/ECDM-MANT/DomQueryN` |
Notificaciones no leídas | `www1.agenciatributaria.gob.es/wlpl/GNNO-JDIT/ResumenInteresados` |
Mis expedientes | `www1.agenciatributaria.gob.es/wlpl/TEWV-CORE/ResumenVlt` |
Mis últimos accesos | `www1.agenciatributaria.gob.es/wlpl/ADHT-AUTH/UltimasConexionesW` |
Mi área personal | `sede.agenciatributaria.gob.es/Sede/mi-area-personal.html` |
Simulador 303 2026 (без входа) | `www2.agenciatributaria.gob.es/wlpl/A303-FWME/E2026/OPEN/index.zul` |
Asientos registrales | `www1.agenciatributaria.gob.es/wlpl/REGD-JDIT/SvRegMisAsiIntQue` |
Calendario del contribuyente | `sede.agenciatributaria.gob.es/Sede/en_gb/calendario-contribuyente.html` |
Calendario — iCalendar (подписка) | `sede.agenciatributaria.gob.es/Sede/en_gb/ayuda/calendario-contribuyente/icalendar.html` |
Проверка подлинности документа по CSV | `sede.administracion.gob.es/pagSedeFront/servicios/consultaCSV.htm` |

⚠️ Ссылки с `NIFOBLIGADO=` и `nifRepresentado=` несут NIF в query-строке. Не пересылайте
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
декларации. Квартальных 130 и 303 здесь не будет никогда. Пустая ветка IRPF **не значит**,
что декларации не подавались; она значит, что по ним не открыто процедур.

Обратное тоже верно и полезно: **expediente в закладке *En tramitación* — это
незакрытая процедура.** Открытый expediente по модели 100 может быть чем угодно —
обработка возврата, *comprobación limitada*, *paralela*. Что именно — видно только
внутри expediente, из истории actuaciones. Не выводить по названию ветки.

💡 Ветка *Certificados → Censales* стоит проверять первой: если сертификат
*Situación censal* уже выдавался, PDF с режимом и кодами IAE можно скачать оттуда, не
запрашивая заново. ⚠️ Сверить дату: сертификат отражает положение на момент выдачи.

## Первые шаги при переходе на самоподачу

- [ ] Получить и проверить собственный доступ (Cl@ve Móvil, сертификат или DNIe)
- [ ] *Mi área personal → Mis datos censales* → выписать режим, коды IAE, список
      обязательных моделей
- [ ] *Modelo 130 / 303 → Todas las gestiones → Consulta de declaraciones presentadas* →
      скачать декларации, поданные гестором, как образец заполнения
- [ ] *Pagar, aplazar y consultar deudas* → убедиться, что нет незамеченных долгов
- [ ] *Mi área personal → Mis expedientes* → закладка *En tramitación*: нет ли
      незакрытых процедур
- [ ] *Modelo 303 → Todas las gestiones → Cartera de cuotas de IVA a compensar* →
      зафиксировать накопленный НДС-кредит
- [ ] *Domiciliaciones* → сверить, какие списания привязаны к счёту
- [ ] *Mi área personal → Mis notificaciones* + *Suscripción a avisos informativos* →
      включить оповещения
- [ ] *Mi área personal → Mis apoderamientos otorgados* → кто имеет к вам доступ
- [ ] Скачать *Instrucciones* к 130 и 303 за текущий год — сверить нумерацию casillas
- [ ] Первую самостоятельную подачу прогнать через **Pre303** / **Pre 130**, а цифры
      предварительно — через **Simulador 303 (OPEN)**

## Полезно знать

- У AEAT есть телефонная поддержка и запись на приём (*cita previa*). Для сложных
  случаев это работает и бесплатно.
- *Calendario del contribuyente* — 🔴 первоисточник по срокам:
  https://sede.agenciatributaria.gob.es/Sede/en_gb/calendario-contribuyente.html
  Доступен как HTML и как **iCalendar** — подписаться можно прямо из официального
  источника. Внешние календари и боты (см. `deadlines.md`) удобны фильтрацией под
  профиль и напоминаниями, но **не видят** адресованные лично вам требования: для этого
  только *Mis notificaciones*.
- *Justificante de presentación* — единственное доказательство подачи. Сохраняйте PDF
  каждой декларации (в `my-data/`, не в git). У каждого документа есть **CSV** (*Código
  Seguro de Verificación*) — по нему подлинность проверяется на общей сервисной странице
  госадминистрации, ссылка выше. Полезно, когда justificante прислал кто-то другой,
  например прежний гестор.
- Интерфейс Sede переключается на **английский** (ES / CA / GL / VA / EN в правом
  верхнем углу). Для неносителя испанского это заметно снижает цену ошибки при чтении
  формы. ⚠️ Названия casillas в переводе иногда расходятся с официальной терминологией —
  сверять номера, а не подписи.
- Срок хранения документов по налоговым обязательствам — не менее **4 лет**
  (срок давности *prescripción*). Практичнее — 6 лет.
